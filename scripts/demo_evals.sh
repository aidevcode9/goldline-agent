#!/bin/bash
# ─────────────────────────────────────────────────────────
# GoldLine Agent — Eval Suite Demo
# Runs all tests (unit + LLM behavioral evals) and produces
# an HTML report you can open in any browser.
#
# Usage:
#   bash scripts/demo_evals.sh            # full suite
#   bash scripts/demo_evals.sh --unit     # unit tests only (no API keys)
#   bash scripts/demo_evals.sh --evals    # LLM evals only
# ─────────────────────────────────────────────────────────
set -e

REPORT_DIR="reports"
REPORT_FILE="$REPORT_DIR/eval-report.html"
mkdir -p "$REPORT_DIR"

# Determine which tests to run
MARKER_FLAG=""
LABEL="all tests (unit + LLM evals)"
if [ "$1" = "--unit" ]; then
    MARKER_FLAG='-m "not eval"'
    LABEL="unit tests only"
elif [ "$1" = "--evals" ]; then
    MARKER_FLAG='-m eval'
    LABEL="LLM behavioral evals only"
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   GoldLine Agent — Eval Suite Demo           ║"
echo "║   Running: $LABEL"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Run pytest with HTML report generation
eval uv run pytest tests/ \
    $MARKER_FLAG \
    -v \
    --tb=short \
    --html="$REPORT_FILE" \
    --self-contained-html \
    || true  # don't exit on test failures — we still want the report

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Report saved: $REPORT_FILE"
echo "  Open in browser to view results."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
