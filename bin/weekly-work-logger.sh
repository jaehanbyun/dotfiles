#!/bin/bash
# Weekly work logger - runs Codex to generate weekly work log
set -e
cd "$HOME/dotfiles"
codex exec --ephemeral --skip-git-repo-check -C "$HOME/dotfiles" \
  --ask-for-approval never --sandbox danger-full-access \
  "/weekly-work-logger" 2>/tmp/weekly-work-logger.err || true
echo "$(date '+%Y-%m-%d %H:%M') weekly-work-logger" >> /tmp/work-logger.log
