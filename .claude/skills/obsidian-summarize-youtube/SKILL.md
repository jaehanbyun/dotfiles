---
name: obsidian-summarize-youtube
description: |
  YouTube URL 또는 트랜스크립트를 한국어로 번역/정리해 Obsidian 문서로 저장할 때 사용.
  사용자가 "obsidian:summarize-youtube", "/obsidian:summarize-youtube", "obsidan:summarize-youtube",
  "유튜브를 Obsidian에 요약", "youtube transcript 요약 저장" 등을 요청하면 적용.
argument-hint: "[kr|en] [transcript or YouTube URL]"
user_invocable: true
---

# Obsidian Summarize YouTube

Claude command 호환 wrapper다. 실행할 때 원본 command를 먼저 읽고 그 절차를 따른다.

Source command:

```text
/Users/byeonjaehan/.claude/commands/obsidian/summarize-youtube.md
```

Codex 실행 규칙:

- 사용자가 제공한 입력을 원본 command의 `$ARGUMENTS`로 간주한다.
- 첫 번째 인자가 `kr` 또는 `en`이면 원본 command의 언어 옵션으로 해석한다.
- YouTube URL은 메타데이터와 트랜스크립트 수집 절차를 따른다. 트랜스크립트가 직접 제공되면 그대로 사용한다.
- vault 경로는 `$VAULT_ROOT`가 있으면 우선 사용하고, 없으면 `~/Documents/Obsidian Vault/`를 사용한다.
- 기존 파일을 덮어쓸 가능성이 있으면 먼저 사용자 확인을 받는다.
