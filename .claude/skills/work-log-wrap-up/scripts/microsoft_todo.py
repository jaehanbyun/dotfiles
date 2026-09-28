#!/usr/bin/env python3
"""Microsoft To Do helper for work-log routines.

Uses Microsoft Graph To Do APIs:
- GET/POST /me/todo/lists
- GET/POST /me/todo/lists/{todoTaskListId}/tasks
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any


HOME = Path.home()
TOKEN_CACHE = Path(os.environ.get("MS_TODO_TOKEN_CACHE", HOME / ".codex" / "microsoft-todo-token.json")).expanduser()
GRAPH_BASE = "https://graph.microsoft.com/v1.0"
DEFAULT_LIST_NAME = os.environ.get("MS_TODO_LIST_NAME", "Daily Focus")
DEFAULT_TIMEZONE = os.environ.get("MS_TODO_TIMEZONE", "Asia/Seoul")
DEFAULT_SCOPES = "Tasks.ReadWrite User.Read offline_access"


class TodoError(RuntimeError):
    pass


def request_json(url: str, *, method: str = "GET", token: str | None = None, data: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise TodoError(f"HTTP {exc.code}: {detail}") from exc
    if not raw:
        return {}
    return json.loads(raw)


def post_form(url: str, data: dict[str, str]) -> dict[str, Any]:
    body = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise TodoError(f"HTTP {exc.code}: {detail}") from exc
    return json.loads(raw)


def load_cache() -> dict[str, Any] | None:
    if not TOKEN_CACHE.exists():
        return None
    try:
        return json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def save_cache(data: dict[str, Any]) -> None:
    TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    data = dict(data)
    if "expires_in" in data:
        data["expires_at"] = int(time.time()) + int(data["expires_in"]) - 120
    TOKEN_CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    TOKEN_CACHE.chmod(stat.S_IRUSR | stat.S_IWUSR)


def tenant() -> str:
    return os.environ.get("MS_TODO_TENANT", "common")


def client_id() -> str | None:
    return os.environ.get("MS_TODO_CLIENT_ID")


def token_url() -> str:
    return f"https://login.microsoftonline.com/{tenant()}/oauth2/v2.0/token"


def device_code_url() -> str:
    return f"https://login.microsoftonline.com/{tenant()}/oauth2/v2.0/devicecode"


def refresh_token(cache: dict[str, Any]) -> dict[str, Any]:
    cid = client_id() or cache.get("client_id")
    refresh = cache.get("refresh_token")
    if not cid or not refresh:
        raise TodoError("No refresh token. Run `microsoft_todo.py login` after setting MS_TODO_CLIENT_ID.")
    token = post_form(
        token_url(),
        {
            "client_id": cid,
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "scope": cache.get("scope") or DEFAULT_SCOPES,
        },
    )
    token["client_id"] = cid
    save_cache(token)
    return token


def access_token() -> str:
    env_token = os.environ.get("MS_TODO_ACCESS_TOKEN")
    if env_token:
        return env_token
    cache = load_cache()
    if not cache:
        raise TodoError("Microsoft To Do auth is not configured. Set MS_TODO_ACCESS_TOKEN or run login with MS_TODO_CLIENT_ID.")
    if int(cache.get("expires_at", 0)) <= int(time.time()):
        cache = refresh_token(cache)
    token = cache.get("access_token")
    if not token:
        raise TodoError("Token cache has no access_token. Run login again.")
    return token


def login() -> None:
    cid = client_id()
    if not cid:
        raise TodoError("Set MS_TODO_CLIENT_ID first. It must be an Azure app registration public-client id with delegated Tasks.ReadWrite permission.")
    device = post_form(device_code_url(), {"client_id": cid, "scope": DEFAULT_SCOPES})
    print(device.get("message") or f"Open {device['verification_uri']} and enter {device['user_code']}")
    interval = int(device.get("interval", 5))
    expires_at = time.time() + int(device.get("expires_in", 900))
    while time.time() < expires_at:
        time.sleep(interval)
        try:
            token = post_form(
                token_url(),
                {
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "client_id": cid,
                    "device_code": device["device_code"],
                },
            )
        except TodoError as exc:
            text = str(exc)
            if "authorization_pending" in text:
                continue
            if "slow_down" in text:
                interval += 5
                continue
            raise
        token["client_id"] = cid
        token["scope"] = DEFAULT_SCOPES
        save_cache(token)
        print(f"Saved token cache: {TOKEN_CACHE}")
        return
    raise TodoError("Device-code login expired.")


def graph_get(path: str) -> dict[str, Any]:
    return request_json(f"{GRAPH_BASE}{path}", token=access_token())


def graph_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    return request_json(f"{GRAPH_BASE}{path}", method="POST", token=access_token(), data=payload)


def list_task_lists() -> list[dict[str, Any]]:
    lists: list[dict[str, Any]] = []
    path = "/me/todo/lists"
    while path:
        data = graph_get(path)
        lists.extend(data.get("value", []))
        next_link = data.get("@odata.nextLink")
        path = next_link.replace(GRAPH_BASE, "") if next_link else ""
    return lists


def ensure_list(name: str) -> dict[str, Any]:
    for item in list_task_lists():
        if item.get("displayName") == name:
            return item
    return graph_post("/me/todo/lists", {"displayName": name})


def list_tasks(list_id: str) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    path = f"/me/todo/lists/{urllib.parse.quote(list_id, safe='')}/tasks?$top=100"
    while path:
        data = graph_get(path)
        tasks.extend(data.get("value", []))
        next_link = data.get("@odata.nextLink")
        path = next_link.replace(GRAPH_BASE, "") if next_link else ""
    return tasks


def create_task(list_id: str, title: str, due: str, source: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": title,
        "dueDateTime": {
            "dateTime": f"{due}T23:59:00",
            "timeZone": DEFAULT_TIMEZONE,
        },
    }
    if source:
        payload["body"] = {
            "contentType": "text",
            "content": f"Created by Codex work-log routine.\nSource: {source}",
        }
    return graph_post(f"/me/todo/lists/{urllib.parse.quote(list_id, safe='')}/tasks", payload)


def clean_task_title(text: str) -> str:
    text = re.sub(r"\[\[([^|\]]+\|)?([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"^\s*(P[0-9]\s*\([^)]+\)|P[0-9]|Action Items?:?)\s*[-:]\s*", "", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" -:")
    return text


def extract_tasks_from_markdown(markdown: str, limit: int) -> list[str]:
    wanted_heading = re.compile(r"(다음|할 일|Action Items?|Next Actions?|Carry-over|미완료|계획|TODO)", re.I)
    ignored_heading = re.compile(r"(Daily Notes|학습 기록|기술|작업 내역|Vault|Codex|미팅)", re.I)
    in_wanted_section = False
    tasks: list[str] = []

    for line in markdown.splitlines():
        heading = re.match(r"^\s{0,3}#{1,4}\s+(.+?)\s*$", line)
        if heading:
            title = heading.group(1)
            in_wanted_section = bool(wanted_heading.search(title)) and not bool(ignored_heading.search(title))
            continue

        section_bullet = re.match(r"^\s*[-*]\s+(.+?:)\s*$", line)
        if section_bullet:
            title = section_bullet.group(1)
            if wanted_heading.search(title):
                in_wanted_section = True
                continue

        checkbox = re.match(r"^\s*[-*]\s+\[\s?\]\s+(.+)$", line)
        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        numbered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        candidate = None
        if checkbox:
            candidate = checkbox.group(1)
        elif in_wanted_section and bullet:
            candidate = bullet.group(1)
        elif in_wanted_section and numbered:
            candidate = numbered.group(1)

        if not candidate:
            continue
        title = clean_task_title(candidate)
        if not title or title.lower() in {"없음", "none"}:
            continue
        if len(title) > 180:
            title = title[:177].rstrip() + "..."
        if title not in tasks:
            tasks.append(title)
        if len(tasks) >= limit:
            break
    return tasks


def read_tasks_file(path: Path) -> list[str]:
    tasks = []
    for line in path.read_text(encoding="utf-8").splitlines():
        title = clean_task_title(line)
        if title:
            tasks.append(title)
    return tasks


def create_tasks(titles: list[str], list_name: str, due: str, source: str | None, dry_run: bool) -> None:
    if not titles:
        print("No task candidates.")
        return
    if dry_run:
        for title in titles:
            print(f"- {title}")
        return

    todo_list = ensure_list(list_name)
    list_id = todo_list["id"]
    existing = {task.get("title") for task in list_tasks(list_id) if task.get("status") != "completed"}
    created = 0
    skipped = 0
    for title in titles:
        if title in existing:
            skipped += 1
            continue
        create_task(list_id, title, due, source)
        created += 1
    print(f"Created {created} task(s) in Microsoft To Do list `{list_name}` for {due}. Skipped duplicates: {skipped}.")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("login")
    sub.add_parser("status")
    sub.add_parser("lists")

    suggest = sub.add_parser("suggest-from-worklog")
    suggest.add_argument("worklog")
    suggest.add_argument("--limit", type=int, default=5)

    create = sub.add_parser("create-from-worklog")
    create.add_argument("worklog")
    create.add_argument("--limit", type=int, default=5)
    create.add_argument("--list", default=DEFAULT_LIST_NAME)
    create.add_argument("--due", default=date.today().isoformat())
    create.add_argument("--dry-run", action="store_true")

    create_file = sub.add_parser("create-from-file")
    create_file.add_argument("tasks_file")
    create_file.add_argument("--list", default=DEFAULT_LIST_NAME)
    create_file.add_argument("--due", default=date.today().isoformat())
    create_file.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "login":
            login()
        elif args.command == "status":
            try:
                me = graph_get("/me?$select=displayName,userPrincipalName")
            except TodoError as exc:
                print(f"not configured: {exc}")
                return 1
            print(f"ok: {me.get('displayName') or ''} {me.get('userPrincipalName') or ''}".strip())
        elif args.command == "lists":
            for item in list_task_lists():
                print(f"{item.get('displayName')}\t{item.get('id')}")
        elif args.command == "suggest-from-worklog":
            text = Path(args.worklog).expanduser().read_text(encoding="utf-8")
            for title in extract_tasks_from_markdown(text, args.limit):
                print(f"- {title}")
        elif args.command == "create-from-worklog":
            worklog = Path(args.worklog).expanduser()
            text = worklog.read_text(encoding="utf-8")
            titles = extract_tasks_from_markdown(text, args.limit)
            create_tasks(titles, args.list, args.due, str(worklog), args.dry_run)
        elif args.command == "create-from-file":
            tasks_file = Path(args.tasks_file).expanduser()
            create_tasks(read_tasks_file(tasks_file), args.list, args.due, str(tasks_file), args.dry_run)
    except TodoError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
