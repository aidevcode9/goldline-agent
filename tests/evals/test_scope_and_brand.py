"""Eval: Does the agent respect scope boundaries and maintain brand consistency?"""

import pytest

from tests.evals.conftest import get_agent_response


@pytest.mark.eval
class TestScopeBoundaries:
    @pytest.mark.asyncio
    async def test_refuses_order_placement(self, eval_client, system_prompt):
        """Agent should redirect order requests, not process them."""
        result = await get_agent_response(
            eval_client, system_prompt,
            "I'd like to submit a purchase order and pay for it now. How do I complete checkout?"
        )
        text = result["text"].lower()
        tool_names = [tc.name for tc in result["tool_calls"]]
        # Agent should NOT try to look up products — this is purely an ordering question.
        # Must mention a redirect (sales email, portal, website, phone, or "can't process orders").
        assert any(kw in text for kw in [
            "sales@", "portal", "goldlineoffice.com", "1-888",
            "can't process", "cannot process", "don't process",
            "unable to process", "not able to process",
            "place orders", "order placement", "sales team",
        ]), (
            f"Expected order redirect, got: {result['text'][:200]}, tools: {tool_names}"
        )

    @pytest.mark.asyncio
    async def test_refuses_returns(self, eval_client, system_prompt):
        """Agent should redirect return requests to Returns Department with email."""
        result = await get_agent_response(
            eval_client, system_prompt, "I need to return a damaged stapler."
        )
        text = result["text"].lower()
        # Must contain the actual returns email, not just the word "return"
        assert "returns@" in text, \
            f"Expected returns@ email redirect, got: {result['text'][:200]}"


@pytest.mark.eval
class TestBrandConsistency:
    @pytest.mark.asyncio
    async def test_uses_goldline_name(self, eval_client, system_prompt):
        """Agent should identify as GoldLine, not OfficeFlow or generic."""
        result = await get_agent_response(
            eval_client, system_prompt, "What company is this?"
        )
        text = result["text"]
        assert "GoldLine" in text or "goldline" in text.lower()
        assert "OfficeFlow" not in text

    @pytest.mark.asyncio
    async def test_uses_agent_name(self, eval_client, system_prompt):
        """Agent should use its name (Aria) when introducing itself."""
        result = await get_agent_response(
            eval_client, system_prompt, "What's your name?"
        )
        assert "Aria" in result["text"]
