#!/usr/bin/env python3
"""Behavior tests for the complexity scanner CLI."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCANNER = Path(__file__).with_name("analyze_complexity.py")


class AnalyzeComplexityCliTest(unittest.TestCase):
    def run_scanner(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCANNER), str(root), "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_sequential_loops_do_not_leak_loop_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sequential.js").write_text(
                """\
for (const item of first) {
  consume(item);
}
values.includes(target);
for (const item of second) {
  consume(item);
}
""",
                encoding="utf-8",
            )

            result = self.run_scanner(root)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([], json.loads(result.stdout))

    def test_missing_root_fails_instead_of_returning_an_empty_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"

            result = self.run_scanner(missing)

        self.assertNotEqual(0, result.returncode)
        self.assertIn("root does not exist", result.stderr)

    def test_nested_loop_is_still_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nested.js").write_text(
                """\
for (const item of first) {
  for (const candidate of second) {
    consume(item, candidate);
  }
}
""",
                encoding="utf-8",
            )

            result = self.run_scanner(root)

        self.assertEqual(0, result.returncode, result.stderr)
        kinds = {finding["kind"] for finding in json.loads(result.stdout)}
        self.assertIn("nested-or-callback-loop", kinds)

    def test_query_calls_with_common_arguments_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "queries.js").write_text(
                """\
for (const id of ids) {
  request("/items");
  client.findMany({ where: { id } });
  query();
}
""",
                encoding="utf-8",
            )

            result = self.run_scanner(root)

        self.assertEqual(0, result.returncode, result.stderr)
        query_lines = {
            finding["line"]
            for finding in json.loads(result.stdout)
            if finding["kind"] == "io-or-query-in-loop"
        }
        self.assertEqual({2, 3, 4}, query_lines)


if __name__ == "__main__":
    unittest.main()
