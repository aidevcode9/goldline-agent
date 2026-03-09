"""Eval fixtures — shared setup for LLM behavioral tests."""

import os
import re
import sqlite3
import tempfile
from pathlib import Path

import pytest
from anthropic import AsyncAnthropic
from langsmith.wrappers import wrap_anthropic

from src.config import MODEL
from src.prompts import build_system_prompt
from src.tools import ALL_TOOLS, _sanitize_results


@pytest.fixture(scope="session")
def eval_client():
    """Real Anthropic client for evals."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set — skipping evals")
    return wrap_anthropic(AsyncAnthropic(api_key=api_key))


@pytest.fixture(scope="session")
def system_prompt():
    return build_system_prompt()


@pytest.fixture
def eval_db():
    """Temporary DB with known test data for eval scenarios."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)
    cursor.executemany(
        "INSERT INTO products (id, name, category, price, quantity) VALUES (?, ?, ?, ?, ?)",
        [
            (1, "Copy Paper 500 Sheets", "Paper", 8.99, 45),
            (2, "Blue Pens (12-pack)", "Writing", 6.49, 3),
            (3, "Printer Ink - Color", "Ink & Toner", 34.99, 0),
        ],
    )
    conn.commit()
    conn.close()

    yield db_path

    try:
        Path(db_path).unlink(missing_ok=True)
    except PermissionError:
        pass


async def get_agent_response(client, system_prompt, user_message):
    """Send a single message to the agent and return the text response + tool calls."""
    messages = [{"role": "user", "content": user_message}]

    response = await client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
        tools=ALL_TOOLS,
    )

    tool_calls = [
        block for block in response.content if block.type == "tool_use"
    ]
    text_blocks = [
        block.text for block in response.content if hasattr(block, "text")
    ]

    return {
        "text": " ".join(text_blocks),
        "tool_calls": tool_calls,
        "stop_reason": response.stop_reason,
    }
