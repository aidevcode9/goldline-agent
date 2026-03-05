# GoldLine Agent — Technical Documentation

## Architecture Diagram

```
                                 +---------------------------+
                                 |      LangSmith Cloud      |
                                 |   (Observability/Traces)  |
                                 +-------------+-------------+
                                               ^
                                               | traces
                                               |
+------------------+    SSE     +----------------------------------+     SDK      +------------------+
|                  |  /chat/    |                                  |  ----------> |  Anthropic API   |
|   Next.js Web    |  stream   |        FastAPI Backend           |              |  Claude Haiku    |
|   (port 3000)    | --------> |        (port 8000)               |              |  4.5             |
|                  |            |                                  | <----------  +------------------+
|  +------------+  |    JSON    |  +----------+    +-----------+   |   response
|  | ChatPanel  |  | <-----    |  | agent.py |    | api.py    |   |
|  +------------+  |    SSE     |  |          |    |           |   |     SDK      +------------------+
|  +------------+  |  events    |  | Tool     |    | /health   |   |  ----------> |  OpenAI API      |
|  | TracePanel |  |            |  | Loop     |    | /chat     |   |              |  Embeddings      |
|  +------------+  |            |  |          |    | /chat/    |   |              |  text-embedding-  |
|  +------------+  |            |  +----+-----+    |  stream   |   |              |  3-small          |
|  | useChat    |  |  GET       |       |          | /quotes/  |   | <----------  +------------------+
|  | (SSE hook) |  |  /quotes/  |       v          |  {file}   |   |   embeddings
|  +------------+  |  {file}    |  +---------+     +-----------+   |
+------------------+ --------> |  | tools.py |                    |
        ^                       |  +---------+                    |
        |                       |   |   |   |                     |
   User Browser                 |   v   v   v                     |
                                |  +--+ +-+ +--+                  |
                                |  |DB| |KB| |Q |                 |
                                |  +--+ +--+ +--+                 |
                                +---|----|----|-------------------+
                                    |    |    |
                          +---------+    |    +-----------+
                          v              v                v
                   +------------+  +------------+  +------------+
                   | SQLite     |  | Knowledge  |  | generated  |
                   | inventory  |  | Base       |  | _quotes/   |
                   | .db        |  | /documents |  | *.pdf      |
                   | (215 items)|  | (5 docs)   |  |            |
                   +------------+  +------------+  +------------+
```

```
Data Flow — Single User Message:

  User types "quote on 50 copy paper"
       |
       v
  [useChat.ts] POST /chat/stream {message, thread_id}
       |
       v
  [api.py] → [agent.py] chat_stream(question, tid)
       |
       v
  [agent.py] Load history → Build messages → Call Claude API
       |
       v
  Claude returns tool_use: query_database
       |                                        SSE events streamed
       v                                        back to frontend:
  [tools.py] Execute SQL → Sanitize stock  -->  event: tool_call
       |                                        event: tool_result
       v
  Claude returns tool_use: generate_quote
       |
       v
  [quotes.py] Validate → Fetch prices     -->  event: tool_call
       |       → Build PDF → Save file          event: tool_result
       v
  Claude returns final text with link      -->  event: text
       |                                        event: done {thread_id}
       v
  [useChat.ts] Captures thread_id for next turn
  [ChatPanel]  Renders message + clickable PDF link
  [TracePanel] Shows all tool calls with latency
```

---

## 1. Overview

GoldLine Agent is an AI customer support system for GoldLine Office Supplies, a paper and office supplies distributor serving SMBs across North America. The agent ("Aria") answers product questions, searches company policies, and generates branded PDF quotes.

| Attribute | Value |
|-----------|-------|
| Company | GoldLine Office Supplies |
| Agent Name | Aria |
| LLM | Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) |
| Embeddings | OpenAI `text-embedding-3-small` |
| Observability | LangSmith |
| Database | SQLite (215 products) |
| Backend | Python 3.12+ / FastAPI |
| Frontend | Next.js 16 / React 19 / Tailwind CSS v4 |
| CLI | Rich library |

---

## 2. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| LLM | Anthropic Claude Haiku 4.5 | Conversational AI with tool use |
| Embeddings | OpenAI text-embedding-3-small | Knowledge base semantic search |
| Tracing | LangSmith | Full request traces, latency, token usage |
| Backend | FastAPI + Uvicorn | REST API with SSE streaming |
| Frontend | Next.js 16 + TypeScript | Split-screen chat + reasoning view |
| Styling | Tailwind CSS v4 | Dark theme with gold/amber accents |
| Database | SQLite | Product catalog + quote tracking |
| PDF | fpdf2 | Branded quote generation |
| CLI | Rich | Terminal UI with spinners, panels, markdown |
| Package Mgr | uv | Python dependency management |
| Testing | pytest + pytest-asyncio | Unit tests + LLM behavioral evals |

---

## 3. Project Structure

```
goldline-agent/
├── src/
│   ├── agent.py          # Core agent: tool loop, streaming, history
│   ├── api.py            # FastAPI endpoints (health, chat, stream, quotes)
│   ├── cli.py            # Rich CLI entry point
│   ├── config.py         # All branding constants + settings
│   ├── history.py        # In-memory thread store
│   ├── knowledge.py      # Embedding-based semantic search
│   ├── prompts.py        # System prompt builder
│   ├── quotes.py         # PDF quote generation (fpdf2)
│   └── tools.py          # Tool definitions, dispatch, stock sanitization
├── web/
│   └── app/
│       ├── page.tsx              # Split-screen layout
│       ├── layout.tsx            # Root layout + metadata
│       ├── globals.css           # Dark theme + animations
│       ├── icon.svg              # Gold "GL" favicon
│       ├── components/
│       │   ├── ChatPanel.tsx     # Chat messages, input, "New Chat"
│       │   └── TracePanel.tsx    # Agent Reasoning View
│       └── hooks/
│           └── useChat.ts        # SSE client, thread management
├── knowledge_base/
│   └── documents/                # 5 policy markdown files
├── inventory/
│   ├── inventory.db              # SQLite (215 products)
│   └── seed_inventory.py         # DB seeder script
├── generated_quotes/             # PDF output directory
├── tests/
│   ├── test_tools.py             # 38 tests: SQL safety, sanitization
│   ├── test_prompts.py           # 10 tests: branding, prompt integrity
│   ├── test_knowledge.py         # 6 tests: embeddings, staleness
│   ├── test_history.py           # 6 tests: thread store
│   └── evals/                    # LLM behavioral evals (7 tests)
│       ├── test_stock_leakage.py
│       ├── test_scope_and_brand.py
│       └── test_tool_routing.py
├── pyproject.toml
├── CLAUDE.md
└── STATUS.md
```

---

## 4. Agent Tools

### Tool 1: `query_database`

Executes read-only SQL against the product catalog.

| Property | Value |
|----------|-------|
| Input | `query` (SQL string) |
| Allowed | `SELECT`, `PRAGMA` only |
| Blocked | `DROP`, `DELETE`, `UPDATE`, `INSERT`, `CREATE` |
| Connection | Read-only (`?mode=ro`) |
| Safety | Stock quantities replaced with labels |

**Stock Sanitization** (code-level, not just prompt):

| Raw Quantity | Label |
|-------------|-------|
| 0 | `out_of_stock` |
| 1-4 | `very_limited` |
| 5-9 | `limited` |
| 10-20 | `low_stock` |
| 21+ | `in_stock` |

Column-aware: only sanitizes columns named `quantity`, `stock`, `qty`, `inventory`, `count`. Preserves IDs (integers) and prices (floats).

### Tool 2: `search_knowledge_base`

Semantic search over company policy documents.

| Property | Value |
|----------|-------|
| Input | `query` (natural language) |
| Method | Cosine similarity on OpenAI embeddings |
| Top-K | 2 results |
| Threshold | 0.3 minimum relevance |
| Cache | `knowledge_base/embeddings/embeddings.json` |
| Auto-refresh | Detects when docs are newer than cache |

**Documents covered:**
- Company info, history, mission
- Store locations, department contacts, business hours
- Ordering process, payment methods, minimums
- Returns eligibility, process, refunds
- Shipping methods, delivery, tracking

### Tool 3: `generate_quote`

Generates a branded PDF quote with validated pricing.

| Property | Value |
|----------|-------|
| Inputs | `items` (product_id + quantity), `customer_name`, `notes` |
| Validation | 1-50 items, positive quantities, DB-verified product IDs |
| Pricing | Fetched from database (LLM cannot set prices) |
| Tax | 8% |
| Validity | 30 days |
| Quote Number | `GQ-YYYYMMDD-NNNN` |
| Output | PDF in `generated_quotes/` |
| Tracking | Inserted into `quotes` table |

**PDF layout:** Gold header bar, company branding, line items table, subtotal/tax/total, notes section, sales contact footer.

**Security:** Text sanitization (100 char name, 500 char notes), control character stripping, filename regex validation, path traversal prevention.

---

## 5. API Endpoints

Base URL: `http://localhost:8000`

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| `GET` | `/health` | Health check + KB status | None |
| `POST` | `/chat` | Non-streaming chat | None |
| `POST` | `/chat/stream` | SSE streaming with trace events | None |
| `GET` | `/quotes/{filename}` | Download generated PDF | None |

### POST `/chat/stream`

**Request:**
```json
{
  "message": "Do you have copy paper?",
  "thread_id": "01234567-..."    // optional, null for new conversation
}
```

**SSE Response Events:**

| Event | Data | When |
|-------|------|------|
| `thinking` | `{"status": "Processing..."}` | Agent starts processing |
| `tool_call` | `{"tool": "query_database", "input": {...}, "iteration": 1}` | Tool invoked |
| `tool_result` | `{"tool": "query_database", "result": "...", "latency_ms": 45}` | Tool returned |
| `text` | `{"content": "We have several..."}` | Final response |
| `done` | `{"thread_id": "...", "total_latency_ms": 2500, "input_tokens": 145, "output_tokens": 89, "tool_calls": 2}` | Request complete |
| `error` | `{"message": "..."}` | Error occurred |

### GET `/quotes/{filename}`

- Validates filename matches `^GQ-\d{8}-\d{4}\.pdf$`
- Resolves path and checks it's within `QUOTE_OUTPUT_DIR`
- Returns `application/pdf` with `Content-Disposition`

---

## 6. Frontend Architecture

### Split-Screen Layout

```
+----------------------------------------------------------+
|  [GL] GoldLine Office Supplies     Agent Reasoning View   |
+----------------------------+-----------------------------+
|                            |                             |
|   ChatPanel                |   TracePanel                |
|                            |                             |
|   [GL] GoldLine Assistant  |   LIVE                      |
|         [New Chat]         |                             |
|                            |   [thinking] Processing...  |
|   User: Do you have        |                             |
|   copy paper?              |   [tool_call] query_database|
|                            |   SELECT * FROM products... |
|   Aria: Yes! We carry      |                             |
|   several types...         |   [tool_result] 45ms        |
|                            |   [(1, 'Copy Paper',...)]   |
|                            |                             |
|                            |   ---                       |
|                            |   Latency: 2.5s             |
|   [Ask about products...]  |   Tokens: 145 in / 89 out  |
|                  [Send]    |   Tool calls: 1             |
+----------------------------+-----------------------------+
```

### Components

**ChatPanel** — Chat messages with markdown link rendering, auto-scroll, suggestion chips, "New Chat" button. XSS-safe href validation (blocks `javascript:`, `data:` URLs).

**TracePanel** — Real-time Agent Reasoning View showing each tool call with color-coded badges, input/output details, latency measurements, and aggregate stats.

**useChat Hook** — SSE client that:
- Streams events from `/chat/stream`
- Parses SSE spec-compliant format (blank-line dispatch)
- Captures `thread_id` from `done` event for conversation continuity
- Supports `AbortController` for request cancellation
- Provides `resetChat()` for "New Chat" functionality
- Guards against race conditions (abort signal check in dispatchEvent)

---

## 7. Conversational Memory

**How it works:**

1. First message: frontend sends `thread_id: null`
2. Backend creates new thread via `new_thread_id()` (UUID7)
3. Messages stored in `_thread_store[tid]` (in-memory dict)
4. Backend returns `thread_id` in SSE `done` event
5. Frontend captures and stores in `useRef`
6. Subsequent messages send same `thread_id`
7. Backend loads history from store, appends to context
8. "New Chat" button resets `thread_id` to `null`

**History truncation:** Max 100 messages per thread (oldest trimmed).

**Limitation:** In-memory only — history lost on backend restart. Production would need SQLite/Redis with TTL eviction.

---

## 8. Security Hardening

| Threat | Mitigation | Location |
|--------|-----------|----------|
| Stock quantity leakage | Column-aware sanitization at code level | `tools.py:_sanitize_results` |
| SQL injection | SELECT/PRAGMA allowlist + read-only connection | `tools.py:query_database` |
| Path traversal (quotes) | Regex filename validation + resolve/startswith check | `api.py:download_quote` |
| XSS via markdown links | Safe href validation (http/https only) | `ChatPanel.tsx:isSafeHref` |
| PDF text injection | Sanitize + truncate customer_name/notes, strip control chars | `quotes.py:_sanitize_text` |
| Price hallucination | Tool fetches real prices from DB, ignores LLM | `quotes.py:_validate_and_fetch_items` |
| Unbounded items | Max 50 line items per quote | `quotes.py:_validate_items` |
| Exception leakage | Generic error messages, internal logging only | `tools.py:execute_tool` |
| Stale SSE events after abort | AbortController + signal check in dispatchEvent | `useChat.ts` |
| API keys in source | `.env` file, gitignored | `.gitignore` |
| CORS | Restricted to `http://localhost:3000` | `api.py` |

---

## 9. System Prompt Summary

Agent persona: **Aria**, 3-year GoldLine customer support specialist.

**Can help with:** Product info, inventory/availability, recommendations, general inquiries, PDF quotes.

**Cannot handle:** Order placement, order tracking, returns/refunds, account changes, tech support — redirects to appropriate department email.

**Key behaviors:**
- Check database FIRST before asking clarifying questions
- Never expose raw stock quantities (use labels)
- Always generate PDF when customer says "quote"
- Concise, warm, professional tone

---

## 10. Testing

**59 unit tests + 7 LLM evals**

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_tools.py` | 38 | Stock classification, sanitization, SQL allowlist, query execution |
| `test_prompts.py` | 10 | Branding variables, no hardcoded values, policy/tool/scope presence |
| `test_knowledge.py` | 6 | Embedding staleness detection, relevance threshold |
| `test_history.py` | 6 | Thread creation, message save/retrieve, thread isolation |
| `evals/test_stock_leakage.py` | 6 | Quantity sanitization under various query patterns |
| `evals/test_scope_and_brand.py` | 4* | Scope boundaries, brand consistency |
| `evals/test_tool_routing.py` | 3* | Correct tool selection per question type |

*Evals marked `SKIPPED` without API keys.

```bash
uv run pytest tests/ -v              # All tests
uv run pytest tests/evals/ -v        # LLM evals only (needs API keys)
```

---

## 11. Configuration

### Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...         # Required: Claude API
OPENAI_API_KEY=sk-proj-...           # Required: Embeddings
LANGSMITH_API_KEY=lsv2_pt_...        # Optional: Tracing
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=goldline-agent
NEXT_PUBLIC_API_URL=http://localhost:8000  # Frontend → Backend
```

### Branding Constants (`src/config.py`)

```python
COMPANY_NAME    = "GoldLine Office Supplies"
AGENT_NAME      = "Aria"
TAGLINE         = "Premium supplies. Proven reliability."
MAIN_PHONE      = "1-888-GOLDLINE"
WEBSITE         = "www.goldlineoffice.com"
EMAIL_DOMAIN    = "goldlineoffice.com"
SALES_EMAIL     = "sales@goldlineoffice.com"
MODEL           = "claude-haiku-4-5-20251001"
TAX_RATE        = 0.08
QUOTE_VALIDITY_DAYS = 30
```

---

## 12. Running Locally

```bash
# 1. Install
cp .env.example .env    # Fill in API keys
uv sync
cd web && npm install

# 2. Seed database
uv run python inventory/seed_inventory.py

# 3. Start backend (terminal 1)
uv run uvicorn src.api:app --reload --port 8000

# 4. Start frontend (terminal 2)
cd web && npm run dev

# 5. Open browser
# http://localhost:3000

# Alternative: CLI mode
uv run goldline
```

---

## 13. Product Catalog

215 products across 19 categories:

| Category | Count | Price Range |
|----------|-------|-------------|
| Paper & Notebooks | 20 | $3.49 - $34.99 |
| Writing Instruments | 25 | $1.99 - $24.99 |
| Desk Supplies | 20 | $2.49 - $18.99 |
| Filing & Organization | 20 | $3.99 - $34.99 |
| Ink & Toner | 15 | $19.99 - $89.99 |
| Technology & Accessories | 25 | $4.99 - $79.99 |
| Boards & Presentation | 12 | $8.99 - $89.99 |
| Mailing & Shipping | 15 | $3.99 - $44.99 |
| Cleaning & Breakroom | 20 | $2.99 - $39.99 |
| Furniture & Ergonomics | 15 | $19.99 - $249.99 |
| Badges & ID | 5 | $8.99 - $24.99 |
| Laminating | 4 | $7.99 - $12.99 |
| Calendars & Planners | 4 | $8.99 - $14.99 |
| + Legacy items | 15 | Various |

---

## 14. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Claude Haiku 4.5 | Cost-effective for demos, fast response times |
| Stock sanitization at code level | Prompt instructions alone can be bypassed |
| fpdf2 for PDFs | Pure Python, no C dependencies, Windows-compatible |
| In-memory thread store | Simple for demo; production needs persistence |
| SSE over WebSockets | Simpler protocol, sufficient for one-way streaming |
| Split-screen Reasoning View | "Wow factor" for demos — shows agent thinking in real-time |
| Price validation from DB | Prevents LLM from hallucinating prices on quotes |
| Column-aware sanitization | Preserves product IDs while hiding stock numbers |
| uv package manager | Fast, reliable Python dependency resolution |
