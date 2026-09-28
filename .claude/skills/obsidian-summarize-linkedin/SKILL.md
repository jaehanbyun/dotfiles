---
name: obsidian-summarize-linkedin
description: |
  LinkedIn 게시물 또는 아티클을 한국어로 번역/정리해 Obsidian 문서로 저장할 때 사용.
  사용자가 "obsidian:summarize-linkedin", "/obsidian:summarize-linkedin", "obsidan:summarize-linkedin",
  "LinkedIn 글을 Obsidian에 정리" 등을 요청하면 적용.
argument-hint: "[linkedin-url]"
user_invocable: true
---

# Obsidian Summarize LinkedIn

Claude command 호환 wrapper다. 실행할 때 원본 command를 먼저 읽고 그 절차를 따른다.

Source command:

```text
/Users/byeonjaehan/.claude/commands/obsidian/summarize-linkedin.md
```

Codex 실행 규칙:

- 사용자가 제공한 입력을 원본 command의 `$ARGUMENTS`로 간주한다.
- LinkedIn은 인증/동적 렌더링 이슈가 잦으므로 Browser 또는 Chrome 플러그인 도구를 우선 사용한다.
- 접근이 막히면 우회하지 말고 접근 제한을 보고한다.
- vault 경로는 `$VAULT_ROOT`가 있으면 우선 사용하고, 없으면 `~/Documents/Obsidian Vault/`를 사용한다.
- 기존 파일을 덮어쓸 가능성이 있으면 먼저 사용자 확인을 받는다.
