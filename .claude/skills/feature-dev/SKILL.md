---
name: feature-dev
version: 1.0.0
description: |
  Feature development harness combining gstack skills for insights/review with
  Anthropic harness engineering patterns for implementation. Four phases:
  Ideation (gstack), Planning (gstack), Implementation (sprint harness), QA & Ship (gstack).
  Full evaluator per sprint with GAN-like design iteration for UI features.
  Use when asked to "develop a feature", "feature dev", "build this feature",
  or "start feature development".
benefits-from: [office-hours, autoplan, ship]
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
  - WebSearch
---

# /feature-dev — Full Feature Development Harness

One command. Idea in, shipped feature out. Combines gstack for insights/review with
Anthropic's harness engineering for disciplined sprint-based implementation.

```
Phase 0: Ideation (gstack)     → spec.md
Phase 1: Planning (gstack)     → plan.md + sprint contracts
Phase 2: Implementation (harness) → code + handoffs + commits
Phase 3: QA & Ship (gstack)    → PR + deploy
```

---

## Initialization

### Step 1: Create feature folder

```bash
FEATURE_INPUT="$ARGUMENTS"  # user's feature description
SLUG=$(echo "$FEATURE_INPUT" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-' | head -c 40)
DATE=$(date +%Y-%m-%d)
FEATURE_DIR=".claude/plans/${DATE}-${SLUG}"
mkdir -p "$FEATURE_DIR/sprints"
echo "FEATURE_DIR=$FEATURE_DIR"
echo "SLUG=$SLUG"
```

### Step 2: Detect project type

```bash
detect_evaluators() {
  local dir
  dir=$(pwd)

  # Build command
  if [ -f "$dir/package.json" ]; then
    echo "BUILD=npm run build"
  elif [ -f "$dir/Cargo.toml" ]; then
    echo "BUILD=cargo build"
  elif [ -f "$dir/go.mod" ]; then
    echo "BUILD=go build ./..."
  elif [ -f "$dir/build.gradle.kts" ] || [ -f "$dir/build.gradle" ]; then
    echo "BUILD=./gradlew build"
  elif [ -f "$dir/pom.xml" ]; then
    echo "BUILD=./mvnw compile"
  elif [ -f "$dir/requirements.txt" ] || [ -f "$dir/pyproject.toml" ]; then
    echo "BUILD=python -m py_compile"
  else
    echo "BUILD=echo 'no build system detected'"
  fi

  # Test command
  if [ -f "$dir/package.json" ]; then
    echo "TEST=npm test"
  elif [ -f "$dir/Cargo.toml" ]; then
    echo "TEST=cargo test"
  elif [ -f "$dir/go.mod" ]; then
    echo "TEST=go test ./..."
  elif [ -f "$dir/build.gradle.kts" ] || [ -f "$dir/build.gradle" ]; then
    echo "TEST=./gradlew test"
  elif [ -f "$dir/pom.xml" ]; then
    echo "TEST=./mvnw test"
  elif [ -f "$dir/pytest.ini" ] || [ -f "$dir/pyproject.toml" ]; then
    echo "TEST=pytest"
  else
    echo "TEST=echo 'no test runner detected'"
  fi

  # Lint command
  if [ -f "$dir/package.json" ]; then
    echo "LINT=npm run lint 2>/dev/null || npx eslint . 2>/dev/null || echo 'no linter'"
  elif [ -f "$dir/Cargo.toml" ]; then
    echo "LINT=cargo clippy"
  elif [ -f "$dir/go.mod" ]; then
    echo "LINT=golangci-lint run 2>/dev/null || go vet ./..."
  else
    echo "LINT=echo 'no linter detected'"
  fi

  # Typecheck command
  if [ -f "$dir/tsconfig.json" ]; then
    echo "TYPECHECK=npx tsc --noEmit"
  elif [ -f "$dir/pyproject.toml" ] && grep -q "mypy" "$dir/pyproject.toml" 2>/dev/null; then
    echo "TYPECHECK=mypy ."
  else
    echo "TYPECHECK=echo 'no typecheck available'"
  fi

  # UI detection
  if [ -f "$dir/package.json" ] && grep -qE '"react"|"vue"|"svelte"|"next"|"nuxt"|"angular"' "$dir/package.json" 2>/dev/null; then
    echo "HAS_UI=true"
  else
    echo "HAS_UI=false"
  fi
}

detect_evaluators
```

### Step 3: Write initial INDEX.md

Write `$FEATURE_DIR/INDEX.md`:

```markdown
# Feature: {feature description}
Created: {DATE} | Status: active | Phase: 0
Resume Point: Phase 0 — ideation not started

## Project Detection
- Type: {detected type}
- Build: `{BUILD}`
- Test: `{TEST}`
- Lint: `{LINT}`
- Typecheck: `{TYPECHECK}`
- Has UI: {HAS_UI}

## Phase Status
- [ ] Phase 0: Ideation
- [ ] Phase 1: Planning
- [ ] Phase 2: Implementation
- [ ] Phase 3: QA & Ship
```

Report to user: "Feature folder created at `$FEATURE_DIR`. Starting Phase 0."

---

## Phase 0: Ideation & Scoping

### Step 0.1: Run /office-hours

Read the office-hours skill from disk:

```bash
cat ~/.claude/skills/gstack/office-hours/SKILL.md
```

Follow the office-hours skill inline, **skipping these sections** (handled by parent):
- Preamble (run first)
- AskUserQuestion Format
- Completeness Principle
- Search Before Building
- Contributor Mode
- Completion Status Protocol
- Telemetry (run last)

If the Read fails: "Could not load /office-hours. Proceeding with manual spec creation."

### Step 0.2: Clarify if needed

If the feature requirements are still ambiguous after office-hours, run /clarify:vague inline:

```bash
cat ~/.claude/skills/clarify/vague/SKILL.md 2>/dev/null
```

Follow inline with same skip list as above.

### Step 0.3: Write spec.md

Write `$FEATURE_DIR/spec.md` with this structure:

```markdown
# Feature Spec: {name}

## Problem Statement
{What problem does this solve? Who has this problem? Why now?}

## Success Criteria
1. {Measurable criterion with verification method}
2. {Measurable criterion with verification method}
3. ...

## Non-Goals
- {What this feature explicitly does NOT do}

## Design Direction (UI features only)
- Mood/aesthetic: {description, NOT "modern clean"}
- Reference: {DESIGN.md tokens, inspiration, or "establish in Phase 1"}
- Anti-patterns: {what to avoid}

## Original Input
{User's original feature description, verbatim}
```

### Step 0.4: Phase gate

AskUserQuestion:
> **Phase 0 complete.** Spec written to `$FEATURE_DIR/spec.md`.
>
> [Show spec summary]
>
> Proceed to Phase 1 (Planning)?

Options:
- A) Proceed to Phase 1
- B) Edit the spec first
- C) Cancel

Update INDEX.md: Phase 0 complete, Resume Point → "Phase 1 — planning not started"

---

## Phase 1: Planning & Review

### Step 1.1: Design system check (UI features only)

If `HAS_UI=true` and no DESIGN.md exists in the project root:

AskUserQuestion:
> No DESIGN.md found. For UI features, a design system improves consistency and evaluator accuracy.
>
> RECOMMENDATION: Run /design-consultation to establish design tokens.

Options:
- A) Run /design-consultation now (recommended)
- B) Skip — proceed without design system

If A: Read and follow `~/.claude/skills/gstack/design-consultation/SKILL.md` inline.

### Step 1.2: Create plan with sprint breakdown

Enter plan mode. Create `$FEATURE_DIR/plan.md` with:

```markdown
# Implementation Plan: {feature name}

## Architecture Overview
{High-level design, component relationships, data flow}

## Sprint Breakdown

### Sprint 01: {goal}
- Type: backend | frontend | fullstack
- Files: {list}
- Dependencies: none | sprint-NN
- Success criteria:
  1. {criterion} — verify: {method}

### Sprint 02: {goal}
...

## Sprint Ordering Rationale
{Why this order: infrastructure first, features next, polish last}
```

**Sprint sizing rules:**
- Each sprint: one focused aspect (~1 file group, ~1 test group)
- Sprint descriptions are concrete: "Add UserService.create() with validation and unit tests"
- Mark each sprint as `backend`, `frontend`, or `fullstack` (determines evaluator config)
- Order by dependency: infrastructure → core logic → features → UI polish → integration

### Step 1.3: Run review gauntlet

AskUserQuestion:
> Plan created with {N} sprints. Choose review depth:
>
> RECOMMENDATION: Choose A for thorough review.

Options:
- A) /autoplan — full CEO + Eng + Design review (recommended, ~$5-8)
- B) /plan-eng-review only — architecture review (~$2-3)
- C) Skip reviews — proceed with plan as-is

If A: Read and follow `~/.claude/skills/gstack/autoplan/SKILL.md` inline.
If B: Read and follow `~/.claude/skills/gstack/plan-eng-review/SKILL.md` inline.

### Step 1.4: Generate sprint contracts

For each sprint in the approved plan, write `$FEATURE_DIR/sprints/sprint-NN-contract.md`:

```markdown
# Sprint NN: {Goal}

## Context
{1-2 sentences: what was done so far, why this sprint exists}

## Goal
{One sentence deliverable}

## Type
backend | frontend | fullstack

## Success Criteria
- [ ] {Criterion 1} — verify: {exact command or check}
- [ ] {Criterion 2} — verify: {exact command or check}

## Files to Modify
- `path/to/file.ts` — {what changes}
- `path/to/file.test.ts` — {new: tests}

## Constraints
- {Architectural constraints from plan/reviews}
- {Dependencies from previous sprints}

## Design Direction (frontend sprints only)
- Mood: {from spec.md or DESIGN.md}
- Tokens: {colors, fonts, spacing from DESIGN.md}
- Anti-patterns: {avoid purple gradients, Inter font, generic layouts}
- Reference: {screenshot paths or descriptions}

## Evaluation Commands
```bash
{BUILD}
{TEST}
{LINT}
{TYPECHECK}
```
```

### Step 1.5: Phase gate

Update INDEX.md: Phase 1 complete, list all sprint contracts, Resume Point → "Phase 2 — sprint 01"

---

## Phase 2: Implementation (Harness Loop)

For each sprint (01, 02, ...):

### Step 2.1: Sprint setup

Read the sprint contract: `$FEATURE_DIR/sprints/sprint-NN-contract.md`
Read the previous handoff (if any): `$FEATURE_DIR/sprints/sprint-(NN-1)-handoff.md`

Display to user:
> **Sprint NN: {goal}**
> Type: {backend|frontend|fullstack}
> Success criteria: {list}
> Starting generator...

### Step 2.2: Generator (subagent)

Dispatch a subagent with this prompt:

```
You are implementing Sprint NN of a feature development harness.

## Sprint Contract
{paste full contract content}

## Previous Sprint Context
{paste previous handoff, or "This is the first sprint."}

## Spec Context
{paste relevant sections from spec.md}

## Instructions
1. Read existing code to understand patterns and conventions
2. Implement the changes described in the contract
3. Write tests that verify each success criterion
4. Run the evaluation commands and fix any failures
5. When all evaluation commands pass, report your results

## Output Format
When done, report:
- Files created/modified (with brief description of changes)
- Test results (pass/fail counts)
- Any decisions you made that weren't in the contract
- Any concerns or edge cases you noticed

DO NOT skip tests. DO NOT leave TODOs. Implement completely.
```

Subagent type: `general-purpose` (full tool access)

### Step 2.3: Programmatic evaluation (Layer 1)

After generator returns, run evaluation commands:

```bash
echo "=== BUILD ===" && {BUILD} 2>&1
echo "=== TEST ===" && {TEST} 2>&1
echo "=== LINT ===" && {LINT} 2>&1
echo "=== TYPECHECK ===" && {TYPECHECK} 2>&1
```

Capture output. If any command fails → FAIL with output.

### Step 2.4: Agent evaluation (Layer 2)

Dispatch the feature-evaluator agent:

```
Read the agent definition at ~/.claude/agents/feature-evaluator.md and follow it.

Sprint contract: $FEATURE_DIR/sprints/sprint-NN-contract.md
Sprint type: {backend|frontend|fullstack}
Programmatic results: {paste Layer 1 results}

Evaluate this sprint against its contract. Follow the full evaluation procedure.
{If frontend sprint: "This is a UI sprint. Include design grading (Step 5)."}
```

Subagent type: `general-purpose` (evaluator has read-only tools only per its agent def)

### Step 2.5: Visual evaluation (Layer 3, UI sprints only)

**Only for sprints with type `frontend` or `fullstack`:**

```bash
# Start dev server if not running
{START_DEV_SERVER} &
sleep 3

# Take screenshot via /browse
$B goto {APP_URL}
$B screenshot /tmp/sprint-NN-screenshot.png
$B snapshot -i -a -o /tmp/sprint-NN-annotated.png
```

Read the screenshots. The agent evaluator's design grading (from Step 2.4) covers
the 4 dimensions. Check if all scores are >= 6/10.

### Step 2.6: Verdict

Combine results from all 3 layers:

**PASS** if ALL of:
- Layer 1: all evaluation commands pass
- Layer 2: agent evaluator returns PASS
- Layer 3 (UI only): all 4 design dimensions >= 6/10

**FAIL** if ANY layer fails.

### Step 2.7a: On PASS

```bash
# Auto-commit
git add -A
git commit -m "feat(sprint-NN): {sprint goal}"
```

Write handoff file `$FEATURE_DIR/sprints/sprint-NN-handoff.md`:

```markdown
# Sprint NN Handoff

## Completed
- {What was done, 2-3 bullets}

## Test Status
- Build: PASS/FAIL
- Tests: PASS (N/M)
- Lint: PASS/FAIL
- Typecheck: PASS/FAIL

## Design Scores (UI sprints only)
- Design Quality: N/10
- Originality: N/10
- Craft: N/10
- Functionality: N/10

## Key Decisions
- {Decision 1: chose X over Y because Z}

## Files Changed
- `path/file.ts` — {summary}

## Next Sprint Context
{What the next sprint needs to know}

## Commit
{hash} — `feat(sprint-NN): {goal}`
```

Write evaluation results to `$FEATURE_DIR/sprints/sprint-NN-eval.md` (full evaluator output).

Update INDEX.md: mark sprint NN as PASS with commit hash.

**Compress older handoffs:** If sprint NN >= 3, compress sprint (NN-2) handoff to:
```
## Sprint {NN-2} Summary (compressed)
Goal: {one line}. Status: PASS. Files: {list}. Key decision: {one line}.
```

### Step 2.7b: On FAIL (retry loop)

Determine max retries: 3 (backend) or 5 (frontend/fullstack).

If retries remaining:
1. Extract structured feedback from evaluator
2. Display to user: "Sprint NN failed evaluation (attempt {X}/{max}). Retrying with feedback..."
3. Dispatch generator subagent again with:
   - Original contract
   - Previous handoff
   - **Evaluator feedback** (the specific failures and suggestions)
   - Instruction: "Fix the issues identified by the evaluator. Focus specifically on: {list failures}"
4. Return to Step 2.3

If max retries exceeded:
AskUserQuestion:
> **Sprint NN failed after {max} attempts.**
>
> Last evaluation:
> {summary of failures}
>
> Evaluator feedback:
> {last feedback}

Options:
- A) Let me fix it manually, then continue to next sprint
- B) Skip this sprint and continue (mark as SKIPPED)
- C) Abort feature development

### Step 2.8: Between sprints

After each sprint completes (pass or skip):
- Update INDEX.md with sprint status
- Report progress: "Sprint NN complete. {N-remaining} sprints remaining."
- If sprint NN was the last → proceed to Phase 3

---

## Phase 3: QA & Ship

### Step 3.1: Full QA

AskUserQuestion:
> **All sprints complete.** Choose QA depth:
>
> RECOMMENDATION: Choose A for UI features, B for backend-only.

Options:
- A) /qa — full systematic testing with bug fixing (recommended for UI)
- B) /qa-only — report bugs without fixing
- C) /design-review — visual QA only (UI features)
- D) Skip QA — proceed to review

If A/B/C: Read and follow the selected skill inline.

If QA finds issues:
AskUserQuestion:
> QA found {N} issues. Create fix sprints?

Options:
- A) Create fix sprints and return to Phase 2 (recommended)
- B) Ship with known issues
- C) Cancel

If A: Generate fix sprint contracts from QA findings, return to Phase 2.

### Step 3.2: Code review

Read and follow `~/.claude/skills/gstack/review/SKILL.md` inline.

### Step 3.3: Ship

Read and follow `~/.claude/skills/gstack/ship/SKILL.md` inline.

### Step 3.4: Completion

Update INDEX.md: Status → completed, all phases checked off.

Report to user:
> **Feature complete.**
> - Sprints: {N} total, {passed} passed, {skipped} skipped
> - Commits: {list}
> - PR: {URL if created}

---

## Session Resumability

When resuming a feature dev session (detected by `<when-starting-a-new-session>`):

1. Read `$FEATURE_DIR/INDEX.md`
2. Report current state: "Feature '{name}' at Phase {N}, Sprint {NN}."
3. Read the current sprint contract and last handoff
4. Resume from the Resume Point

The INDEX.md Resume Point must be specific enough to immediately continue:
- "Phase 2 — sprint 03, evaluation failed attempt 2/3, awaiting generator retry"
- "Phase 3 — /qa complete, /review not started"

---

## Cost Model

| Phase | Tool | Model | Est. Cost |
|-------|------|-------|-----------|
| 0 | /office-hours | Opus | $3-5 |
| 1 | /autoplan | Opus | $5-10 |
| 1 | /design-consultation (if UI) | Opus | $3-5 |
| 2 | Generator subagent × N sprints | Sonnet | $15-50 |
| 2 | Evaluator agent × N sprints | Sonnet | $10-30 |
| 2 | Retries (avg 1 per sprint) | Sonnet | $10-30 |
| 3 | /qa + /review | Sonnet | $5-10 |
| 3 | /ship | Sonnet | $2-3 |
| **Total** | | | **$53-143** |

Backend-only features will be on the lower end (~$50-80).
UI-heavy features with design iteration will be higher (~$100-150+).

---

## Escalation

At any point, if the harness encounters an unrecoverable error:

```
STATUS: BLOCKED
REASON: {what happened}
ATTEMPTED: {what was tried}
RECOMMENDATION: {what the user should do}
```

Save current state to INDEX.md before escalating. The feature can always be resumed.
