#!/usr/bin/env python3
"""Resolve fallback paths for durable development documents."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import unicodedata


KIND_DIRECTORIES = {
    "spec": pathlib.PurePosixPath("docs/specs"),
    "decision": pathlib.PurePosixPath("docs/decisions"),
    "research": pathlib.PurePosixPath("docs/research"),
    "diagnosis": pathlib.PurePosixPath("docs/reports/diagnostics"),
    "review": pathlib.PurePosixPath("docs/reports/reviews"),
}

MAX_FILENAME_BYTES = 240
MAX_SLUG_CHARACTERS = 80


def positive_issue(value: str) -> int:
    issue = int(value)
    if issue <= 0:
        raise argparse.ArgumentTypeError("issue must be a positive integer")
    return issue


def iso_date(value: str) -> str:
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from error


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    slug = "".join(character if character.isalnum() else "-" for character in normalized)
    slug = re.sub(r"-+", "-", slug).strip("-")
    slug = slug[:MAX_SLUG_CHARACTERS].rstrip("-")
    return slug or "document"


def fit_slug_to_filename(slug: str, source_key: str) -> str:
    fixed_bytes = len(f"{source_key}-.md".encode("utf-8"))
    available_bytes = MAX_FILENAME_BYTES - fixed_bytes
    if available_bytes < 1:
        raise ValueError("source key is too long for a portable filename")

    encoded = slug.encode("utf-8")
    if len(encoded) <= available_bytes:
        return slug

    fitted = encoded[:available_bytes].decode("utf-8", errors="ignore").rstrip("-")
    if not fitted:
        raise ValueError("title cannot fit in a portable filename")
    return fitted


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--kind", choices=sorted(KIND_DIRECTORIES), required=True)
    result.add_argument("--title", required=True)
    result.add_argument("--issue", type=positive_issue)
    result.add_argument(
        "--date",
        type=iso_date,
        default=dt.datetime.now(dt.timezone.utc).date().isoformat(),
    )
    result.add_argument("--root", default=".")
    return result


def main() -> None:
    argument_parser = parser()
    args = argument_parser.parse_args()
    source_key = f"issue-{args.issue}" if args.issue else args.date
    try:
        slug = fit_slug_to_filename(slugify(args.title), source_key)
    except ValueError as error:
        argument_parser.error(str(error))
    filename = f"{source_key}-{slug}.md"
    relative = KIND_DIRECTORIES[args.kind] / filename
    root = pathlib.Path(args.root).expanduser().resolve()
    payload = {
        "absolutePath": str(root / pathlib.Path(*relative.parts)),
        "authority": "repository",
        "documentId": f"{args.kind}:{source_key}:{slug}",
        "indexPath": "docs/README.md",
        "kind": args.kind,
        "relativePath": relative.as_posix(),
        "sourceKey": source_key,
        "status": "draft",
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
