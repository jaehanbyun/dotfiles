---
name: go
description: Verify work end-to-end, simplify code, and open a PR. Use after completing a task to ship it.
---

# /go — Verify, Simplify, Ship

Run this after completing a task. It verifies the work end-to-end, simplifies code, and puts up a PR.

**Flow:** Detect project type → Test E2E → Simplify → Create PR

---

## Step 1: Detect Project Type & Verification Method

Inspect the project to determine the right verification strategy:

```
IF package.json has "dev" or "start" script with frontend framework (next, vite, react, vue, svelte, astro)
  → FRONTEND (browser-based verification)
ELSE IF package.json has "start" or "dev" script (express, fastify, nest, hono)
  → BACKEND (HTTP endpoint verification)
ELSE IF Dockerfile or docker-compose.yml exists
  → CONTAINER (docker-based verification)
ELSE IF go.mod, Cargo.toml, pom.xml, build.gradle exists
  → COMPILED (build + test verification)
ELSE IF has desktop/native indicators (electron, tauri, swift, SwiftUI)
  → DESKTOP (computer use verification)
ELSE IF *.py with main or CLI entry point
  → SCRIPT (bash execution verification)
ELSE
  → GENERIC (test suite only)
```

## Step 2: Run Verification

Execute the appropriate verification based on detected type. **Every path must produce a PASS/FAIL result.**

### Frontend Projects
1. Run linter and type checker if configured (`npm run lint`, `tsc --noEmit`)
2. Run test suite (`npm test` or equivalent)
3. Start dev server in background
4. Use `/browse` to take a screenshot of the main page
5. Visually verify no obvious broken layout, console errors, or blank pages
6. Stop the dev server

### Backend Projects
1. Run linter and type checker if configured
2. Run test suite
3. Start the server in background
4. Hit health check endpoint (`curl localhost:{port}/health` or `/`)
5. Hit the specific endpoints related to the change (if identifiable from git diff)
6. Verify 2xx responses and expected response shapes
7. Stop the server

### Container Projects
1. Run `docker compose build` (or `docker build`)
2. Run `docker compose up -d`
3. Wait for health check to pass
4. Test endpoints or run container-level tests
5. `docker compose down`

### Compiled Projects (Go, Rust, Java, etc.)
1. Build the project (`go build`, `cargo build`, `./gradlew build`, `mvn compile`)
2. Run test suite (`go test ./...`, `cargo test`, `./gradlew test`, `mvn test`)
3. If a binary/server is produced, start and verify it responds

### Desktop/Native Apps
1. Build the app
2. Use computer-use MCP to launch and screenshot the app
3. Verify the UI renders correctly

### Script Projects
1. Run the script with a test input or `--help` flag
2. Verify expected output

### Generic (any project)
1. Run whatever test command exists (`npm test`, `pytest`, `go test`, `cargo test`, `make test`)
2. Run linter if configured
3. Report results

**On failure:** Stop immediately. Report what failed, the error output, and suggest a fix. Do NOT proceed to Step 3.

## Step 3: Simplify

Only if Step 2 passed:

1. Run `git diff HEAD` to see all changes made in this session
2. Review the diff for:
   - **Dead code** — unused imports, unreachable branches, commented-out code
   - **Unnecessary complexity** — premature abstractions, over-engineered patterns
   - **Duplication** — repeated logic that should be extracted
   - **Naming** — unclear variable/function names
   - **Large functions** — anything over 50 lines that could be split
3. Make simplification edits if warranted (skip if changes are already clean)
4. Re-run the verification from Step 2 to confirm simplifications didn't break anything

**On failure after simplification:** Revert the simplification edits and proceed with the original passing code.

## Step 4: Create PR

Only if Step 2 (or re-verification after Step 3) passed:

1. Check current branch — if on `main`/`master`, create a feature branch first
2. Stage and commit any uncommitted changes using `/commit` skill if available, otherwise:
   - Analyze the diff
   - Write a conventional commit message
   - Commit with `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`
3. Push the branch
4. Create PR via `gh pr create` with:
   - Concise title (under 70 chars)
   - Summary section with bullet points
   - Test plan section describing what was verified
   - Verification result (which tests passed, what was visually checked)

## Output

Report a summary at the end:

```
## /go Results

| Step | Status | Details |
|------|--------|---------|
| Detect | ✅ | {project type} |
| Verify | ✅/❌ | {what was tested and result} |
| Simplify | ✅/⏭️ | {changes made or "already clean"} |
| PR | ✅/❌ | {PR URL or reason for skip} |
```

---

## Important Notes

- If no tests exist and the project has no runnable entry point, warn the user: "No verification method available. Consider adding tests."
- Never skip verification. The whole point is that when you come back to a task, you KNOW the code works.
- If the user passes arguments (e.g., `/go skip-pr`), respect them:
  - `skip-pr` — verify and simplify but don't create PR
  - `skip-simplify` — verify and PR but skip simplification
  - `verify-only` — only run verification, no simplify or PR
