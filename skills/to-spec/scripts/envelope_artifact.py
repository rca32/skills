#!/usr/bin/env python3
"""Encode, validate, or extract a canonical conversation artifact envelope."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys


BEGIN = b"---BEGIN CODEX CONVERSATION ARTIFACT---\n"
CONTENT = b"---CONTENT---\n"
END = b"\n---END CODEX CONVERSATION ARTIFACT---\n"
MAX_CONTENT_BYTES = 10 * 1024 * 1024
ARTIFACT_ID = re.compile(r"[a-z0-9][a-z0-9:._-]{0,199}\Z")


def read_bytes(path: str | None, limit: int) -> bytes:
    if path:
        candidate = pathlib.Path(path)
        if candidate.stat().st_size > limit:
            raise ValueError("input exceeds the allowed size")
        with candidate.open("rb") as stream:
            value = stream.read(limit + 1)
    else:
        value = sys.stdin.buffer.read(limit + 1)
    if len(value) > limit:
        raise ValueError("input exceeds the allowed size")
    try:
        value.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("content must be valid UTF-8") from error
    return value


def encode(artifact_id: str, body: bytes) -> bytes:
    if not ARTIFACT_ID.fullmatch(artifact_id):
        raise ValueError("artifact ID contains unsupported characters")
    header = (
        f"id: {artifact_id}\ncontent_bytes: {len(body)}\n".encode("ascii")
    )
    return BEGIN + header + CONTENT + body + END


def decode(envelope: bytes) -> tuple[str, bytes]:
    if not envelope.startswith(BEGIN):
        raise ValueError("missing canonical begin marker")
    content_at = envelope.find(CONTENT, len(BEGIN))
    if content_at < 0:
        raise ValueError("missing canonical content marker")
    header = envelope[len(BEGIN) : content_at]
    try:
        lines = header.decode("ascii").splitlines()
    except UnicodeDecodeError as error:
        raise ValueError("envelope header must be ASCII") from error
    if len(lines) != 2 or not lines[0].startswith("id: ") or not lines[1].startswith(
        "content_bytes: "
    ):
        raise ValueError("envelope header is not canonical")
    artifact_id = lines[0].removeprefix("id: ")
    if not ARTIFACT_ID.fullmatch(artifact_id):
        raise ValueError("artifact ID contains unsupported characters")
    length_text = lines[1].removeprefix("content_bytes: ")
    if not length_text.isascii() or not length_text.isdecimal():
        raise ValueError("content_bytes must be an unsigned decimal integer")
    expected_length = int(length_text)
    if length_text != str(expected_length):
        raise ValueError("content_bytes is not canonical")
    if expected_length > MAX_CONTENT_BYTES:
        raise ValueError("content exceeds the 10 MiB limit")
    body_at = content_at + len(CONTENT)
    body_end = body_at + expected_length
    if envelope[body_end:] != END:
        raise ValueError("content length mismatch or trailing envelope data")
    body = envelope[body_at:body_end]
    try:
        body.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("content must be valid UTF-8") from error
    return artifact_id, body


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="action", required=True)
    encoder = subparsers.add_parser("encode")
    encoder.add_argument("--id", required=True)
    encoder.add_argument("path", nargs="?")
    for action in ("validate", "extract"):
        command = subparsers.add_parser(action)
        command.add_argument("path", nargs="?")
    return result


def main() -> None:
    args = parser().parse_args()
    try:
        if args.action == "encode":
            sys.stdout.buffer.write(
                encode(args.id, read_bytes(args.path, MAX_CONTENT_BYTES))
            )
            return
        envelope = read_bytes(args.path, MAX_CONTENT_BYTES + 1024)
        artifact_id, body = decode(envelope)
        if args.action == "extract":
            sys.stdout.buffer.write(body)
            return
        print(
            json.dumps(
                {
                    "artifactId": artifact_id,
                    "contentBytes": len(body),
                    "valid": True,
                },
                sort_keys=True,
            )
        )
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
