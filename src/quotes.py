"""GoldLine Agent — PDF quote generation."""

import logging
import re
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from fpdf import FPDF
from langsmith import traceable

from src.config import (
    COMPANY_NAME,
    MAIN_PHONE,
    WEBSITE,
    SALES_EMAIL,
    TAGLINE,
    TAX_RATE,
    QUOTE_VALIDITY_DAYS,
    QUOTE_OUTPUT_DIR,
)

logger = logging.getLogger(__name__)

MAX_ITEMS = 50
MAX_CUSTOMER_NAME_LEN = 100
MAX_NOTES_LEN = 500
_SAFE_TEXT_PATTERN = re.compile(r"^[\w\s.,\-'\"&()/#@:;!?]+$", re.UNICODE)


def _sanitize_text(text: str, max_len: int, label: str) -> str:
    """Sanitize and truncate user-supplied text for PDF rendering."""
    text = text.strip()[:max_len]
    # Strip control characters (keep printable + whitespace)
    text = "".join(c for c in text if c.isprintable() or c in "\n\t")
    return text


def _validate_items(items: list[dict]) -> None:
    """Validate the items array before any DB calls."""
    if not items:
        raise ValueError("At least one item is required.")
    if len(items) > MAX_ITEMS:
        raise ValueError(f"Quote cannot exceed {MAX_ITEMS} line items.")
    for item in items:
        pid = item.get("product_id")
        qty = item.get("quantity")
        if not isinstance(pid, int) or pid <= 0:
            raise ValueError(f"Invalid product_id: {pid}")
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("Quantity must be a positive integer.")


def _ensure_quotes_table(db_path: str) -> None:
    """Create the quotes tracking table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_number TEXT UNIQUE NOT NULL,
            customer_name TEXT,
            total REAL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def _next_quote_number(db_path: str) -> str:
    """Generate next sequential quote number: GQ-YYYYMMDD-NNNN."""
    today = date.today().strftime("%Y%m%d")
    prefix = f"GQ-{today}-"

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT COUNT(*) FROM quotes WHERE quote_number LIKE ?",
        (f"{prefix}%",),
    ).fetchone()
    seq = (row[0] if row else 0) + 1
    conn.close()

    return f"{prefix}{seq:04d}"


def _validate_and_fetch_items(db_path: str, items: list[dict]) -> list[dict]:
    """Look up product IDs in the database and return enriched line items."""
    product_ids = [item["product_id"] for item in items]
    placeholders = ",".join("?" * len(product_ids))

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    rows = conn.execute(
        f"SELECT id, name, price FROM products WHERE id IN ({placeholders})",
        product_ids,
    ).fetchall()
    conn.close()

    db_products = {row[0]: {"name": row[1], "price": row[2]} for row in rows}

    missing = [pid for pid in product_ids if pid not in db_products]
    if missing:
        raise ValueError(f"Product IDs not found: {missing}")

    enriched = []
    for item in items:
        pid = item["product_id"]
        qty = item["quantity"]
        product = db_products[pid]
        enriched.append({
            "product_id": pid,
            "name": product["name"],
            "price": product["price"],
            "quantity": qty,
            "extended": round(product["price"] * qty, 2),
        })

    return enriched


class _QuotePDF(FPDF):
    """Custom PDF with GoldLine branding."""

    def header(self):
        self.set_fill_color(218, 165, 32)
        self.rect(0, 0, 210, 12, "F")

        self.set_y(16)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, COMPANY_NAME, new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "I", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, TAGLINE, new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"{WEBSITE}  |  {MAIN_PHONE}", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, f"Thank you for choosing {COMPANY_NAME}!", align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"Questions? Contact {SALES_EMAIL} or call {MAIN_PHONE}",
                  align="C")


@traceable(name="generate_quote", run_type="tool")
def generate_quote_pdf(
    db_path: str,
    items: list[dict],
    customer_name: str = "Valued Customer",
    notes: str | None = None,
) -> dict:
    """Generate a branded PDF quote. Returns metadata dict."""
    _validate_items(items)
    customer_name = _sanitize_text(customer_name, MAX_CUSTOMER_NAME_LEN, "customer_name")
    if notes:
        notes = _sanitize_text(notes, MAX_NOTES_LEN, "notes")

    _ensure_quotes_table(db_path)
    enriched_items = _validate_and_fetch_items(db_path, items)
    quote_number = _next_quote_number(db_path)

    today = date.today()
    valid_until = today + timedelta(days=QUOTE_VALIDITY_DAYS)

    subtotal = sum(item["extended"] for item in enriched_items)
    tax = round(subtotal * TAX_RATE, 2)
    total = round(subtotal + tax, 2)

    # Build PDF
    pdf = _QuotePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    # Quote info block
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, "QUOTE", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Quote #: {quote_number}")
    pdf.cell(0, 6, f"Date: {today.strftime('%B %d, %Y')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(95, 6, f"Prepared for: {customer_name}")
    pdf.cell(0, 6, f"Valid until: {valid_until.strftime('%B %d, %Y')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # Table header
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("Helvetica", "B", 9)
    col_widths = [12, 90, 20, 30, 38]
    headers = ["#", "Product", "Qty", "Unit Price", "Extended"]
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 8, h, border=1, fill=True)
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", "", 9)
    for i, item in enumerate(enriched_items, 1):
        pdf.cell(col_widths[0], 7, str(i), border=1)
        pdf.cell(col_widths[1], 7, item["name"][:45], border=1)
        pdf.cell(col_widths[2], 7, str(item["quantity"]), border=1, align="R")
        pdf.cell(col_widths[3], 7, f"${item['price']:.2f}", border=1, align="R")
        pdf.cell(col_widths[4], 7, f"${item['extended']:.2f}", border=1, align="R")
        pdf.ln()

    # Totals
    pdf.ln(4)
    totals_x = sum(col_widths[:3])
    pdf.set_x(pdf.l_margin + totals_x)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(col_widths[3], 7, "Subtotal:", align="R")
    pdf.cell(col_widths[4], 7, f"${subtotal:,.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(pdf.l_margin + totals_x)
    pdf.cell(col_widths[3], 7, f"Tax ({TAX_RATE:.0%}):", align="R")
    pdf.cell(col_widths[4], 7, f"${tax:,.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(pdf.l_margin + totals_x)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(col_widths[3], 8, "TOTAL:", align="R")
    pdf.cell(col_widths[4], 8, f"${total:,.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

    # Notes
    if notes:
        pdf.ln(8)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Notes:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, notes)

    # CTA
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"To place this order, reply to this quote or contact {SALES_EMAIL}.",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Prices valid for {QUOTE_VALIDITY_DAYS} days from the quote date.")

    # Save
    output_dir = Path(QUOTE_OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    filename = f"{quote_number}.pdf"
    filepath = output_dir / filename
    pdf.output(str(filepath))

    # Track in DB
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO quotes (quote_number, customer_name, total) VALUES (?, ?, ?)",
        (quote_number, customer_name, total),
    )
    conn.commit()
    conn.close()

    logger.info("Generated quote %s: $%.2f (%d items)", quote_number, total, len(enriched_items))

    return {
        "quote_number": quote_number,
        "filename": filename,
        "total": total,
        "item_count": len(enriched_items),
    }
