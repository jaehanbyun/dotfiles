---
name: prmt
description: Use when the user asks to improve, rewrite, expand, or structure a rough prompt, abstract request, vague requirement, Korean prompt, or prompt-engineering draft for Codex or another AI assistant.
---

# Prmt

## Overview

Turn a rough user request into a prompt that another Codex session can answer well. Preserve the user's intent, remove ambiguity, and add the minimum useful structure.

## Core Rules

- Return a prompt, not the answer to the original task, unless the user explicitly asks for both.
- Match the user's language by default. If the source prompt is Korean, write the refined prompt in Korean.
- Keep the user's goal intact. Do not invent domain facts, constraints, repositories, files, dates, tools, or preferences.
- Make reasonable assumptions only when they help execution; label them inside the prompt.
- Ask clarification questions only when missing information would make the prompt unsafe, irreversible, or likely wrong. Otherwise produce a usable prompt.
- Prefer concrete instructions over meta advice. The result should be ready to paste into Codex.

## Prompt Shape

Use this structure when it fits the request:

```text
[역할/관점]
You are ...

[목표]
...

[입력/맥락]
...

[작업 지시]
1. ...
2. ...
3. ...

[제약/선호]
- ...

[출력 형식]
- ...

[검증 기준]
- ...
```

Omit sections that add no value. For small requests, a compact paragraph or short checklist is better than a heavy template.

## Refinement Checklist

Before returning the prompt, ensure it answers:

- What should Codex accomplish?
- What context or inputs are available?
- What should Codex avoid changing or assuming?
- Should Codex implement, explain, research, review, debug, or plan?
- What should the final output look like?
- How should Codex verify the work or quality?

## Output Format

Default response:

````markdown
아래처럼 요청하면 됩니다.

```text
<refined prompt>
```
````

If assumptions matter, add a short `가정:` line before the prompt. If clarification is required, ask at most three concise questions instead of generating a weak prompt.

## Common Mistakes

- Do not over-expand a simple request into a long process document.
- Do not add generic instructions such as "be detailed" unless they map to a concrete output requirement.
- Do not include private chain-of-thought requests.
- Do not make the prompt depend on tools the user did not mention unless the task clearly requires them.
- Do not remove uncertainty; expose it as assumptions, options, or questions.
