#!/usr/bin/env python3
"""Create Apple Reminders from work-log tasks."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import urllib.parse
from datetime import date
from pathlib import Path

from microsoft_todo import clean_task_title, extract_tasks_from_markdown


DEFAULT_LIST_NAME = os.environ.get("REMINDERS_LIST_NAME", "Daily Focus")


APPLESCRIPT_CREATE = r'''
on run argv
  set taskName to item 1 of argv
  set listName to item 2 of argv
  set dueYear to (item 3 of argv) as integer
  set dueMonth to (item 4 of argv) as integer
  set dueDay to (item 5 of argv) as integer
  set taskBody to item 6 of argv

  set dueDate to current date
  set year of dueDate to dueYear
  set month of dueDate to dueMonth
  set day of dueDate to dueDay
  set time of dueDate to 86340

  tell application "Reminders"
    if not (exists list listName) then
      make new list with properties {name:listName}
    end if
    tell list listName
      set duplicateFound to false
      repeat with itemReminder in reminders
        if (name of itemReminder is taskName) and (completed of itemReminder is false) then
          set duplicateFound to true
          exit repeat
        end if
      end repeat

      if duplicateFound then
        return "skipped"
      end if

      make new reminder with properties {name:taskName, body:taskBody, due date:dueDate}
      return "created"
    end tell
  end tell
end run
'''


APPLESCRIPT_UPSERT_COMPLETED_LINK = r'''
on run argv
  set taskName to item 1 of argv
  set listName to item 2 of argv
  set taskBody to item 3 of argv

  tell application "Reminders"
    if not (exists list listName) then
      make new list with properties {name:listName}
    end if
    tell list listName
      set targetReminder to missing value
      repeat with itemReminder in reminders
        if name of itemReminder is taskName then
          set targetReminder to itemReminder
          exit repeat
        end if
      end repeat

      if targetReminder is missing value then
        make new reminder with properties {name:taskName, body:taskBody, completed:true, completion date:(current date)}
        return "created"
      end if

      set body of targetReminder to taskBody
      set completed of targetReminder to true
      set completion date of targetReminder to current date
      return "updated"
    end tell
  end tell
end run
'''


def resolve_path(path: Path) -> Path:
    try:
        return path.expanduser().resolve()
    except OSError:
        return path.expanduser().absolute()


def obsidian_uri_for(path: Path) -> str:
    absolute = resolve_path(path)
    vault_root = resolve_path(
        Path(os.environ.get("WORK_LOG_VAULT_ROOT", "~/Documents/work-logs"))
    )
    try:
        relative = absolute.relative_to(vault_root)
    except ValueError:
        return f"obsidian://open?path={urllib.parse.quote(str(absolute))}"
    vault = urllib.parse.quote(vault_root.name)
    file_path = urllib.parse.quote(relative.as_posix())
    return f"obsidian://open?vault={vault}&file={file_path}"


def source_body(source: str | None) -> str:
    body = "Created by Codex work-log routine."
    if not source:
        return body

    path = resolve_path(Path(source))
    body += "\n\nWork log:"
    body += f"\nObsidian: {obsidian_uri_for(path)}"
    body += f"\nFile: {path.as_uri()}"
    body += f"\nPath: {path}"
    return body


def completed_link_title(source: str) -> str:
    stem = resolve_path(Path(source)).stem
    return f"Daily Work Log - {stem}"


def read_tasks_file(path: Path) -> list[str]:
    tasks = []
    for line in path.read_text(encoding="utf-8").splitlines():
        title = clean_task_title(line)
        if title:
            tasks.append(title)
    return tasks


def parse_due(value: str) -> tuple[int, int, int]:
    due = date.fromisoformat(value)
    return due.year, due.month, due.day


def create_reminder(title: str, list_name: str, due: str, source: str | None) -> str:
    y, m, d = parse_due(due)
    body = source_body(source)
    result = subprocess.run(
        [
            "osascript",
            "-e",
            APPLESCRIPT_CREATE,
            title,
            list_name,
            str(y),
            str(m),
            str(d),
            body,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "osascript failed")
    return result.stdout.strip()


def upsert_completed_link(list_name: str, source: str) -> str:
    result = subprocess.run(
        [
            "osascript",
            "-e",
            APPLESCRIPT_UPSERT_COMPLETED_LINK,
            completed_link_title(source),
            list_name,
            source_body(source),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "osascript failed")
    return result.stdout.strip()


def create_tasks(titles: list[str], list_name: str, due: str, source: str | None, dry_run: bool, completed_link: bool) -> None:
    if not titles:
        print("No task candidates.")
        return
    if dry_run:
        for title in titles:
            print(f"- {title}")
        if source and completed_link:
            print(f"\nCompleted link reminder: {completed_link_title(source)}")
            print(source_body(source))
        return

    created = 0
    skipped = 0
    for title in titles:
        status = create_reminder(title, list_name, due, source)
        if status == "created":
            created += 1
        else:
            skipped += 1
    link_status = None
    if source and completed_link:
        link_status = upsert_completed_link(list_name, source)
    summary = f"Created {created} reminder(s) in `{list_name}` for {due}. Skipped duplicates: {skipped}."
    if link_status:
        summary += f" Completed work-log link reminder: {link_status}."
    print(summary)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    suggest = sub.add_parser("suggest-from-worklog")
    suggest.add_argument("worklog")
    suggest.add_argument("--limit", type=int, default=5)

    create = sub.add_parser("create-from-worklog")
    create.add_argument("worklog")
    create.add_argument("--limit", type=int, default=5)
    create.add_argument("--list", default=DEFAULT_LIST_NAME)
    create.add_argument("--due", default=date.today().isoformat())
    create.add_argument("--dry-run", action="store_true")
    create.add_argument("--no-completed-link", action="store_true")

    create_file = sub.add_parser("create-from-file")
    create_file.add_argument("tasks_file")
    create_file.add_argument("--list", default=DEFAULT_LIST_NAME)
    create_file.add_argument("--due", default=date.today().isoformat())
    create_file.add_argument("--dry-run", action="store_true")
    create_file.add_argument("--no-completed-link", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "suggest-from-worklog":
            text = Path(args.worklog).expanduser().read_text(encoding="utf-8")
            for title in extract_tasks_from_markdown(text, args.limit):
                print(f"- {title}")
        elif args.command == "create-from-worklog":
            worklog = Path(args.worklog).expanduser()
            text = worklog.read_text(encoding="utf-8")
            titles = extract_tasks_from_markdown(text, args.limit)
            create_tasks(titles, args.list, args.due, str(worklog), args.dry_run, not args.no_completed_link)
        elif args.command == "create-from-file":
            tasks_file = Path(args.tasks_file).expanduser()
            create_tasks(read_tasks_file(tasks_file), args.list, args.due, str(tasks_file), args.dry_run, not args.no_completed_link)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
