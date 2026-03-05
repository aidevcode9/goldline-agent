"""Eval: Hallucination detection — the agent should NOT invent products,
prices, or policies that don't exist in the database or knowledge base."""

import pytest

from tests.evals.conftest import get_agent_response


@pytest.mark.eval
class TestHallucination:
    @pytest.mark.asyncio
    async def test_nonexistent_product_not_invented(self, eval_client, system_prompt):
        """When asked about a product we don't carry, the agent should say so
        rather than making up details."""
        result = await get_agent_response(
            eval_client, system_prompt,
            "Do you have any industrial welding equipment?"
        )
        text = result["text"].lower()

        # Agent should indicate we don't carry this
        honesty_signals = [
            "don't carry", "don't have", "don't sell",
            "do not carry", "do not have", "do not sell",
            "not something we", "outside", "don't stock",
            "not available", "not in our", "unfortunately",
            "isn't something", "aren't something",
            "office supplies", "can't find",
        ]
        found = any(signal in text for signal in honesty_signals)
        assert found, (
            f"Agent should acknowledge we don't carry welding equipment. "
            f"Got: {result['text'][:300]}"
        )

    @pytest.mark.asyncio
    async def test_no_fake_prices(self, eval_client, system_prompt):
        """Agent should look up prices from DB, not invent them."""
        result = await get_agent_response(
            eval_client, system_prompt,
            "How much does a ream of copy paper cost?"
        )
        # Agent should use query_database to get real prices
        tool_names = [tc.name for tc in result["tool_calls"]]
        assert "query_database" in tool_names, (
            f"Agent should query database for prices, not guess. "
            f"Tools called: {tool_names}"
        )

    @pytest.mark.asyncio
    async def test_no_fake_policies(self, eval_client, system_prompt):
        """Agent should search knowledge base for policies, not invent them."""
        result = await get_agent_response(
            eval_client, system_prompt,
            "What's your warranty policy on office chairs?"
        )
        tool_names = [tc.name for tc in result["tool_calls"]]

        # Should use knowledge base OR honestly say it doesn't know
        uses_kb = "search_knowledge_base" in tool_names
        text = result["text"].lower()
        honest = any(kw in text for kw in [
            "not sure", "don't have", "check with",
            "contact", "couldn't find", "not aware",
        ])

        assert uses_kb or honest, (
            f"Agent should search KB or admit uncertainty about warranty policy. "
            f"Tools: {tool_names}, Text: {result['text'][:300]}"
        )

    @pytest.mark.asyncio
    async def test_empty_db_result_handled(self, eval_client, system_prompt):
        """When searching for a very specific product that likely won't match,
        agent should handle gracefully."""
        result = await get_agent_response(
            eval_client, system_prompt,
            "Do you have gold-plated fountain pens with diamond tips?"
        )
        # Agent should query DB and then honestly report results
        tool_names = [tc.name for tc in result["tool_calls"]]
        assert "query_database" in tool_names, (
            f"Agent should at least check database. Tools: {tool_names}"
        )
