#!/usr/bin/env bash
set -u

ROOT="${1:-$(pwd)}"
cd "$ROOT" || exit 1

echo "== Workspace snapshot =="
printf "cwd: %s\n" "$(pwd)"
printf "date: %s\n" "$(date '+%Y-%m-%d %H:%M:%S %Z')"

echo
echo "== Git =="
git status --short --branch 2>/dev/null || true
printf "branch: "
git branch --show-current 2>/dev/null || true
echo "recent commits:"
git log --oneline --decorate --max-count=5 2>/dev/null || true

echo
echo "== Remotes =="
git remote -v 2>/dev/null || true

origin_url="$(git config --get remote.origin.url 2>/dev/null || true)"
repo="$origin_url"
repo="${repo#https://github.com/}"
repo="${repo#git@github.com:}"
repo="${repo%.git}"
if [ -z "$repo" ]; then
  repo=""
fi

gh_token_env=""
if command -v gh >/dev/null 2>&1; then
  if [[ "$repo" == jaehanbyun/* ]] && gh auth token --user jaehanbyun >/dev/null 2>&1; then
    gh_token_env="$(gh auth token --user jaehanbyun)"
  elif [ -n "$repo" ] && ! gh repo view "$repo" >/dev/null 2>&1 && gh auth token --user jaehanbyun >/dev/null 2>&1; then
    gh_token_env="$(gh auth token --user jaehanbyun)"
  fi
fi

run_gh() {
  if [ -n "$gh_token_env" ]; then
    GH_TOKEN="$gh_token_env" gh "$@"
  else
    gh "$@"
  fi
}

if command -v gh >/dev/null 2>&1 && [ -n "$repo" ]; then
  echo
  echo "== Current PR =="
  current_branch="$(git branch --show-current 2>/dev/null || true)"
  run_gh pr view --repo "$repo" --json number,title,url,state,isDraft,mergeable,baseRefName,headRefName 2>/dev/null \
    || run_gh pr list --repo "$repo" --head "$current_branch" --json number,title,url,state,isDraft,mergeable,baseRefName,headRefName 2>/dev/null \
    || echo "No PR detected for current branch."

  echo
  echo "== Open PRs =="
  run_gh pr list --repo "$repo" --state open --limit 20 --json number,title,url,isDraft,mergeable,baseRefName,headRefName 2>/dev/null || echo "Could not list PRs."

  echo
  echo "== Open issues =="
  run_gh issue list --repo "$repo" --state open --limit 30 --json number,title,labels,url,updatedAt 2>/dev/null || echo "Could not list issues."
else
  echo
  echo "== GitHub =="
  echo "gh or GitHub remote unavailable; use HANDOFF.md and docs/exec-plans/active as fallback."
fi

echo
echo "== Active exec plans =="
find docs/exec-plans/active -maxdepth 1 -name '*.md' -type f 2>/dev/null | sort | tail -20 || true

echo
echo "== Handoff pointers =="
if [ -f HANDOFF.md ]; then
  rg -n "2026-|current|현재|next|다음|TODO|PR #|Open Design|issue|이슈" HANDOFF.md 2>/dev/null | head -80 || true
fi
