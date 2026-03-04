---
description: Verify implementation works correctly
---

Verify the current implementation works correctly.

Steps:
1. Run linter: `uv run ruff check src/`
2. Run import check: `uv run python -c "from src.agent import chat, load_knowledge_base; print('agent ok')"`
3. Run CLI check: `uv run python -c "from src.cli import main; print('cli ok')"`
4. Verify inventory DB exists and has data: `uv run python -c "import sqlite3; conn = sqlite3.connect('inventory/inventory.db'); print(conn.execute('SELECT COUNT(*) FROM products').fetchone())"`
5. If there are failures:
   - Analyze the error
   - Suggest a fix
   - Ask if I want you to fix it
6. If all pass:
   - Report summary
   - Suggest running the agent manually: `uv run goldline`
   - Confirm ready to commit
