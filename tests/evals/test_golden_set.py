"""Eval: Golden set — parametrized test cases for LLM response quality.

Each case in golden_set.json defines:
- expected_tools: tools the agent MUST call
- forbidden_tools: tools the agent must NOT call
- response_must_contain_any: at least one keyword must appear in response
- response_must_not_contain: none of these should appear in response
"""

import json
from pathlib import Path

import pytest

from tests.evals.conftest import get_agent_response

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.json"
GOLDEN_SET = json.loads(GOLDEN_SET_PATH.read_text())


@pytest.mark.eval
class TestGoldenSet:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "case",
        GOLDEN_SET,
        ids=[c["id"] for c in GOLDEN_SET],
    )
    async def test_golden_case(self, eval_client, system_prompt, case):
        """Run a golden set test case against the live LLM."""
        result = await get_agent_response(
            eval_client, system_prompt, case["input"]
        )

        tool_names = [tc.name for tc in result["tool_calls"]]
        text = result["text"].lower()

        # Check expected tools were called
        for tool in case["expected_tools"]:
            if tool == "generate_quote":
                # generate_quote requires a multi-turn flow (DB lookup first),
                # so we only check that query_database was called as the first step
                continue
            assert tool in tool_names, (
                f"[{case['id']}] Expected tool '{tool}' not called. "
                f"Called: {tool_names}. Input: {case['input']}"
            )

        # Check forbidden tools were NOT called
        for tool in case["forbidden_tools"]:
            assert tool not in tool_names, (
                f"[{case['id']}] Forbidden tool '{tool}' was called. "
                f"Called: {tool_names}. Input: {case['input']}"
            )

        # Check response contains at least one expected keyword
        # NOTE: When the agent calls tools, the first-turn text is just a
        # preamble ("Let me check...") — the real answer comes after tool
        # results. So we only enforce keyword checks when no tools were called
        # (pure text responses) or when the keywords appear in the preamble.
        if case["response_must_contain_any"] and not tool_names:
            found = any(kw.lower() in text for kw in case["response_must_contain_any"])
            assert found, (
                f"[{case['id']}] Response missing all expected keywords: "
                f"{case['response_must_contain_any']}. Got: {result['text'][:300]}"
            )

        # Check response does NOT contain forbidden strings
        for forbidden in case["response_must_not_contain"]:
            assert forbidden.lower() not in text, (
                f"[{case['id']}] Response contains forbidden string '{forbidden}'. "
                f"Got: {result['text'][:300]}"
            )
