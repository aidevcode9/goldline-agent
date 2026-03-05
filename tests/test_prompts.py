"""Tests for src/prompts.py — branding and content checks."""

from src.config import COMPANY_NAME, AGENT_NAME, MAIN_PHONE, EMAIL_DOMAIN
from src.prompts import build_system_prompt


class TestBuildSystemPrompt:
    def setup_method(self):
        self.prompt = build_system_prompt()

    def test_contains_company_name(self):
        assert COMPANY_NAME in self.prompt

    def test_contains_agent_name(self):
        assert AGENT_NAME in self.prompt

    def test_contains_phone(self):
        assert MAIN_PHONE in self.prompt

    def test_contains_email_domain(self):
        assert EMAIL_DOMAIN in self.prompt

    def test_no_hardcoded_officeflow(self):
        assert "OfficeFlow" not in self.prompt

    def test_no_hardcoded_placeholder(self):
        """Ensure no unresolved f-string placeholders."""
        assert "{COMPANY_NAME}" not in self.prompt
        assert "{AGENT_NAME}" not in self.prompt
        assert "{EMAIL_DOMAIN}" not in self.prompt

    def test_stock_policy_present(self):
        assert "STOCK INFORMATION POLICY" in self.prompt

    def test_tool_instructions_present(self):
        assert "query_database" in self.prompt
        assert "search_knowledge_base" in self.prompt

    def test_scope_boundaries_present(self):
        assert "CANNOT DIRECTLY HANDLE" in self.prompt
        assert f"sales@{EMAIL_DOMAIN}" in self.prompt
        assert f"returns@{EMAIL_DOMAIN}" in self.prompt
