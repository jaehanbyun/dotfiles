---
name: obsidian-summarize-reddit
description: |
  Reddit 게시물/스레드 URL 또는 검색어를 한국어로 번역/정리해 Obsidian 문서로 저장할 때 사용.
  사용자가 "obsidian:summarize-reddit", "/obsidian:summarize-reddit", "obsidan:summarize-reddit",
  "Reddit 글을 Obsidian에 정리", "레딧 스레드 요약 저장" 등을 요청하면 적용.
argument-hint: "[reddit-url-or-query]"
user_invocable: true
---

# Obsidian Summarize Reddit

Claude command 호환 wrapper다. 실행할 때 원본 command를 먼저 읽고 그 절차를 따른다.

Source command:

```text
/Users/byeonjaehan/.claude/commands/obsidian/summarize-reddit.md
```

Codex 실행 규칙:

- 사용자가 제공한 입력을 원본 command의 `$ARGUMENTS`로 간주한다.
- Reddit URL 또는 검색어는 브라우징으로 현재 내용을 확인한다.
- Reddit 원문을 인용할 때는 출처 링크를 포함한다.
- vault 경로는 `$VAULT_ROOT`가 있으면 우선 사용하고, 없으면 `~/Documents/Obsidian Vault/`를 사용한다.
- 기존 파일을 덮어쓸 가능성이 있으면 먼저 사용자 확인을 받는다.
