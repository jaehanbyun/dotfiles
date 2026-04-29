#!/bin/bash
# WorktreeCreate hook: prompts for branch name, falls back to date-based default
set -e

INPUT=$(cat)
PROJECT_DIR=$(echo "$INPUT" | jq -r '.cwd')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id')

SHORT_ID="${SESSION_ID:0:6}"
DATE=$(date +%Y-%m-%d)
DEFAULT_BRANCH="claude/${DATE}-${SHORT_ID}"

MAIN_BRANCH=""
for candidate in main master develop; do
  if git -C "$PROJECT_DIR" show-ref --verify --quiet "refs/heads/$candidate" 2>/dev/null; then
    MAIN_BRANCH="$candidate"
    break
  fi
done
[ -z "$MAIN_BRANCH" ] && MAIN_BRANCH=$(git -C "$PROJECT_DIR" symbolic-ref --short HEAD 2>/dev/null || echo "HEAD")

BRANCH_NAME="$DEFAULT_BRANCH"
if [ -e /dev/tty ] && [ -r /dev/tty ]; then
  {
    echo ""
    echo "📝 Worktree branch name (Enter for default: $DEFAULT_BRANCH)"
    printf "> "
  } >/dev/tty
  if read -r -t 60 USER_INPUT </dev/tty; then
    USER_INPUT=$(echo "$USER_INPUT" | xargs | tr ' ' '-')
    if [ -n "$USER_INPUT" ]; then
      if [[ "$USER_INPUT" == */* ]]; then
        BRANCH_NAME="$USER_INPUT"
      else
        BRANCH_NAME="feature/$USER_INPUT"
      fi
    fi
  fi
fi

SAFE_NAME=$(echo "$BRANCH_NAME" | tr '/' '-')
WORKTREE_DIR="$PROJECT_DIR/.claude/worktrees/$SAFE_NAME"

echo "Creating worktree: branch=$BRANCH_NAME path=$WORKTREE_DIR base=$MAIN_BRANCH" >&2

mkdir -p "$(dirname "$WORKTREE_DIR")"
git -C "$PROJECT_DIR" worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" "$MAIN_BRANCH" >&2

for envfile in .env .env.local .env.development .env.production; do
  if [ -f "$PROJECT_DIR/$envfile" ]; then
    cp "$PROJECT_DIR/$envfile" "$WORKTREE_DIR/$envfile"
    echo "Copied $envfile" >&2
  fi
done

echo "$WORKTREE_DIR"
exit 0
