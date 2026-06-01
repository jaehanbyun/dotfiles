---
name: daily-work-logger
description: |
  매일 아침 업무 시작 전 어제 작업 내역을 Codex 세션, Obsidian 문서, 미팅 노트에서 수집해 work-log/daily/에 반영하고, 오늘 할 일 후보를 Apple Reminders에 생성할 때 사용.
  "어제 작업 정리해줘", "daily log", "업무 내역 정리", "/daily-work-logger" 요청 시 사용.
argument-hint: "[YYYY-MM-DD]"
user_invocable: true
---

# Daily Work Logger

기존 Claude Code daily routine의 Codex 버전이다. 구조는 `문서 / 세션 / 미팅`을 유지하되, 세션 수집원은 `~/.codex`다. Things는 더 이상 사용하지 않는다.

## 실행

1. 대상 날짜를 정한다. 인수가 없으면 Asia/Seoul 기준 어제다.
2. 공통 수집 스크립트를 실행한다.

```bash
python3 ~/.codex/skills/work-log-wrap-up/scripts/collect_work_log_context.py daily {TARGET_DATE}
```

3. 수집 결과를 중복 제거하고 기존 포맷으로 요약해 저장한다.
4. daily log의 Action Items/다음 할 일/미완료 작업에서 오늘 수행할 일 3~5개를 뽑아 `## 다음 할 일` 섹션에 적는다.
5. Apple Reminders의 `Daily Focus` 리스트에 오늘 due date로 task를 생성한다. 리스트가 없으면 자동 생성한다.
   - 각 task의 notes에는 생성된 daily work log의 Obsidian 링크, file URL, filesystem path를 넣는다.
   - 같은 리스트의 completed 항목에는 `Daily Work Log - {TARGET_DATE}` reminder를 만들거나 갱신해 work log 링크를 보관한다.

출력 경로:

```text
$VAULT_ROOT/notes/work-log/daily/{TARGET_DATE}.md
```

`$VAULT_ROOT`가 없으면 `~/Documents/Obsidian Vault`를 사용한다.

## 출력 포맷

```markdown
---
date: {TARGET_DATE}
type: daily
tags: [work-log, daily]
---

# Daily Work Log - {TARGET_DATE}

## 작업 내역

### Vault 문서 작업
- **문서명**: 작업 내용 요약

### 미팅
- **미팅명**: 주제, 결정 사항, Action Items

### Codex 작업
- **프로젝트/스레드명**: 수행 작업 요약

## 학습 기록

### 기술/도구
- **도구명**: 학습 내용

### 해결방법
- **문제**: 해결 방법

## 다음 할 일

- [ ] 오늘 할 일 1
- [ ] 오늘 할 일 2
- [ ] 오늘 할 일 3
```

기존 daily 파일이 있으면 먼저 읽고, 명백히 같은 날짜의 generated work-log일 때만 갱신한다. 수동으로 추가된 내용이 섞여 있어 보이면 덮어쓰기 전에 확인한다.

Apple Reminders 생성:

```bash
python3 ~/.codex/skills/work-log-wrap-up/scripts/apple_reminders.py create-from-worklog "$DAILY_LOG" --due "$(date +%Y-%m-%d)" --list "Daily Focus"
```

이 명령은 기본적으로 완료된 reminder `Daily Work Log - {TARGET_DATE}`도 생성/갱신한다. 해당 completed 항목의 notes에서 Obsidian 링크로 생성된 문서를 바로 열 수 있어야 한다.
