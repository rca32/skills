#!/usr/bin/env python3
"""Compute the canonical revision fingerprint for a sanitized planning source."""

import argparse
import hashlib
import json
import pathlib
import sys


ALGORITHM = "to-tickets-source-v1"
MAGIC = (ALGORITHM + "\0").encode("ascii")
MAX_INPUT_BYTES = 10_000_000


class FingerprintError(ValueError):
    pass


def frame(value):
    encoded = value.encode("utf-8")
    return len(encoded).to_bytes(8, "big") + encoded


def fingerprint(document):
    if not isinstance(document, dict) or set(document) != {"source_body", "decisions"}:
        raise FingerprintError("input requires exactly source_body and decisions")
    source_body = document["source_body"]
    decisions = document["decisions"]
    if not isinstance(source_body, str) or not isinstance(decisions, list):
        raise FingerprintError("source_body must be a string and decisions must be a list")

    normalized = []
    seen = set()
    for item in decisions:
        if not isinstance(item, dict) or set(item) != {"id", "body"}:
            raise FingerprintError("each decision requires exactly id and body")
        identifier = item["id"]
        body = item["body"]
        if not isinstance(identifier, str) or not identifier or not isinstance(body, str):
            raise FingerprintError("decision id must be non-empty and body must be a string")
        if identifier in seen:
            raise FingerprintError("decision ids must be unique")
        seen.add(identifier)
        normalized.append((identifier, body))
    normalized.sort(key=lambda item: item[0].encode("utf-8"))

    digest = hashlib.sha256()
    digest.update(MAGIC)
    digest.update(frame(source_body))
    digest.update(len(normalized).to_bytes(8, "big"))
    for identifier, body in normalized:
        digest.update(frame(identifier))
        digest.update(frame(body))
    return {
        "algorithm": ALGORITHM,
        "decision_ids": [identifier for identifier, _ in normalized],
        "fingerprint": digest.hexdigest(),
    }


def read_document(path):
    if path == "-":
        payload = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    else:
        candidate = pathlib.Path(path)
        if candidate.stat().st_size > MAX_INPUT_BYTES:
            raise FingerprintError("input exceeds size limit")
        payload = candidate.read_bytes()
    if len(payload) > MAX_INPUT_BYTES:
        raise FingerprintError("input exceeds size limit")
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FingerprintError("input must be UTF-8 JSON") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSON input file, or - for stdin")
    args = parser.parse_args()
    try:
        result = fingerprint(read_document(args.input))
    except (OSError, FingerprintError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
