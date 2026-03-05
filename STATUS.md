# STATUS

Last updated: 2026-03-04

## Now
- Add unit tests + LLM evals

## Next
- Add web UI (Next.js + FastAPI)

## Done (This Week)
- Initial repo setup and demo polish
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
