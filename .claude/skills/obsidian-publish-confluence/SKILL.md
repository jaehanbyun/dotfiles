---
name: obsidian-publish-confluence
description: |
  Obsidian 문서를 Confluence에 발행할 때 사용. Mermaid 다이어그램과 이미지 첨부 업로드 포함.
  사용자가 "obsidian:publish-confluence", "/obsidian:publish-confluence", "obsidan:publish-confluence",
  "Obsidian 문서를 Confluence에 발행" 등을 요청하면 적용.
argument-hint: "[문서이름] [space_key(선택)] [parent_page_id(선택)]"
user_invocable: true
---

# Obsidian Publish Confluence

Claude command 호환 wrapper다. 실행할 때 원본 command를 먼저 읽고 그 절차를 따른다.

Source command:

```text
/Users/byeonjaehan/.claude/commands/obsidian/publish-confluence.md
```

Codex 실행 규칙:

- 사용자가 제공한 입력을 원본 command의 `$ARGUMENTS`로 간주한다.
- vault 경로는 `$VAULT_ROOT`가 있으면 우선 사용하고, 없으면 `~/Documents/Obsidian Vault/`를 사용한다.
- Atlassian/Confluence 도구가 필요하면 사용 가능한 Atlassian Rovo 도구를 먼저 찾는다.
- Confluence에 페이지를 생성하거나 갱신하기 전, 대상 space/page가 모호하면 사용자에게 확인한다.
- 원본 command가 Playwright 또는 Claude MCP 도구명을 언급하면 현재 Codex에서 사용 가능한 Browser/Atlassian 동등 도구로 매핑한다.
