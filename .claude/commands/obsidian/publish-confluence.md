---
argument-hint: "[문서이름] [space_key(선택)] [parent_page_id(선택)]"
description: "Obsidian 문서를 Confluence에 발행 (Mermaid 다이어그램/이미지 포함)"
allowed-tools: playwright, mcp__atlassian__, mcp__claude_ai_Atlassian__, mcp__playwright__
color: blue
---

# Obsidian → Confluence 발행 - $ARGUMENTS

Obsidian 문서를 읽어 Confluence 페이지로 발행합니다. Mermaid 다이어그램은 이미지로 변환하고, 로컬/외부 이미지도 모두 첨부파일로 업로드합니다.

## 인자 파싱

$ARGUMENTS에서 다음을 추출합니다:

- **문서이름** (필수): Obsidian vault 내 문서명 (확장자 생략 가능)
- **space_key** (선택): Confluence space key
- **parent_page_id** (선택): 부모 페이지 ID

미지정 인자는 사용자에게 질문하여 입력받습니다.

## 사전 준비

- Obsidian Vault 경로: `~/Documents/Obsidian Vault`
- ATTACHMENTS 경로: `~/Documents/Obsidian Vault/notes/ATTACHMENTS`
- 임시 이미지 디렉토리: `/tmp/confluence-publish-<timestamp>/`

## 작업 프로세스

### Phase 1: 문서 읽기 및 파싱

1. **문서 찾기**
   - vault 내에서 문서이름으로 검색 (Glob 사용)
   - 확장자 없이 입력된 경우 `.md` 자동 추가
   - 여러 개 매칭되면 목록을 보여주고 사용자에게 선택 요청

2. **문서 읽기**
   - Read 도구로 파일 내용 전체 읽기
   - YAML frontmatter 파싱 (title, tags 등 메타데이터 활용)

3. **미지정 인자 질문**
   - space_key가 없으면: "어떤 Confluence Space에 발행할까요? (예: DEV, TEAM)" 질문
   - parent_page_id가 없으면: "부모 페이지 ID를 지정할까요? (미지정 시 Space 루트에 생성)" 질문

### Phase 2: 이미지 리소스 수집

임시 디렉토리를 생성하고 모든 이미지를 한 곳에 모읍니다:

```bash
WORK_DIR="/tmp/confluence-publish-$(date +%s)"
mkdir -p "$WORK_DIR/images"
```

1. **Mermaid 다이어그램 추출 및 변환**
   - 문서에서 모든 ` ```mermaid ... ``` ` 블록을 추출
   - 각 블록을 임시 `.mmd` 파일로 저장
   - `mmdc`로 PNG 변환:
     ```bash
     mmdc -i block_1.mmd -o "$WORK_DIR/images/mermaid-1.png" -t neutral -b transparent -w 1200
     ```
   - 문서 내 Mermaid 블록 위치를 기록 (나중에 `<ac:image>` 태그로 교체)

2. **wiki-link 로컬 이미지 수집**
   - `![[파일명.png]]` 또는 `![[ATTACHMENTS/파일명.png]]` 패턴 추출
   - vault 내 ATTACHMENTS 폴더에서 파일을 찾아 `$WORK_DIR/images/`에 복사
   - 파일을 못 찾으면 사용자에게 경고

3. **외부 이미지 다운로드**
   - `![alt](https://...)` 패턴 추출
   - curl로 다운로드하여 `$WORK_DIR/images/`에 저장:
     ```bash
     curl -sL "https://i.imgur.com/xxx.png" -o "$WORK_DIR/images/external-1.png"
     ```
   - 다운로드 실패 시 사용자에게 경고하고 해당 이미지는 건너뜀

### Phase 3: 마크다운 → Confluence 변환

문서 본문을 Confluence storage format으로 변환합니다:

1. **frontmatter 제거** — YAML 블록은 Confluence 본문에 포함하지 않음

2. **이미지 참조 변환**
   - Mermaid 블록 → `<ac:image ac:width="800"><ri:attachment ri:filename="mermaid-1.png" /></ac:image>`
   - `![[file.png]]` → `<ac:image ac:width="800"><ri:attachment ri:filename="file.png" /></ac:image>`
   - `![alt](external-url)` → `<ac:image ac:width="800"><ri:attachment ri:filename="external-1.png" /></ac:image>`

3. **내부 링크 변환**
   - `[[문서명]]` → 일반 텍스트로 변환 (굵게 표시): `<strong>문서명</strong>`

4. **마크다운 → HTML 기본 변환**
   - 헤딩: `## 제목` → `<h2>제목</h2>`
   - 볼드/이탤릭: `**bold**` → `<strong>bold</strong>`, `*italic*` → `<em>italic</em>`
   - 코드 블록: ` ```lang ... ``` ` → `<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">lang</ac:parameter><ac:plain-text-body><![CDATA[...]]></ac:plain-text-body></ac:structured-macro>`
   - 인라인 코드: `` `code` `` → `<code>code</code>`
   - 리스트: `- item` → `<ul><li>item</li></ul>`
   - 테이블: 마크다운 테이블 → `<table>` HTML
   - callout/blockquote: `> text` → `<blockquote><p>text</p></blockquote>`
   - 수평선: `---` → `<hr />`

### Phase 4: Confluence 페이지 생성 (텍스트만)

Atlassian MCP로 페이지를 생성합니다. 이 단계에서는 이미지 placeholder만 포함합니다.

1. **페이지 제목 결정**
   - frontmatter의 `aliases` 또는 `id` 사용
   - 없으면 파일명에서 추출

2. **페이지 생성**
   ```
   mcp__claude_ai_Atlassian__createConfluencePage(
     spaceKey: <space_key>,
     title: <페이지 제목>,
     parentPageId: <parent_page_id 또는 미지정>,
     content: <Phase 3에서 변환된 본문 (이미지 태그 포함)>
   )
   ```

3. **생성된 page_id 기록**

### Phase 5: 이미지 업로드 (confluence-image-publisher 활용)

`~/.claude/skills/confluence-image-publisher/SKILL.md`의 Phase 2~4 워크플로우를 따릅니다:

1. **Playwright로 Confluence 페이지 접속**
   ```
   Navigate to: https://supergate.atlassian.net/wiki/spaces/<SPACE>/pages/<PAGE_ID>
   ```

2. **cloud.session.token 쿠키 추출**
   ```javascript
   // Playwright browser context에서 추출
   const cookies = await page.context().cookies();
   const token = cookies.find(c => c.name === 'cloud.session.token');
   return token?.value;
   ```

3. **이미지 업로드**
   ```bash
   bash ~/.claude/skills/confluence-image-publisher/scripts/upload-attachments.sh \
     <page_id> "<cookie_value>" "$WORK_DIR/images" "*.*"
   ```

### Phase 6: 마무리

1. **업로드 결과 확인**
   - 페이지 URL을 사용자에게 보고:
     ```
     Confluence 발행 완료!

     페이지: https://supergate.atlassian.net/wiki/spaces/<SPACE>/pages/<PAGE_ID>
     업로드된 이미지: <N>개
       - mermaid-1.png (Mermaid 다이어그램)
       - screenshot.png (로컬 이미지)
       - external-1.png (외부 이미지)
     ```

2. **Obsidian frontmatter 업데이트**
   - 원본 문서의 frontmatter에 `confluence:` 필드 추가/업데이트:
     ```yaml
     confluence: "https://supergate.atlassian.net/wiki/spaces/<SPACE>/pages/<PAGE_ID>"
     ```

3. **임시 파일 정리**
   ```bash
   rm -rf "$WORK_DIR"
   ```

## 주의사항

1. **Mermaid 렌더링**: `mmdc`가 필요합니다. 미설치 시 `npm install -g @mermaid-js/mermaid-cli`
2. **인증**: Confluence 로그인 세션이 Playwright 브라우저에 있어야 합니다. 없으면 수동 로그인 필요
3. **이미지 크기**: `ac:width="800"` 기본값. 필요 시 조정
4. **중복 발행 방지**: frontmatter에 `confluence:` URL이 이미 있으면 사용자에게 "이미 발행된 문서입니다. 업데이트할까요?" 확인
5. **마크다운 변환 한계**: 복잡한 Obsidian 플러그인 문법(dataview, tasks 등)은 변환하지 않고 원문 그대로 포함

## 사용 예시

### 기본 사용 (space/parent 질문)

```
/obsidian:publish-confluence "Clean Architecture - Chapter 3"
```

### space와 부모 페이지 지정

```
/obsidian:publish-confluence "API 설계 가이드" DEV 1228177436
```
