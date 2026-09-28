---
name: obsidian-summarize-pdf
description: |
  기술 서적 PDF를 챕터나 페이지 범위별로 읽어 Obsidian 노트로 정리할 때 사용.
  사용자가 "obsidian:summarize-pdf", "/obsidian:summarize-pdf", "obsidan:summarize-pdf",
  "PDF를 Obsidian 노트로 정리", "기술서 챕터 요약" 등을 요청하면 적용.
argument-hint: "[pdf파일경로] [챕터번호 또는 페이지범위(선택)]"
user_invocable: true
---

# Obsidian Summarize PDF

Claude command 호환 wrapper다. 실행할 때 원본 command를 먼저 읽고 그 절차를 따른다.

Source command:

```text
/Users/byeonjaehan/.claude/commands/obsidian/summarize-pdf.md
```

Codex 실행 규칙:

- 사용자가 제공한 입력을 원본 command의 `$ARGUMENTS`로 간주한다.
- PDF 파일 경로가 상대 경로면 현재 작업 디렉터리 기준으로 해석한다.
- 대용량 PDF는 원본 command의 챕터/페이지 범위 절차를 따라 필요한 범위만 읽는다.
- vault 경로는 `$VAULT_ROOT`가 있으면 우선 사용하고, 없으면 `~/Documents/Obsidian Vault/`를 사용한다.
- 기존 파일을 덮어쓸 가능성이 있으면 먼저 사용자 확인을 받는다.
