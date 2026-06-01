#!/bin/bash
# Daily work logger - runs Codex to generate daily work log
set -e
TARGET_DATE=$(date -v-1d +%Y-%m-%d)
if [ -f "$HOME/.codex/work-log.env" ]; then
  set -a
  . "$HOME/.codex/work-log.env"
  set +a
fi
cd "$HOME/dotfiles"
codex exec --ephemeral --skip-git-repo-check -C "$HOME/dotfiles" \
  --ask-for-approval never --sandbox danger-full-access \
  "/daily-work-logger $TARGET_DATE. work log를 만든 뒤 Apple Reminders의 Daily Focus 리스트에 오늘 할 일 3~5개를 생성해줘." 2>/tmp/daily-work-logger.err || true
echo "$(date '+%Y-%m-%d %H:%M') daily-work-logger: $TARGET_DATE" >> /tmp/work-logger.log
