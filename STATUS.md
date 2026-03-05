# STATUS

Last updated: 2026-03-04

## Now
- End-to-end testing with live API, demo polish

## Next
- Deploy (Vercel frontend + API hosting)
- Add LRU/TTL eviction to in-memory thread store (production hardening)

## Done (This Week)
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
