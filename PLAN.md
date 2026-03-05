# GoldLine Agent — Session Plan

## Current Session: Unit Tests + Evals + Next.js Web UI

### Batch 1: Testing & Evals
| Step | Workflow | Task | Status |
|------|----------|------|--------|
| 1 | `/wsresearch` | Understand test patterns, inventory schema, eval frameworks | pending |
| 2 | `/wsstart` | Create unit tests (test_tools, test_knowledge, test_history, test_prompts) | pending |
| 3 | `/wsstart` | Create LLM evals (stock leakage, SQL injection, tool routing, scope, brand) | pending |
| 4 | `/wsverify` | Run all tests, verify passing | pending |
| 5 | `/wsskeptic` | Adversarial review of test coverage | pending |
| 6 | `/wscommit` | Commit test suite | pending |

### Batch 2: Next.js Web UI
| Step | Workflow | Task | Status |
|------|----------|------|--------|
| 1 | `/wsresearch` | Research FastAPI + Next.js integration patterns | pending |
| 2 | `/wsstart` | Create FastAPI backend (expose agent as API) | pending |
| 3 | `/wsstart` | Create Next.js frontend (chat UI) | pending |
| 4 | `/wsverify` | Verify both services run and communicate | pending |
| 5 | `/wsskeptic` | Adversarial review | pending |
| 6 | `/wscommit` | Commit web UI | pending |

### Wrap Up
| Step | Workflow | Task | Status |
|------|----------|------|--------|
| 1 | `/wsstatus` | Update STATUS.md with progress | pending |
| 2 | `/wscommit` | Final commit + push | pending |

## Decisions
- pytest + pytest-asyncio for unit tests (already added to dev deps)
- Evals will use real LLM calls (require API keys)
- Next.js frontend with FastAPI backend (replaces "Python only" decision)
- No Gradio — using Next.js instead

## Conventions
- All tests in `tests/` directory
- Test files mirror source: `src/tools.py` → `tests/test_tools.py`
- Evals in `tests/evals/` directory
- Run tests: `uv run pytest`
- Run evals: `uv run pytest tests/evals/ -v`
