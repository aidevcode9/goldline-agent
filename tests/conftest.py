"""Shared test fixtures."""

import sqlite3
import tempfile
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database with test inventory data."""
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
            (4, "Sticky Notes", "Paper", 7.99, 15),
            (5, "File Folders", "Organization", 11.49, 8),
        ],
    )
    conn.commit()
    conn.close()

    yield db_path

    try:
        Path(db_path).unlink(missing_ok=True)
    except PermissionError:
        pass  # Windows may hold a brief lock on SQLite files
