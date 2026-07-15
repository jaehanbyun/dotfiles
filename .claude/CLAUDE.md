# Global Working Agreement

## Scope and precedence

- Respond in Korean by default. Introduce technical terms in English first when that improves clarity.
- Direct user requests and project-local instructions define task-specific behavior. These rules provide global defaults; safety constraints remain in force.
- Explanation, review, diagnosis, research, and status requests are read-only unless the user also asks for changes.
- Do not create or update journals, learning files, plans, branches, commits, issues, PRs, or other persistent state unless the request or an established project workflow requires it.

## Execution

- Inspect the relevant files, repository state, and existing conventions before acting.
- Ask a clarifying question only when ambiguity creates meaningful risk of rework, data loss, security problems, or an architectural mismatch.
- For clear and low-risk work, make reasonable routine assumptions, state material ones, and proceed.
- Use a written plan for multi-step, risky, or cross-cutting work. Do not force Plan Mode for simple questions, lookups, or small edits.
- Use subagents only when independent parallel work materially improves speed or protects the main context. Keep simple tasks with the main agent.
- For long-running work, preserve enough state to resume safely, but create progress files only when they are genuinely useful.

## Engineering

- Prefer the simplest sufficient solution that fits the existing architecture.
- Fix root causes rather than masking symptoms. Do not hardcode values merely to satisfy tests.
- Keep changes surgical: avoid unrelated refactors, renames, reformatting, abstractions, and speculative features.
- Handle real and likely edge cases without adding complexity for hypothetical future needs.
- Preserve existing user changes. Inspect a dirty worktree before editing and never discard unrelated work.
- Reuse existing utilities, patterns, and dependencies before introducing new ones.
- Remove temporary artifacts created for the task when they are no longer needed.

## Tools and context

- Prefer `rg` for text search, `fd` for file discovery, and `sg` or an LSP when structural or symbol-aware search provides a clear benefit.
- If an LSP is unavailable or fails, fall back to `rg` and direct inspection without blocking for approval.
- Use browser automation for dynamic, authenticated, or interaction-heavy pages. Use WebFetch, API clients, or `curl` when they are the simpler appropriate tool.
- Avoid dumping large outputs into the conversation. Narrow searches, read relevant ranges, and summarize material findings.
- Combine independent read-only checks when doing so reduces latency without obscuring results.

## Verification

- Run the most relevant focused tests, type checks, linters, builds, or smoke checks after code changes.
- Inspect the final diff and confirm that only intended files and behavior changed.
- Do not claim completion when required verification has not passed. If a check cannot run, report the reason and remaining uncertainty.
- Scale verification to risk; do not require heavyweight harnesses for trivial changes.

## Git and GitHub

- Do not commit, push, create a branch, or publish externally unless the user requests it or it is an explicit step in the requested workflow.
- When committing, use concise English Conventional Commit messages unless the repository specifies another convention.
- Before GitHub writes, run `gh auth status` and select the account using this precedence: repository path, `origin` owner, then `git config user.name`.
- For `/Users/byeonjaehan/projects/personal/`, `jaehanbyun`-owned origins, or git users `jaehanbyun` and `jhbyun`, use `jaehanbyun`.
- For `/Users/byeonjaehan/projects/supergate/`, `/Users/byeonjaehan/projects/launcher-dev/`, and `/Users/byeonjaehan/projects/cluster-stack/`, use `supergate-jhbyun`.
- After switching with `gh auth switch -h github.com -u <account>`, verify the account again.
- For repository-scoped issue or PR drafts and writes, inspect the repository templates and related `config.yml`; match their fields and check for related issues.

## Communication

- Lead with the result or current conclusion. Be direct, concise, and specific.
- Explain tradeoffs when they materially affect risk, maintainability, time, or scope.
- Use English for code comments and identifiers unless project conventions require otherwise.
- Include an uncertainty section only when uncertainty is material to the decision or outcome.

## Conditional workflows

- Use Graphify only when the user explicitly requests Graphify, a knowledge graph, or persistent graph operations. Then read `~/.agents/skills/graphify/SKILL.md`; do not load it for routine code exploration.
- For an explicit browser-harness request, read `~/Developer/browser-harness/SKILL.md` before acting; do not import it into every session.
- Use the installed Obsidian skills for Obsidian work instead of hardcoding a vault workflow globally.
- Keep Java-specific LSP rules, feature-development harnesses, deployment procedures, and other specialized workflows in project-local instructions or dedicated skills.
