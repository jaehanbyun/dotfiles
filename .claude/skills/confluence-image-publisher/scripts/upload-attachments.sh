#!/bin/bash
# Upload images to a Confluence page as attachments via REST API
# Usage: upload-attachments.sh <page_id> <cookie_value> <image_dir> [file_pattern]
#
# Arguments:
#   page_id      - Confluence page ID (e.g., 1228177436)
#   cookie_value - cloud.session.token value from Playwright browser context
#   image_dir    - Directory containing images to upload
#   file_pattern - Optional glob pattern (default: *.png)
#
# Example:
#   ./upload-attachments.sh 1228177436 "eyJra..." /tmp/screenshots "civo-*.png"

set -euo pipefail

PAGE_ID="${1:?Usage: $0 <page_id> <cookie> <image_dir> [pattern]}"
COOKIE="${2:?Cookie value required}"
IMAGE_DIR="${3:?Image directory required}"
PATTERN="${4:-*.png}"
BASE_URL="${CONFLUENCE_BASE_URL:-https://supergate.atlassian.net}"

if [ ! -d "$IMAGE_DIR" ]; then
  echo "ERROR: Directory $IMAGE_DIR does not exist"
  exit 1
fi

FILES=($(ls "$IMAGE_DIR"/$PATTERN 2>/dev/null))
if [ ${#FILES[@]} -eq 0 ]; then
  echo "ERROR: No files matching $PATTERN in $IMAGE_DIR"
  exit 1
fi

echo "Uploading ${#FILES[@]} files to page $PAGE_ID..."

FAILED=0
for f in "${FILES[@]}"; do
  (
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
      -X POST \
      -H "X-Atlassian-Token: nocheck" \
      -H "Cookie: cloud.session.token=$COOKIE" \
      -F "file=@$f" \
      "$BASE_URL/wiki/rest/api/content/$PAGE_ID/child/attachment")

    BASENAME=$(basename "$f")
    if [ "$STATUS" = "200" ]; then
      echo "  OK: $BASENAME"
    else
      echo "  FAIL ($STATUS): $BASENAME"
    fi
  ) &
done
wait

echo "Upload complete."
