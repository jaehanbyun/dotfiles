---
argument-hint: "[reddit-url-or-query]"
description: "Reddit 게시물/스레드 URL 또는 검색어를 입력받아 번역, 정리해서 Obsidian 문서로 저장"
color: orange
---

# Reddit to Obsidian - $ARGUMENTS

Reddit 게시물 또는 검색 결과를 번역/정리해서 Obsidian 문서를 생성합니다.

$ARGUMENTS가 제공되지 않은 경우, 사용법을 표시합니다:
```
/obsidian:summarize-reddit https://www.reddit.com/r/subreddit/comments/xxx/title/
/obsidian:summarize-reddit "검색어"
```

## 경로 정보

| 항목 | 경로 |
|------|------|
| vault | `~/Documents/Obsidian Vault/` |
| 저장 위치 | `~/Documents/Obsidian Vault/notes/community-insights/reddit/` |

## 작업 프로세스

### Step 1: 입력 타입 판별

```bash
INPUT="$ARGUMENTS"
if [[ "$INPUT" == *"reddit.com"* ]] || [[ "$INPUT" == *"redd.it"* ]]; then
    echo "TYPE=url"
else
    echo "TYPE=search"
fi
```

### Step 2: 콘텐츠 수집

#### URL인 경우: 게시물 + 댓글 전문 읽기

Reddit URL에서 POST_ID를 추출하고 `rdt read`로 전문을 가져옵니다:

```bash
# URL에서 POST_ID 추출 (reddit.com/r/sub/comments/POST_ID/...)
POST_ID=$(echo "$INPUT" | sed -E 's|.*comments/([^/]+).*|\1|')
rdt read "$POST_ID" --yaml
```

#### 검색어인 경우: 검색 후 가장 관련성 높은 게시물 읽기

```bash
rdt search "$INPUT" --limit 5 --yaml
```

검색 결과를 사용자에게 보여주고 어떤 게시물을 정리할지 선택하게 합니다.
사용자가 선택하면 해당 POST_ID로 `rdt read`를 실행합니다.

### Step 3: 중복 체크

```bash
grep -rl "source: $INPUT" ~/Documents/Obsidian\ Vault/notes/community-insights/reddit/ 2>/dev/null
```

기존 문서가 발견되면 사용자에게 덮어쓰기/취소를 확인합니다.

### Step 4: 문서 생성

```bash
mkdir -p ~/Documents/Obsidian\ Vault/notes/community-insights/reddit
```

#### yaml frontmatter 형식

```yaml
---
id: "{게시물 제목 원문}"
aliases:
  - "{게시물 제목 한국어 번역}"
tags:
  - community/reddit
  - {subreddit 관련 기술 태그}
  - {내용 기반 도메인 태그}
author: "u/{reddit_username}"
subreddit: "r/{subreddit_name}"
upvotes: {upvote_count}
comments_count: {comment_count}
created_at: "{현재 YYYY-MM-DD HH:mm}"
source: "{reddit_url}"
related: []
---
```

- id: 게시물 제목 원문
- aliases: 제목의 한국어 번역
- author: Reddit 사용자명 (u/ 접두사 포함)
- subreddit: 서브레딧명 (r/ 접두사 포함)
- tags: 최대 6개, 반드시 `community/reddit` 포함

#### 문서 본문 구조

```markdown
# {게시물 제목 한국어 번역}

> 원문: [{게시물 제목}]({reddit_url})
> 서브레딧: r/{subreddit} | 작성자: u/{author} | 추천: {upvotes}

## 요약

[게시물 핵심 내용을 2-3 문단으로 요약 - 한국어]

## 본문 번역

[게시물 본문 전체를 한국어로 번역]
[코드 블록, 링크 등은 원문 유지]

## 주요 댓글 분석

[추천수가 높거나 통찰력 있는 댓글 5-10개를 선별하여 번역/정리]

각 댓글 형식:
### u/{commenter} (↑{upvotes})
[댓글 내용 한국어 번역]

## 핵심 인사이트

- **인사이트 1**: [커뮤니티에서 도출된 핵심 교훈/의견]
- **인사이트 2**: [실무 적용 가능한 팁이나 경험]
- **인사이트 3**: [논쟁 포인트나 다양한 시각]

## 관련 링크

- [원문]({reddit_url})
- [댓글에서 언급된 유용한 링크들]
```

### Step 5: 저장

Write 도구로 문서를 저장합니다:
- 경로: `~/Documents/Obsidian Vault/notes/community-insights/reddit/{slugified-title}.md`
- 파일명: 게시물 제목을 소문자로, 공백은 `-`로, 특수문자 제거, 최대 60자

완료 메시지:
```
✅ Reddit 게시물이 Obsidian에 정리되었습니다:
   📁 ~/Documents/Obsidian Vault/notes/community-insights/reddit/{filename}.md
   📌 r/{subreddit}
   👤 u/{author}
   ↑ {upvotes} upvotes
```

## 번역 규칙

- 전체 문서를 한국어로 작성
- 기술 용어는 첫 등장 시 원문 병기: "의존성 주입(Dependency Injection)"
- 코드 예시, CLI 명령어, URL은 원문 유지
- Reddit 특유의 줄임말/밈은 괄호 안에 설명 추가: "LGTM (Looks Good To Me)"
- 댓글의 tone/nuance도 가능한 한 보존

## 에러 처리

- **rdt-cli 미설치**: "rdt-cli가 설치되어 있지 않습니다. `pipx install rdt-cli`로 설치해주세요." 출력
- **게시물 없음/삭제됨**: rdt read 실패 시 "게시물에 접근할 수 없습니다" 메시지 출력
- **검색 결과 없음**: "검색 결과가 없습니다. 다른 키워드로 시도해주세요." 출력
