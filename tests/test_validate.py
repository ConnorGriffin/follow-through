from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate import validate_repository  # noqa: E402


class ValidateRepositoryTests(unittest.TestCase):
    def copy_example(self, destination: Path) -> Path:
        target = destination / "records"
        shutil.copytree(ROOT / "examples" / "maya-chen", target)
        return target

    def validate_quietly(self, target: Path) -> int:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            return validate_repository(target)

    def test_synthetic_example_is_valid(self) -> None:
        self.assertEqual(validate_repository(ROOT / "examples" / "maya-chen"), 0)

    def test_rejects_illegal_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.copy_example(Path(temporary))
            plan = target / "plans" / "test-four-day-workweek.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "status: reviewed", "status: settled"
                ),
                encoding="utf-8",
            )
            self.assertEqual(self.validate_quietly(target), 1)

    def test_rejects_broken_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.copy_example(Path(temporary))
            person = target / "people" / "jordan-lee.md"
            person.write_text(
                person.read_text(encoding="utf-8").replace(
                    "../areas/relationships.md", "../areas/missing.md"
                ),
                encoding="utf-8",
            )
            self.assertEqual(self.validate_quietly(target), 1)

    def test_accepts_yaml_block_lists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.copy_example(Path(temporary))
            person = target / "people" / "jordan-lee.md"
            person.write_text(
                person.read_text(encoding="utf-8").replace(
                    'areas: ["../areas/relationships.md"]',
                    'areas:\n  - "../areas/relationships.md"',
                ),
                encoding="utf-8",
            )
            self.assertEqual(self.validate_quietly(target), 0)

    def test_rejects_index_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.copy_example(Path(temporary))
            index = target / "INDEX.md"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "- [Jordan Lee](people/jordan-lee.md) — Maya's partner and shared-planning\n"
                    "  context.\n",
                    "",
                ),
                encoding="utf-8",
            )
            self.assertEqual(self.validate_quietly(target), 1)

    def test_rejects_illegal_historical_transition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.copy_example(Path(temporary))
            subprocess.run(["git", "init", "-b", "main"], cwd=target, check=True, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=target, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Follow Through Test",
                    "-c",
                    "user.email=test@example.invalid",
                    "commit",
                    "-m",
                    "Record awaiting outcome",
                ],
                cwd=target,
                check=True,
                capture_output=True,
            )
            plan = target / "plans" / "test-four-day-workweek.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "status: reviewed", "status: awaiting-outcome"
                ),
                encoding="utf-8",
            )
            index = target / "INDEX.md"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "## Plans\n",
                    "## Plans\n\n"
                    "- [Test a four-day workweek](plans/test-four-day-workweek.md)\n",
                ),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                stderr
            ):
                result = validate_repository(target)
            self.assertEqual(result, 1)
            self.assertIn("illegal historical transition", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
