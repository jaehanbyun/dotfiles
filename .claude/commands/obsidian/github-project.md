---
argument-hint: "[github-url]"
description: "GitHub 저장소 URL을 입력받아 분석 후 Obsidian 프로젝트 문서로 저장"
color: green
---

# GitHub Project to Obsidian - $ARGUMENTS

GitHub 저장소를 분석하여 한국어 Obsidian 프로젝트 문서를 생성합니다.

$ARGUMENTS가 제공되지 않은 경우, 사용법을 표시합니다:
```
/obsidian:github-project https://github.com/owner/repo
```

## 경로 정보

| 항목 | 경로 |
|------|------|
| vault | `~/Documents/Obsidian Vault/` |
| 저장 위치 | `~/Documents/Obsidian Vault/notes/github-projects/{Category}/` |
| 태그 규칙 | `~/.claude/commands/obsidian/add-tag.md` |

## 작업 프로세스

### Step 1: URL 파싱

$ARGUMENTS에서 owner와 repo를 추출합니다.

```bash
# URL에서 owner/repo 추출
URL="$ARGUMENTS"
OWNER_REPO=$(echo "$URL" | sed -E 's|https?://github\.com/||' | sed 's|/$||' | sed 's|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d'/' -f1)
REPO=$(echo "$OWNER_REPO" | cut -d'/' -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

### Step 2: GitHub 정보 수집

`gh` CLI로 저장소 정보를 수집합니다. **아래 4개 API를 병렬로 호출하세요.**

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

#### 2-3. 디렉토리 구조 (상위 2레벨)
```bash
gh api "repos/${OWNER}/${REPO}/git/trees/HEAD?recursive=1" --jq '[.tree[] | select(.type=="tree") | .path] | map(select(split("/") | length <= 2))[]'
```

#### 2-4. 의존성 파일 탐지
```bash
# 주요 의존성 파일 존재 여부 확인
for f in package.json pom.xml build.gradle go.mod Cargo.toml requirements.txt pyproject.toml Gemfile; do
  gh api "repos/${OWNER}/${REPO}/contents/${f}" --jq '.name' 2>/dev/null && echo " → Found: $f"
done
```

발견된 의존성 파일 중 가장 대표적인 것 1개를 읽어서 주요 의존성을 파악합니다:
```bash
# 예: package.json인 경우
gh api "repos/${OWNER}/${REPO}/contents/package.json" --jq '.content' | base64 -d | jq '{dependencies, devDependencies}'
```

### Step 3: 카테고리 자동 분류

수집된 정보를 종합 분석하여 아래 카테고리 중 가장 적합한 것을 선택합니다:

| 카테고리 | 판단 기준 | 예시 저장소 |
|----------|-----------|-------------|
| DevTools | CLI 도구, 개발 유틸리티, 린터, 포매터 | eslint, prettier, gh |
| Library | npm/pip 등으로 설치하는 재사용 라이브러리 | lodash, axios, guava |
| Framework | 애플리케이션 프레임워크, 풀스택 도구 | Next.js, Spring Boot, Django |
| Tutorial | 학습 자료, awesome 목록, 로드맵 | coding-interview, roadmap |
| Application | 완성된 애플리케이션, 에디터, IDE | VS Code, Obsidian |
| Infrastructure | 인프라, DevOps, 컨테이너, CI/CD | Docker, Terraform, k8s |
| Data | 데이터 처리, DB, 분석 도구 | pandas, dbt, PostgreSQL |
| AI-ML | AI/ML 모델, LLM, 에이전트 프레임워크 | langchain, transformers |

**분류 로직**: topics, description, README 내용, 디렉토리 구조를 종합하여 LLM이 판단합니다.
카테고리명은 영문으로 하되, 폴더명으로 사용 가능하도록 합니다.

### Step 4: 중복 체크

```bash
# vault 내 동일 GitHub URL 검색
grep -rl "source: ${URL}" ~/Documents/Obsidian\ Vault/notes/github-projects/ 2>/dev/null
```

- 기존 문서가 발견되면 AskUserQuestion으로 사용자에게 알립니다:
  - **덮어쓰기**: 기존 문서를 최신 정보로 교체
  - **취소**: 작업 중단

### Step 5: 문서 생성

카테고리 폴더를 생성하고 문서를 작성합니다:

```bash
mkdir -p ~/Documents/Obsidian\ Vault/notes/github-projects/{Category}
```

#### yaml frontmatter 형식

```yaml
---
id: "{repo-name}"
aliases:
  - "{프로젝트 한국어 설명 (description 번역)}"
tags:
  - github-project
  - {기술스택 태그 - add-tag.md 규칙 준수}
  - {도메인 태그 - add-tag.md 규칙 준수}
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

- id: 저장소 이름 (원문)
- aliases: description의 한국어 번역
- author: owner명을 소문자, 공백은 `-`로 변환
- tags: `~/.claude/commands/obsidian/add-tag.md` 규칙 준수, 최대 6개
  - 반드시 `github-project` 태그 포함
  - 기술 스택 태그 예: `java/spring-boot`, `typescript/react`
  - 도메인 태그 예: `tools/cli`, `ai/llm-framework`

#### 문서 본문 구조

```markdown
# {프로젝트명}

## 개요

[프로젝트 목적과 핵심 가치를 2-3 문단으로 요약 - 한국어]
[description과 README 도입부를 바탕으로 작성]

## 주요 기능

- **기능 1**: 설명
- **기능 2**: 설명
- **기능 3**: 설명
[README에서 핵심 기능 5-7개 추출]

## 기술 스택

| 구분 | 기술 |
|------|------|
| 언어 | {primary_language} |
| 프레임워크 | {감지된 프레임워크} |
| 주요 의존성 | {의존성 파일에서 추출} |
| 빌드 도구 | {감지된 빌드 도구} |

## 설치 및 사용법

[README의 Installation/Getting Started 섹션을 한국어로 번역]
[코드 블록과 CLI 명령어는 원문 유지]

## 코드 구조

```
{디렉토리 트리 - 상위 2레벨}
```

[주요 디렉토리와 파일의 역할 설명 - 한국어]

## 활용 시나리오

[이 프로젝트가 유용한 상황 2-3가지를 한국어로 설명]
[대상 사용자와 적합한 프로젝트 유형 명시]

## 관련 링크

- [GitHub]({github_url})
- [공식 문서]({homepage_url}) ← homepage가 있는 경우
- [npm/PyPI/Maven 등]({패키지 레지스트리 URL}) ← 해당되는 경우
```

### Step 6: 저장 및 완료

Write 도구로 문서를 저장합니다:
- 경로: `~/Documents/Obsidian Vault/notes/github-projects/{Category}/{repo-name}.md`
- 파일명: 저장소 이름을 소문자로, 공백은 `-`로 변환

완료 메시지:
```
✅ GitHub 프로젝트 문서가 생성되었습니다:
   📁 ~/Documents/Obsidian Vault/notes/github-projects/{Category}/{repo-name}.md
   🏷️  카테고리: {Category}
   ⭐ Stars: {star_count}
   🔧 언어: {language}
```

## 번역 규칙

- 전체 문서를 한국어로 작성
- 기술 용어는 첫 등장 시 원문 병기: "의존성 주입(Dependency Injection)"
- 프로젝트명, 코드 예시, CLI 명령어는 원문 유지
- 설치 명령어(`npm install`, `pip install` 등)는 원문 유지

## 태그 부여 규칙

`~/.claude/commands/obsidian/add-tag.md`에 정의된 hierarchical tagging 규칙을 준수합니다:

- 계층 구분은 `/` 사용
- 태그명은 소문자
- 공백은 `-`로 대체
- 최대 6개 태그
- 반드시 `github-project` 태그 포함
- 디렉토리 기반 태그 사용 금지 (resources/, slipbox/ 등)
- 의미 중심 태그 사용

## 에러 처리

- **URL 형식 오류**: "올바른 GitHub URL을 입력해주세요" 메시지 출력
- **저장소 없음/접근 불가**: `gh api` 오류 시 "저장소에 접근할 수 없습니다" 메시지 출력
- **README 없음**: 개요 섹션을 description으로 대체
- **의존성 파일 없음**: 기술 스택 섹션에서 language 정보만 표시

## 관련 Command

- `obsidian:add-tag` - 태그 부여/개선
- `obsidian:summarize-article` - 기술 문서 요약 (유사 패턴)
- `obsidian:related-contents` - 관련 노트 연결
