#!/bin/bash
# Weekly work logger - runs claude to generate weekly work log
set -e
cd "$HOME/dotfiles"
claude -p "/weekly-work-logger" --dangerously-skip-permissions 2>/tmp/weekly-work-logger.err || true
echo "$(date '+%Y-%m-%d %H:%M') weekly-work-logger" >> /tmp/work-logger.log
