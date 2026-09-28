---
name: obsidian-translate-article
description: |
  기술 문서 URL을 요약하지 않고 한국어로 번역해 원문 구조를 유지한 Obsidian 문서로 저장할 때 사용.
  사용자가 "obsidian:translate-article", "/obsidian:translate-article", "obsidan:translate-article",
  "아티클 번역해서 Obsidian에 저장" 등을 요청하면 적용.
argument-hint: "[url]"
user_invocable: true
---

# Obsidian Translate Article

Claude command 호환 wrapper다. 실행할 때 원본 command를 먼저 읽고 그 절차를 따른다.

Source command:

```text
/Users/byeonjaehan/.claude/commands/obsidian/translate-article.md
```

Codex 실행 규칙:

- 사용자가 제공한 입력을 원본 command의 `$ARGUMENTS`로 간주한다.
- 원본 command가 Playwright-only 접근을 요구하면 Codex에서는 Browser 또는 Chrome 플러그인 도구를 우선 사용한다.
- 요약하지 않고 원문 문서 구조를 최대한 유지해 번역한다.
- vault 경로는 `$VAULT_ROOT`가 있으면 우선 사용하고, 없으면 `~/Documents/Obsidian Vault/`를 사용한다.
- 기존 파일을 덮어쓸 가능성이 있으면 먼저 사용자 확인을 받는다.
