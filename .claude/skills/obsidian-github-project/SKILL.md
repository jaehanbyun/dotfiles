---
name: obsidian-github-project
description: |
  GitHub 저장소 URL을 분석해 한국어 Obsidian 프로젝트 문서로 저장할 때 사용.
  사용자가 "obsidian:github-project", "/obsidian:github-project", "GitHub 프로젝트를 Obsidian에 정리",
  "obsidan:github-project", "깃허브 repo 문서화" 등을 요청하면 적용.
argument-hint: "[github-url]"
user_invocable: true
---

# Obsidian GitHub Project

GitHub 저장소를 분석하여 한국어 Obsidian 프로젝트 문서를 생성한다.

실행할 때 원본 Claude command가 있으면 먼저 읽고 그 절차를 우선한다. 이 파일의 나머지 내용은 Codex 실행용 보정 및 fallback 절차다.

Source command:

```text
/Users/byeonjaehan/.claude/commands/obsidian/github-project.md
```

사용자가 URL을 제공하지 않은 경우 다음 사용법을 안내한다:

```bash
obsidian:github-project https://github.com/owner/repo
```

## 경로 정보

| 항목 | 경로 |
|------|------|
| vault | `$VAULT_ROOT` 또는 `~/Documents/Obsidian Vault/` |
| 저장 위치 | `$VAULT_ROOT/notes/github-projects/{Category}/` |
| 태그 규칙 | 이 스킬의 "태그 부여 규칙" 섹션 |

## 작업 프로세스

### Step 1: URL 파싱

입력에서 owner와 repo를 추출한다.

```bash
URL="<github-url>"
OWNER_REPO=$(echo "$URL" | sed -E 's|https?://github\.com/||' | sed 's|/$||' | sed 's|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d'/' -f1)
REPO=$(echo "$OWNER_REPO" | cut -d'/' -f2)
```

URL 형식이 올바르지 않으면 "올바른 GitHub URL을 입력해주세요"라고 답한다.

### Step 2: GitHub 정보 수집

`gh` CLI로 저장소 정보를 수집한다. 가능한 경우 아래 4개 API를 병렬로 호출한다.

#### 2-1. 메타데이터

```bash
gh api "repos/${OWNER}/${REPO}" --jq '{
  name: .name,
  full_name: .full_name,
  description: .description,
  stars: .stargazers_count,
  forks: .forks_count,
  language: .language,
  license: (.license.spdx_id // "N/A"),
  topics: .topics,
  homepage: (.homepage // ""),
  created_at: .created_at,
  updated_at: .updated_at,
  default_branch: .default_branch
}'
```

#### 2-2. README

```bash
gh api "repos/${OWNER}/${REPO}/readme" --jq '.content' | base64 -d
```

README가 없으면 개요 섹션은 GitHub description과 메타데이터로 작성한다.

#### 2-3. 디렉토리 구조

상위 2레벨 디렉토리만 수집한다.

```bash
gh api "repos/${OWNER}/${REPO}/git/trees/HEAD?recursive=1" --jq '[.tree[] | select(.type=="tree") | .path] | map(select(split("/") | length <= 2))[]'
```

#### 2-4. 의존성 파일 탐지

```bash
for f in package.json pom.xml build.gradle go.mod Cargo.toml requirements.txt pyproject.toml Gemfile; do
  gh api "repos/${OWNER}/${REPO}/contents/${f}" --jq '.name' 2>/dev/null && echo "Found: $f"
done
```

발견된 의존성 파일 중 대표 파일 1개를 읽어서 주요 의존성을 파악한다.

```bash
gh api "repos/${OWNER}/${REPO}/contents/package.json" --jq '.content' | base64 -d | jq '{dependencies, devDependencies}'
```

### Step 3: 카테고리 자동 분류

수집된 topics, description, README, 디렉토리 구조를 종합해 아래 카테고리 중 하나를 선택한다.

| 카테고리 | 판단 기준 |
|----------|-----------|
| DevTools | CLI 도구, 개발 유틸리티, 린터, 포매터 |
| Library | npm/pip 등으로 설치하는 재사용 라이브러리 |
| Framework | 애플리케이션 프레임워크, 풀스택 도구 |
| Tutorial | 학습 자료, awesome 목록, 로드맵 |
| Application | 완성된 애플리케이션, 에디터, IDE |
| Infrastructure | 인프라, DevOps, 컨테이너, CI/CD |
| Data | 데이터 처리, DB, 분석 도구 |
| AI-ML | AI/ML 모델, LLM, 에이전트 프레임워크 |

카테고리명은 영문으로 하며 폴더명으로 사용 가능해야 한다.

### Step 4: 중복 체크

```bash
grep -rl "source: ${URL}" "$VAULT_ROOT/notes/github-projects/" 2>/dev/null
```

기존 문서가 발견되면 사용자에게 덮어쓰기 또는 취소 여부를 묻는다. 명시적 승인 없이 기존 문서를 덮어쓰지 않는다.

### Step 5: 문서 생성

카테고리 폴더를 생성하고 문서를 작성한다.

```bash
mkdir -p "$VAULT_ROOT/notes/github-projects/{Category}"
```

#### YAML frontmatter 형식

```yaml
---
id: "{repo-name}"
aliases:
  - "{프로젝트 한국어 설명}"
tags:
  - github-project
  - {기술스택 태그}
  - {도메인 태그}
author: "{owner}"
stars: {star_count}
language: "{primary_language}"
license: "{license_spdx_id}"
topics: [{GitHub topics 배열}]
category: "{Category}"
created_at: "{현재 YYYY-MM-DD HH:mm}"
source: "{github_url}"
related: []
---
```

### 태그 부여 규칙

태그는 다음 hierarchical tagging 규칙을 따른다:

- 계층 구분은 `/` 사용
- 태그명은 소문자
- 공백은 `-`로 대체
- 최대 6개 태그
- 반드시 `github-project` 태그 포함
- 디렉토리 기반 태그 사용 금지
- 의미 중심 태그 사용

#### 본문 구조

```markdown
# {프로젝트명}

## 개요

{프로젝트 목적과 핵심 가치를 한국어 2-3문단으로 요약}

## 주요 기능

- **기능 1**: 설명
- **기능 2**: 설명
- **기능 3**: 설명

## 기술 스택

| 구분 | 기술 |
|------|------|
| 언어 | {primary_language} |
| 프레임워크 | {감지된 프레임워크} |
| 주요 의존성 | {의존성 파일에서 추출} |
| 빌드 도구 | {감지된 빌드 도구} |

## 설치 및 사용법

{README의 Installation/Getting Started 섹션을 한국어로 번역. 코드 블록과 CLI 명령어는 원문 유지}

## 코드 구조

{상위 2레벨 디렉토리 트리}

{주요 디렉토리와 파일의 역할 설명}

## 활용 시나리오

{유용한 상황 2-3가지와 대상 사용자}

## 관련 링크

- [GitHub]({github_url})
- [공식 문서]({homepage_url})
```

### Step 6: 저장 및 완료

저장 경로:

```text
$VAULT_ROOT/notes/github-projects/{Category}/{repo-name}.md
```

파일명은 저장소 이름을 소문자로 바꾸고 공백은 `-`로 변환한다.

완료 메시지:

```text
GitHub 프로젝트 문서가 생성되었습니다:
파일: $VAULT_ROOT/notes/github-projects/{Category}/{repo-name}.md
카테고리: {Category}
Stars: {star_count}
언어: {language}
```

## 번역 규칙

- 전체 문서는 한국어로 작성
- 기술 용어는 첫 등장 시 원문 병기: "의존성 주입(Dependency Injection)"
- 프로젝트명, 코드 예시, CLI 명령어는 원문 유지
- 설치 명령어는 원문 유지

## 에러 처리

- URL 형식 오류: "올바른 GitHub URL을 입력해주세요"
- 저장소 없음/접근 불가: `gh api` 오류를 확인하고 "저장소에 접근할 수 없습니다"
- README 없음: description과 메타데이터로 개요 작성
- 의존성 파일 없음: 기술 스택 섹션에서 language 정보만 표시

## 관련 스킬

- `obsidian-vault`: vault 작업 기본 가이드
- `gh`: GitHub CLI 작업
