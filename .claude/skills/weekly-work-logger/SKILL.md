---
name: weekly-work-logger
description: |
  실행 기준 저번 주(월~일)의 daily work log를 종합해 주간 업무 요약을 work-log/weekly/에 저장.
  "주간 정리", "weekly log", "이번 주 정리", "/weekly-work-logger" 요청 시 사용.
argument-hint: "[base YYYY-MM-DD]"
user_invocable: true
---

# Weekly Work Logger

Daily Work Log를 소스로 사용한다. Daily가 Codex 세션 중심으로 작성되므로 weekly도 Codex 작업 내역 기준으로 요약한다.

## 실행

1. 기준 날짜를 정한다. 인수가 없으면 오늘이다.
2. 기준 날짜가 속한 주의 이전 주 월요일~일요일을 계산한다.
3. 공통 수집 스크립트로 해당 주 daily 파일을 모은다.

```bash
python3 ~/.codex/skills/work-log-wrap-up/scripts/collect_work_log_context.py weekly {BASE_DATE}
```

4. 수집된 daily 파일을 종합해 저장한다.

출력 경로:

```text
$VAULT_ROOT/notes/work-log/weekly/{YEAR}-{MONTH}-W{WEEK_IN_MONTH}.md
```

## 출력 포맷

기존 Claude Code weekly 포맷을 유지한다.

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

## 주요 성과
## 프로젝트별 업무
## 일별 요약
## 기술 & 학습
## 이슈 & 다음 주 계획
## Daily Notes
```

기존 weekly 파일이 있으면 덮어쓰기 전에 내용을 확인하고, 수동 편집이 있어 보이면 사용자 확인을 받는다.
