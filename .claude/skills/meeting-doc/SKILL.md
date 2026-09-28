---
name: meeting-doc
description: Create or update concise Korean Confluence meeting documents for jh.byun's Monday/Thursday meeting workflow. Use when the user asks to make a meeting doc, prepare material for a meeting, summarize information for confirmation, collect opinions in a meeting, or add content to the next Mon/Thu meeting document.
---

# Meeting Doc

## Purpose

Prepare short Confluence meeting documents that let the user share minimal context, ask for opinions, and capture decisions quickly.

Default target:

- Cloud: `https://supergate.atlassian.net`
- Cloud ID: `eae1b0fb-feef-4cf8-8e60-d062125bf0c2`
- Space name: `jh.byun`
- Space key: `~71202041a179cedefb4b7e88259f404bb3b743`
- Numeric space ID: `1040384418`
- Meeting parent page: `회의`
- Parent page ID: `1353842786`
- Parent page URL: `https://supergate.atlassian.net/wiki/spaces/~71202041a179cedefb4b7e88259f404bb3b743/pages/1353842786`

## Date Selection

Use Asia/Seoul dates.

1. If the user gives an explicit date, use it.
2. If the user explicitly says "오늘", use today's date even when today is Monday or Thursday.
3. Otherwise choose the nearest future Monday or Thursday. Do not choose today by default.
4. If the user says only "월요일" or "목요일", choose the nearest future occurrence of that weekday.
5. Format document titles as `YYYY-MM-DD - <주제>`.

Example from Tuesday `2026-06-16`:

- No date given -> `2026-06-18`
- "목요일 회의" -> `2026-06-18`
- "다음 월요일" -> `2026-06-22`
- "오늘 회의" -> `2026-06-16`

## Topic Selection

Infer a concise topic from the user's request.

- Good: `OpenStack Ops Docs 문서화 도구 선정`
- Good: `Kolla-Ansible 네트워크 설계 리뷰`
- Avoid: `회의`, `문서`, `공유 자료`

If the topic is unclear and a write operation would create a vague page title, ask one short question for the topic. If the user asks only for a draft in chat, use a reasonable topic and label it as editable.

## Confluence Workflow

Use Atlassian Rovo/Confluence tools when available.

1. Confirm the target parent page if needed:
   - page ID `1353842786`
   - title `회의`
   - space ID `1040384418`
2. Build the target title: `YYYY-MM-DD - <주제>`.
3. Search under the `회의` parent page for an existing page with the exact title.
   - Prefer descendant lookup by parent page ID if available.
   - CQL fallback: `space = "~71202041a179cedefb4b7e88259f404bb3b743" AND type = page AND title = "<title>"`
4. If exactly one matching page exists, update it.
5. If none exists, create a new page under parent ID `1353842786` in space ID `1040384418`.
6. If multiple plausible pages exist, ask which page to update.
7. If Confluence tools are unavailable, auth fails, or the target location is not confirmed, do not create a page. Return a paste-ready Markdown draft instead.

When updating an existing page:

- Preserve existing `회의 중 결정 사항` and `액션 아이템` unless the user explicitly asks to replace them.
- Add new information into the matching section when possible.
- Keep the first screen short; move detailed notes into `참고: 세부 조사 내용`.

## Document Style

Write in Korean. Optimize for a meeting where the user briefly provides information and asks for feedback.

Required style:

- Start with `1분 요약`.
- Put `오늘 의견 받고 싶은 사항` near the top.
- State the recommendation early if there is one.
- Limit choices to 2-3 options unless the user asks for a broader comparison.
- Use checklist-like bullets for questions attendees should answer.
- Put long background, research notes, source links, and implementation details under `참고: 세부 조사 내용`.
- Keep the document useful before the meeting and editable during the meeting.

Avoid:

- Long narrative introductions.
- Hiding the recommendation until the end.
- Creating a generic "meeting notes" page with no decision points.
- Writing a large report when the user needs a short confirmation document.

## Template

Use this structure for new pages:

```markdown
# YYYY-MM-DD - <주제>

## 1분 요약

<회의 시작 시 1분 안에 읽을 수 있는 요약. 추천안이 있으면 여기서 먼저 말한다.>

## 오늘 의견 받고 싶은 사항

* <참석자에게 확인받을 질문 1>
* <참석자에게 확인받을 질문 2>
* <결정이 필요한 항목>

## 선택지 / 제안안

| 선택지 | 요약 | 의견이 필요한 지점 |
|---|---|---|
| A |  |  |
| B |  |  |

## 참고 화면 또는 자료

<스크린샷 삽입 위치, 링크, 짧은 설명>

## 회의 중 결정 사항

회의 중 업데이트 예정.

## 액션 아이템

회의 후 업데이트 예정.

## 참고: 세부 조사 내용

<배경, 조사 내용, 출처, 구현 세부사항>
```

Remove unused table rows or sections if they add noise.

## Examples

User: "OpenStack 문서화 도구 선정 관련해서 다음 회의 때 의견 받을 문서 만들어줘"

Action:

- Choose the nearest future Monday/Thursday.
- Create or update `YYYY-MM-DD - OpenStack 문서화 도구 선정`.
- Put the recommendation and decision questions at the top.

User: "목요일 회의에서 공유할 Kolla-Ansible 네트워크 설계 초안 만들어줘"

Action:

- Choose the nearest future Thursday unless an explicit date is present.
- Create or update `YYYY-MM-DD - Kolla-Ansible 네트워크 설계 리뷰`.

User: "다음 월/목 회의 문서에 이 내용 추가해줘"

Action:

- Choose the nearest future Monday/Thursday.
- Find the most relevant existing page for that date.
- If no relevant page exists and the topic is clear, create it.
- If topic is unclear, ask one short question before writing.
