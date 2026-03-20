#!/bin/bash
# Install .claude/ config files to ~/.claude/
# Run: ./install-claude.sh

set -e

SRC="$(cd "$(dirname "$0")" && pwd)/.claude"
DEST="$HOME/.claude"

if [ ! -d "$SRC" ]; then
  echo "Error: $SRC not found"
  exit 1
fi

mkdir -p "$DEST"

# Files to sync
FILES="CLAUDE.md settings.json keybindings.json code-review.yml"
DIRS="agents commands skills hooks docs"

for f in $FILES; do
  [ -f "$SRC/$f" ] && cp "$SRC/$f" "$DEST/$f" && echo "  $f"
done

for d in $DIRS; do
  if [ -d "$SRC/$d" ]; then
    mkdir -p "$DEST/$d"
    cp -r "$SRC/$d"/* "$DEST/$d"/ 2>/dev/null && echo "  $d/"
  fi
done

echo "Claude config installed to $DEST"
