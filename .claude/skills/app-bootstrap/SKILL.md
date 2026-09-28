---
name: app-bootstrap
description: |
  Interview-driven bootstrap for a new app development workspace. Use when the
  user starts a new app folder/repo and wants reusable product, design,
  architecture, implementation, verification, and release workflow setup before
  coding. Creates project operating docs, ADR/plan templates, and the first
  vertical-slice execution plan. Does not start implementation unless the user
  explicitly asks after the plan is ready.
---

# App Bootstrap

Set up a new app workspace by interviewing the user, creating durable project
operating documents, and stopping at a clear first implementation plan.

This skill is intentionally conservative: it should prevent premature coding,
early dependency sprawl, and unclear product direction.

## Trigger

Use this skill when the user says or implies:

- "Set up this folder as a new app workspace"
- "Start a new app project"
- "Bootstrap app development workflow"
- "Use app-bootstrap"
- They want an interview-style setup instead of pasting a long prompt

## Outcome

By the end, the repo should have:

- `AGENTS.md`
- `HANDOFF.md`
- `docs/ARCHITECTURE.md`
- `docs/conventions.md`
- `docs/workflow-orchestration.md`
- `docs/ai-native-workflow.md`
- `docs/design/research-protocol.md`
- `docs/tooling-stack.md`
- `docs/exec-plans/active/0001-bootstrap.md`
- `docs/decisions/0000-template.md`

If the user explicitly requests a minimal setup, create only:

- `AGENTS.md`
- `HANDOFF.md`
- `docs/exec-plans/active/0001-bootstrap.md`
- `docs/decisions/0000-template.md`

## Non-Goals

- Do not implement app features during bootstrap.
- Do not install dependencies unless the user explicitly asks for scaffolding.
- Do not connect paid services, deployment targets, remotes, or secrets.
- Do not create production credentials.
- Do not commit, push, or open PRs unless explicitly requested.

## Workflow

### 1. Inspect The Workspace

Run lightweight read-only checks:

```bash
pwd
git status --short
find . -maxdepth 2 -type f | sed -n '1,120p'
```

If the folder is not a git repo, do not run `git init` unless the user confirms.

If important files already exist, read them before editing:

```bash
sed -n '1,220p' AGENTS.md 2>/dev/null || true
sed -n '1,220p' README.md 2>/dev/null || true
sed -n '1,220p' HANDOFF.md 2>/dev/null || true
```

### 2. Infer Defaults Before Asking

Before asking the user about platform or stack, infer them from the workspace
and the user's wording.

Workspace signals:

- `package.json` with Expo dependencies -> React Native Expo + TypeScript
- `app.json` or `app.config.*` -> React Native Expo
- `next.config.*` -> Next.js + TypeScript
- `vite.config.*` -> Vite + TypeScript
- `pyproject.toml` with FastAPI -> FastAPI backend
- `ios/` or `android/` native folders -> native mobile project

User wording defaults:

- "app" or "mobile app" with no other stack signal -> React Native Expo +
  TypeScript
- "web app", "website", "site", "admin web", "internal tool", or explicit
  "web dashboard" -> Next.js + TypeScript
- "dashboard", "SaaS", "CRM", or "operational tool" are product/interface
  style signals, not platform signals by themselves. Do not use them alone to
  override the app/mobile default.
- "API" or "backend" -> FastAPI + Python unless another stack is present

Only ask about platform/stack when:

- the user's wording clearly conflicts with workspace files
- multiple stacks are already present and the first target is unclear
- the product sounds like both a mobile app and an operator dashboard, and the
  first build target is not explicit
- the user explicitly asks to choose or compare stacks

When defaults are inferred, write them as assumptions in `HANDOFF.md` and the
first exec plan instead of asking the user to confirm upfront.

### 3. Ask Intake Questions

Ask no more than 4 questions at once. Prefer the user's language. Do not ask
questions that the user already answered in the current request.

Required first pass:

1. What is the app name or working name?
2. Who is the target user, and what painful problem does the app solve?
3. Are there reference apps, competitors, design directions, or styles to avoid?
4. What is the first user-visible outcome this app must deliver?

Conditional questions:

- Ask platform/stack only if inference failed or there is a real conflict.
- Ask scope only if the user has not already said `docs-only`, `scaffold`, or
  `vertical-slice`.

If the user cannot answer, proceed with explicit assumptions and mark them in
`HANDOFF.md` under "Open Questions".

Optional second pass, only if needed:

- Monetization expectation
- Auth/account needs
- Data persistence needs
- AI/LLM usage
- Offline/background behavior
- Initial release target such as TestFlight, web beta, or internal demo

### 4. Choose Scope

Use one of these scope labels in `HANDOFF.md`:

- `docs-only`: project operating docs and first plan only
- `scaffold`: create app skeleton after docs are ready
- `vertical-slice`: implement the first minimal flow after user approval

Default to `docs-only` unless the user clearly asks otherwise.

### 5. Create Operating Docs

Create concise, project-specific docs. Keep `AGENTS.md` short and put detail in
`docs/`.

Use the templates in this skill as a starting point:

- `templates/AGENTS.md`
- `templates/HANDOFF.md`
- `templates/docs/ARCHITECTURE.md`
- `templates/docs/conventions.md`
- `templates/docs/workflow-orchestration.md`
- `templates/docs/ai-native-workflow.md`
- `templates/docs/design/research-protocol.md`
- `templates/docs/tooling-stack.md`
- `templates/docs/exec-plans/active/0001-bootstrap.md`
- `templates/docs/decisions/0000-template.md`

Replace placeholders such as:

- `{APP_NAME}`
- `{APP_ONE_LINER}`
- `{TARGET_USER}`
- `{CORE_PROBLEM}`
- `{PLATFORM}`
- `{STACK}`
- `{VERIFY_COMMANDS}`
- `{FIRST_SLICE}`

If a template does not exactly fit, adapt it to the project instead of copying
mechanically.

### 6. Design Research Protocol

Document a research order that can transfer between projects:

1. Refero MCP for broad screen and flow patterns.
2. Mobbin for deeper mobile references or regional apps when available.
3. Open Design or Claude Design for high-fidelity exploration and handoff.
4. Save durable references under `docs/design/_references/`.
5. Convert accepted patterns into `docs/design/` specs before implementation.

Do not claim a design direction is validated unless references were actually
reviewed in the current project.

### 7. Architecture And Tooling

For architecture docs, prefer:

- minimal layers
- one app first unless multi-app structure is necessary
- no premature monorepo/packages/codegen
- ADR before major infrastructure decisions
- external services introduced by phase, not all at once

For tooling docs, include:

- local verification commands
- lint/typecheck/test expectations
- release-readiness checklist
- secret management rules
- when to add Sentry/PostHog/Supabase/RevenueCat/Stripe/EAS/Vercel/etc.

Only include services relevant to the app. Mark uncertain services as
`deferred`.

### 8. First Vertical Slice Plan

Write `docs/exec-plans/active/0001-bootstrap.md` with:

- Context
- Goals
- Non-goals
- Assumptions
- Work plan checklist
- Verification checklist
- Open questions
- Stop point

The stop point should usually be:

> Stop after docs and first plan are ready. Do not implement until the user
> approves the first vertical slice.

### 9. Final Response

End with a concise summary:

- created/updated files
- assumptions made
- decisions needed from the user
- recommended next prompt

Example next prompt:

```text
Read HANDOFF.md and docs/exec-plans/active/0001-bootstrap.md, then implement
the approved first vertical slice. Keep the scope narrow and run the documented
verification commands before finishing.
```

## Quality Bar

- The setup should be reusable but not generic filler.
- Every generated doc must help future agents act correctly.
- Keep project-specific facts in the project, not in this global skill.
- If user answers conflict with existing files, report the conflict and ask
  before overwriting.
- Prefer clear stop points over open-ended planning.
