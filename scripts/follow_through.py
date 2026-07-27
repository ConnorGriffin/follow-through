#!/usr/bin/env python3
"""Set up, locate, validate, and update a Follow Through repository."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "repository-template"
MANAGED_FILES = ("AGENTS.md", "CONTEXT.md", ".follow-through.json")
RECORD_DIRS = ("profile", "people", "areas", "work", "decisions", "plans", "outcomes")


class FollowThroughError(RuntimeError):
    """A user-correctable setup or configuration error."""


def config_path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base).expanduser() if base else Path.home() / ".config"
    return root / "follow-through" / "config.json"


def configured_repository() -> Path:
    override = os.environ.get("FOLLOW_THROUGH_HOME")
    if override:
        return Path(override).expanduser().resolve()

    path = config_path()
    if not path.is_file():
        raise FollowThroughError(
            "Follow Through is not configured. Run "
            "`python3 scripts/follow_through.py setup PATH`."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        repository = data["repository"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise FollowThroughError(f"Invalid config at {path}: {error}") from error
    if not isinstance(repository, str) or not repository.strip():
        raise FollowThroughError(f"Invalid repository path in {path}")
    return Path(repository).expanduser().resolve()


def write_config(repository: Path, replace: bool) -> None:
    path = config_path()
    if path.exists() and not replace:
        current = configured_repository()
        if current != repository:
            raise FollowThroughError(
                f"Follow Through already points to {current}. "
                "Pass --replace to change it."
            )
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps({"repository": str(repository)}, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def require_repository(path: Path) -> Path:
    path = path.expanduser().resolve()
    if not path.is_dir():
        raise FollowThroughError(f"Repository does not exist: {path}")
    missing = [name for name in ("AGENTS.md", "CONTEXT.md", "INDEX.md") if not (path / name).is_file()]
    if missing:
        raise FollowThroughError(
            f"{path} is not a Follow Through repository; missing: {', '.join(missing)}"
        )
    return path


def resolve_argument(value: str | None) -> Path:
    return require_repository(Path(value)) if value else require_repository(configured_repository())


def install_template(target: Path) -> None:
    target.mkdir(parents=True)
    for source in TEMPLATE_DIR.iterdir():
        if source.is_file():
            shutil.copy2(source, target / source.name)
    for directory in RECORD_DIRS:
        (target / directory).mkdir()

    claude = target / "CLAUDE.md"
    try:
        claude.symlink_to("AGENTS.md")
    except OSError:
        claude.write_text("@AGENTS.md\n", encoding="utf-8")

    if shutil.which("git"):
        result = subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=target,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise FollowThroughError(result.stderr.strip() or "git init failed")


def command_setup(args: argparse.Namespace) -> int:
    target = Path(args.path).expanduser().resolve()
    if target.exists() and any(target.iterdir()):
        raise FollowThroughError(
            f"Refusing to write into non-empty directory: {target}. "
            "Use `connect` for an existing repository."
        )
    if target.exists():
        target.rmdir()
    install_template(target)
    write_config(target, args.replace)
    print(f"Created Follow Through repository at {target}")
    print("No remote was created and nothing was pushed.")
    return 0


def command_connect(args: argparse.Namespace) -> int:
    target = require_repository(Path(args.path))
    write_config(target, args.replace)
    print(f"Connected Follow Through to {target}")
    return 0


def command_where(_args: argparse.Namespace) -> int:
    print(require_repository(configured_repository()))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    from validate import validate_repository

    target = resolve_argument(args.path)
    return validate_repository(target)


def schema_diffs(target: Path) -> list[str]:
    chunks: list[str] = []
    for name in MANAGED_FILES:
        source = TEMPLATE_DIR / name
        destination = target / name
        before = destination.read_text(encoding="utf-8").splitlines(keepends=True) if destination.exists() else []
        after = source.read_text(encoding="utf-8").splitlines(keepends=True)
        chunks.extend(
            difflib.unified_diff(
                before,
                after,
                fromfile=str(destination),
                tofile=f"{destination} (Follow Through current)",
            )
        )
    return chunks


def command_schema_diff(args: argparse.Namespace) -> int:
    target = resolve_argument(args.path)
    chunks = schema_diffs(target)
    if not chunks:
        print("Schema files match the installed Follow Through version.")
        return 0
    sys.stdout.writelines(chunks)
    return 1


def command_schema_update(args: argparse.Namespace) -> int:
    target = resolve_argument(args.path)
    chunks = schema_diffs(target)
    if not chunks:
        print("Schema files already match the installed Follow Through version.")
        return 0
    if not args.apply:
        sys.stdout.writelines(chunks)
        print("\nNo files changed. Re-run with --apply after reviewing this diff.")
        return 1
    for name in MANAGED_FILES:
        shutil.copy2(TEMPLATE_DIR / name, target / name)
    print(f"Updated managed schema files in {target}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="follow-through")
    commands = result.add_subparsers(dest="command", required=True)

    setup = commands.add_parser("setup", help="create a new private repository")
    setup.add_argument("path")
    setup.add_argument("--replace", action="store_true", help="replace existing configured path")
    setup.set_defaults(handler=command_setup)

    connect = commands.add_parser("connect", help="connect an existing repository")
    connect.add_argument("path")
    connect.add_argument("--replace", action="store_true", help="replace existing configured path")
    connect.set_defaults(handler=command_connect)

    where = commands.add_parser("where", help="print the configured repository")
    where.set_defaults(handler=command_where)

    validate = commands.add_parser("validate", help="validate records and index")
    validate.add_argument("path", nargs="?")
    validate.set_defaults(handler=command_validate)

    schema_diff = commands.add_parser("schema-diff", help="show managed schema changes")
    schema_diff.add_argument("path", nargs="?")
    schema_diff.set_defaults(handler=command_schema_diff)

    schema_update = commands.add_parser("schema-update", help="update managed schema files")
    schema_update.add_argument("path", nargs="?")
    schema_update.add_argument("--apply", action="store_true")
    schema_update.set_defaults(handler=command_schema_update)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except FollowThroughError as error:
        print(f"follow-through: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
