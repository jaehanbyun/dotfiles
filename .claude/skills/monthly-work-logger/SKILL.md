---
name: monthly-work-logger
description: |
  실행 기준 저번 달의 weekly work log를 종합해 월간 업무 요약을 work-log/monthly/에 저장.
  "월간 정리", "monthly log", "지난달 정리", "/monthly-work-logger" 요청 시 사용.
argument-hint: "[YYYY-MM]"
user_invocable: true
---

# Monthly Work Logger

Weekly Work Log를 소스로 사용한다. Weekly가 없으면 같은 월의 daily 파일로 fallback한다.

## 실행

1. 대상 월을 정한다. 인수가 없으면 Asia/Seoul 기준 저번 달이다.
2. 공통 수집 스크립트로 해당 월과 겹치는 weekly 파일을 모은다.

```bash
python3 ~/.codex/skills/work-log-wrap-up/scripts/collect_work_log_context.py monthly {YYYY-MM}
```

3. weekly 파일이 없으면 스크립트가 daily fallback을 제공한다.
4. 수집 결과를 월간 관점으로 재구성해 저장한다.

출력 경로:

```text
$VAULT_ROOT/notes/work-log/monthly/{YYYY-MM}.md
```

## 출력 포맷

```markdown
---
date: {YYYY-MM}-01
type: monthly
month: {YYYY-MM}
tags: [work-log, monthly]
---

# Monthly Work Log - {YYYY-MM}

## 월간 요약
## 주별 요약
## 월간 학습 기록
### 기술/도구
### 해결방법
### 개념
## 주요 프로젝트 진행 현황
## 다음 달 계획
```

기존 monthly 파일이 있으면 덮어쓰기 전에 내용을 확인하고, 수동 편집이 있어 보이면 사용자 확인을 받는다.
