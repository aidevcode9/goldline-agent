---
description: Commit, push, and create PR
---

Commit the current changes, push, and create a PR.

Steps:
1. Run `git status` and `git diff --stat` to understand what changed
2. Run a quick smoke test: `uv run python -c "from src.agent import chat; print('import ok')"`
3. If import fails, fix before committing
4. If it passes, write a commit message:
   - Format: `type(scope): description`
   - Types: feat, fix, test, docs, refactor, chore
   - Example: `feat(agent): add price queries to inventory tool`
5. Commit: `git add -A && git commit -m "message"`
6. Push: `git push -u origin HEAD`
7. Create PR with summary of what changed and why

If this is a work-in-progress, ask me if I want to commit anyway or keep working.
