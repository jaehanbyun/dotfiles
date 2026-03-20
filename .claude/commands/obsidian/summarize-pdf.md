---
argument-hint: "[pdf파일경로] [챕터번호 또는 페이지범위(선택)]"
description: "기술 서적 PDF를 챕터별로 읽어 Obsidian 노트로 정리 (개별 노트 생성, 이미지/다이어그램 추출 포함)"
color: green
---

# PDF 기술 서적 정리 - $ARGUMENTS

기술 서적 PDF를 챕터 단위로 읽고, 이해하기 쉽게 정리하여 Obsidian 노트로 생성합니다.

## 인자 파싱

$ARGUMENTS에서 다음을 추출합니다:

- **PDF 파일 경로** (필수): PDF 파일의 절대 또는 상대 경로
- **챕터번호 또는 페이지 범위** (선택): 특정 챕터만 처리할 때 지정
  - 예: `3` → 3장만 처리
  - 예: `1-5` → 1~5장 처리
  - 예: `p.45-80` → 45~80페이지 처리
  - 미지정 시: 목차를 먼저 보여주고 사용자에게 선택 요청

## 작업 프로세스

### Phase 1: 책 구조 파악

1. **PDF 메타데이터 확인**
   - Read 도구로 PDF 첫 5페이지를 읽어 책 제목, 저자, 목차(Table of Contents) 파악
   - 목차가 없으면 전체를 훑어 챕터 구분 확인 (페이지 20개씩)

2. **책 정보를 사용자에게 보고**
   ```
   📖 책 제목: [제목]
   ✍️ 저자: [저자]
   📑 총 페이지: [페이지 수]
   📋 목차:
     Chapter 1: [제목] (p.1-25)
     Chapter 2: [제목] (p.26-52)
     ...
   ```

3. **처리 범위 확인**
   - 인자에 챕터/페이지 범위가 지정되어 있으면 해당 범위만 처리
   - 미지정 시 사용자에게 어떤 챕터를 처리할지 질문

### Phase 2: 챕터별 노트 생성

각 챕터에 대해 아래 과정을 반복합니다:

1. **PDF 읽기**
   - Read 도구로 해당 챕터의 페이지 범위를 읽기 (한 번에 최대 20페이지)
   - 20페이지 초과 시 분할하여 순차적으로 읽기

2. **이미지/다이어그램 추출**
   - PDF 내 다이어그램, 도표, 그림을 식별
   - 이미지가 포함된 페이지를 Read 도구로 읽어 시각적으로 확인
   - 중요한 다이어그램은 텍스트로 설명하고, 가능하면 Mermaid 다이어그램으로 재현
   - 원본 이미지가 추출 가능한 경우 ATTACHMENTS 폴더에 저장

3. **내용 정리 및 번역**
   - 아래 `## 문서 작성 규칙`에 따라 정리
   - `~/.claude/commands/obsidian/add-tag.md`의 태그 규칙 준수

4. **Obsidian 파일 저장**
   - 파일명: `[책제목] - Chapter [번호] [챕터제목].md`
   - 저장 경로: `~/Documents/Obsidian Vault/003-RESOURCES/`
   - ATTACHMENTS: `~/Documents/Obsidian Vault/ATTACHMENTS/`

### Phase 3: 책 인덱스 노트 생성

모든 챕터 처리 완료 후 (또는 첫 챕터 처리 시) 인덱스 노트를 생성/업데이트:

- 파일명: `[책제목] - Index.md`
- 각 챕터 노트로의 `[[링크]]` 포함
- 책 전체 개요 포함

## yaml frontmatter

### 챕터 노트용

```yaml
id: "[책 원제] - Chapter [번호] [챕터 원제]"
aliases: "[책 한글제목] - [번호]장 [챕터 한글제목]"
tags:
  - book/[책-이름-소문자]
  - book/[책-이름-소문자]/chapter-[번호]
  - [내용 기반 토픽 태그 3-4개]
author: [저자-소문자-하이픈]
created_at: [파일 생성 시점]
related: []
source: "book: [책 제목], ISBN: [있으면]"
chapter: [번호]
pages: "[시작]-[끝]"
```

### 인덱스 노트용

```yaml
id: "[책 원제]"
aliases: "[책 한글제목]"
tags:
  - book/[책-이름-소문자]
  - source/book
  - [주요 토픽 태그 3-4개]
author: [저자-소문자-하이픈]
created_at: [파일 생성 시점]
related: []
source: "book: [책 제목], ISBN: [있으면]"
```

## 문서 작성 규칙

```
You are a professional technical writer and software development expert. Your task is to read a chapter from a technical book and create a comprehensive, easy-to-understand Obsidian note in Korean.

CRITICAL ASSUMPTION: The reader has shallow knowledge of the topic. They are encountering these concepts for the first time or have only surface-level understanding. Every difficult term, concept, or pattern must be explained clearly with context.

Here is the chapter content:
<chapter_content>
{{CHAPTER_CONTENT}}
</chapter_content>

Writing requirements:

1. Translate and organize the content into Korean.
2. For technical terms and programming concepts, include the original English term in parentheses when first mentioned.
   - Include as many original terms as possible.
3. Use natural Korean expressions while maintaining technical accuracy.
4. Include all code examples from the original without omission.
5. Reproduce diagrams as Mermaid diagrams when possible; otherwise describe them in detail.

BEGINNER-FRIENDLY RULES (MANDATORY):

1. **Every difficult concept gets a plain-language explanation**:
   - When a term like "Dependency Injection" appears, don't just translate it.
   - Add a 1-2 sentence explanation in a callout box:
     > 💡 **의존성 주입 (Dependency Injection)이란?**
     > 객체가 필요로 하는 다른 객체(의존성)를 직접 생성하지 않고, 외부에서 전달받는 방식입니다.
     > 마치 레스토랑에서 재료를 직접 기르지 않고 납품업체로부터 받는 것과 비슷합니다.

2. **Analogy first, definition second**:
   - 복잡한 패턴이나 아키텍처를 설명할 때 일상적인 비유를 먼저 제시
   - 그 후에 정확한 기술적 정의를 제공

3. **"왜 중요한가?" 섹션 추가**:
   - 각 주요 개념 후에 "이것이 왜 중요한가?"를 1-2문장으로 설명
   - 실무에서 이 개념을 모르면 어떤 문제가 생기는지 간략히 언급

4. **코드 예시에는 반드시 주석 추가**:
   - 모든 코드 블록에 한국어 주석을 추가하여 각 줄이 무엇을 하는지 설명
   - 초보자가 코드만 보고도 흐름을 이해할 수 있도록

5. **전제 지식(prerequisite) 표시**:
   - 챕터 시작 부분에 이 챕터를 이해하기 위해 필요한 사전 지식 목록 제공
   - 이전 챕터와의 연관성 명시

Document structure:

## 1. 챕터 개요
- 이 챕터에서 다루는 내용을 2-3문장으로 요약
- 이 챕터를 읽고 나면 알게 되는 것들 (학습 목표) 목록

## 2. 사전 지식 (Prerequisites)
- 이 챕터를 이해하기 위해 알아야 할 개념들
- 이전 챕터와의 연결점

## 3. 핵심 내용 정리
- 원문의 구조를 따르되, 각 섹션별로 상세하게 정리
- 모든 코드 예시 포함 (한국어 주석 추가)
- 다이어그램 포함 (Mermaid 또는 텍스트 설명)
- 어려운 개념마다 💡 callout으로 쉬운 설명 추가

## 4. 핵심 용어 정리 (Glossary)
- 이 챕터에서 등장한 주요 용어를 표로 정리
- | 용어 (영문) | 한국어 | 쉬운 설명 |

## 5. 챕터 요약 및 핵심 포인트
- 이 챕터의 핵심 내용을 5-10개 문장으로 정리
- 실무에서 적용할 수 있는 takeaway 포함

## 6. 생각해볼 질문
- 이 챕터 내용을 기반으로 한 복습/심화 질문 3-5개
- 독자가 이해도를 스스로 점검할 수 있는 질문

Important considerations:
- The target audience is a Korean developer who wants to deeply understand the material
- They may not have strong English reading skills
- They value practical applicability over theoretical completeness
- Complex concepts should be broken down into digestible pieces
- Use tables, callouts, and visual formatting to improve readability

Constraints:
- Explicitly mark any uncertainties in the translation process
- Include all example codes without omission, with Korean comments added
- If diagrams exist in the original, reproduce as Mermaid or describe in detail
- Never skip content - translate and explain everything in the chapter
- Balance thoroughness with readability
```

## 사용 예시

### 기본 사용 (목차 확인 후 선택)

```
/obsidian:summarize-pdf ~/Downloads/clean-architecture.pdf
```

### 특정 챕터 처리

```
/obsidian:summarize-pdf ~/Downloads/clean-architecture.pdf 3
```

### 여러 챕터 범위 처리

```
/obsidian:summarize-pdf ~/Downloads/clean-architecture.pdf 1-5
```

### 특정 페이지 범위 처리

```
/obsidian:summarize-pdf ~/Downloads/clean-architecture.pdf p.45-80
```

## 작업 결과 형식

```
📖 처리 완료!

생성된 파일:
  📝 Clean Architecture - Index.md
  📝 Clean Architecture - Chapter 3 Design Principles.md

저장 위치: ~/Documents/Obsidian Vault/003-RESOURCES/
이미지: ~/Documents/Obsidian Vault/ATTACHMENTS/ (다이어그램 2개)

다음 챕터를 계속 처리하시겠습니까?
```

## 주의사항

1. **PDF 크기 제한**: Read 도구는 한 번에 최대 20페이지까지 읽을 수 있으므로, 긴 챕터는 분할 처리
2. **스캔본 PDF**: OCR이 필요한 스캔본은 텍스트 추출 품질이 떨어질 수 있음 → 사용자에게 알림
3. **이미지 추출**: PDF 내 이미지를 직접 파일로 추출하기 어려운 경우 Mermaid 다이어그램으로 재현
4. **저작권**: 책 내용을 개인 학습 목적으로만 정리. 요약본은 외부 공유 불가
5. **기존 노트 덮어쓰기 방지**: 동일 파일명이 존재하면 사용자에게 확인 후 처리
