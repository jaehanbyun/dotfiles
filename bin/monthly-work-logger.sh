#!/bin/bash
# Monthly work logger - runs Codex to generate monthly work log
set -e
TARGET_MONTH=$(date -v-1m +%Y-%m)
cd "$HOME/dotfiles"
codex exec --ephemeral --skip-git-repo-check -C "$HOME/dotfiles" \
  --ask-for-approval never --sandbox danger-full-access \
  "/monthly-work-logger $TARGET_MONTH" 2>/tmp/monthly-work-logger.err || true
echo "$(date '+%Y-%m-%d %H:%M') monthly-work-logger: $TARGET_MONTH" >> /tmp/work-logger.log
