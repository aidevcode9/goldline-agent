"""Eval: Does the agent select the correct tool for different question types?"""

import pytest

from tests.evals.conftest import get_agent_response


@pytest.mark.eval
class TestToolRouting:
    @pytest.mark.asyncio
    async def test_product_query_uses_database(self, eval_client, system_prompt):
        """Product questions should trigger query_database."""
        result = await get_agent_response(
            eval_client, system_prompt, "Do you have any copy paper in stock?"
        )
        assert result["stop_reason"] == "tool_use"
        tool_names = [tc.name for tc in result["tool_calls"]]
        assert "query_database" in tool_names

    @pytest.mark.asyncio
    async def test_policy_query_uses_knowledge_base(self, eval_client, system_prompt):
        """Policy questions should trigger search_knowledge_base."""
        result = await get_agent_response(
            eval_client, system_prompt, "What is your return policy?"
        )
        assert result["stop_reason"] == "tool_use"
        tool_names = [tc.name for tc in result["tool_calls"]]
        assert "search_knowledge_base" in tool_names

    @pytest.mark.asyncio
    async def test_greeting_uses_no_tools(self, eval_client, system_prompt):
        """Simple greetings should not trigger any tools."""
        result = await get_agent_response(
            eval_client, system_prompt, "Hi there!"
        )
        assert result["stop_reason"] == "end_turn"
        assert len(result["tool_calls"]) == 0
