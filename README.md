# GoldLine Office Supplies — AI Customer Support Agent

> Premium supplies. Proven reliability.

An AI-powered customer support agent built with **Claude** (Anthropic), featuring a split-screen web UI with real-time Agent Reasoning View, PDF quote generation, semantic knowledge base search, and full observability through **LangSmith** tracing.

## Demo

```
+----------------------------------------------------------+
|  [GL] GoldLine Office Supplies     Agent Reasoning View   |
+----------------------------+-----------------------------+
|                            |                             |
|   ChatPanel                |   TracePanel                |
|                            |                             |
|   User: Do you have        |   [tool_call] query_database|
|   copy paper?              |   SELECT * FROM products... |
|                            |   [tool_result] 45ms        |
|   Aria: Yes! We carry      |                             |
|   several types of copy    |   Latency: 2.5s             |
|   paper in stock...        |   Tokens: 145 in / 89 out  |
|                            |   Tool calls: 1             |
|   [Ask about products...]  |                             |
|                  [Send]    |                             |
+----------------------------+-----------------------------+
```

## Architecture

```
+------------------+   SSE    +------------------+   SDK   +------------------+
|   Next.js Web    | -------> |  FastAPI Backend  | ------> | Anthropic Claude |
|   (port 3000)    | <------- |  (port 8000)      | <------ | Haiku 4.5        |
+------------------+  events  +--------+---------+         +------------------+
                               |       |       |
                      +--------+  +----+  +----+-------+
                      v           v        v            v
                  +-------+  +-------+  +-------+  +----------+
                  |SQLite |  |  KB   |  | Quotes|  | LangSmith|
                  |215 prd|  |5 docs |  | PDFs  |  | Traces   |
                  +-------+  +-------+  +-------+  +----------+
```

| Component | Technology |
|-----------|-----------|
| LLM | Claude Haiku 4.5 (Anthropic) |
| Embeddings | OpenAI text-embedding-3-small |
| Backend | FastAPI + SSE streaming |
| Frontend | Next.js 16 + React 19 + Tailwind CSS v4 |
| Database | SQLite (215 products across 19 categories) |
| PDF | fpdf2 (branded quote generation) |
| Observability | LangSmith (every conversation traced) |
| CLI | Rich (styled output, spinners, markdown) |

## Quick Start

```bash
# 1. Clone and install
git clone <repo-url> && cd goldline-agent
cp .env.example .env        # Fill in API keys
uv sync

# 2. Seed the database
uv run python inventory/seed_inventory.py

# 3. Start backend (terminal 1)
uv run uvicorn src.api:app --reload --port 8000

# 4. Start frontend (terminal 2)
cd web && npm install && npm run dev

# 5. Open http://localhost:3000
```

**CLI mode** (no web UI needed):
```bash
uv run goldline
```

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...         # Claude API
OPENAI_API_KEY=sk-proj-...           # Embeddings

# Optional — Tracing
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=goldline-agent

# Optional — Deployment (defaults work for local dev)
CORS_ORIGINS=http://localhost:3000   # Comma-separated allowed origins
DATABASE_PATH=                       # Default: inventory/inventory.db
QUOTE_OUTPUT_DIR=                    # Default: generated_quotes/
```

## Features

### 3 Agent Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `query_database` | SQL queries against 215-product inventory | "Do you have copy paper?" |
| `search_knowledge_base` | Semantic search of company policies | "What's your return policy?" |
| `generate_quote` | Branded PDF quote with validated pricing | "Quote me 50 reams of paper" |

### Agent Reasoning View

Split-screen UI showing the agent's real-time thinking process:
- Tool calls with SQL queries and inputs
- Tool results with latency measurements
- Token usage (input/output)
- Total request latency

### PDF Quote Generator

Customers can request formal quotes and receive downloadable branded PDFs:
- Gold-branded header with company info
- Line items table with validated pricing from database
- Subtotal, tax (8%), and total
- 30-day validity, sequential quote numbering (`GQ-YYYYMMDD-NNNN`)

### Conversational Memory

Thread-based conversation history — the agent remembers context across turns. Ask about products, then say "give me a quote for the recycled one" and it knows what you mean.

### Security Hardening

- Stock quantities never exposed (code-level sanitization, not just prompt)
- SQL allowlist (SELECT/PRAGMA only, read-only connection)
- PDF text sanitization (control chars stripped, length caps)
- Path traversal prevention on quote downloads
- XSS-safe link rendering in frontend
- Price validation from database (LLM cannot hallucinate prices)

## Project Structure

```
src/
├── agent.py          # Core agent: tool loop, streaming, history
├── api.py            # FastAPI endpoints (health, chat, stream, quotes)
├── cli.py            # Rich CLI entry point
├── config.py         # All branding constants + settings
├── history.py        # In-memory thread store
├── knowledge.py      # Embedding-based semantic search
├── prompts.py        # System prompt builder
├── quotes.py         # PDF quote generation (fpdf2)
└── tools.py          # Tool definitions, dispatch, stock sanitization

web/app/
├── page.tsx                  # Split-screen layout
├── components/
│   ├── ChatPanel.tsx         # Chat messages, input, "New Chat"
│   └── TracePanel.tsx        # Agent Reasoning View
└── hooks/
    └── useChat.ts            # SSE client, thread management

knowledge_base/documents/     # 5 company policy markdown files
inventory/                    # SQLite DB + seeder (215 products)
tests/                        # 59 unit tests + 29 LLM evals
```

## Testing

```bash
uv run pytest tests/ -v                # All 88 tests
uv run pytest tests/evals/ -v          # LLM evals only (needs API keys)
```

| Test Area | Tests | Coverage |
|-----------|-------|----------|
| Tool safety (SQL allowlist, sanitization) | 38 | Stock leakage, SQL injection, query execution |
| System prompt integrity | 10 | Branding, no hardcoded values, policy presence |
| Knowledge base | 6 | Embedding staleness, relevance threshold |
| Conversation history | 6 | Thread creation, save/retrieve, isolation |
| Golden set evals | 16 | Product search, policy lookup, quotes, greetings, scope, brand, pricing |
| Hallucination detection | 4 | No fake products, prices, or policies |
| Multi-turn quote flow | 2 | DB lookup → generate_quote tool chain |
| Stock leakage evals | 6 | Quantity sanitization under various query patterns |
| Scope & brand evals | 4 | Scope boundaries, brand consistency |
| Tool routing evals | 3 | Correct tool selection per question type |

## Deployment

### Frontend → Vercel

1. Import repo on [vercel.com](https://vercel.com) → "Add New Project"
2. Set **Root Directory** to `web`
3. Add environment variable:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://<your-railway-url>` |

4. Deploy — Vercel auto-detects Next.js

### Backend → Railway

1. Create project on [railway.com](https://railway.com) → "Deploy from GitHub Repo"
2. Railway auto-detects the `Dockerfile`
3. Add a **persistent volume** mounted at `/data`
4. Set environment variables:

| Variable | Value | Required |
|----------|-------|----------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Yes |
| `OPENAI_API_KEY` | `sk-proj-...` | Yes |
| `CORS_ORIGINS` | `https://your-app.vercel.app` | Yes |
| `DATABASE_PATH` | `/data/inventory.db` | Yes |
| `QUOTE_OUTPUT_DIR` | `/data/quotes` | Yes |
| `PORT` | `8000` | Yes |
| `LANGSMITH_API_KEY` | `lsv2_pt_...` | Optional |
| `LANGSMITH_TRACING` | `true` | Optional |
| `LANGSMITH_PROJECT` | `goldline-agent` | Optional |

5. Deploy — the startup script auto-seeds the DB on first run

**Important:** After both are deployed, copy the Vercel URL into Railway's `CORS_ORIGINS` and the Railway URL into Vercel's `NEXT_PUBLIC_API_URL`.

### Security

- All API keys are environment variables — never committed to Git
- CORS restricted to your Vercel domain only
- Railway volumes encrypted at rest
- Both platforms enforce HTTPS by default
- SQL allowlist (SELECT/PRAGMA only) prevents destructive queries
- PDF downloads validated with filename regex + path traversal prevention

## Regenerating Data

```bash
# Rebuild inventory database (215 products)
uv run python inventory/seed_inventory.py

# Embeddings regenerate automatically when documents change
```

## Documentation

See [TECHNICAL.md](TECHNICAL.md) for the full technical specification including architecture diagrams, API contracts, SSE event formats, and security details.
