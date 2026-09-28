---
name: obsidian-summarize-x
description: |
  Twitter/X 트윗, 스레드 URL 또는 검색어를 한국어로 번역/정리해 Obsidian 문서로 저장할 때 사용.
  사용자가 "obsidian:summarize-x", "obsidian:summarize-twitter", "/obsidian:summarize-x",
  "obsidan:summarize-x", "X 스레드를 Obsidian에 정리" 등을 요청하면 적용.
argument-hint: "[twitter-url-or-query]"
user_invocable: true
---

# Obsidian Summarize X

Claude command 호환 wrapper다. 실행할 때 원본 command를 먼저 읽고 그 절차를 따른다.

Source command:

```text
/Users/byeonjaehan/.claude/commands/obsidian/summarize-x.md
```

Codex 실행 규칙:

- 사용자가 제공한 입력을 원본 command의 `$ARGUMENTS`로 간주한다.
- X/Twitter는 인증/동적 렌더링 이슈가 잦으므로 Browser 또는 Chrome 플러그인 도구를 우선 사용한다.
- 접근이 막히면 우회하지 말고 접근 제한을 보고한다.
- vault 경로는 `$VAULT_ROOT`가 있으면 우선 사용하고, 없으면 `~/Documents/Obsidian Vault/`를 사용한다.
- 기존 파일을 덮어쓸 가능성이 있으면 먼저 사용자 확인을 받는다.
