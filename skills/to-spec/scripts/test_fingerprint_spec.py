#!/usr/bin/env python3
"""Tests for authoritative spec body fingerprinting."""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).with_name("fingerprint_spec.py")


class FingerprintSpecTest(unittest.TestCase):
    def run_script(self, body: bytes) -> dict[str, str]:
        result = subprocess.run(
            ["python3", str(SCRIPT), "-"],
            input=body,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        return json.loads(result.stdout)

    def test_known_body_has_stable_versioned_fingerprint(self) -> None:
        value = self.run_script(b"REQ-001: retry once\n")
        self.assertEqual(value["status"], "ok")
        self.assertEqual(
            value["fingerprint"],
            "to-spec-body-v1:f597fbf0f5280d4f1b71a8feade3dca289ed35d8c15d6a27042648a5797f0027",
        )

    def test_any_body_change_changes_fingerprint(self) -> None:
        first = self.run_script(b"REQ-001: retry once\n")
        second = self.run_script(b"REQ-001: retry twice\n")
        self.assertNotEqual(first["fingerprint"], second["fingerprint"])

    def test_file_and_stdin_use_identical_bytes(self) -> None:
        body = "REQ-001: 주문 재시도\n".encode()
        stdin_value = self.run_script(body)
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "spec.md"
            path.write_bytes(body)
            result = subprocess.run(
                ["python3", str(SCRIPT), str(path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(stdin_value, json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
