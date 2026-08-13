#!/usr/bin/env python3
"""Tests for canonical conversation artifact envelopes."""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).with_name("envelope_artifact.py")


def run(*args: str, stdin: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class EnvelopeArtifactTest(unittest.TestCase):
    def encode(self, body: bytes) -> bytes:
        result = run("encode", "--id", "conversation-spec:checkout-v1", stdin=body)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        return result.stdout

    def test_unicode_byte_length_and_round_trip(self) -> None:
        body = "# 결제 명세\n\n처리 중\n".encode()
        envelope = self.encode(body)
        self.assertIn(f"content_bytes: {len(body)}\n".encode(), envelope)
        validated = run("validate", stdin=envelope)
        self.assertEqual(validated.returncode, 0, validated.stderr.decode())
        self.assertEqual(json.loads(validated.stdout)["contentBytes"], len(body))
        extracted = run("extract", stdin=envelope)
        self.assertEqual(extracted.returncode, 0, extracted.stderr.decode())
        self.assertEqual(extracted.stdout, body)

    def test_marker_like_content_does_not_end_envelope(self) -> None:
        body = b"before\n---END CODEX CONVERSATION ARTIFACT---\nafter"
        envelope = self.encode(body)
        extracted = run("extract", stdin=envelope)
        self.assertEqual(extracted.returncode, 0, extracted.stderr.decode())
        self.assertEqual(extracted.stdout, body)

    def test_truncated_content_fails_closed(self) -> None:
        envelope = self.encode(b"normative body")
        result = run("validate", stdin=envelope[:-5])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"mismatch", result.stderr)

    def test_declared_length_mismatch_fails_closed(self) -> None:
        envelope = self.encode(b"abc").replace(
            b"content_bytes: 3", b"content_bytes: 4", 1
        )
        result = run("extract", stdin=envelope)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"mismatch", result.stderr)

    def test_oversized_stdin_fails_closed(self) -> None:
        result = run(
            "encode",
            "--id",
            "conversation-spec:large",
            stdin=b"x" * (10 * 1024 * 1024 + 1),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"allowed size", result.stderr)

    def test_oversized_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "large.md"
            path.write_bytes(b"x" * (10 * 1024 * 1024 + 1))
            result = run(
                "encode",
                "--id",
                "conversation-spec:large",
                str(path),
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"allowed size", result.stderr)


if __name__ == "__main__":
    unittest.main()
