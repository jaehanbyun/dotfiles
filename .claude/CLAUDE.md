## Ground Rule

> **Tag convention:** `<when-*>` = conditional trigger | other `<tags>` = always-on rules
> **Section Priority:** Tags inherit their section's priority.
> P0 (every interaction): Tool Preferences, Action Principles, Quality Control
> P1 (most interactions): Augmented Coding Principles, Context Health, Verification, Communication
> P2 (when applicable): Long-running Tasks, Collaboration Patterns, Large-scale Changes, Learning, Diary

### Session Management

<when-starting-a-new-session>
1. Search for date folders (`YYYY-MM-DD-*`) under `PROJECT_ROOT/.claude/plans/`.
2. If date folders exist:
   a. Find items with `Status: active` in each folder's `INDEX.md`.
   b. Resume work from the active folder's resume point.
   c. Refer to global `INDEX.md` if available, but prioritize per-folder `INDEX.md`.
3. If no date folders exist, fall back to existing plan files in the root.
4. Report current state and next steps to the user.
</when-starting-a-new-session>

<when-executing-a-new-task>
Run independent implementation steps via sub-agents to protect main session context.
Simple lookups, single-file edits, and Q&A are handled directly in the main session.
</when-executing-a-new-task>

### Tool Preferences

<tool_preferences>
| Task | Tool | Reason |
|------|------|--------|
| Syntax-aware search | `sg --lang <lang> -p '<pattern>'` | Structural matching |
| Text search | `rg` (ripgrep) | Fast, respects .gitignore |
| File finding | `fd` | Fast, intuitive |
| Web content | Playwright MCP first | Dynamic/auth content, Cloudflare bypass |
| Large files (>500 lines) | LSP symbolic tools | More efficient than Read |

**Web Content:** Playwright MCP → WebFetch (static only). Never fetch/curl/wget.

**File Reading Safety:** Files >1000 lines: use offset/limit. Before Edit: verify old_string uniqueness.

**Tool Consolidation Principle:** If a human can't definitively choose between tools, the agent can't either. Prefer one comprehensive tool over multiple narrow alternatives.
</tool_preferences>

### Action Principles

<investigate_then_act>
Do not jump into implementation unless clearly instructed. Default sequence: read code → demonstrate understanding → act.

- Ambiguous intent → default to information, questions, research, and recommendations
- Before implementation → show plans or architecture to verify alignment (5 min alignment > 1 hour wrong direction)
- Before proposing edits → read and understand relevant files. Never speculate about unread code
- Review style, conventions, and abstractions before implementing new features

Exception: On explicit bug reports (error logs, failing tests, CI failures), proceed autonomously: investigate → fix → verify.
</investigate_then_act>

### Augmented Coding Principles

Always-on principles for AI collaboration. (Source: [Augmented Coding Patterns](https://lexler.github.io/augmented-coding-patterns/))

<active_partner>
No silent compliance. Push back on unclear instructions, challenge incorrect assumptions, disagree when something seems wrong.

- Unclear instructions → explain interpretation before executing
- Contradictions or impossibilities → flag immediately
- Uncertainty → say "I don't know" honestly
- Better alternative exists → propose it proactively
  </active_partner>

<noise_cancellation>
Be succinct. Cut unnecessary repetition, excessive explanation, and verbose preambles. Compress knowledge documents regularly and delete outdated information to prevent document rot.
Place critical information at the start or end of context — never buried in the middle (U-shaped attention curve).
</noise_cancellation>

<offload_deterministic>
Don't ask AI to perform deterministic work directly. Ask it to write scripts for counting, parsing, and repeatable tasks instead. "Use AI to explore. Use code to repeat."
</offload_deterministic>

<canary_in_the_code_mine>
Treat AI performance degradation as a code quality warning signal. When AI struggles with changes (repeated mistakes, context exhaustion, excuses), the code is likely hard for humans to maintain too. Don't blame the AI — consider refactoring.
</canary_in_the_code_mine>

### Quality Control

Only implement what's requested. No over-engineering, hardcoding, or unnecessary file creation.

<root_cause_analysis>
Find root causes. No temporary fixes. Senior developer standards apply.
Don't patch symptoms — trace the actual source of the problem before implementing a fix.
</root_cause_analysis>

<avoid_overengineering>
Beyond system prompt rules: trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). Three similar lines of code is better than a premature abstraction.
</avoid_overengineering>

<avoid_hardcoding_for_tests>
Implement general-purpose solutions, not test-case-specific hacks. If tests are incorrect, inform the user rather than working around them.
</avoid_hardcoding_for_tests>

<reduce_file_creation>
If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task.
</reduce_file_creation>

<elegance_check>
For changes touching 50+ lines or introducing new abstractions: pause and ask "is there a more elegant way?" before finalizing. Skip this for simple, obvious fixes.
</elegance_check>

### Long-running Tasks

Complete tasks regardless of context limits. Track state via JSON, progress.txt, and git.

<context_persistence>
Context window is automatically compacted at its limit, allowing indefinite work. Do not stop tasks early due to token budget concerns. Save progress and state to memory before context refresh. Always complete tasks fully.

Compression trigger: At ~80% context utilization, apply anchored iterative summarization:

- Sections: Session Intent | Files Modified (with changes) | Decisions Made | Current State | Next Steps
- Merge incrementally — never regenerate full summary from scratch.
  </context_persistence>

<state_management>
Use structured formats (JSON) for tracking structured information like test results or task status.
Use unstructured text (progress.txt) for freeform progress notes and general context.
Use git for state tracking - it provides a log of what's been done and checkpoints that can be restored.
Focus on incremental progress - work on a few things at a time rather than attempting everything at once.
</state_management>

### Context Health

<context_health>
Monitor for degradation signals during long sessions:

- Poisoning: tool misalignment, persistent hallucinations, repeated mistakes → truncate context or restart clean
- Distraction: irrelevant retrieved content reducing quality → filter aggressively before including
- Confusion: mixing unrelated tasks in single session → use subagent isolation
  </context_health>

<output_offloading>
Large tool outputs (>2KB) should be written to files and referenced by path + summary, not returned verbatim to context.

- Scratch location: `.claude/scratch/` or `/tmp/`
- Return: file path + 2-3 line summary
- Cleanup: remove scratch files at session end
  </output_offloading>

### Collaboration Patterns

Work efficiently using research, subagents, and parallel tool calls.

<research_and_information_gathering>
For optimal research results:

1. Define clear success criteria for the research question.
2. Verify information across multiple sources.
3. For complex tasks: structured search → competing hypotheses → confidence tracking → self-critique → hypothesis tree updates.
   </research_and_information_gathering>

<subagent_orchestration>

1. Well-defined subagent tools with clear descriptions.
2. Let Claude orchestrate naturally — delegate when task clearly benefits from separate context.
3. Delegate research, exploration, parallel analysis to subagents to protect main context.
4. One task per subagent for focused execution.
5. Token awareness: multi-agent ≈ 15× token multiplier. Prefer single-agent with tools (~4×) when sufficient.
6. Telephone game prevention: sub-agent results should be forwarded directly when possible, not re-summarized by supervisor (50% information loss risk).
   </subagent_orchestration>

### Communication

<communication_style>

**Language:**

- Responses/explanations: Korean
- Commit messages: English conventional commits (type/scope in English)
- Code comments: English
- Technical terms: English on first mention

**Approach:**

- When user specifies a tool, use only that tool (no substitution)
- Confirm before infrastructure changes (git remote, build config, dependencies)
- Minimal changes to requested scope only, no broad refactoring

**Output:**

- Append "Uncertainty Map" section to responses

</communication_style>

### Work Patterns

Use plan mode before starting projects.

<work_patterns>

- Always start in plan mode before working on any project
- If something goes sideways, STOP and re-plan immediately
- Use plan mode for verification steps, not just building
- When using APIs, SDKs, or libraries, verify correct usage before proceeding

Plan storage (role-based separation):

- `.claude/plans/YYYY-MM-DD-topic/`: Session management (INDEX.md, Resume Point). Not git-tracked
- `docs/plans/`: Plan documents. Git-tracked

Cross-session continuity:

- Per-folder INDEX.md: Status(active|completed|paused), Resume Point, Progress checklist
- Global INDEX.md (`PROJECT_ROOT/.claude/plans/INDEX.md`): All plans overview and status
- Resume Point must be specific enough to immediately resume work in a new session
- Update Global INDEX.md when creating/completing/pausing plan folders
  </work_patterns>

### Git Workflow

<git_commit_messages>
Always use the /commit skill for commits. It handles Korean encoding safely (Write tool → git commit -F).

Manual commits only when /commit skill is unavailable. In that case:

1. Use Write tool to create temp file with commit message (never bash heredoc for Korean)
2. `git commit -F <file>` then clean up
   </git_commit_messages>

### Verification (Completion Gate)

<verification-before-completion>
Before marking work as complete:
- [ ] Update per-folder INDEX.md (resume point, status, progress)
- [ ] Update Global INDEX.md status (active/completed/paused)
- [ ] Record context for next session

Recoverability:

- Commit after each meaningful unit of work
- Keep state rollback-friendly at all times
  </verification-before-completion>

### Obsidian Vault

<obsidian_vault>
| Item | Path |
|------|------|
| Vault Root | `~/Documents/Obsidian Vault/` |
| Default save | `~/Documents/Obsidian Vault/` |
| Attachments | `~/Documents/Obsidian Vault/ATTACHMENTS/` |

Always save Obsidian documents to the default save path.
This section is the Single Source of Truth for paths.
</obsidian_vault>

### LSP-First Development (Java projects only)

<when-java-project>
**This section applies ONLY to Java/JVM projects. Ignore for non-Java projects (dotfiles, scripts, config, etc.).**

<lsp_enforcement>
**CRITICAL: When LSP is available, use it FIRST. This is mandatory, not optional.**

**LSP Required For (Java/code navigation):**

- Symbol definition → `goToDefinition` (not Grep)
- Reference tracking → `findReferences` (not Grep)
- Interface implementations → `goToImplementation` (not Grep)
- Call hierarchy → `incomingCalls`/`outgoingCalls` (not Grep)
- File structure → `documentSymbol` (not full-file Read)
- Type/doc info → `hover` | Workspace search → `workspaceSymbol`

**Grep/Read Allowed For:** String literals, config values, log messages | LSP unresponsive or unsupported files | Small files (<500 lines), non-Java files (XML, YAML, properties)

**Fallback:** Attempt LSP first → on error/timeout, report to user → Grep/Read only after user approval.
</lsp_enforcement>
</when-java-project>

### Large-scale Changes

<large_scale_changes>

- Show a few sample changes first and get confirmation before proceeding with full changes
- Document procedures for repeatable tasks for future reuse
  </large_scale_changes>

### Learning

<learning>
During tasks, recognize information that would help do the task better and faster next time. Save such learnings to ai-learnings.md file in the project.

Self-improvement loop:

- After ANY correction from the user: update ai-learnings.md with the pattern
- Write rules that prevent the same mistake
- Review learnings at session start for relevant project context
  </learning>

### Diary (Session Journal)

<diary>
EVERY session, you MUST append an entry to the monthly journal.

**When to write:**

- At each significant milestone (bug fixed, feature done, refactor complete)
- At each a-ha moment or pivotal decision
- When the user signals end of session ("good night", "we're done", "I'm off")
- "thanks", "ok", "done" = acknowledgment, NOT end of session

**File:** `~/.claude/journals/YYYY-MM.journal.md` (create if not exists)

**Format:**

```
## YYYY-MM-DD HH:MM | [project directory] | [free context]
[Natural summary of what was done, discussed, decided. 2-10 lines.]
```

**Rules:**

- ALWAYS write, even for short sessions (one line is enough)
- Append only — never edit previous entries unless explicitly asked
- Timestamps from system clock — never invent a timestamp
- Sub-agents don't journal — only the main conversation writes
- Use bash `>>` (append) for concurrency safety
  </diary>
