"""Tool definitions and execution for the GoldLine agent."""

import json
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

# Tables the LLM is allowed to query (block access to quotes, etc.)
_ALLOWED_TABLES = {"products", "sqlite_master", "sqlite_sequence"}

# Enforce a max row limit on all SELECT queries
_MAX_ROWS = 50

# Pattern to detect table names referenced in FROM / JOIN clauses
_TABLE_REF_PATTERN = re.compile(
    r"\b(?:FROM|JOIN)\s+[\"']?(\w+)[\"']?", re.IGNORECASE
)


def _sql_references_allowed_tables_only(query: str) -> bool:
    """Return True if the query only references allowed tables."""
    tables = _TABLE_REF_PATTERN.findall(query)
    return all(t.lower() in _ALLOWED_TABLES for t in tables)

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

GENERATE_QUOTE_TOOL: ToolParam = {
    "name": "generate_quote",
    "description": (
        "Generate a branded PDF quote for a customer. Use this after looking up "
        "product prices with query_database. Provide the product IDs and quantities; "
        "the tool will validate prices from the database."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_name": {
                "type": "string",
                "description": "Customer name or company for the quote header. Use 'Valued Customer' if unknown.",
            },
            "items": {
                "type": "array",
                "description": "Line items for the quote",
                "items": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "Product ID from the inventory database",
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Quantity requested",
                        },
                    },
                    "required": ["product_id", "quantity"],
                },
            },
            "notes": {
                "type": "string",
                "description": "Optional notes to include on the quote",
            },
        },
        "required": ["items"],
    },
}

ALL_TOOLS: list[ToolParam] = [
    QUERY_DATABASE_TOOL,
    SEARCH_KNOWLEDGE_BASE_TOOL,
    GENERATE_QUOTE_TOOL,
]


# Column names that should have their values replaced with stock labels
_QUANTITY_COLUMNS = {"quantity", "stock", "qty", "inventory", "count"}


def _classify_stock(quantity: int) -> str:
    """Convert raw quantity to a stock-level label (never expose exact numbers)."""
    if quantity <= 0:
        return "out_of_stock"
    if quantity <= 4:
        return "very_limited"
    if quantity <= 9:
        return "limited"
    if quantity <= 20:
        return "low_stock"
    return "in_stock"


def _sanitize_results(
    rows: list[tuple],
    column_names: list[str] | None = None,
    query: str = "",
) -> list[tuple]:
    """Replace quantity column values with stock-level labels.

    Uses a conservative approach: any integer column is sanitized UNLESS
    it can be positively identified as a safe column (like id or price).
    This prevents leaking exact stock numbers via column aliases or
    computed expressions.
    """
    if not rows:
        return []

    # Columns known to be safe (non-sensitive integers like IDs)
    _SAFE_INT_COLUMNS = {"id", "product_id", "rowid"}

    sanitized = []
    for row in rows:
        new_row = []
        for i, val in enumerate(row):
            if isinstance(val, int) and not isinstance(val, bool):
                # Only skip sanitization if we can confirm this is a safe column
                col_name = column_names[i].lower() if column_names and i < len(column_names) else ""
                if col_name in _SAFE_INT_COLUMNS:
                    new_row.append(val)
                else:
                    new_row.append(_classify_stock(val))
            else:
                new_row.append(val)
        sanitized.append(tuple(new_row))
    return sanitized


@traceable(name="query_database", run_type="tool")
def query_database(query: str, db_path: str) -> str:
    """Execute a read-only SQL query against the inventory database."""
    if not _ALLOWED_SQL_PATTERN.match(query):
        return "Only SELECT and PRAGMA queries are allowed."

    if not _sql_references_allowed_tables_only(query):
        return "Access denied. You may only query the products table."

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchmany(_MAX_ROWS)

        # Extract column names from cursor.description when available
        column_names = (
            [desc[0] for desc in cursor.description]
            if cursor.description
            else None
        )

        conn.close()
        return str(_sanitize_results(results, column_names, query))
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

    if tool_name == "generate_quote":
        if on_tool_call:
            on_tool_call("Generating PDF quote...")
        from src.quotes import generate_quote_pdf

        try:
            result = generate_quote_pdf(
                db_path=db_path,
                items=tool_input["items"],
                customer_name=tool_input.get("customer_name", "Valued Customer"),
                notes=tool_input.get("notes"),
            )
            return json.dumps({
                "status": "success",
                "quote_number": result["quote_number"],
                "filename": result["filename"],
                "total": result["total"],
                "download_url": f"/quotes/{result['filename']}",
                "message": f"Quote {result['quote_number']} generated successfully.",
            })
        except ValueError as e:
            return json.dumps({"status": "error", "message": str(e)})
        except Exception:
            logger.exception("Quote generation failed")
            return json.dumps({"status": "error", "message": "Quote generation failed. Please try again."})

    return f"Error: Unknown tool {tool_name}"
