#!/usr/bin/env python3
"""Fail when publishable files contain likely private-source residue or secrets."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_ROOTS = (
    ROOT / "SKILL.md",
    ROOT / "references",
    ROOT / "assets",
    ROOT / "examples",
)
TEXT_SUFFIXES = {"", ".md", ".json", ".yaml", ".yml", ".py", ".txt"}
RESIDUE_PATTERNS = {
    "private absolute macOS path": re.compile(r"/Users/[^/\s]+/"),
    "private owner coupling": re.compile(r"\b[A-Z][a-z]+'s durable personal context\b"),
    "private personal-context remote": re.compile(
        r"github\.com(?::|/)[^/\s]+/personal-context(?:\.git)?"
    ),
}
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\b(?:gh[opusr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "OpenAI key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def files() -> list[Path]:
    result: list[Path] = []
    for root in SCAN_ROOTS:
        if root.is_file():
            result.append(root)
        elif root.is_dir():
            result.extend(
                path
                for path in root.rglob("*")
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
            )
    return sorted(result)


def main() -> int:
    findings: list[str] = []
    for path in files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        for label, pattern in RESIDUE_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{relative}: {label}")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{relative}: likely {label}")

    if findings:
        print("privacy-check: blocked publish", file=sys.stderr)
        for finding in findings:
            print(f"  {finding}", file=sys.stderr)
        return 1
    print(f"privacy-check: {len(files())} publishable files clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
