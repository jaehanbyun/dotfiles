---
argument-hint: "[twitter-url-or-query]"
description: "Twitter/X 트윗/스레드 URL 또는 검색어를 입력받아 번역, 정리해서 Obsidian 문서로 저장"
color: blue
---

# Twitter to Obsidian - $ARGUMENTS

Twitter/X 트윗 또는 스레드를 번역/정리해서 Obsidian 문서를 생성합니다.

$ARGUMENTS가 제공되지 않은 경우, 사용법을 표시합니다:
```
/obsidian:summarize-twitter https://x.com/username/status/123456789
/obsidian:summarize-twitter "검색어"
```

## 경로 정보

| 항목 | 경로 |
|------|------|
| vault | `~/Documents/Obsidian Vault/` |
| 저장 위치 | `~/Documents/Obsidian Vault/notes/community-insights/twitter/` |

## 작업 프로세스

### Step 1: 입력 타입 판별

```bash
INPUT="$ARGUMENTS"
if [[ "$INPUT" == *"x.com"* ]] || [[ "$INPUT" == *"twitter.com"* ]]; then
    echo "TYPE=url"
else
    echo "TYPE=search"
fi
```

### Step 2: 콘텐츠 수집

#### URL인 경우: 트윗/스레드 읽기

```bash
# 단일 트윗 또는 스레드 읽기
twitter tweet "$INPUT"

# X Article (장문) 인 경우
twitter article "$INPUT"
```

#### 검색어인 경우: 검색 후 선택

```bash
twitter search "$INPUT" --limit 10
```

검색 결과를 사용자에게 보여주고 어떤 트윗/스레드를 정리할지 선택하게 합니다.

### Step 3: 스레드 여부 판단

트윗 내용에 연속된 reply chain이 있으면 스레드로 판단합니다.
- **단일 트윗**: 간결한 노트 형식으로 정리
- **스레드 (2개 이상 연결된 트윗)**: 상세 문서 형식으로 정리
- **Article (장문)**: 기술 문서 형식으로 정리 (`summarize-article` 패턴 적용)

### Step 4: 중복 체크

```bash
grep -rl "source: $INPUT" ~/Documents/Obsidian\ Vault/notes/community-insights/twitter/ 2>/dev/null
```

### Step 5: 문서 생성

```bash
mkdir -p ~/Documents/Obsidian\ Vault/notes/community-insights/twitter
```

#### yaml frontmatter 형식

```yaml
---
id: "{트윗 첫 줄 또는 스레드 주제 (원문, 최대 80자)}"
aliases:
  - "{한국어 번역}"
tags:
  - community/twitter
  - {내용 기반 기술 태그}
  - {도메인 태그}
author: "@{username}"
tweet_type: "{single|thread|article}"
likes: {like_count}
retweets: {retweet_count}
created_at: "{현재 YYYY-MM-DD HH:mm}"
source: "{tweet_url}"
related: []
---
```

- id: 트윗 첫 줄 또는 스레드의 핵심 주제 (원문)
- aliases: 한국어 번역
- author: @username 형식
- tweet_type: single / thread / article
- tags: 최대 6개, 반드시 `community/twitter` 포함

#### 단일 트윗 본문 구조

```markdown
# {핵심 내용 한국어 요약}

> 원문: [{트윗 첫 줄}]({tweet_url})
> 작성자: @{username} | ♥ {likes} | 🔄 {retweets}

## 번역

[트윗 전문 한국어 번역]

## 맥락 및 의의

[이 트윗이 중요한 이유나 맥락 1-2 문단]

## 주요 반응

[인용 리트윗이나 주요 답글 중 인사이트 있는 것 정리]
```

#### 스레드 본문 구조

```markdown
# {스레드 주제 한국어 요약}

> 원문: [{스레드 첫 트윗}]({tweet_url})
> 작성자: @{username} | 트윗 {N}개 | ♥ {likes}

## 요약

[스레드 전체 내용을 2-3 문단으로 요약]

## 스레드 전문 번역

### 1/{N}
[첫 번째 트윗 번역]

### 2/{N}
[두 번째 트윗 번역]

... (모든 트윗 포함)

## 핵심 인사이트

- **포인트 1**: [핵심 교훈/주장]
- **포인트 2**: [실무 적용점]
- **포인트 3**: [추가 참고사항]

## 관련 링크

- [원문]({tweet_url})
- [스레드에서 언급된 링크들]
```

#### Article 본문 구조

`summarize-article` 스킬과 동일한 "요약 → 상세 → 결론" 구조를 적용합니다.

### Step 6: 저장

- 경로: `~/Documents/Obsidian Vault/notes/community-insights/twitter/{slugified-title}.md`
- 파일명: 핵심 주제를 소문자로, 공백은 `-`로, 특수문자 제거, 최대 60자

완료 메시지:
```
✅ Twitter 게시물이 Obsidian에 정리되었습니다:
   📁 ~/Documents/Obsidian Vault/notes/community-insights/twitter/{filename}.md
   👤 @{username}
   📝 {single|thread|article}
   ♥ {likes}
```

## 번역 규칙

- 전체 문서를 한국어로 작성
- 기술 용어는 첫 등장 시 원문 병기
- 코드 예시, CLI 명령어, URL, 해시태그는 원문 유지
- 트윗 특유의 축약/이모지 톤은 번역에서도 적절히 유지
- @멘션은 원문 유지

## 에러 처리

- **twitter-cli 미설치/미인증**: "Twitter CLI가 설정되어 있지 않습니다. Agent Reach로 설정해주세요." 출력
- **트윗 삭제/비공개**: "트윗에 접근할 수 없습니다" 메시지 출력
- **검색 결과 없음**: "검색 결과가 없습니다. 다른 키워드로 시도해주세요." 출력
