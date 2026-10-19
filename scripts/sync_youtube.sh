#!/bin/bash
# YouTube sync wrapper for launchd
# Runs with delay to avoid impacting startup/wake performance

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DELAY_SECONDS="${1:-300}"  # Default 5 minute delay
LOG_FILE="$SCRIPT_DIR/data/sync.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Delay to avoid impacting startup/wake
if [ "$DELAY_SECONDS" -gt 0 ]; then
    log "Waiting ${DELAY_SECONDS}s before sync..."
    sleep "$DELAY_SECONDS"
fi

# Check if Ollama is running (needed for embedding)
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    log "Ollama not running, attempting to start..."
    open -a Ollama
    sleep 10  # Wait for Ollama to start
    
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log "ERROR: Could not start Ollama"
        exit 1
    fi
fi

# Run sync
cd "$SCRIPT_DIR"
log "Starting YouTube sync..."

if uv run python -m src.youtube_sync >> "$LOG_FILE" 2>&1; then
    log "Sync completed successfully"
else
    log "Sync completed with errors"
fi
