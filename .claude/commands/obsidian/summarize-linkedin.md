---
argument-hint: "[linkedin-url]"
description: "LinkedIn 게시물/아티클 URL을 입력받아 번역, 정리해서 Obsidian 문서로 저장"
color: cyan
---

# LinkedIn to Obsidian - $ARGUMENTS

LinkedIn 게시물 또는 아티클을 번역/정리해서 Obsidian 문서를 생성합니다.

$ARGUMENTS가 제공되지 않은 경우, 사용법을 표시합니다:
```
/obsidian:summarize-linkedin https://www.linkedin.com/posts/username_topic-activity-123456789/
/obsidian:summarize-linkedin https://www.linkedin.com/pulse/article-title-author/
```

## 경로 정보

| 항목 | 경로 |
|------|------|
| vault | `~/Documents/Obsidian Vault/` |
| 저장 위치 | `~/Documents/Obsidian Vault/notes/community-insights/linkedin/` |

## 작업 프로세스

### Step 1: URL 타입 판별

```bash
INPUT="$ARGUMENTS"
if [[ "$INPUT" == *"/pulse/"* ]] || [[ "$INPUT" == *"/article/"* ]]; then
    echo "TYPE=article"
elif [[ "$INPUT" == *"/posts/"* ]] || [[ "$INPUT" == *"/feed/"* ]]; then
    echo "TYPE=post"
else
    echo "TYPE=unknown"
fi
```

### Step 2: 콘텐츠 수집

LinkedIn 콘텐츠는 Jina Reader로 읽습니다:

```bash
curl -s "https://r.jina.ai/$INPUT"
```

Jina Reader가 충분한 콘텐츠를 가져오지 못하는 경우, linkedin-scraper MCP가 설정되어 있으면 fallback:

```bash
mcporter call 'linkedin-scraper.get_person_profile(linkedin_url: "URL")'
```

### Step 3: 중복 체크

```bash
grep -rl "source: $INPUT" ~/Documents/Obsidian\ Vault/notes/community-insights/linkedin/ 2>/dev/null
```

### Step 4: 문서 생성

```bash
mkdir -p ~/Documents/Obsidian\ Vault/notes/community-insights/linkedin
```

#### yaml frontmatter 형식

```yaml
---
id: "{게시물/아티클 제목 또는 첫 줄 (원문, 최대 80자)}"
aliases:
  - "{한국어 번역}"
tags:
  - community/linkedin
  - {내용 기반 기술/도메인 태그}
author: "{작성자 이름}"
post_type: "{post|article}"
created_at: "{현재 YYYY-MM-DD HH:mm}"
source: "{linkedin_url}"
related: []
---
```

- id: 아티클 제목 또는 게시물 첫 줄 (원문)
- aliases: 한국어 번역
- author: 작성자 이름 (소문자, 공백은 `-`로)
- post_type: post / article
- tags: 최대 6개, 반드시 `community/linkedin` 포함

#### 게시물(post) 본문 구조

```markdown
# {핵심 내용 한국어 요약}

> 원문: [{게시물 첫 줄}]({linkedin_url})
> 작성자: {author_name} | {author_title}

## 번역

[게시물 전문 한국어 번역]
[이미지나 슬라이드 내용이 있으면 텍스트로 설명]

## 핵심 포인트

- **포인트 1**: [핵심 주장/교훈]
- **포인트 2**: [실무 적용점]
- **포인트 3**: [추가 맥락]

## 관련 링크

- [원문]({linkedin_url})
- [게시물에서 언급된 링크들]
```

#### 아티클(article) 본문 구조

아티클은 `summarize-article` 스킬과 동일한 상세 구조를 적용합니다:

```markdown
# {아티클 제목 한국어 번역}

> 원문: [{아티클 제목}]({linkedin_url})
> 작성자: {author_name} | {author_title}

## 1. 하이라이트/요약

[전체 내용을 2-3 문단으로 요약]

## 2. 상세 요약

[섹션별로 나누어 각 2-3 문단으로 상세 요약]

### 2.1 {섹션 제목}
[번역 및 요약]

### 2.2 {섹션 제목}
[번역 및 요약]

## 3. 결론 및 시사점

- [전체 내용 5-10개 문장으로 정리]
- [이 정보가 중요한 이유]

## 관련 링크

- [원문]({linkedin_url})
- [아티클에서 언급된 참고 자료]
```

### Step 5: 저장

- 경로: `~/Documents/Obsidian Vault/notes/community-insights/linkedin/{slugified-title}.md`
- 파일명: 핵심 주제를 소문자로, 공백은 `-`로, 특수문자 제거, 최대 60자

완료 메시지:
```
✅ LinkedIn 게시물이 Obsidian에 정리되었습니다:
   📁 ~/Documents/Obsidian Vault/notes/community-insights/linkedin/{filename}.md
   👤 {author_name}
   📝 {post|article}
```

## 번역 규칙

- 전체 문서를 한국어로 작성
- 기술 용어는 첫 등장 시 원문 병기: "의존성 주입(Dependency Injection)"
- 코드 예시, CLI 명령어, URL은 원문 유지
- LinkedIn 특유의 비즈니스/리더십 용어도 원문 병기: "심리적 안전감(Psychological Safety)"

## 에러 처리

- **Jina Reader 실패**: "LinkedIn 콘텐츠를 가져올 수 없습니다. URL을 확인해주세요." 출력
- **로그인 필요 콘텐츠**: "이 콘텐츠는 로그인이 필요합니다. linkedin-scraper-mcp 설정을 확인해주세요." 출력
- **빈 콘텐츠**: Jina Reader가 빈 결과를 반환하면 playwright tool로 재시도
