---
argument-hint: "[문제 정보 및 리뷰 내용을 대화에 포함하여 전달]"
description: "LeetCode 풀이 리뷰를 정리해서 Obsidian 노트로 저장"
---

# LeetCode Review → Obsidian - $ARGUMENTS

ChatGPT/Claude 등과 나눈 LeetCode 풀이 리뷰 대화를 구조화된 Obsidian 노트로 정리합니다.

## 작업 프로세스

### 1. 정보 추출

대화 내용에서 다음을 추출합니다:

- **문제 번호, 제목, 난이도**
- **내 풀이 코드** (대화에 포함된 코드 또는 leetcode repo에서 탐색)
- **리뷰 포인트** (버그, 성능 이슈, 코드 스타일 등)
- **개선안/대안 풀이** (코드 + 설명)
- **핵심 학습 포인트**

### 2. 소스 코드 탐색

leetcode repo에서 해당 문제의 소스 코드를 찾습니다:

```bash
fd '{문제번호}_' ~/projects/leetcode/
```

파일이 있으면 repo의 코드를 포함하고, 없으면 대화에서 추출한 코드를 사용합니다.

### 3. Obsidian 노트 생성

#### 저장 경로

```
~/Documents/Obsidian Vault/notes/leetcode/{번호}_{제목}.md
```

파일명은 leetcode repo의 네이밍 규칙과 동일합니다 (공백은 `_`).

#### YAML Frontmatter

```yaml
---
id: "190. Reverse Bits"
aliases: "190. 비트 뒤집기"
tags:
  - leetcode/{easy|medium|hard}
  - algorithms/{topic}
  - {language}/{concept}
date: YYYY-MM-DD
difficulty: Easy|Medium|Hard
language: CPP|Python|SQL|Go
source: https://leetcode.com/problems/{slug}/
---
```

- `id`: 문제 번호 + 영문 제목
- `aliases`: 문제 번호 + 한국어 제목
- `tags`: hierarchical tag (add-tag.md 규칙 준수, 최대 6개)
  - `leetcode/{난이도}` (필수)
  - `algorithms/{알고리즘 분류}` (dp, bit-manipulation, two-pointers 등)
  - `{언어}/{관련 개념}` (선택)
- `source`: LeetCode 문제 URL

#### 본문 구조

```markdown
# {번호}. {제목} ({난이도})

> 한 줄 요약

## 문제 요약
- 핵심 조건과 제약사항

## 내 풀이
- 코드 블록 (언어 명시)
- 접근 방식 간단 설명

## 리뷰
- 정답 여부
- 시간/공간 복잡도
- 발견된 문제점 (버그, 성능, 스타일)

## 개선안
### 개선안 1: (이름)
- 핵심 아이디어
- 코드
- 복잡도

### 개선안 2: (이름)  (있는 경우)

## 배운 점
- 핵심 교훈 (bullet)
```

### 4. 태그 규칙

`~/.claude/commands/obsidian/add-tag.md`에 정의된 hierarchical tagging 규칙을 준수합니다.

주요 알고리즘 태그 예시:
- `algorithms/dp`, `algorithms/greedy`, `algorithms/binary-search`
- `algorithms/bit-manipulation`, `algorithms/two-pointers`
- `algorithms/tree/traversal`, `algorithms/graph/bfs`
- `algorithms/string-manipulation`, `algorithms/matrix`
- `algorithms/divide-and-conquer`, `algorithms/sliding-window`

### 5. 중복 확인

동일 번호의 노트가 이미 존재하면 사용자에게 알리고 덮어쓸지 확인합니다.

## 사용 예시

사용자가 대화 내용을 직접 붙여넣기하거나, 파일로 제공합니다:

```
/obsidian:leetcode-review

[ChatGPT 대화 내용 붙여넣기]
```

또는 문제 번호만 제공하면 repo 코드를 읽고 자체 리뷰를 생성합니다:

```
/obsidian:leetcode-review 190
```

## 주의사항

- 대화 내용이 여러 문제를 포함하면 문제별로 개별 파일 생성
- 영어 표현 리뷰 등 비-코드 내용은 제외
- 코드 블록에는 반드시 언어 태그 포함 (`cpp`, `python` 등)
