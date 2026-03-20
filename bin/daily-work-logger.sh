#!/bin/bash
# Daily work logger - runs claude to generate daily work log
set -e
TARGET_DATE=$(date -v-1d +%Y-%m-%d)
cd "$HOME/dotfiles"
claude -p "/daily-work-logger $TARGET_DATE" --dangerously-skip-permissions 2>/tmp/daily-work-logger.err || true
echo "$(date '+%Y-%m-%d %H:%M') daily-work-logger: $TARGET_DATE" >> /tmp/work-logger.log
