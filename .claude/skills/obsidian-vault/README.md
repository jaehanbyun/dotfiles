# obsidian-vault

> Obsidian 작업의 대상 vault 선택, 도구 라우팅, 변경 안전성을 담당하는 전역 코어 스킬

## 설계 원칙

이 스킬은 자주 호출되므로 **얇은 코어와 단단한 가드레일**만 유지한다.

- 대상 vault를 명시적으로 확정한다.
- Obsidian CLI를 기본 인터페이스로 사용한다.
- 읽기 요청과 변경 요청의 경계를 지킨다.
- 대상 vault의 기존 폴더, 태그, frontmatter 관례를 따른다.
- 특정 콘텐츠 작업은 더 구체적인 Obsidian 스킬에 맡긴다.

태그 체계, Zettelkasten 구조, 시맨틱 검색기, 토큰 관리 규칙은 전역 코어에서 강제하지 않는다.

## 적용 시점

- 사용자가 Obsidian 또는 vault를 명시한 경우
- 현재 문맥에서 기록 대상이 Obsidian으로 명확한 경우
- Obsidian의 백링크, 태그, 작업, 속성을 다루는 경우

일반 코드 저장소의 Markdown, README, 태그 작업에는 적용하지 않는다.

## 핵심 보장

1. `obsidian vaults verbose`로 등록된 vault를 확인한다.
2. 활성 vault에 의존하지 않고 모든 명령에 대상을 지정한다.
3. 읽기 요청에서는 파일을 변경하지 않는다.
4. 수정 전 기존 노트와 필요한 주변 관례를 확인한다.
5. 삭제, 덮어쓰기, 대량 변경은 정확한 대상과 권한을 확인한다.
6. 오류가 나도 자동으로 보고용 파일을 만들지 않는다.

```bash
obsidian vault="<vault-name>" <command> [options]
```

전역 `vault=<name>` 옵션은 Obsidian 명령 앞에 둔다.

## 비목표

- 모든 vault에 동일한 폴더나 태그 체계 강제
- 존재가 확인되지 않은 LSP, MCP, 시맨틱 검색기 가정
- 일반 Markdown 편집 가로채기
- 기사, PDF, YouTube, 업무 로그 등 특화 워크플로 복제

실행 규칙의 단일 원본은 `SKILL.md`다.
