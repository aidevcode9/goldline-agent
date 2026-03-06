# GoldLine Office Supplies — Branding & Configuration

COMPANY_NAME = "GoldLine Office Supplies"
AGENT_NAME = "Aria"
TAGLINE = "Premium supplies. Proven reliability."

# Contact info
MAIN_PHONE = "1-888-GOLDLINE"
WEBSITE = "www.goldlineoffice.com"
EMAIL_DOMAIN = "goldlineoffice.com"

# Rich CLI colors
BRAND_COLOR = "gold1"
ACCENT_COLOR = "dark_goldenrod"

# Project root (one level up from src/)
import os as _os
from pathlib import Path as _Path

PROJECT_ROOT = _Path(__file__).resolve().parent.parent

# Database
DATABASE_PATH = _os.getenv("DATABASE_PATH", str(PROJECT_ROOT / "inventory" / "inventory.db"))

# Quote/Invoice settings
TAX_RATE = 0.08
QUOTE_VALIDITY_DAYS = 30
QUOTE_OUTPUT_DIR = _Path(_os.getenv("QUOTE_OUTPUT_DIR", str(PROJECT_ROOT / "generated_quotes")))
SALES_EMAIL = f"sales@{EMAIL_DOMAIN}"

# Model
MODEL = "claude-haiku-4-5-20251001"

# Knowledge base
EMBEDDING_MODEL = "text-embedding-3-small"
KB_TOP_K = 2
KB_RELEVANCE_THRESHOLD = 0.4
