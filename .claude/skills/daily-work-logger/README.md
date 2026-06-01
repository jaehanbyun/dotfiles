# daily-work-logger

매일 아침 전날 업무 기록을 Codex 세션, Obsidian 문서, 미팅 노트에서 수집해 `work-log/daily/`에 정리하고, 오늘 할 일 후보를 Apple Reminders에 생성하는 스킬입니다.

## 사용법

```bash
/daily-work-logger             # 어제 작업 내역 정리
/daily-work-logger 2026-06-01  # 특정 날짜 작업 내역 정리
```

자연어 요청도 가능합니다.

- "어제 작업 정리해줘"
- "daily log"
- "업무 내역 정리"

## 주요 기능

- Obsidian Vault에서 해당 날짜에 생성/수정된 업무 문서 요약
- `~/.codex/sessions`, `~/.codex/archived_sessions`, `~/.codex/session_index.jsonl` 기반 Codex 세션 요약
- 미팅 노트의 논의 사항, 결정 사항, Action Items 정리
- daily log의 `## 다음 할 일`에서 3~5개를 뽑아 Apple Reminders `Daily Focus` 리스트에 생성
- 각 reminder notes와 completed `Daily Work Log - YYYY-MM-DD` reminder에 생성된 work log 문서 링크 저장

## 의존성

| 도구/서비스 | 용도 | 비고 |
|------------|------|------|
| Obsidian Vault | work log 저장소 | `$VAULT_ROOT`가 없으면 `~/Documents/Obsidian Vault` 사용 |
| Codex session files | Codex 작업 내역 수집 | 없으면 해당 섹션 건너뜀 |
| Reminders.app | 오늘 할 일 생성 | macOS 기본 앱, 리스트 없으면 자동 생성 |
| Python 3 | 수집/생성 스크립트 실행 | macOS 기본 제공 |

## 실행 구조

```text
daily-work-logger
  -> work-log-wrap-up/scripts/collect_work_log_context.py
  -> Obsidian work-log/daily/YYYY-MM-DD.md 생성 또는 갱신
  -> work-log-wrap-up/scripts/apple_reminders.py
  -> Reminders.app Daily Focus 리스트에 오늘 할 일 생성
```

출력 경로:

```text
$VAULT_ROOT/notes/work-log/daily/YYYY-MM-DD.md
```

관련 공통 스킬과 스크립트는 `~/.codex/skills/work-log-wrap-up/`에 있습니다.
