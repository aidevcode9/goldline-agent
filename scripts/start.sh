#!/bin/bash
set -e

# If using persistent volume and DB doesn't exist yet, seed it
if [ -n "$DATABASE_PATH" ] && [ ! -f "$DATABASE_PATH" ]; then
    echo "Seeding database at $DATABASE_PATH..."
    mkdir -p "$(dirname "$DATABASE_PATH")"
    uv run python inventory/seed_inventory.py
    cp inventory/inventory.db "$DATABASE_PATH"
fi

# Ensure quotes directory exists
if [ -n "$QUOTE_OUTPUT_DIR" ]; then
    mkdir -p "$QUOTE_OUTPUT_DIR"
fi

# Start the server
exec uv run uvicorn src.api:app --host 0.0.0.0 --port "${PORT:-8000}"
