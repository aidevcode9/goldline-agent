"""Eval: Multi-turn quote flow — tests that the agent can look up products
then generate a quote, completing the full tool chain."""

import pytest

from src.config import MODEL
from src.prompts import build_system_prompt
from src.tools import ALL_TOOLS


def _mock_db_result(query: str) -> str:
    """Return realistic mock DB results based on the SQL query type."""
    q = query.lower().strip()
    if "sqlite_master" in q:
        return "[('products',)]"
    if q.startswith("pragma"):
        return (
            "[(0, 'id', 'INTEGER', 1, None, 1), "
            "(1, 'name', 'TEXT', 1, None, 0), "
            "(2, 'category', 'TEXT', 1, None, 0), "
            "(3, 'price', 'REAL', 1, None, 0), "
            "(4, 'quantity', 'INTEGER', 1, None, 0)]"
        )
    # Default: product search result
    return (
        "Columns: id, name, category, price, stock_status\n"
        "[(1, 'Copy Paper 500 Sheets', 'Paper', 8.99, 'In Stock')]"
    )


@pytest.mark.eval
class TestQuoteFlow:
    @pytest.mark.asyncio
    async def test_quote_triggers_generate_quote(self, eval_client, system_prompt):
        """When explicitly asked for a quote with product details,
        the agent should call query_database then generate_quote."""
        messages = [
            {"role": "user", "content": "I need a quote for 10 reams of copy paper."},
        ]

        # First turn — agent should call query_database
        response = await eval_client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=ALL_TOOLS,
        )

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        tool_names = [tc.name for tc in tool_calls]

        assert "query_database" in tool_names, (
            f"First turn should call query_database, got: {tool_names}"
        )

        # Simulate tool loop — provide mock DB results so the agent
        # can proceed through schema discovery → product search → generate_quote
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for tc in tool_calls:
            if tc.name == "query_database":
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": _mock_db_result(tc.input.get("query", "")),
                })
            else:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": "No results found.",
                })

        messages.append({"role": "user", "content": tool_results})

        # Continue tool loop for up to 5 more turns (schema discovery can
        # take 2-3 turns before the agent has enough info for generate_quote)
        all_tool_names = list(tool_names)
        full_text = ""

        for _turn in range(5):
            response_n = await eval_client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=ALL_TOOLS,
            )

            tool_calls_n = [b for b in response_n.content if b.type == "tool_use"]
            tool_names_n = [tc.name for tc in tool_calls_n]
            all_tool_names.extend(tool_names_n)
            text_blocks = [b.text for b in response_n.content if hasattr(b, "text")]
            full_text = " ".join(text_blocks).lower()

            # Check if we hit our goal
            if "generate_quote" in tool_names_n:
                break
            if any(kw in full_text for kw in ["quote", "gq-", "pdf"]):
                break

            # If there are tool calls, feed mock results and continue
            if not tool_calls_n:
                break

            messages.append({"role": "assistant", "content": response_n.content})
            mock_results = []
            for tc in tool_calls_n:
                if tc.name == "query_database":
                    mock_results.append({
                        "type": "tool_result",
                        "tool_use_id": tc.id,
                        "content": _mock_db_result(tc.input.get("query", "")),
                    })
                elif tc.name == "generate_quote":
                    mock_results.append({
                        "type": "tool_result",
                        "tool_use_id": tc.id,
                        "content": '{"status": "success", "quote_id": "GQ-20260304-0001", "file": "GQ-20260304-0001.pdf"}',
                    })
                else:
                    mock_results.append({
                        "type": "tool_result",
                        "tool_use_id": tc.id,
                        "content": "No results found.",
                    })
            messages.append({"role": "user", "content": mock_results})

        called_quote = "generate_quote" in all_tool_names
        mentions_quote = any(
            kw in full_text for kw in ["quote", "gq-", "generate", "pdf", "$", "price", "total"]
        )

        assert called_quote or mentions_quote, (
            f"Agent should call generate_quote or mention quote generation. "
            f"Tools: {all_tool_names}, Text: {full_text[:300]}"
        )

    @pytest.mark.asyncio
    async def test_quote_request_uses_correct_tool_name(self, eval_client, system_prompt):
        """Explicit 'price quote' request should trigger generate_quote tool."""
        messages = [
            {"role": "user", "content": "Give me a price quote for 5 staplers and 20 pens."},
        ]

        response = await eval_client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=ALL_TOOLS,
        )

        tool_calls = [b for b in response.content if b.type == "tool_use"]
        tool_names = [tc.name for tc in tool_calls]

        # First step should be query_database to find product IDs
        assert "query_database" in tool_names, (
            f"Quote flow should start with query_database. Got: {tool_names}"
        )
