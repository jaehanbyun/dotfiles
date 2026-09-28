---
name: next-workspace-start
description: Start or resume a Conductor app workspace. Use when the user opens a new workspace/session and wants Codex to choose the next GitHub issue, continue the current PR, or infer the next documented task without pasting a long prompt; also use when they say "next-workspace-start", "workspace start", "다음 이슈 골라서 진행", or "이 워크스페이스 이어서 해줘".
---

# Next Workspace Start

Use this as the entry workflow for Conductor app workspaces. The goal is to
remove the need for the user to paste a long startup prompt every time.

## Outcome

By the end of the turn, either:

- a concrete issue/PR task is chosen, implemented, verified, committed, pushed,
  and PR-created/updated; or
- a blocker is documented with evidence and the next action is clear.

Do not stop after planning unless the user explicitly asks for planning only.

## Fast Start

Run the bundled read-only snapshot first:

```bash
bash ~/.codex/skills/next-workspace-start/scripts/session_snapshot.sh
```

Then read only the project documents that exist and are needed for the chosen
path:

```bash
sed -n '1,180p' AGENTS.md 2>/dev/null
sed -n '1,160p' HANDOFF.md 2>/dev/null
sed -n '1,220p' docs/workflow-orchestration.md 2>/dev/null
sed -n '1,220p' docs/ai-native-workflow.md 2>/dev/null
sed -n '1,180p' README.md 2>/dev/null
```

If the task touches UI, also read the project's design/iteration docs when they
exist, for example `docs/rn-iteration.md`, `docs/design/README.md`, or relevant
`docs/design/04-screens/*.md`.

## Task Selection

Choose the task in this order:

1. **Explicit user task wins.** If the user named an issue, PR, file, bug, or
   feature, work that.
2. **Current branch PR continuation.** If the current branch has an open PR,
   inspect it with `gh pr view` and continue hardening/review fixes unless the
   user clearly wants a new task.
3. **Open PR dedupe.** If no current-branch PR exists, inspect open PRs before
   choosing an issue. Do not duplicate work already covered by an open PR;
   continue/review that PR or choose the next uncovered issue.
4. **Open GitHub issue queue.** If no task is specified, list open issues and
   pick the highest priority non-decision issue:
   - Prefer labels/titles containing `P0`, then `P1`, then lower priority.
   - Prefer lower issue number when priority is tied.
   - Skip `[Decision]` issues unless they block the chosen implementation.
   - If a design dependency exists, handle the design handoff first.
5. **Docs fallback.** If GitHub is unavailable, use `HANDOFF.md`,
   `docs/exec-plans/active/`, and project docs to pick the next clearly
   documented task.

Ask the user only when two unrelated tasks are equally urgent or when the next
step would require an infrastructure-level change, secret, paid service, or
destructive operation.

## Required Workspace Rules

- Use repository root from the active Conductor workspace; do not rename the
  current branch.
- Follow `AGENTS.md` strictly when present.
- For 3+ step work, create/update an exec plan under `docs/exec-plans/active/`
  before implementation when the project uses that convention.
- Keep changes scoped. Do not do opportunistic cleanup.
- Respect dirty worktrees. Never revert unrelated user changes.
- Leave GitHub issue comments when scope/status changes.
- Use English Conventional Commits.
- Prefer Korean for user-facing summaries.

## Design Workflow

When the project has design work and Open Design MCP is available, use Open
Design first:

1. `mcp__open_design__list_projects`
2. `mcp__open_design__get_project(project: "<project name or id>")`
3. `mcp__open_design__list_files(project: "<project name or id>")`
4. `mcp__open_design__search_files(project: "<project name or id>", query: "<short keyword>")`
5. `mcp__open_design__get_file(...)` for relevant artifact files

For CookPick, the default Open Design project is usually `coopick`.

For screen/flow QA, use:

- the project's screen QA prompt if present, such as
  `docs/design/_open-design-screen-qa-prompt.md`
- the project's visual loop docs if present, such as `docs/rn-iteration.md`

For external references, use Refero MCP first with short 3-5 word queries. Use
Mobbin only when Korean app references are needed and the session has access.

## Implementation Workflow

1. State the selected task in a short update.
2. Create/update the exec plan if the task has 3+ steps.
3. Read the smallest relevant code/docs surface.
4. Implement using existing architecture and conventions.
5. Run focused tests during development.
6. Run required verification before final.
7. Update `HANDOFF.md`, exec plan, design docs, ADRs, and GitHub comments when
   status changed.
8. Commit, push, and create/update a PR against `main` when the work is ready.

## Verification Defaults

Run the project's documented verification commands. Common defaults:

```bash
(test -d apps/api && cd apps/api && uv run pytest && uv run ruff check .)
(test -d apps/mobile && cd apps/mobile && pnpm typecheck && pnpm lint && pnpm test:unit)
test -f package.json && pnpm typecheck && pnpm lint
git diff --check
```

For RN UI changes, run the simulator visual capture where practical. E2E/Maestro
is required only when the relevant native/dev setup exists; otherwise document
the known blocker.

## Final Response

Keep the final response compact and include:

- selected task / issue / PR
- changed files summary
- verification commands and results
- PR URL or branch status
- remaining blockers, if any
