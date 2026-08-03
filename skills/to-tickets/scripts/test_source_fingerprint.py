#!/usr/bin/env python3
"""Tests for the canonical to-tickets source fingerprint."""

import json
import pathlib
import subprocess
import sys
import unittest


SCRIPT = pathlib.Path(__file__).with_name("source_fingerprint.py")
sys.path.insert(0, str(SCRIPT.parent))
import source_fingerprint as subject  # noqa: E402


class SourceFingerprintTest(unittest.TestCase):
    def test_fixed_vector_without_decisions(self):
        result = subject.fingerprint({"source_body": "approved\nsource", "decisions": []})
        self.assertEqual(result["algorithm"], "to-tickets-source-v1")
        self.assertEqual(result["decision_ids"], [])
        self.assertEqual(result["fingerprint"], "13a7b7a3021bc473433e4d1ecd7d65e99e427ac9476fd8fdce61a209e1343efe")

    def test_decisions_are_sorted_by_utf8_identifier(self):
        left = {"source_body": "S", "decisions": [{"id": "b", "body": "B"}, {"id": "a", "body": "A"}]}
        right = {"source_body": "S", "decisions": list(reversed(left["decisions"]))}
        self.assertEqual(subject.fingerprint(left), subject.fingerprint(right))
        self.assertEqual(subject.fingerprint(left)["decision_ids"], ["a", "b"])

    def test_length_framing_distinguishes_component_boundaries(self):
        first = {"source_body": "S", "decisions": [{"id": "ab", "body": "c"}]}
        second = {"source_body": "S", "decisions": [{"id": "a", "body": "bc"}]}
        self.assertNotEqual(subject.fingerprint(first)["fingerprint"], subject.fingerprint(second)["fingerprint"])

    def test_exact_newlines_and_unicode_affect_digest(self):
        lf = {"source_body": "한글\n", "decisions": []}
        crlf = {"source_body": "한글\r\n", "decisions": []}
        self.assertNotEqual(subject.fingerprint(lf)["fingerprint"], subject.fingerprint(crlf)["fingerprint"])

    def test_rejects_duplicate_ids_and_unknown_fields(self):
        with self.assertRaises(subject.FingerprintError):
            subject.fingerprint({"source_body": "S", "decisions": [{"id": "a", "body": "1"}, {"id": "a", "body": "2"}]})
        with self.assertRaises(subject.FingerprintError):
            subject.fingerprint({"source_body": "S", "decisions": [], "extra": True})

    def test_cli_reads_json_from_stdin(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps({"source_body": "S", "decisions": []}),
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "ok")


if __name__ == "__main__":
    unittest.main()
