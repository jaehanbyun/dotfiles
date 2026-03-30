---
name: weekly-work-logger
description: |
  실행 기준 저번 주(월~일) daily work log를 종합하여 주간 work log 생성.
  work-log/daily/ 문서를 바탕으로 주간 요약을 work-log/weekly/에 저장.
  "주간 정리", "weekly log", "이번 주 정리", "weekly work log" 등의 요청 시 자동 적용.
---

# Weekly Work Logger Skill

## 개요

실행하는 날 기준 **저번 주 월요일~일요일**에 해당하는 daily work log 문서들을 읽어 **주간 work log**를 생성합니다.

## 인수 (Arguments)

| 인수 | 설명 | 기본값 |
|------|------|--------|
| 날짜 | 기준 날짜 (YYYY-MM-DD) | 오늘 |

**사용 예시**:
- `/weekly-work-logger` - 저번 주 (오늘 기준)
- `/weekly-work-logger 2026-03-10` - 2026-03-10이 속한 주의 이전 주

## 경로 정보

| 항목 | 경로 |
|------|------|
| Daily 소스 | `~/Documents/Obsidian Vault/notes/work-log/daily/` |
| Weekly 출력 | `~/Documents/Obsidian Vault/notes/work-log/weekly/` |
| 파일명 형식 | `YYYY-MM-Wn.md` (예: `2026-03-W4.md`) — 해당 월의 n번째 주 (월요일 기준) |

---

## 실행 절차

### Phase 1: 날짜 범위 계산

```bash
# 기준 날짜 (인수 또는 오늘)
BASE_DATE="${1:-$(date +%Y-%m-%d)}"

# 저번 주 월요일 계산 (macOS)
# 현재 요일 번호 (1=월, 7=일)
DOW=$(date -j -f "%Y-%m-%d" "$BASE_DATE" +%u)
# 이번 주 월요일
THIS_MON=$(date -j -f "%Y-%m-%d" -v-$((DOW-1))d "$BASE_DATE" +%Y-%m-%d)
# 저번 주 월요일
LAST_MON=$(date -j -f "%Y-%m-%d" -v-7d "$THIS_MON" +%Y-%m-%d)
# 저번 주 일요일
LAST_SUN=$(date -j -f "%Y-%m-%d" -v+6d "$LAST_MON" +%Y-%m-%d)
# 월-주차 계산 (해당 월의 n번째 주, 월요일 기준)
MONTH=$(date -j -f "%Y-%m-%d" "$LAST_MON" +%m)
YEAR=$(date -j -f "%Y-%m-%d" "$LAST_MON" +%Y)
DAY_OF_MONTH=$(date -j -f "%Y-%m-%d" "$LAST_MON" +%d | sed 's/^0//')
# 1일의 요일 (1=월~7=일)
FIRST_DOW=$(date -j -f "%Y-%m-%d" "${YEAR}-${MONTH}-01" +%u)
# 첫 번째 월요일 날짜
if [ "$FIRST_DOW" -eq 1 ]; then FIRST_MON=1; else FIRST_MON=$((8 - FIRST_DOW + 1)); fi
# n번째 주 계산
WEEK_IN_MONTH=$(( (DAY_OF_MONTH - FIRST_MON) / 7 + 1 ))

echo "범위: $LAST_MON ~ $LAST_SUN (${YEAR}-${MONTH}-W${WEEK_IN_MONTH})"
```

### Phase 2: Daily 문서 수집

```bash
VAULT_ROOT="$HOME/Documents/Obsidian Vault"
DAILY_DIR="$VAULT_ROOT/notes/work-log/daily"

# 해당 주의 daily 파일 목록
for i in $(seq 0 6); do
  DAY=$(date -j -f "%Y-%m-%d" -v+${i}d "$LAST_MON" +%Y-%m-%d)
  FILE="$DAILY_DIR/${DAY}.md"
  [ -f "$FILE" ] && echo "$FILE"
done
```

발견된 각 daily 파일을 **Read 도구**로 읽습니다.

### Phase 3: 주간 요약 생성

읽은 daily 문서들을 종합하여 다음 구조로 작성:

```markdown
---
id: {YEAR}-{MONTH}-W{WEEK_IN_MONTH}-summary
aliases:
  - {YEAR}년 {MONTH_KR}월 {WEEK_IN_MONTH}주차 업무 요약
tags:
  - work-log/weekly
  - work-log/summary
created_at: {TODAY}
period: {LAST_MON} ~ {LAST_SUN}
related: []
---

# 주간 업무 요약 — {MONTH_KR}월 {WEEK_IN_MONTH}주차

> **기간**: {LAST_MON} (월) ~ {LAST_SUN} (일) | **분석된 Daily Notes**: {COUNT}/7일

---

## 주요 성과

- **{성과 제목}** ({날짜}) — {1줄 설명}
{3~5개 블릿, 날짜 포함, 가장 임팩트 있는 것 우선}

---

## 프로젝트별 업무

### {프로젝트명}
- **완료**: {완료 항목들}
- **진행 중**: {진행 중 항목들}

{프로젝트 단위로 그룹핑, daily의 Claude Code 세션 기반}

---

## 일별 요약

| 날짜 | 핵심 업무 |
|------|----------|
| {MM-DD (요일)} | {Vault N건, CC N세션 — 한 줄 요약} |

{Daily Note 없는 날은 "Daily Note 없음"}

---

## 기술 & 학습

### 주요 기술 학습

| 기술/도구 | 내용 | 날짜 |
|----------|------|------|
| {기술명} | {한 줄 설명} | {M/D} |

### 해결한 기술 문제

- **{문제명}**: {해결 방법} ({날짜})

### 사용 기술 스택

- **백엔드**: ...
- **프론트엔드**: ...
- **인프라**: ...

---

## 이슈 & 다음 주 계획

### 미완료 작업 (Carry-over)

- [ ] {미완료 항목}

### 이슈/블로커

- **{이슈명}** — {설명}

### 다음 주 제안 (Next Actions)

**P1 (즉시 착수)**
- [ ] {항목}

**P2 (병렬 진행)**
- [ ] {항목}

---

## Daily Notes

- [[{YYYY-MM-DD}]]
{해당 주의 daily note Obsidian 백링크}
```

### Phase 4: 파일 저장

```bash
WEEKLY_FILE="$VAULT_ROOT/notes/work-log/weekly/${YEAR}-${MONTH}-W${WEEK_IN_MONTH}.md"
```

Write 도구로 저장 후 완료 메시지:
`{YEAR}-{MONTH}-W{WEEK_IN_MONTH} ({LAST_MON} ~ {LAST_SUN}) 주간 work log가 생성되었습니다.`

---

## 에러 처리

- daily 파일이 하나도 없을 때: 빈 주간 로그 생성 + "해당 주에 daily work log가 없습니다" 안내
- 일부 날짜만 있을 때: 있는 날짜만 포함, 없는 날은 "작업 기록 없음"
- 기존 weekly 파일 존재 시: 덮어쓰기 전 확인 요청

## 관련 Skill

- `daily-work-logger`: 일일 work log (이 스킬의 소스)
- `monthly-work-logger`: 월간 work log (이 스킬의 출력이 소스)
