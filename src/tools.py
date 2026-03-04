"""Tool definitions and execution for the GoldLine agent."""

import logging
import re
import sqlite3
from pathlib import Path
from typing import Callable, Optional

from langsmith import traceable

from anthropic.types import ToolParam

from src.knowledge import KnowledgeBase

logger = logging.getLogger(__name__)

# Only allow read-only SQL statements
_ALLOWED_SQL_PATTERN = re.compile(
    r"^\s*(SELECT|PRAGMA)\s", re.IGNORECASE
)

QUERY_DATABASE_TOOL: ToolParam = {
    "name": "query_database",
    "description": "SQL query to get information about our inventory for customers like products, quantities and prices.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "SQL query to execute against the inventory database.\n\n"
                    "YOU DO NOT KNOW THE SCHEMA. ALWAYS discover it first:\n"
                    '1. Query \'SELECT name FROM sqlite_master WHERE type="table"\' to see available tables\n'
                    "2. Use 'PRAGMA table_info(table_name)' to inspect columns for each table\n"
                    "3. Only after understanding the schema, construct your search queries"
                ),
            }
        },
        "required": ["query"],
    },
}

SEARCH_KNOWLEDGE_BASE_TOOL: ToolParam = {
    "name": "search_knowledge_base",
    "description": (
        "Search company knowledge base for information about policies, procedures, "
        "company info, shipping, returns, ordering, contact information, store locations, "
        "and business hours. Use this for non-product questions."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language question or search query about company policies or information",
            }
        },
        "required": ["query"],
    },
}

ALL_TOOLS: list[ToolParam] = [QUERY_DATABASE_TOOL, SEARCH_KNOWLEDGE_BASE_TOOL]


def _classify_stock(quantity: int) -> str:
    """Convert raw quantity to a stock-level label (never expose exact numbers)."""
    if quantity == 0:
        return "out_of_stock"
    if quantity <= 4:
        return "very_limited"
    if quantity <= 9:
        return "limited"
    if quantity <= 20:
        return "low_stock"
    return "in_stock"


def _sanitize_results(rows: list[tuple]) -> list[tuple]:
    """Replace numeric quantity columns with stock-level labels.

    Heuristic: any integer column named 'quantity' or 'stock' will have its
    value replaced. Since we don't have column names from fetchall(), we
    apply the heuristic to all integer values in the result set. This is
    conservative — prices (floats) pass through unchanged.
    """
    sanitized = []
    for row in rows:
        new_row = tuple(
            _classify_stock(val) if isinstance(val, int) and not isinstance(val, bool)
            else val
            for val in row
        )
        sanitized.append(new_row)
    return sanitized


@traceable(name="query_database", run_type="tool")
def query_database(query: str, db_path: str) -> str:
    """Execute a read-only SQL query against the inventory database."""
    if not _ALLOWED_SQL_PATTERN.match(query):
        return "Only SELECT and PRAGMA queries are allowed."

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return str(_sanitize_results(results))
    except Exception as e:
        logger.exception("Database query failed")
        return "Database query failed. Please try a different query."


async def execute_tool(
    tool_name: str,
    tool_input: dict,
    *,
    db_path: str,
    knowledge_base: KnowledgeBase,
    on_tool_call: Optional[Callable[[str], None]] = None,
) -> str:
    """Dispatch a tool call and return its result."""
    if tool_name == "query_database":
        if on_tool_call:
            on_tool_call("Querying inventory database...")
        return query_database(query=tool_input["query"], db_path=db_path)

    if tool_name == "search_knowledge_base":
        if on_tool_call:
            on_tool_call("Searching knowledge base...")
        return await knowledge_base.search(query=tool_input["query"])

    return f"Error: Unknown tool {tool_name}"
