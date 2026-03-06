FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ src/
COPY inventory/ inventory/
COPY knowledge_base/ knowledge_base/
COPY scripts/ scripts/

# Install dependencies (no dev deps)
RUN uv sync --no-dev

# Seed inventory DB at build time (startup script copies to volume if needed)
RUN uv run python inventory/seed_inventory.py

# Make startup script executable
RUN chmod +x scripts/start.sh

EXPOSE 8000

CMD ["bash", "scripts/start.sh"]
