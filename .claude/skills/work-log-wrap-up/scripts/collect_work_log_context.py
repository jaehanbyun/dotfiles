#!/usr/bin/env python3
"""Collect source context for Codex-centered work logs."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None


TZ_NAME = os.environ.get("WORK_LOG_TZ", "Asia/Seoul")
TZ = ZoneInfo(TZ_NAME) if ZoneInfo else timezone(timedelta(hours=9))
HOME = Path.home()
VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", HOME / "Documents/Obsidian Vault")).expanduser()
WORK_LOG_VAULT_ROOT = Path(
    os.environ.get("WORK_LOG_VAULT_ROOT", HOME / "Documents/work-logs")
).expanduser()
CODEX_HOME = Path(os.environ.get("CODEX_HOME", HOME / ".codex")).expanduser()


@dataclass
class MarkdownDoc:
    path: str
    modified: str
    created: str | None
    title: str
    headings: list[str]
    excerpt: str


@dataclass
class CodexSession:
    session_id: str
    thread_name: str
    cwd: str
    started_at: str
    updated_at: str
    file: str
    user_messages: list[str]
    assistant_messages: list[str]


def parse_day(value: str | None) -> date:
    if value:
        return date.fromisoformat(value)
    return datetime.now(TZ).date() - timedelta(days=1)


def previous_month() -> str:
    today = datetime.now(TZ).date()
    first = today.replace(day=1)
    last_prev = first - timedelta(days=1)
    return f"{last_prev.year:04d}-{last_prev.month:02d}"


def parse_month(value: str | None) -> tuple[int, int]:
    value = value or previous_month()
    if not re.fullmatch(r"\d{4}-\d{2}", value):
        raise SystemExit(f"Invalid month: {value}. Expected YYYY-MM.")
    return int(value[:4]), int(value[5:7])


def parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        seconds = value / 1000 if value > 10_000_000_000 else value
        return datetime.fromtimestamp(seconds, timezone.utc).astimezone(TZ)
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)
    return dt.astimezone(TZ)


def dt_day(value: Any) -> date | None:
    dt = parse_dt(value)
    return dt.date() if dt else None


def iso_local(value: Any) -> str:
    dt = parse_dt(value)
    return dt.isoformat(timespec="seconds") if dt else ""


def truncate(text: str, limit: int = 700) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def strip_frontmatter(text: str) -> str:
    return re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, flags=re.S)


def summarize_markdown(path: Path, excerpt_chars: int = 1200) -> MarkdownDoc | None:
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        stat = path.stat()
    except OSError:
        return None

    body = strip_frontmatter(raw)
    title = path.stem
    first_h1 = re.search(r"^#\s+(.+)$", body, flags=re.M)
    if first_h1:
        title = first_h1.group(1).strip()
    headings = [h.strip() for h in re.findall(r"^#{1,4}\s+(.+)$", body, flags=re.M)[:8]]
    lines = []
    for line in body.splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or clean.startswith("!["):
            continue
        lines.append(clean)
        if sum(len(x) for x in lines) > excerpt_chars:
            break
    excerpt = truncate(" ".join(lines), excerpt_chars)
    created = None
    if hasattr(stat, "st_birthtime"):
        created = datetime.fromtimestamp(stat.st_birthtime, TZ).isoformat(timespec="seconds")
    return MarkdownDoc(
        path=str(path),
        modified=datetime.fromtimestamp(stat.st_mtime, TZ).isoformat(timespec="seconds"),
        created=created,
        title=title,
        headings=headings,
        excerpt=excerpt,
    )


def is_work_log(path: Path) -> bool:
    parts = set(path.parts)
    if "work-log" in parts:
        return True
    try:
        relative = path.relative_to(WORK_LOG_VAULT_ROOT)
    except ValueError:
        return False
    return bool(relative.parts) and relative.parts[0] in {"daily", "weekly", "monthly"}


def markdown_files_for_day(target: date, max_items: int) -> list[MarkdownDoc]:
    docs: list[MarkdownDoc] = []
    if not VAULT_ROOT.exists():
        return docs
    for path in VAULT_ROOT.rglob("*.md"):
        if is_work_log(path) or ".obsidian" in path.parts:
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        dates = {datetime.fromtimestamp(stat.st_mtime, TZ).date()}
        if hasattr(stat, "st_birthtime"):
            dates.add(datetime.fromtimestamp(stat.st_birthtime, TZ).date())
        if target not in dates:
            continue
        doc = summarize_markdown(path)
        if doc:
            docs.append(doc)
    docs.sort(key=lambda d: (d.modified, d.path), reverse=True)
    return docs[:max_items]


def meeting_files_for_day(target: date, max_items: int) -> list[MarkdownDoc]:
    docs: dict[str, MarkdownDoc] = {}
    if not VAULT_ROOT.exists():
        return []
    patterns: list[Path] = []
    dailies = VAULT_ROOT / "notes" / "dailies"
    if dailies.exists():
        patterns.extend(dailies.glob(f"{target.isoformat()}*.md"))
    patterns.extend(VAULT_ROOT.rglob(f"*{target.isoformat()}*.md"))
    for path in patterns:
        if not path.is_file() or is_work_log(path):
            continue
        doc = summarize_markdown(path, excerpt_chars=1800)
        if doc:
            docs[str(path)] = doc
        if len(docs) >= max_items:
            break
    return sorted(docs.values(), key=lambda d: d.path)


def load_session_index() -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    path = CODEX_HOME / "session_index.jsonl"
    if not path.exists():
        return index
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return index
    for line in lines:
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        sid = item.get("id")
        if not sid:
            continue
        index[sid] = {
            "thread_name": item.get("thread_name") or "",
            "updated_at": iso_local(item.get("updated_at")),
        }
    return index


def text_from_content(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [text_from_content(v) for v in value]
        return "\n".join(p for p in parts if p)
    if isinstance(value, dict):
        for key in ("text", "message", "content", "input_text", "output_text"):
            if key in value:
                text = text_from_content(value[key])
                if text:
                    return text
    return ""


def is_noise_user_message(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    noise_prefixes = (
        "# AGENTS.md instructions",
        "<system_instruction>",
        "<turn_aborted>",
    )
    if stripped.startswith(noise_prefixes):
        return True
    if "You are generating a short conversation title" in stripped:
        return True
    if "Return only the title" in stripped and "conversation title" in stripped:
        return True
    if "Generate a title for this conversation" in stripped:
        return True
    return False


def is_title_utility_session(user_messages: list[str], assistant_messages: list[str]) -> bool:
    if len(assistant_messages) > 1:
        return False
    joined = "\n".join(user_messages)
    return "conversation title" in joined and "Return only the title" in joined


def candidate_session_files(target: date, index: dict[str, dict[str, str]]) -> list[Path]:
    files: set[Path] = set()
    date_dir = CODEX_HOME / "sessions" / f"{target.year:04d}" / f"{target.month:02d}" / f"{target.day:02d}"
    if date_dir.exists():
        files.update(date_dir.glob("*.jsonl"))
    archived = CODEX_HOME / "archived_sessions"
    if archived.exists():
        files.update(archived.glob(f"*{target.isoformat()}*.jsonl"))

    target_ids = [
        sid
        for sid, info in index.items()
        if dt_day(info.get("updated_at")) == target
    ]
    for sid in target_ids:
        for root in (CODEX_HOME / "sessions", CODEX_HOME / "archived_sessions"):
            if root.exists():
                files.update(root.rglob(f"*{sid}.jsonl"))
    return sorted(files)


def parse_codex_session(path: Path, target: date, index: dict[str, dict[str, str]]) -> CodexSession | None:
    session_id = ""
    cwd = ""
    started_at = ""
    user_messages: list[str] = []
    assistant_messages: list[str] = []
    saw_target_line = False

    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None

    for line in lines:
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        line_day = dt_day(item.get("timestamp"))
        if line_day == target:
            saw_target_line = True

        typ = item.get("type")
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}

        if typ == "session_meta":
            session_id = payload.get("id") or session_id
            cwd = payload.get("cwd") or cwd
            started_at = iso_local(payload.get("timestamp")) or started_at
            continue

        if line_day is not None and line_day != target:
            continue

        if typ == "event_msg" and payload.get("type") == "user_message":
            text = text_from_content(payload.get("message"))
            if text and not is_noise_user_message(text):
                user_messages.append(truncate(text, 900))
            continue

        if typ == "response_item":
            role = payload.get("role")
            if role == "user":
                text = text_from_content(payload.get("content"))
                if text and not is_noise_user_message(text):
                    user_messages.append(truncate(text, 900))
            elif role == "assistant":
                text = text_from_content(payload.get("content"))
                if text:
                    assistant_messages.append(truncate(text, 900))

    if not session_id:
        match = re.search(r"([0-9a-f]{8}-[0-9a-f-]{27,})", path.name)
        session_id = match.group(1) if match else path.stem
    info = index.get(session_id, {})
    if not saw_target_line and dt_day(info.get("updated_at")) != target:
        return None
    raw_user_messages = dedupe(user_messages)
    raw_assistant_messages = dedupe(assistant_messages)
    if is_title_utility_session(raw_user_messages, raw_assistant_messages):
        return None
    if not raw_user_messages and len(raw_assistant_messages) == 1 and len(raw_assistant_messages[0]) < 160:
        return None
    if not user_messages and not assistant_messages:
        return None
    return CodexSession(
        session_id=session_id,
        thread_name=info.get("thread_name") or "",
        cwd=cwd,
        started_at=started_at,
        updated_at=info.get("updated_at") or "",
        file=str(path),
        user_messages=raw_user_messages[:8],
        assistant_messages=raw_assistant_messages[:5],
    )


def dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        key = value.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def codex_sessions_for_day(target: date, max_items: int) -> list[CodexSession]:
    index = load_session_index()
    sessions: list[CodexSession] = []
    for path in candidate_session_files(target, index):
        session = parse_codex_session(path, target, index)
        if session:
            sessions.append(session)
    sessions.sort(key=lambda s: (s.updated_at or s.started_at, s.thread_name), reverse=True)
    return sessions[:max_items]


def daily_context(target: date, max_items: int) -> dict[str, Any]:
    return {
        "kind": "daily",
        "target_date": target.isoformat(),
        "vault_root": str(VAULT_ROOT),
        "work_log_vault_root": str(WORK_LOG_VAULT_ROOT),
        "daily_file": str(WORK_LOG_VAULT_ROOT / "daily" / f"{target.isoformat()}.md"),
        "vault_documents": [asdict(d) for d in markdown_files_for_day(target, max_items)],
        "codex_sessions": [asdict(s) for s in codex_sessions_for_day(target, max_items)],
        "meeting_notes": [asdict(d) for d in meeting_files_for_day(target, max_items)],
    }


def week_in_month(monday: date) -> int:
    first = monday.replace(day=1)
    first_dow = first.isoweekday()
    first_monday_day = 1 if first_dow == 1 else 9 - first_dow
    return ((monday.day - first_monday_day) // 7) + 1


def weekly_context(base: date) -> dict[str, Any]:
    this_monday = base - timedelta(days=base.isoweekday() - 1)
    last_monday = this_monday - timedelta(days=7)
    last_sunday = last_monday + timedelta(days=6)
    year = last_monday.year
    month = last_monday.month
    week_no = week_in_month(last_monday)
    daily_dir = WORK_LOG_VAULT_ROOT / "daily"
    daily_files = []
    for i in range(7):
        day = last_monday + timedelta(days=i)
        path = daily_dir / f"{day.isoformat()}.md"
        if path.exists():
            daily_files.append({"date": day.isoformat(), "path": str(path), "content": read_limited(path, 14000)})
        else:
            daily_files.append({"date": day.isoformat(), "path": str(path), "content": ""})
    return {
        "kind": "weekly",
        "base_date": base.isoformat(),
        "period_start": last_monday.isoformat(),
        "period_end": last_sunday.isoformat(),
        "year": year,
        "month": f"{month:02d}",
        "week_in_month": week_no,
        "weekly_file": str(WORK_LOG_VAULT_ROOT / "weekly" / f"{year:04d}-{month:02d}-W{week_no}.md"),
        "daily_files": daily_files,
    }


def read_limited(path: Path, limit: int) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n\n...[truncated]"


def parse_period(text: str) -> tuple[date, date] | None:
    match = re.search(r"period:\s*[\"']?(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})", text)
    if not match:
        match = re.search(r"기간\*\*:\s*(\d{4}-\d{2}-\d{2}).*?~\s*(\d{4}-\d{2}-\d{2})", text)
    if not match:
        return None
    return date.fromisoformat(match.group(1)), date.fromisoformat(match.group(2))


def overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return a_start <= b_end and b_start <= a_end


def monthly_context(year: int, month: int) -> dict[str, Any]:
    first = date(year, month, 1)
    next_month = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
    last = next_month - timedelta(days=1)
    weekly_dir = WORK_LOG_VAULT_ROOT / "weekly"
    weekly_files = []
    if weekly_dir.exists():
        for path in sorted(weekly_dir.glob("*.md")):
            text = read_limited(path, 20000)
            period = parse_period(text)
            include = False
            if period:
                include = overlaps(period[0], period[1], first, last)
            elif path.name.startswith(f"{year:04d}-{month:02d}-"):
                include = True
            if include:
                weekly_files.append({"path": str(path), "period": [d.isoformat() for d in period] if period else [], "content": text})

    daily_files = []
    if not weekly_files:
        daily_dir = WORK_LOG_VAULT_ROOT / "daily"
        if daily_dir.exists():
            for path in sorted(daily_dir.glob(f"{year:04d}-{month:02d}-*.md")):
                daily_files.append({"path": str(path), "content": read_limited(path, 10000)})

    return {
        "kind": "monthly",
        "target_month": f"{year:04d}-{month:02d}",
        "period_start": first.isoformat(),
        "period_end": last.isoformat(),
        "monthly_file": str(WORK_LOG_VAULT_ROOT / "monthly" / f"{year:04d}-{month:02d}.md"),
        "weekly_files": weekly_files,
        "daily_fallback_files": daily_files,
    }


def render_doc(doc: dict[str, Any]) -> str:
    headings = ", ".join(doc.get("headings") or [])
    parts = [f"- **{doc.get('title') or Path(doc['path']).stem}**"]
    parts.append(f"  - path: `{doc['path']}`")
    if doc.get("modified"):
        parts.append(f"  - modified: {doc['modified']}")
    if headings:
        parts.append(f"  - headings: {headings}")
    if doc.get("excerpt"):
        parts.append(f"  - excerpt: {doc['excerpt']}")
    return "\n".join(parts)


def render_markdown(data: dict[str, Any]) -> str:
    kind = data["kind"]
    lines = [f"# Work Log Source Context - {kind}", ""]
    if kind == "daily":
        lines.append(f"- target_date: {data['target_date']}")
        lines.append(f"- output: `{data['daily_file']}`")
        lines.append("")
        lines.append("## Vault Documents")
        docs = data["vault_documents"]
        lines.extend([render_doc(d) for d in docs] or ["- 해당 날짜에 수정/생성된 Vault 문서 없음"])
        lines.append("")
        lines.append("## Codex Sessions")
        sessions = data["codex_sessions"]
        if not sessions:
            lines.append("- 해당 날짜의 Codex 세션 없음")
        for session in sessions:
            title = session.get("thread_name") or session.get("session_id", "")[:8]
            lines.append(f"- **{title}**")
            lines.append(f"  - session: `{session.get('session_id')}`")
            if session.get("cwd"):
                lines.append(f"  - cwd: `{session['cwd']}`")
            if session.get("updated_at"):
                lines.append(f"  - updated_at: {session['updated_at']}")
            if session.get("user_messages"):
                lines.append("  - user messages:")
                for msg in session["user_messages"]:
                    lines.append(f"    - {msg}")
            if session.get("assistant_messages"):
                lines.append("  - assistant messages:")
                for msg in session["assistant_messages"]:
                    lines.append(f"    - {msg}")
        lines.append("")
        lines.append("## Meeting Notes")
        meetings = data["meeting_notes"]
        lines.extend([render_doc(d) for d in meetings] or ["- 해당 날짜에 미팅 노트 없음"])
    elif kind == "weekly":
        lines.append(f"- period: {data['period_start']} ~ {data['period_end']}")
        lines.append(f"- output: `{data['weekly_file']}`")
        lines.append("")
        lines.append("## Daily Files")
        for item in data["daily_files"]:
            status = "found" if item["content"] else "missing"
            lines.append(f"### {item['date']} ({status})")
            if item["content"]:
                lines.append("```markdown")
                lines.append(item["content"])
                lines.append("```")
            else:
                lines.append("- Daily Note 없음")
    elif kind == "monthly":
        lines.append(f"- month: {data['target_month']}")
        lines.append(f"- period: {data['period_start']} ~ {data['period_end']}")
        lines.append(f"- output: `{data['monthly_file']}`")
        lines.append("")
        lines.append("## Weekly Files")
        if data["weekly_files"]:
            for item in data["weekly_files"]:
                lines.append(f"### {Path(item['path']).stem}")
                lines.append(f"- path: `{item['path']}`")
                if item.get("period"):
                    lines.append(f"- period: {item['period'][0]} ~ {item['period'][1]}")
                lines.append("```markdown")
                lines.append(item["content"])
                lines.append("```")
        else:
            lines.append("- 해당 월 weekly 파일 없음. Daily fallback 사용.")
            for item in data["daily_fallback_files"]:
                lines.append(f"### {Path(item['path']).stem}")
                lines.append("```markdown")
                lines.append(item["content"])
                lines.append("```")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["daily", "weekly", "monthly"])
    parser.add_argument("value", nargs="?")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--max-items", type=int, default=40)
    args = parser.parse_args()

    if args.kind == "daily":
        data = daily_context(parse_day(args.value), args.max_items)
    elif args.kind == "weekly":
        data = weekly_context(parse_day(args.value) if args.value else datetime.now(TZ).date())
    else:
        year, month = parse_month(args.value)
        data = monthly_context(year, month)

    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
