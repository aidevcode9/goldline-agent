"""Seed script for GoldLine inventory database."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "inventory.db"


def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS products")

    # Create products table with price
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)

    # 15 products with varied stock levels for demo
    products = [
        (1, "Premium Copy Paper 500 Sheets", "Paper", 8.99, 45),
        (2, "Blue Ballpoint Pens (12-pack)", "Writing", 6.49, 23),
        (3, "Heavy-Duty Stapler", "Office Equipment", 14.99, 12),
        (4, "Spiral Notebooks (3-pack)", "Paper", 9.99, 31),
        (5, "Manila File Folders (25-pack)", "Organization", 11.49, 8),
        (6, "Sticky Notes Assorted Colors (12-pack)", "Paper", 7.99, 50),
        (7, "Black Permanent Markers (6-pack)", "Writing", 8.49, 35),
        (8, "Desk Organizer - Mesh Metal", "Organization", 24.99, 6),
        (9, "Legal Pads Yellow Ruled (6-pack)", "Paper", 12.99, 28),
        (10, "Binder Clips Assorted Sizes (48-pack)", "Office Equipment", 5.99, 42),
        (11, "Whiteboard Markers (8-pack)", "Writing", 10.99, 15),
        (12, "Printer Ink Cartridge - Black", "Ink & Toner", 29.99, 3),
        (13, "Printer Ink Cartridge - Color", "Ink & Toner", 34.99, 0),
        (14, "Paper Shredder - Cross Cut", "Office Equipment", 89.99, 7),
        (15, "Ergonomic Mouse Pad with Wrist Rest", "Accessories", 16.99, 18),
    ]

    cursor.executemany(
        "INSERT INTO products (id, name, category, price, quantity) VALUES (?, ?, ?, ?, ?)",
        products
    )

    conn.commit()
    conn.close()
    print(f"Seeded {len(products)} products into {DB_PATH}")


if __name__ == "__main__":
    seed()
