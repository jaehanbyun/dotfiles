---
name: daily-work-logger
description: |
  매일 아침 업무 시작 전 어제 작업 내역을 정리하여 work-log/daily/에 반영.
  서브 에이전트 기반 병렬 처리로 메인 컨텍스트 절약.
  "어제 작업 정리해줘", "daily log", "업무 내역 정리" 등의 요청 시 자동 적용.
---

# Daily Work Logger Skill

## 개요

매일 아침 업무 시작 전 실행하여 어제 작성/수정된 문서들에서 **업무 수행 관련 내용**을 추출하고 `work-log/daily/`에 **자동으로 반영**하는 skill.

## 핵심 아키텍처

> **서브 에이전트 기반 병렬 처리**로 메인 에이전트의 컨텍스트를 최소화합니다.

```
Main Agent (Orchestrator)
  │
  ├── Sub 1: Vault Files Analyzer
  ├── Sub 2: Claude Sessions & Learning Analyzer
  ├── Sub 3: Meeting Notes Analyzer
  └── Sub 4: Things Analyzer
  │
  └── 결과 통합 → work-log/daily/{TARGET_DATE}.md
```

## 인수 (Arguments)

| 인수 | 설명 | 기본값 |
|------|------|--------|
| 날짜 | 분석할 날짜 (YYYY-MM-DD 형식) | 어제 날짜 |

**사용 예시**:
- `/daily-work-logger` - 어제 날짜 분석 및 반영
- `/daily-work-logger 2026-01-12` - 특정 날짜 분석 및 반영

## 경로 정보

| 항목 | 경로 |
|------|------|
| Vault Root | `~/Documents/Obsidian Vault/` |
| Daily Work Log | `~/Documents/Obsidian Vault/work-log/daily/` |
| Weekly Work Log | `~/Documents/Obsidian Vault/work-log/weekly/` |
| Monthly Work Log | `~/Documents/Obsidian Vault/work-log/monthly/` |
| Claude 세션 | `~/.claude/history.jsonl` |

---

## 실행 절차

### Phase 1: 초기화 (메인 에이전트 - 순차)

1. **날짜 결정** - 인수가 없으면 어제 날짜 사용
```bash
TARGET_DATE="${1:-$(date -v-1d +%Y-%m-%d)}"
echo "대상 날짜: $TARGET_DATE"
```

2. **Daily Work Log 경로 확인**
```bash
VAULT_ROOT="$HOME/Documents/Obsidian Vault"
DAILY_LOG="$VAULT_ROOT/work-log/daily/${TARGET_DATE}.md"
```

---

### Phase 2: 서브 에이전트 병렬 실행

> **중요**: 아래 4개의 Task를 **단일 메시지에서 동시에 호출**하여 병렬 실행합니다.
> 비용/속도 최적화를 위해 **haiku 모델**을 사용합니다.

#### SubAgent 1: Vault Files Analyzer

| 파라미터 | 값 |
|---------|-----|
| description | "Vault 파일 분석" |
| model | "haiku" |

**프롬프트 (TARGET_DATE 치환 필요):**

```
Obsidian Vault 파일 분석. 코드를 작성하지 말고 분석만 수행.

## 작업
{TARGET_DATE}에 생성/수정된 .md 파일을 분석하여 업무 관련 내용 추출.

## 실행
1. Bash로 해당 날짜 수정 파일 찾기 (macOS):
   find "$HOME/Documents/Obsidian Vault" -name "*.md" -type f -exec stat -f "%Sm %N" -t "%Y-%m-%d" {} \; 2>/dev/null | grep "{TARGET_DATE}" | awk '{print $2}' | grep -v "work-log/"

2. 발견된 파일 Read로 읽기
3. 업무 관련 내용 추출 (기술 학습, 문서 작성, 프로젝트 작업)

## 출력 형식
### Vault 문서 작업
- **[파일명]**: 작업 내용 요약 (1-2줄)

(없으면 "해당 날짜에 수정된 vault 문서 없음" 반환)
```

#### SubAgent 2: Claude Sessions & Learning Analyzer

| 파라미터 | 값 |
|---------|-----|
| description | "Claude 세션 및 학습 분석" |
| model | "haiku" |

**프롬프트 (TARGET_DATE 치환 필요):**

```
Claude Code 세션 분석. 코드를 작성하지 말고 분석만 수행.

## 작업
{TARGET_DATE}의 Claude Code 세션을 ~/.claude/history.jsonl에서 파싱.

## 실행
Bash로 python3 스크립트 실행:

python3 -c "
import json, datetime, os
with open(os.path.expanduser('~/.claude/history.jsonl')) as f:
    lines = f.readlines()
target_start = datetime.datetime(int('{TARGET_DATE}'[:4]), int('{TARGET_DATE}'[5:7]), int('{TARGET_DATE}'[8:10]), 0, 0, 0).timestamp() * 1000
target_end = target_start + 86400000
sessions = {}
for line in lines:
    obj = json.loads(line)
    ts = obj.get('timestamp', 0)
    if target_start <= ts < target_end:
        sid = obj.get('sessionId', 'no-sid')
        proj = obj.get('project', 'unknown')
        display = obj.get('display', '').strip()
        if not display: continue
        proj_name = proj.split('/')[-1] if '/' in proj else proj
        if sid not in sessions:
            sessions[sid] = {'project': proj_name, 'messages': []}
        sessions[sid]['messages'].append(display[:200])
for sid, info in sorted(sessions.items(), key=lambda x: x[1]['project']):
    print(f'### {info[\"project\"]} (세션: {sid[:8]}...)')
    for m in info['messages']:
        print(f'  > {m}')
    print()
"

## 출력 형식

### Claude Code 작업
- **[프로젝트명]**: 수행 작업 요약

### 학습 기록
#### 기술/도구
- **[도구명]**: 설명
#### 해결방법
- **[문제]**: 해결 방법 요약

(history.jsonl 없으면 "Claude 세션 분석 건너뜀" 반환)
```

#### SubAgent 3: Meeting Notes Analyzer

| 파라미터 | 값 |
|---------|-----|
| description | "미팅 노트 분석" |
| model | "haiku" |

**프롬프트:**

```
{TARGET_DATE} 미팅 노트 분석. Vault 전체에서 파일명에 "{TARGET_DATE}" 포함된 미팅 노트 검색.
ls "$HOME/Documents/Obsidian Vault"/notes/dailies/{TARGET_DATE}-*.md 2>/dev/null
각 미팅에서 주제, 논의 사항, 결정 사항, Action Items 추출.
없으면 "해당 날짜에 미팅 노트 없음" 반환.
```

#### SubAgent 4: Things Analyzer

| 파라미터 | 값 |
|---------|-----|
| description | "Things 활동 분석" |
| model | "haiku" |

**프롬프트:**

```
Things 3 활동 분석. ToolSearch로 "things" 검색하여 MCP 도구 로드.
도구 없으면 "Things MCP 서버 미설정 - 건너뜀" 반환.
```

---

### Phase 3: 결과 통합 및 파일 생성 (메인 에이전트)

1. 4개 서브 에이전트 결과 수집
2. `work-log/daily/{TARGET_DATE}.md` 파일 생성/업데이트:

```markdown
---
date: {TARGET_DATE}
type: daily
tags: [work-log, daily]
---

# Daily Work Log - {TARGET_DATE}

## 작업 내역

{SubAgent 1 결과 - Vault 문서 작업}

{SubAgent 2 결과 중 "Claude Code 작업"}

{SubAgent 3 결과 - 미팅}

{SubAgent 4 결과 - Things 활동}

## 학습 기록

{SubAgent 2 결과 중 "학습 기록"}
```

3. 완료 메시지: `{TARGET_DATE} 작업 내역이 work-log/daily/에 반영되었습니다.`

---

## 관련 Skill

- `weekly-work-logger`: 주간 work log (daily 문서 기반)
- `monthly-work-logger`: 월간 work log (weekly 문서 기반)
