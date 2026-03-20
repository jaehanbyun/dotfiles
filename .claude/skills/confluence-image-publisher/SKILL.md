---
name: confluence-image-publisher
description: This skill should be used when the user wants to publish content with images to Confluence. It handles the complete workflow of creating a Confluence page, uploading image attachments via REST API, and embedding them using Confluence storage format. Triggers on requests involving Confluence page creation with screenshots, diagrams, or any image attachments.
---

# Confluence Image Publisher

## Overview

Publish content with embedded images to Confluence Cloud. The Atlassian MCP tools lack attachment upload capability, so this skill provides a 5-phase workflow combining MCP page creation, Playwright cookie extraction, curl-based parallel upload, and REST API page update with Confluence storage format.

## Prerequisites

- Atlassian MCP configured and authenticated
- Playwright MCP available for browser automation
- `curl` available in shell
- User logged into Confluence in a browser accessible by Playwright

## Workflow

### Phase 1: Create Page via Atlassian MCP (Text Only)

Use `mcp__atlassian__createConfluencePage` or `mcp__claude_ai_Atlassian__createConfluencePage` to create the initial page with text-only content (no images yet).

- Identify the target space key and parent page ID
- Convert source content (Obsidian markdown, etc.) to Confluence-compatible markdown
- Omit all image references in this phase — images are added in Phase 5
- Record the created page ID for subsequent phases

### Phase 2: Login to Confluence via Playwright

Open the Confluence page in a Playwright browser tab to establish an authenticated session.

```
Navigate to: https://<site>.atlassian.net/wiki/spaces/<SPACE>/pages/<PAGE_ID>
```

If not already logged in, the user may need to authenticate manually in the browser.

### Phase 3: Extract Authentication Cookie

Extract the `cloud.session.token` cookie from the Playwright browser context:

```javascript
// via mcp__playwright__browser_evaluate or browser_run_code
const cookies = await page.context().cookies();
const token = cookies.find(c => c.name === 'cloud.session.token');
return token?.value;
```

This cookie is HttpOnly and cannot be accessed via `document.cookie` — it must be extracted from the browser context API.

### Phase 4: Upload Images via REST API

Run `scripts/upload-attachments.sh` to upload images in parallel:

```bash
bash scripts/upload-attachments.sh <page_id> "<cookie_value>" <image_dir> [file_pattern]
```

Arguments:
- `page_id` — Confluence page ID from Phase 1
- `cookie_value` — `cloud.session.token` value from Phase 3
- `image_dir` — Directory containing images to upload
- `file_pattern` — Optional glob pattern (default: `*.png`)

The script uploads all matching files in parallel using `curl` with the Confluence REST API v1 attachment endpoint.

To use a different Confluence site, set `CONFLUENCE_BASE_URL` environment variable (default: `https://supergate.atlassian.net`).

### Phase 5: Update Page with Embedded Images

Update the page body to embed uploaded attachments using **Confluence storage format** via REST API v1.

#### Image Embedding Syntax

Use Confluence storage format `<ac:image>` tags — **NOT** markdown `![]()`  syntax:

```xml
<ac:image ac:width="800"><ri:attachment ri:filename="screenshot.png" /></ac:image>
```

Markdown `![alt](filename)` creates external URL references ("외부 미디어 파일"), not attachment references. This is the most common pitfall.

#### Page Update via REST API v1

```bash
curl -X PUT \
  -H "Content-Type: application/json" \
  -H "X-Atlassian-Token: nocheck" \
  -H "Cookie: cloud.session.token=<cookie>" \
  -d @body.json \
  "https://<site>.atlassian.net/wiki/rest/api/content/<page_id>"
```

The JSON body **must** include `"type": "page"`:

```json
{
  "id": "<page_id>",
  "type": "page",
  "title": "Page Title",
  "body": {
    "storage": {
      "value": "<p>Text content</p><ac:image ac:width=\"800\"><ri:attachment ri:filename=\"image.png\" /></ac:image>",
      "representation": "storage"
    }
  },
  "version": {
    "number": <current_version + 1>
  }
}
```

To get the current version number before updating:

```bash
curl -s -H "Cookie: cloud.session.token=<cookie>" \
  "https://<site>.atlassian.net/wiki/rest/api/content/<page_id>?expand=version" \
  | jq '.version.number'
```

## Critical Pitfalls

1. **Markdown images do NOT reference attachments**: `![alt](file.png)` in Confluence becomes an external URL `<img src="file.png">`, not an attachment reference. Always use `<ac:image><ri:attachment ri:filename="..." /></ac:image>`.

2. **Missing `"type": "page"` in update body**: REST API v1 PUT returns 400 "Type is required" if `"type": "page"` is omitted from the JSON body.

3. **MCP tools cannot upload attachments**: Neither `mcp__atlassian__` nor `mcp__claude_ai_Atlassian__` tools support file attachment upload. The curl + cookie approach is required.

4. **Cookie is HttpOnly**: `cloud.session.token` cannot be read via `document.cookie` in JavaScript. It must be extracted from `page.context().cookies()` via Playwright's browser context API.

5. **Version number must increment**: Each page update requires `version.number` to be exactly `current + 1`. Fetch the current version before updating.

## Resources

### scripts/

- `upload-attachments.sh` — Parallel image upload to Confluence via REST API. Takes page ID, cookie, image directory, and optional file pattern as arguments.
