---
name: opendev-zuul-triage
description: Triage OpenDev, Gerrit, and Zuul CI failures for OpenStack-style contributions. Use when the user provides a Gerrit change, OpenDev review URL, Zuul buildset/build/job link, "Verified -2", "gate failed", "check failed", "recheck?", or asks why an OpenStack/Skyline/Kubernetes website style CI job failed and what action to take next.
---

# Opendev Zuul Triage

## Overview

Use this workflow to turn Gerrit/Zuul failure links into a grounded diagnosis, exact evidence links, and the next safe action for the contributor.

## Inputs

Accept any of:

- Gerrit change URL or change number.
- Zuul buildset URL.
- Zuul build/job URL.
- Pasted Gerrit comments, job matrix, or failure summary.
- Local repository path and branch when the user wants a fix, not just diagnosis.

Do not treat this like a GitHub Actions workflow. Prefer Gerrit and Zuul sources over GitHub mirrors.

## Workflow

1. Identify the review system and current state.

   - Record project, branch, change number, patchset, owner, and current votes.
   - Distinguish check pipeline failures from gate pipeline failures.
   - Note whether the vote was reset by a new patchset or whether the current patchset still has `Verified -2`.

2. Find the authoritative Zuul evidence.

   - Open the buildset linked from Gerrit or the user's pasted failure.
   - Identify all failed jobs, not just the first link.
   - For each failed job, collect job name, result, duration, voting status, build URL, and artifacts/log URL.
   - Compare against passing jobs in the same buildset to avoid blaming unrelated infrastructure.

3. Inspect logs with a failure-first pass.

   - Start with `job-output.txt`, `console.html`, `tox` output, test result summaries, and any `testr_results.html` or subunit artifacts.
   - Search for explicit failure markers: `FAILED`, `Traceback`, `AssertionError`, `ERROR`, `Exception`, `Command failed`, `NoSuch`, `Timeout`, `Connection refused`, `Module not found`, `yarn`, `npm`, `tox`, `pytest`, `selenium`, `devstack`, `tempest`.
   - If the job is long-running E2E, inspect the final failure window first, then walk backward to the first causal error.
   - Separate project test failures from external service, nodepool, package mirror, or transient infrastructure failures.

4. Classify the failure.

   - `change-caused`: a changed file, test, release note, dependency, or behavior plausibly caused the failure.
   - `known unrelated`: logs show an infra outage, unrelated test, or documented flaky job.
   - `unclear`: logs are insufficient, artifacts are missing, or the failure has multiple plausible causes.
   - `process-only`: the next action is Gerrit/Zuul process handling, such as recheck, rebasing, or responding to a reviewer.

5. Decide the next action.

   - If change-caused, propose the smallest local fix and the exact validation command.
   - If unrelated or flaky, draft a concise `recheck` rationale, but do not post it unless the user asks for a write operation.
   - If gate failed after Code-Review/Workflow approval, explain whether the user needs to patch, recheck, or wait for reviewer/workflow reset.
   - If the failure is in a non-voting job, say so and explain whether it still matters.

6. Only modify code when requested.

   - Before edits, inspect the local branch and project docs.
   - For GitHub write operations related to mirrored repos, follow the user's `gh auth status` account-safety rules.
   - For Gerrit comments or uploads, verify the configured Gerrit account and remote before writing or pushing.
   - Keep fix commits review-sized and include the local test result in the final answer.

## Final Output

Lead with findings:

- Failed job(s), status, and exact links.
- Root cause or most likely cause, with confidence.
- Evidence: the smallest useful log excerpts or paraphrased failure lines.
- Whether the failure appears caused by the user's patch.
- Next action: fix, recheck, wait, ask reviewer, or gather more logs.
- Any local commands the user can run to reproduce or validate.

When drafting a recheck/comment, keep it short and evidence-backed:

```text
recheck

Reason: <one sentence summarizing why this looks unrelated or transient, with build/log link if useful>.
```

Stop when the failure is classified with a defensible next action, or when access/logs are missing and the remaining blocker is explicit.
