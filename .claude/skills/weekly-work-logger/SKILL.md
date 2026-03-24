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
| 파일명 형식 | `YYYY-Www.md` (예: `2026-W12.md`) |

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
# ISO 주 번호
WEEK_NUM=$(date -j -f "%Y-%m-%d" "$LAST_MON" +%V)
YEAR=$(date -j -f "%Y-%m-%d" "$LAST_MON" +%Y)

echo "범위: $LAST_MON ~ $LAST_SUN (${YEAR}-W${WEEK_NUM})"
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
date: {LAST_MON}
end_date: {LAST_SUN}
type: weekly
week: {YEAR}-W{WEEK_NUM}
tags: [work-log, weekly]
---

# Weekly Work Log - {YEAR}-W{WEEK_NUM}

> {LAST_MON} (월) ~ {LAST_SUN} (일)

## 주간 요약

{전체 주의 핵심 성과를 3-5줄로 요약}

## 일별 작업 내역

### {월요일 날짜}
{해당 daily에서 주요 내용 발췌/요약}

### {화요일 날짜}
...

(daily 문서가 없는 날은 "작업 기록 없음" 표시)

## 주간 학습 기록

{모든 daily의 학습 기록을 통합하여 중복 제거 후 정리}

### 기술/도구
- ...

### 해결방법
- ...

## 다음 주 계획

{이번 주 미완료 작업이나 다음 단계가 보이면 제안, 없으면 생략}
```

### Phase 4: 파일 저장

```bash
WEEKLY_FILE="$VAULT_ROOT/notes/work-log/weekly/${YEAR}-W${WEEK_NUM}.md"
```

Write 도구로 저장 후 완료 메시지:
`{YEAR}-W{WEEK_NUM} ({LAST_MON} ~ {LAST_SUN}) 주간 work log가 생성되었습니다.`

---

## 에러 처리

- daily 파일이 하나도 없을 때: 빈 주간 로그 생성 + "해당 주에 daily work log가 없습니다" 안내
- 일부 날짜만 있을 때: 있는 날짜만 포함, 없는 날은 "작업 기록 없음"
- 기존 weekly 파일 존재 시: 덮어쓰기 전 확인 요청

## 관련 Skill

- `daily-work-logger`: 일일 work log (이 스킬의 소스)
- `monthly-work-logger`: 월간 work log (이 스킬의 출력이 소스)
