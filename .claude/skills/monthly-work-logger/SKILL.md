---
name: monthly-work-logger
description: |
  실행 기준 저번 달의 weekly work log를 종합하여 월간 work log 생성.
  work-log/weekly/ 문서를 바탕으로 월간 요약을 work-log/monthly/에 저장.
  "월간 정리", "monthly log", "지난달 정리", "monthly work log" 등의 요청 시 자동 적용.
---

# Monthly Work Logger Skill

## 개요

실행하는 날 기준 **저번 달**에 해당하는 weekly work log 문서들을 읽어 **월간 work log**를 생성합니다.

## 인수 (Arguments)

| 인수 | 설명 | 기본값 |
|------|------|--------|
| 월 | 대상 월 (YYYY-MM 형식) | 저번 달 |

**사용 예시**:
- `/monthly-work-logger` - 저번 달 (오늘 기준)
- `/monthly-work-logger 2026-02` - 2026년 2월

## 경로 정보

| 항목 | 경로 |
|------|------|
| Weekly 소스 | `~/Documents/Obsidian Vault/notes/work-log/weekly/` |
| Monthly 출력 | `~/Documents/Obsidian Vault/notes/work-log/monthly/` |
| 파일명 형식 | `YYYY-MM.md` (예: `2026-03.md`) |

---

## 실행 절차

### Phase 1: 대상 월 결정

```bash
# 인수가 있으면 그대로, 없으면 저번 달
TARGET_MONTH="${1:-$(date -v-1m +%Y-%m)}"
YEAR=${TARGET_MONTH:0:4}
MONTH=${TARGET_MONTH:5:2}

echo "대상 월: $TARGET_MONTH"
```

### Phase 2: 해당 월의 Weekly 문서 수집

저번 달에 걸치는 ISO 주를 계산하여 해당 weekly 파일을 찾습니다.

```bash
VAULT_ROOT="$HOME/Documents/Obsidian Vault"
WEEKLY_DIR="$VAULT_ROOT/notes/work-log/weekly"

# 해당 월의 첫째 날과 마지막 날
FIRST_DAY="${TARGET_MONTH}-01"
LAST_DAY=$(date -j -f "%Y-%m-%d" -v+1m -v-1d "$FIRST_DAY" +%Y-%m-%d)

# 해당 월에 걸치는 주 번호들 찾기
FIRST_WEEK=$(date -j -f "%Y-%m-%d" "$FIRST_DAY" +%V)
LAST_WEEK=$(date -j -f "%Y-%m-%d" "$LAST_DAY" +%V)

# weekly 파일 검색 (YYYY-Www.md 패턴)
ls "$WEEKLY_DIR"/${YEAR}-W*.md 2>/dev/null
```

발견된 weekly 파일 중 **해당 월에 속하는 것**만 Read 도구로 읽습니다.
(weekly 파일의 frontmatter `date`/`end_date`를 확인하여 해당 월과 겹치는지 판단)

### Phase 3: 월간 요약 생성

읽은 weekly 문서들을 종합하여 다음 구조로 작성:

```markdown
---
date: {TARGET_MONTH}-01
type: monthly
month: {TARGET_MONTH}
tags: [work-log, monthly]
---

# Monthly Work Log - {TARGET_MONTH}

## 월간 요약

{해당 월의 핵심 성과와 주요 활동을 5-10줄로 요약}

## 주별 요약

### {YEAR}-W{xx} ({날짜 범위})
{해당 주의 주간 요약 발췌}

### {YEAR}-W{xx} ({날짜 범위})
...

## 월간 학습 기록

{모든 weekly의 학습 기록을 통합, 중복 제거, 카테고리별 정리}

### 기술/도구
- ...

### 해결방법
- ...

### 개념
- ...

## 주요 프로젝트 진행 현황

{weekly 문서에서 반복 등장하는 프로젝트를 추출하여 월간 진행 상황 정리}

| 프로젝트 | 주요 작업 | 상태 |
|----------|----------|------|
| ... | ... | ... |

## 다음 달 계획

{미완료 작업, 이어질 프로젝트, 예상 작업 등 제안}
```

### Phase 4: 파일 저장

```bash
MONTHLY_FILE="$VAULT_ROOT/notes/work-log/monthly/${TARGET_MONTH}.md"
```

Write 도구로 저장 후 완료 메시지:
`{TARGET_MONTH} 월간 work log가 생성되었습니다.`

---

## 에러 처리

- weekly 파일이 하나도 없을 때: daily 파일에서 직접 수집 시도 (fallback)
- 일부 주만 있을 때: 있는 주만 포함
- 기존 monthly 파일 존재 시: 덮어쓰기 전 확인 요청
- 연말/연초 주 번호 처리: ISO 8601 기준 (W01이 전년에 속할 수 있음)

## 관련 Skill

- `daily-work-logger`: 일일 work log
- `weekly-work-logger`: 주간 work log (이 스킬의 소스)
