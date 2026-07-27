from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "follow_through.py"


class SetupTests(unittest.TestCase):
    def run_cli(
        self, *arguments: str, config_home: Path, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["XDG_CONFIG_HOME"] = str(config_home)
        environment.pop("FOLLOW_THROUGH_HOME", None)
        return subprocess.run(
            [sys.executable, str(CLI), *arguments],
            check=check,
            capture_output=True,
            text=True,
            env=environment,
        )

    def test_setup_creates_private_repo_and_config(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "records"
            config_home = root / "config"

            self.run_cli("setup", str(repository), config_home=config_home)

            self.assertTrue((repository / ".git").is_dir())
            self.assertTrue((repository / "CONTEXT.md").is_file())
            self.assertTrue((repository / "plans").is_dir())
            self.assertFalse(
                subprocess.run(
                    ["git", "remote"],
                    cwd=repository,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            )
            config = json.loads(
                (config_home / "follow-through" / "config.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(Path(config["repository"]), repository.resolve())
            located = self.run_cli("where", config_home=config_home)
            self.assertEqual(Path(located.stdout.strip()), repository.resolve())

    def test_setup_refuses_nonempty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository = root / "records"
            repository.mkdir()
            (repository / "keep.txt").write_text("keep\n", encoding="utf-8")

            result = self.run_cli(
                "setup",
                str(repository),
                config_home=root / "config",
                check=False,
            )

            self.assertEqual(result.returncode, 2)
            self.assertTrue((repository / "keep.txt").is_file())


if __name__ == "__main__":
    unittest.main()
