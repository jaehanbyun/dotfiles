#!/bin/bash
# Monthly work logger - runs claude to generate monthly work log
set -e
TARGET_MONTH=$(date -v-1m +%Y-%m)
cd "$HOME/dotfiles"
claude -p "/monthly-work-logger $TARGET_MONTH" --dangerously-skip-permissions 2>/tmp/monthly-work-logger.err || true
echo "$(date '+%Y-%m-%d %H:%M') monthly-work-logger: $TARGET_MONTH" >> /tmp/work-logger.log
