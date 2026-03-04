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
- `src/agent.py` — Core agent logic (tool loop, system prompt, knowledge base)
- `src/cli.py` — Rich CLI entry point
- `src/config.py` — All branding constants and configuration
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
- System prompt lives in `src/agent.py` — keep it as a single string, not a template
- Use `uv` for all dependency management — no pip, no requirements.txt

## Red Flags
- Don't expose actual stock quantities to users (see stock policy in system prompt)
- Don't commit .env files or API keys
- Don't modify knowledge base docs without regenerating embeddings (happens automatically on next run)

## Testing
- Manual: run the agent and test product queries, policy questions, multi-turn conversation
- Verify LangSmith traces appear in the `goldline-agent` project
