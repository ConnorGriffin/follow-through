#!/usr/bin/env python3
"""Validate a Follow Through records repository using only the standard library."""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

TYPE_FOLDERS = {
    "profile": "profile",
    "person": "people",
    "area": "areas",
    "work": "work",
    "decision": "decisions",
    "plan": "plans",
    "outcome": "outcomes",
}
LEGAL_STATES = {
    "profile": {"settled"},
    "person": {"settled"},
    "area": {"settled"},
    "work": {"open", "awaiting-input", "settled", "abandoned"},
    "decision": {"open", "awaiting-input", "settled", "abandoned", "superseded"},
    "plan": {
        "open",
        "awaiting-input",
        "awaiting-outcome",
        "reviewed",
        "abandoned",
        "superseded",
    },
    "outcome": {"reviewed"},
}
TRANSITIONS = {
    "profile": {("settled", "settled")},
    "person": {("settled", "settled")},
    "area": {("settled", "settled")},
    "work": {
        ("open", "open"),
        ("open", "awaiting-input"),
        ("awaiting-input", "open"),
        ("awaiting-input", "awaiting-input"),
        ("open", "settled"),
        ("open", "abandoned"),
        ("awaiting-input", "settled"),
        ("awaiting-input", "abandoned"),
    },
    "decision": {
        ("open", "open"),
        ("open", "awaiting-input"),
        ("awaiting-input", "open"),
        ("awaiting-input", "awaiting-input"),
        ("open", "settled"),
        ("open", "abandoned"),
        ("awaiting-input", "settled"),
        ("awaiting-input", "abandoned"),
        ("settled", "settled"),
        ("settled", "superseded"),
    },
    "plan": {
        ("open", "open"),
        ("open", "awaiting-input"),
        ("awaiting-input", "open"),
        ("awaiting-input", "awaiting-input"),
        ("open", "awaiting-outcome"),
        ("open", "abandoned"),
        ("open", "superseded"),
        ("awaiting-input", "awaiting-outcome"),
        ("awaiting-input", "abandoned"),
        ("awaiting-input", "superseded"),
        ("awaiting-outcome", "awaiting-outcome"),
        ("awaiting-outcome", "reviewed"),
        ("awaiting-outcome", "abandoned"),
        ("awaiting-outcome", "superseded"),
    },
    "outcome": {("reviewed", "reviewed")},
}
for transition_type, transition_states in LEGAL_STATES.items():
    TRANSITIONS[transition_type].update(
        (transition_state, transition_state)
        for transition_state in transition_states
    )
REQUIRED_FIELDS = {"type", "status", "created", "updated", "areas", "people"}
OPTIONAL_FIELDS = {
    "profile": {"last_confirmed", "review_after"},
    "person": {"last_confirmed", "review_after"},
    "area": {"last_confirmed", "review_after"},
    "work": set(),
    "decision": {"supersedes", "superseded_by", "upholds"},
    "plan": {"review_after", "supersedes", "superseded_by", "outcomes"},
    "outcome": {"plan"},
}
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


@dataclass(frozen=True)
class Record:
    path: Path
    relative: Path
    metadata: dict[str, Any]
    body: str

    @property
    def type(self) -> str:
        return str(self.metadata.get("type", ""))

    @property
    def status(self) -> str:
        return str(self.metadata.get("status", ""))


class Validation:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.errors: list[str] = []
        self.records: dict[Path, Record] = {}

    def error(self, path: Path | str, message: str) -> None:
        label = path.as_posix() if isinstance(path, Path) else path
        self.errors.append(f"{label}: {message}")

    def parse_scalar(self, raw: str) -> Any:
        value = raw.strip()
        if value == "[]":
            return []
        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = ast.literal_eval(value)
            except (SyntaxError, ValueError) as error:
                raise ValueError(f"invalid inline list: {value}") from error
            if not isinstance(parsed, list):
                raise ValueError(f"expected list: {value}")
            return parsed
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return ast.literal_eval(value)
        return value

    def parse_frontmatter(self, path: Path, text: str) -> tuple[dict[str, Any], str] | None:
        match = FRONTMATTER_RE.match(text)
        if not match:
            self.error(path.relative_to(self.root), "missing YAML frontmatter")
            return None
        metadata: dict[str, Any] = {}
        lines = match.group(1).splitlines()
        index = 0
        while index < len(lines):
            line = lines[index]
            number = index + 2
            if not line.strip() or line.lstrip().startswith("#"):
                index += 1
                continue
            if line.startswith((" ", "\t")) or ":" not in line:
                self.error(path.relative_to(self.root), f"unsupported YAML at line {number}")
                return None
            key, raw = line.split(":", 1)
            key = key.strip()
            if key in metadata:
                self.error(path.relative_to(self.root), f"duplicate frontmatter field `{key}`")
                return None
            if not raw.strip():
                values: list[Any] = []
                index += 1
                while index < len(lines) and lines[index].startswith((" ", "\t")):
                    item = lines[index].strip()
                    if not item.startswith("- "):
                        self.error(
                            path.relative_to(self.root),
                            f"unsupported YAML at line {index + 2}",
                        )
                        return None
                    try:
                        values.append(self.parse_scalar(item[2:]))
                    except ValueError as error:
                        self.error(path.relative_to(self.root), str(error))
                        return None
                    index += 1
                metadata[key] = values
                continue
            try:
                metadata[key] = self.parse_scalar(raw)
            except ValueError as error:
                self.error(path.relative_to(self.root), str(error))
                return None
            index += 1
        return metadata, text[match.end() :]

    def load_records(self) -> None:
        for record_type, folder in TYPE_FOLDERS.items():
            directory = self.root / folder
            if not directory.exists():
                continue
            for path in sorted(directory.glob("*.md")):
                parsed = self.parse_frontmatter(path, path.read_text(encoding="utf-8"))
                if parsed is None:
                    continue
                metadata, body = parsed
                relative = path.relative_to(self.root)
                record = Record(path, relative, metadata, body)
                self.records[relative] = record
                if record.type != record_type:
                    self.error(relative, f"type `{record.type}` does not match `{folder}/`")

    def validate_metadata(self, record: Record) -> None:
        keys = set(record.metadata)
        missing = REQUIRED_FIELDS - keys
        if missing:
            self.error(record.relative, f"missing fields: {', '.join(sorted(missing))}")

        if record.type not in LEGAL_STATES:
            self.error(record.relative, f"unknown type `{record.type}`")
            return
        allowed = REQUIRED_FIELDS | OPTIONAL_FIELDS[record.type]
        extra = keys - allowed
        if extra:
            self.error(record.relative, f"unsupported fields: {', '.join(sorted(extra))}")
        if record.status not in LEGAL_STATES[record.type]:
            self.error(record.relative, f"illegal `{record.status}` status for {record.type}")

        for field in ("created", "updated", "last_confirmed", "review_after"):
            if field not in record.metadata:
                continue
            try:
                date.fromisoformat(str(record.metadata[field]))
            except ValueError:
                self.error(record.relative, f"`{field}` must be ISO YYYY-MM-DD")
        try:
            if date.fromisoformat(str(record.metadata["updated"])) < date.fromisoformat(
                str(record.metadata["created"])
            ):
                self.error(record.relative, "`updated` precedes `created`")
        except (KeyError, ValueError):
            pass

        for field in ("areas", "people", "outcomes"):
            if field in record.metadata and not isinstance(record.metadata[field], list):
                self.error(record.relative, f"`{field}` must be an inline list")

        if record.type == "work" and record.status == "settled":
            if "## Produced" not in record.body or not MARKDOWN_LINK_RE.search(
                record.body.split("## Produced", 1)[1]
            ):
                self.error(record.relative, "settled work must link to a produced artifact")
        if record.type == "outcome" and "plan" not in record.metadata:
            self.error(record.relative, "outcome requires `plan`")
        if record.type == "plan":
            if "outcomes" not in record.metadata:
                self.error(record.relative, "plan requires `outcomes`")
            if "review_after" in record.metadata and record.status != "awaiting-outcome":
                self.error(
                    record.relative,
                    "`review_after` is only allowed while awaiting outcome",
                )

    def local_link(self, record: Record, raw: str) -> Path | None:
        parsed = urlparse(raw)
        if parsed.scheme or parsed.netloc or raw.startswith(("#", "mailto:")):
            return None
        clean = unquote(parsed.path)
        if not clean:
            return None
        return (record.path.parent / clean).resolve()

    def validate_links(self, record: Record) -> None:
        links: list[tuple[str, str]] = []
        for field in (
            "areas",
            "people",
            "outcomes",
            "plan",
            "supersedes",
            "superseded_by",
            "upholds",
        ):
            value = record.metadata.get(field)
            values = value if isinstance(value, list) else [value] if isinstance(value, str) else []
            links.extend((field, item) for item in values if isinstance(item, str))
        links.extend(("body", match) for match in MARKDOWN_LINK_RE.findall(record.body))

        for field, raw in links:
            target = self.local_link(record, raw)
            if target is None:
                continue
            try:
                target.relative_to(self.root)
            except ValueError:
                self.error(record.relative, f"`{field}` link escapes repository: {raw}")
                continue
            if not target.exists():
                self.error(record.relative, f"broken `{field}` link: {raw}")

    def validate_relations(self, record: Record) -> None:
        for field, expected_type in (("areas", "area"), ("people", "person"), ("outcomes", "outcome")):
            for raw in record.metadata.get(field, []):
                target = self.local_link(record, raw)
                if target is None:
                    continue
                linked = self.records.get(target.relative_to(self.root))
                if linked and linked.type != expected_type:
                    self.error(record.relative, f"`{field}` links to {linked.type}: {raw}")

        if record.type == "outcome":
            raw = record.metadata.get("plan")
            target = self.local_link(record, raw) if isinstance(raw, str) else None
            if target and target.exists():
                plan = self.records.get(target.relative_to(self.root))
                if plan and plan.type != "plan":
                    self.error(record.relative, f"`plan` links to {plan.type}")
                elif plan:
                    relative_back = Path(
                        os.path.relpath(record.path, plan.path.parent)
                    ).as_posix()
                    if relative_back not in plan.metadata.get("outcomes", []):
                        self.error(record.relative, "linked plan does not list this outcome")

        if record.type == "plan":
            for raw in record.metadata.get("outcomes", []):
                target = self.local_link(record, raw)
                if not target or not target.exists():
                    continue
                outcome = self.records.get(target.relative_to(self.root))
                if outcome and outcome.type == "outcome":
                    back = outcome.metadata.get("plan")
                    back_target = (
                        self.local_link(outcome, back) if isinstance(back, str) else None
                    )
                    if back_target != record.path.resolve():
                        self.error(record.relative, "linked outcome points to another plan")

        counterpart = {
            "supersedes": "superseded_by",
            "superseded_by": "supersedes",
        }
        for field, reverse in counterpart.items():
            raw = record.metadata.get(field)
            target = self.local_link(record, raw) if isinstance(raw, str) else None
            if not target or not target.exists():
                continue
            other = self.records.get(target.relative_to(self.root))
            if other:
                back = other.metadata.get(reverse)
                back_target = self.local_link(other, back) if isinstance(back, str) else None
                if back_target != record.path.resolve():
                    self.error(record.relative, f"`{field}` relation is not reciprocal")

    def expected_index_records(self) -> set[Path]:
        expected: set[Path] = set()
        for relative, record in self.records.items():
            if record.type in {"profile", "person", "area"}:
                expected.add(relative)
            elif record.type == "work" and record.status in {"open", "awaiting-input"}:
                expected.add(relative)
            elif record.type == "decision" and record.status in {
                "open",
                "awaiting-input",
                "settled",
            }:
                expected.add(relative)
            elif record.type == "plan" and record.status in {
                "open",
                "awaiting-input",
                "awaiting-outcome",
            }:
                expected.add(relative)
        return expected

    def validate_index(self) -> None:
        path = self.root / "INDEX.md"
        if not path.is_file():
            self.error("INDEX.md", "missing index")
            return
        text = path.read_text(encoding="utf-8")
        if not re.search(r"^Bootstrap status:\s*\S", text, re.MULTILINE):
            self.error("INDEX.md", "missing bootstrap status")
        actual: set[Path] = set()
        for raw in MARKDOWN_LINK_RE.findall(text):
            parsed = urlparse(raw)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (self.root / unquote(parsed.path)).resolve()
            try:
                relative = target.relative_to(self.root)
            except ValueError:
                self.error("INDEX.md", f"link escapes repository: {raw}")
                continue
            if not target.exists():
                self.error("INDEX.md", f"broken link: {raw}")
                continue
            if relative in self.records:
                actual.add(relative)
        expected = self.expected_index_records()
        for relative in sorted(expected - actual):
            self.error("INDEX.md", f"missing current record: {relative.as_posix()}")
        for relative in sorted(actual - expected):
            self.error("INDEX.md", f"lists historical record: {relative.as_posix()}")

        pending_text = ""
        pending_match = re.search(
            r"^## Pending reviews\s*$\n(.*?)(?=^## |\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if pending_match:
            pending_text = pending_match.group(1)
        pending_actual: set[Path] = set()
        for raw in MARKDOWN_LINK_RE.findall(pending_text):
            target = (self.root / unquote(urlparse(raw).path)).resolve()
            try:
                relative = target.relative_to(self.root)
            except ValueError:
                continue
            if relative in self.records:
                pending_actual.add(relative)
        pending_expected = {
            relative
            for relative, record in self.records.items()
            if record.type == "plan"
            and record.status == "awaiting-outcome"
            and "review_after" in record.metadata
        }
        for relative in sorted(pending_expected - pending_actual):
            self.error("INDEX.md", f"missing pending review: {relative.as_posix()}")
        for relative in sorted(pending_actual - pending_expected):
            self.error("INDEX.md", f"invalid pending review: {relative.as_posix()}")

    def git_versions(self, record: Record) -> list[str]:
        try:
            top = subprocess.run(
                ["git", "-C", str(self.root), "rev-parse", "--show-toplevel"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            git_root = Path(top)
            git_path = record.path.relative_to(git_root).as_posix()
            commits = subprocess.run(
                ["git", "-C", str(git_root), "log", "--format=%H", "--reverse", "--", git_path],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
        except (subprocess.CalledProcessError, ValueError):
            return []

        statuses: list[str] = []
        for commit in commits:
            shown = subprocess.run(
                ["git", "-C", str(git_root), "show", f"{commit}:{git_path}"],
                check=False,
                capture_output=True,
                text=True,
            )
            if shown.returncode != 0:
                continue
            match = re.search(r"^status:\s*(\S+)\s*$", shown.stdout, re.MULTILINE)
            if match:
                statuses.append(match.group(1).strip("\"'"))
        if not statuses or statuses[-1] != record.status:
            statuses.append(record.status)
        return statuses

    def validate_history(self, record: Record) -> None:
        statuses = self.git_versions(record)
        for before, after in zip(statuses, statuses[1:]):
            if (before, after) not in TRANSITIONS.get(record.type, set()):
                self.error(record.relative, f"illegal historical transition `{before}` → `{after}`")

    def run(self) -> int:
        self.load_records()
        for record in self.records.values():
            self.validate_metadata(record)
            self.validate_links(record)
            self.validate_relations(record)
            self.validate_history(record)
        self.validate_index()

        if self.errors:
            print("follow-through: validation failed", file=sys.stderr)
            for error in sorted(self.errors):
                print(f"  {error}", file=sys.stderr)
            return 1
        print(f"follow-through: {len(self.records)} records valid")
        return 0


def validate_repository(root: Path) -> int:
    return Validation(root).run()


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    return validate_repository(root)


if __name__ == "__main__":
    raise SystemExit(main())
