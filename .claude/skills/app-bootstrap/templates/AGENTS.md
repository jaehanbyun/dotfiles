# AGENTS.md - {APP_NAME}

## What

{APP_ONE_LINER}

## Why

Target user: {TARGET_USER}

Core problem: {CORE_PROBLEM}

## Stack

Initial platform: {PLATFORM}

Preferred stack: {STACK}

## Verify Before Done

{VERIFY_COMMANDS}

## Read These First

1. `HANDOFF.md` - current state and next pickup point
2. `docs/workflow-orchestration.md` - planning and verification rules
3. `docs/ai-native-workflow.md` - agent/design handoff workflow
4. `docs/ARCHITECTURE.md` - architecture and boundaries
5. `docs/conventions.md` - code conventions
6. `docs/design/research-protocol.md` - design reference workflow
7. `docs/tooling-stack.md` - phased service adoption
8. `docs/exec-plans/active/` - active implementation plans
9. `docs/decisions/` - ADRs

## Operating Rules

- Plan first for 3+ step work or architectural decisions.
- Keep implementation scope tied to the active exec plan.
- Do not add dependencies, services, deployment, or paid tooling without an ADR
  or explicit user approval.
- Do not commit, push, open PRs, or deploy unless explicitly requested.
- Verify relevant typecheck, lint, and tests before marking work done.
- Capture blockers and next pickup points in `HANDOFF.md`.

