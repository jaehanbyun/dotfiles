#!/usr/bin/env bash
set -euo pipefail

export HOME="/Users/byeonjaehan"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

lockdir="${TMPDIR:-/tmp}/com.byeonjaehan.brewu.lock"
if ! mkdir "$lockdir" 2>/dev/null; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') brewu already running; skipping."
  exit 0
fi
trap 'rmdir "$lockdir"' EXIT

if ! command -v brew >/dev/null 2>&1; then
  echo "brew not found on PATH: $PATH" >&2
  exit 127
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') starting brewu: brew upgrade; brew cleanup"
brew upgrade
brew cleanup
echo "$(date '+%Y-%m-%d %H:%M:%S') finished brewu"
