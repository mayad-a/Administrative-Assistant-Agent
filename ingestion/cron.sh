#!/bin/bash
# =============================================
# Weekly Cron Job — Smart Admin Assistant
# =============================================
# 
# Usage via crontab:
# 0 2 * * 0 /path/to/smart-admin-assistant/ingestion/cron.sh
# Runs every Sunday at 2:00 AM.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$DIR")"

echo "[$(date)] Starting weekly ingestion cron job..."

# 1. Activate env
source "$PROJECT_ROOT/venv/bin/activate"

# 2. Run Crawler
echo "[$(date)] Running crawler..."
python "$PROJECT_ROOT/ingestion/crawl.py"

# 3. Post Clean
echo "[$(date)] Running cleaner..."
python "$PROJECT_ROOT/ingestion/clean.py"

# 4. Ingest into Vector Store (Future Sprint)
# echo "[$(date)] Running vector DB ingestion..."
# python "$PROJECT_ROOT/ingestion/ingest.py"

echo "[$(date)] Cron job finished successfully."
