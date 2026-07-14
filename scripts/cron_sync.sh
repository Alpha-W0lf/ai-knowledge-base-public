#!/bin/bash
# Cron script to sync YouTube channels periodically
#
# To schedule, add to crontab:
#   crontab -e
#   
#   # Run daily at 6am
#   0 6 * * * /path/to/ai_knowledge_base/scripts/cron_sync.sh >> /path/to/ai_knowledge_base/logs/sync.log 2>&1
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=========================================="
echo "YouTube Sync - $(date)"
echo "=========================================="

# Activate virtual environment if using one
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run sync
uv run python -m src.youtube_sync

echo ""
echo "Sync complete at $(date)"
echo ""
