#!/bin/bash
# Auto-sync dotfiles to git (daily cron)
# Detects changes, commits, and pushes

set -e

DOTFILES_DIR="$HOME/dotfiles"
CLAUDE_DIR="$HOME/.claude"
LOG="$DOTFILES_DIR/.sync.log"

cd "$DOTFILES_DIR"

# 1. Sync .claude/ tracked files to dotfiles
CLAUDE_FILES="CLAUDE.md settings.json keybindings.json code-review.yml"
CLAUDE_DIRS="agents commands skills hooks docs"

for f in $CLAUDE_FILES; do
  [ -f "$CLAUDE_DIR/$f" ] && cp "$CLAUDE_DIR/$f" "$DOTFILES_DIR/.claude/$f" 2>/dev/null
done

for d in $CLAUDE_DIRS; do
  if [ -d "$CLAUDE_DIR/$d" ]; then
    mkdir -p "$DOTFILES_DIR/.claude/$d"
    rsync -a --delete \
      --exclude='*.tmpl' \
      --exclude='gstack/' \
      --exclude='browse/' \
      --exclude='careful/' \
      --exclude='codex/' \
      --exclude='design-consultation/' \
      --exclude='design-review/' \
      --exclude='document-release/' \
      --exclude='freeze/' \
      --exclude='gstack-upgrade/' \
      --exclude='guard/' \
      --exclude='investigate/' \
      --exclude='office-hours/' \
      --exclude='plan-ceo-review/' \
      --exclude='plan-design-review/' \
      --exclude='plan-eng-review/' \
      --exclude='qa-only/' \
      --exclude='qa/' \
      --exclude='retro/' \
      --exclude='review/' \
      --exclude='setup-browser-cookies/' \
      --exclude='ship/' \
      --exclude='unfreeze/' \
      "$CLAUDE_DIR/$d/" "$DOTFILES_DIR/.claude/$d/" 2>/dev/null
  fi
done

# 2. Check for changes
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "$(date '+%Y-%m-%d %H:%M') no changes" >> "$LOG"
  exit 0
fi

# 3. Commit
git add -A
CHANGED=$(git diff --cached --stat | tail -1)
git commit -m "chore: auto-sync dotfiles ($CHANGED)"

# 4. Push
git push origin main

echo "$(date '+%Y-%m-%d %H:%M') synced: $CHANGED" >> "$LOG"
