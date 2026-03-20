#!/bin/bash
# Morning briefing - runs claude to generate daily tech/economy briefing
set -e
cd "$HOME/dotfiles"
claude -p "/morning-briefing" --dangerously-skip-permissions 2>/tmp/morning-briefing.err || true
echo "$(date '+%Y-%m-%d %H:%M') morning-briefing" >> /tmp/work-logger.log
