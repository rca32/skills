#!/usr/bin/env python3
"""Fingerprint an exact authoritative spec body for derived representations."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys


ALGORITHM = "to-spec-body-v1"
MAGIC = (ALGORITHM + "\0").encode("ascii")
MAX_INPUT_BYTES = 10_000_000


def read_body(path: str) -> bytes:
    if path == "-":
        body = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    else:
        candidate = pathlib.Path(path)
        if candidate.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError("spec body exceeds size limit")
        with candidate.open("rb") as stream:
            body = stream.read(MAX_INPUT_BYTES + 1)
    if len(body) > MAX_INPUT_BYTES:
        raise ValueError("spec body exceeds size limit")
    return body


def fingerprint(body: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(MAGIC)
    digest.update(len(body).to_bytes(8, "big"))
    digest.update(body)
    return f"{ALGORITHM}:{digest.hexdigest()}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="spec file or - for stdin")
    args = parser.parse_args()
    try:
        result = fingerprint(read_body(args.input))
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, sort_keys=True))
        return 2
    print(json.dumps({"status": "ok", "fingerprint": result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
