# GoldLine Office Supplies — AI Customer Support Agent

> Premium supplies. Proven reliability.

An AI-powered customer support agent built with **Claude** (Anthropic), featuring semantic knowledge base search, real-time inventory queries, and full observability through **LangSmith** tracing.

## Architecture

| Component | Technology |
|-----------|-----------|
| LLM | Claude Haiku 4.5 (Anthropic) |
| Embeddings | OpenAI text-embedding-3-small |
| Observability | LangSmith — every conversation is traced |
| Tools | SQL inventory queries + semantic knowledge base search |
| Database | SQLite (product inventory with 15 items) |
| CLI | Rich — styled output, spinners, markdown rendering |

## Quick Start

```bash
# 1. Clone and enter the repo
git clone <repo-url> && cd goldline-agent

# 2. Copy env file and fill in API keys
cp .env.example .env

# 3. Install dependencies and run
uv sync
uv run goldline
```

You'll need API keys for:
- **Anthropic** — powers the agent (Claude Haiku 4.5)
- **OpenAI** — generates embeddings for knowledge base search
- **LangSmith** — traces conversations (optional but recommended)

## What It Can Do

- **Product queries** — "Do you have copy paper?" / "What's the cheapest pen?"
- **Policy lookup** — "What's your return policy?" / "How does shipping work?"
- **Inventory awareness** — stock-level language policy (never reveals exact quantities)
- **Multi-turn conversation** — remembers context within a session
- **Smart routing** — directs customers to the right department when it can't help directly

## Technical Highlights

- **Agentic tool-use loop** — Claude autonomously decides which tools to call
- **Automatic embedding regeneration** — detects when knowledge base docs change
- **Full conversation tracing** — every interaction logged to LangSmith
- **Cosine similarity search** — whole-document embeddings, no chunking
- **Rich CLI** — branded output, thinking spinners, markdown rendering

## Project Structure

```
src/
├── agent.py       # Core agent logic, system prompt, tool definitions
├── cli.py         # Rich CLI entry point
└── config.py      # Branding constants

knowledge_base/
└── documents/     # 5 company policy markdown files

inventory/
├── inventory.db       # SQLite product catalog
└── seed_inventory.py  # Script to regenerate the DB
```

## Regenerating Data

```bash
# Rebuild inventory database
uv run python inventory/seed_inventory.py

# Embeddings regenerate automatically when documents change
```
