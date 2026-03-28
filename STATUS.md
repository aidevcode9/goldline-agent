# STATUS

Last updated: 2026-03-27

## Now
- Deploy (Vercel frontend + API hosting)

## Next
- Add LRU/TTL eviction to in-memory thread store (production hardening)
- Rotate API keys (CRIT-1 from adversarial review — keys exposed in .env)

## Done (This Week)
- Security hardening from adversarial review (3 CRIT, 5 HIGH fixed):
  - API auth middleware (bearer token via API_SECRET_KEY env var)
  - SQL table allowlist (products only) + row limit (50 max)
  - Stock quantity sanitization hardened (conservative: all unknown ints sanitized)
  - Input length validation (4000 char max) + per-IP rate limiting (20/min)
  - Non-guessable quote IDs (UUID-based instead of sequential)
  - CORS tightened (specific methods/headers instead of wildcards)
- UI visual overhaul — glass morphism login, gradient header, color-coded trace events, ambient glow effects, markdown bold/italic rendering, icon-enhanced quick actions
- End-to-end testing with live API, demo polish

## Archive
- Added conversational memory — thread_id plumbing between backend/frontend, "New Chat" button
- Added PDF quote generator tool (generate_quote) with branded PDFs, security hardening
- Expanded product catalog from 15 to 215 items across 18 categories
- Built Next.js frontend with Agent Reasoning View (split-screen: chat + trace)
- Created FastAPI backend with SSE streaming (/chat/stream endpoint)
- Added ChatPanel, TracePanel, useChat hook with AbortController
- Adversarial review: fixed SSE parser, XSS prevention, accessibility
- Unit tests (59 passing) + LLM evals (7)
- Refactored agent.py into SOLID modules (knowledge, tools, prompts, history)
- Fixed 2 CRITICAL + 5 HIGH security issues from adversarial review

## Decisions
- Rebranded from OfficeFlow to GoldLine Office Supplies
- Next.js + FastAPI for web UI (replaces Gradio / "Python only" decision)
- Rich CLI for demo presentation
- Claude Haiku 4.5 as primary model
- uv for dependency management
- pytest + pytest-asyncio for testing
- Evals use real LLM calls, marked separately from unit tests
- Agent Reasoning View as "wow factor" — real-time trace of tool calls, SQL, latency, tokens
