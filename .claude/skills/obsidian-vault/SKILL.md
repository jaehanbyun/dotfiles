---
name: obsidian-vault
description: |
  Obsidian vault 및 마크다운 문서 작업 시 사용. obsidian CLI를 표준 인터페이스로 사용하고,
  markdown-oxide LSP는 예외적인 링크 분석과 diagnostics에만 보조적으로 사용. vault 경로, 태그 체계,
  vault-intelligence CLI, 토큰 최적화 전략 제공.
  Obsidian, vault, 마크다운, 태그, 노트 정리, zettelkasten, 백링크, wiki-link, PKM 관련 작업 시 자동 적용.
---

# Obsidian Vault 작업 가이드

## 경로 정보

| 항목 | 경로 |
|------|------|
| vault | `$VAULT_ROOT` (글로벌 CLAUDE.md 참조) |
| vault-intelligence | `~/git/vault-intelligence/` |

## 작업 인터페이스 표준

Obsidian 작업은 기본적으로 `obsidian` CLI를 단일 표준 인터페이스로 사용한다.

1. **우선**: `obsidian` CLI
   - daily note 읽기/추가/열기
   - 파일 생성, 읽기, 열기, 이동, 이름 변경
   - 태그, 백링크, tasks, workspace, 플러그인 상태 확인
   - Obsidian 앱 명령 실행
2. **예외**: markdown-oxide MCP/LSP
   - 사용자가 명시적으로 MCP/LSP 사용을 요청한 경우
   - CLI로 불가능하거나 부정확한 링크 정의 추적, 참조 분석, diagnostics가 필요한 경우
   - 예외 사용 시 이유를 짧게 명시한다
3. **보조**: `rg`와 일반 파일 편집
   - 단순 텍스트 검색
   - 대량 기계 수정
   - Obsidian 앱 상태와 무관한 Markdown 편집

## markdown-oxide LSP 활용

### 사용 가능한 LSP 기능

markdown-oxide MCP 서버가 연결되어 있으면 다음 기능을 활용할 수 있다:

1. **Go to Definition**: `[[링크]]` → 해당 파일로 이동
2. **Find References (백링크)**: 특정 노트를 참조하는 모든 노트 검색
3. **Tag Search**: `#태그`가 사용된 모든 위치 검색
4. **Completion**: 링크, 태그, 프로퍼티 자동완성
5. **Diagnostics**: 깨진 링크, 존재하지 않는 노트 감지

### MCP/LSP 예외 사용 예시

```
# 백링크 찾기
"TDD 노트를 참조하는 모든 노트 찾아줘"
→ LSP find_references 사용

# 태그 검색
"#project/active 태그가 있는 노트들 찾아줘"
→ LSP find_references 사용

# 깨진 링크 확인
"이 vault에서 깨진 링크가 있는 노트 확인해줘"
→ LSP diagnostics 사용
```

### MCP/LSP 예외 원칙

마크다운 파일 검색 시:
1. **우선**: `obsidian` CLI 사용
2. **예외**: markdown-oxide LSP 도구 사용 (CLI로 불가능한 링크 정의/참조/diagnostics)
3. **차선**: vis CLI (시맨틱 검색 필요 시)
4. **보조**: ripgrep (단순 텍스트 매칭 또는 대량 편집 전 확인)


## 태그 체계

### Hierarchical Tags

- 형식: `#category/subcategory/detail`
- 5가지 카테고리: Topic, Document Type, Source, Status, Project

### Zettelkasten 폴더 구조

| 폴더 | 용도 | 작업 권한 |
|------|------|-----------|
| 000-SLIPBOX | 개인 인사이트 | 읽기/쓰기 |
| 001-INBOX | 수집함 | 읽기/쓰기 |
| 003-RESOURCES | 참고자료 | 주로 읽기 |
| archive | 보관 자료 | **접근 금지** |

### 상세 가이드

- 태그: `vault_root/vault-analysis/improved-hierarchical-tags-guide.md`

## vault-intelligence CLI

### 기본 사용법

```bash
# vis daemon 서버 실행 시 HTTP API 직접 호출 (0.4초, CLI는 9초)
curl -s --get --data-urlencode "query=검색어" "http://localhost:8741/search?search_method=hybrid&top_k=10" | jq -r '.results[] | "\(.score) \(.path)"'

# 서버 미실행 시 fallback
vis search "검색어" --search-method hybrid --top-k 10
```

### 주요 옵션

| 옵션 | 값 | 설명 |
|------|-----|------|
| `--search-method` | semantic, keyword, hybrid, colbert | hybrid 권장 |
| `--rerank` | (플래그) | 재순위화로 정확도 향상 |
| `--expand` | (플래그) | 쿼리 확장 (동의어 + HyDE) |
| `--top-k` | 숫자 | 반환 결과 수 |

### 자주 실수하는 옵션

| ❌ 잘못된 사용 | ✅ 올바른 사용 |
|---------------|---------------|
| `--method` | `--search-method` |
| `--k` | `--top-k` |
| `--output-file` | `--output` |
| `--reranking` | `--rerank` |
| `vis search --query "TDD"` | `vis search "TDD"` (positional) |
| `vis collect --topic "TDD"` | `vis collect "TDD"` (positional) |
| `vis related --file "문서.md"` | `vis related "문서.md"` (positional) |
| `vis tag --target "문서.md"` | `vis tag "문서.md"` (positional) |

### 상세 가이드

- `~/git/vault-intelligence/CLAUDE.md`

## 토큰 최적화 전략

### 작업 원칙

1. **한 번에 10개 이하 파일 처리**
2. **archive, .obsidian 폴더 무시**
3. **MOC 노트 먼저 읽고 관련 노트만 선택적 로드**
4. **20회 반복 후 `/compact` 또는 `/clear`**

### 효율적인 요청 패턴

```
# ❌ 비효율적
"vault의 모든 파일을 분석해줘"

# ✅ 효율적
"003-RESOURCES에서 'kubernetes' 태그가 있는 노트 목록만 보여줘"
```

### 컨텍스트 관리

| 명령어 | 용도 | 시점 |
|--------|------|------|
| `/compact` | 히스토리 압축 | 70% 사용 시 |
| `/clear` | 초기화 | 새 작업 시작 |
| `/cost` | 토큰 확인 | 수시 |

## 파일 처리 시 주의사항

### 제외 대상

- `.obsidian/` 폴더
- `archive/` 폴더
- `.canvas` 파일
- 이미지 파일 (`.png`, `.jpg`, `.gif` 등)

### 오류 처리

- 읽기 오류 파일은 `UNPROCESSED-FILES.md`에 기록
- 인코딩 문제 시 UTF-8로 재시도

## 검색 도구 선택 가이드

| 검색 유형 | 권장 도구 |
|-----------|-----------|
| 백링크/참조 관계 | obsidian CLI, 필요 시 markdown-oxide LSP |
| 태그 기반 검색 | obsidian CLI |
| 시맨틱 검색 (의미 기반) | vis |
| 단순 키워드 매칭 | ripgrep |
| 파일명 검색 | glob/find |
