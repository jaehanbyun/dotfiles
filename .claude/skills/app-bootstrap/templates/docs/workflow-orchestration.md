# Workflow Orchestration

## Plan First

For 3+ step work, architecture decisions, dependency changes, or external
service setup, write or update an exec plan before implementation.

Plans live in `docs/exec-plans/active/`.

## Execution Unit

One meaningful issue or vertical slice should map to:

- one plan
- focused implementation
- relevant verification
- `HANDOFF.md` update

## Verification Before Done

Run relevant checks before marking work complete.

Suggested commands:

```bash
{VERIFY_COMMANDS}
```

If verification cannot run, record the reason and residual risk.

## Decisions

Use ADRs for:

- framework or architecture changes
- database/auth/payment choices
- deployment and hosting choices
- third-party services with cost, lock-in, or secret handling

## Core Principles

- Simplicity first
- Root cause over symptom fixes
- Minimal impact
- Explicit handoff

