# GoldLine Agent

## Project Overview
AI customer support agent for GoldLine Office Supplies, powered by Claude (Anthropic).
Uses LangSmith for tracing, OpenAI for embeddings, SQLite for inventory.

## Tech Stack
- Python 3.12+
- Anthropic SDK (Claude Haiku 4.5) — main LLM
- OpenAI SDK — embeddings only (text-embedding-3-small)
- LangSmith — observability and tracing
- Rich — CLI presentation
- SQLite — inventory database
- NumPy — cosine similarity

## Project Structure
- `src/agent.py` — Chat orchestration (tool loop only, ~85 lines)
- `src/cli.py` — Rich CLI entry point
- `src/config.py` — All branding constants and configuration
- `src/knowledge.py` — Knowledge base loading, embedding, and semantic search
- `src/tools.py` — Tool definitions and execution dispatch
- `src/prompts.py` — System prompt builder
- `src/history.py` — Conversation thread store
- `knowledge_base/documents/` — Company policy markdown docs (5 files)
- `inventory/inventory.db` — Product catalog (regenerate with seed_inventory.py)

## Commands
- Install: `uv sync`
- Run: `uv run goldline` or `uv run python -m src.cli`
- Seed DB: `uv run python inventory/seed_inventory.py`

## Conventions
- Commit format: `type(scope): description` (feat, fix, test, docs, refactor, chore)
- All branding constants live in `src/config.py` — never hardcode company name/phone/email
- Embeddings are auto-generated and gitignored — don't commit them
- System prompt lives in `src/prompts.py` — keep it as a single string builder, not a template
- No Python file should exceed 500 lines; no single component/class should exceed 200 lines
- Follow DRY and SOLID principles — each module has a single responsibility
- Use `uv` for all dependency management — no pip, no requirements.txt

## Red Flags
- Don't expose actual stock quantities to users (conservative sanitization in tools.py)
- Don't commit .env files or API keys
- Don't modify knowledge base docs without regenerating embeddings (happens automatically on next run)
- SQL queries restricted to `products` table only — don't add other tables to the allowlist without review
- API auth (`API_SECRET_KEY`) is disabled when env var unset (local dev only) — always set in production
- Quote IDs use UUIDs — don't revert to sequential numbering (enumeration risk)

## Testing
- Unit tests: `uv run pytest tests/ -m "not eval" -v`
- LLM evals: `uv run pytest tests/evals/ -m eval -v` (requires ANTHROPIC_API_KEY)
- All tests: `uv run pytest tests/ -v`
- Test files mirror source: `src/tools.py` → `tests/test_tools.py`
- Evals in `tests/evals/` — test LLM behavior (tool routing, stock leakage, scope, brand)
- Manual: run the agent and test product queries, policy questions, multi-turn conversation
- Verify LangSmith traces appear in the `goldline-agent` project
