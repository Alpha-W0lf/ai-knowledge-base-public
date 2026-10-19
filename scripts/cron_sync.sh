#!/bin/bash
# Cron entry point for the optional YouTube sync. Runs scripts/sync_youtube.sh
# with no start-up delay; that script owns the Ollama check, the sync and the log.
#
# Example crontab line (daily at 6am):
#   0 6 * * * /path/to/your/clone/scripts/cron_sync.sh

set -e
exec "$(cd "$(dirname "$0")" && pwd)/sync_youtube.sh" 0
