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
    "spec-explainer": pathlib.PurePosixPath("docs/spec-explainers"),
    "decision-map": pathlib.PurePosixPath("docs/decision-maps"),
    "local-work": pathlib.PurePosixPath("docs/local-work"),
    "decision": pathlib.PurePosixPath("docs/decisions"),
    "research": pathlib.PurePosixPath("docs/research"),
    "diagnosis": pathlib.PurePosixPath("docs/reports/diagnostics"),
    "review": pathlib.PurePosixPath("docs/reports/reviews"),
}

FIXED_DOCUMENTS = {
    "domain": {
        "document_id": "domain:project",
        "relative_path": pathlib.PurePosixPath("docs/domain.md"),
        "source_key": "project",
    },
}

MAX_FILENAME_BYTES = 240
MAX_SLUG_CHARACTERS = 80


COLLECTION_ENTRYPOINTS = {
    "decision-map": "map.md",
    "local-work": "work.md",
}


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


def parse_spec_document_id(
    argument_parser: argparse.ArgumentParser,
    document_id: str | None,
    issue: int | None,
) -> tuple[str, str]:
    if not document_id:
        argument_parser.error(
            "this document kind requires --source-document-id for its authoritative spec"
        )
    parts = document_id.split(":")
    if len(parts) != 3 or parts[0] != "spec":
        argument_parser.error(
            "--source-document-id must use spec:<issue-or-date-key>:<slug>"
        )
    _, source_key, slug = parts
    issue_match = re.fullmatch(r"issue-([1-9][0-9]*)", source_key)
    if issue_match:
        source_issue = int(issue_match.group(1))
        if issue is not None and issue != source_issue:
            argument_parser.error(
                "--issue must match the issue key in --source-document-id"
            )
    else:
        try:
            iso_date(source_key)
        except argparse.ArgumentTypeError as error:
            argument_parser.error(str(error))
        if issue is not None:
            argument_parser.error(
                "--issue conflicts with the date key in --source-document-id"
            )
    try:
        fitted_slug = fit_slug_to_filename(slugify(slug), source_key)
    except ValueError as error:
        argument_parser.error(str(error))
    if slug != fitted_slug:
        argument_parser.error(
            "the source spec slug must already be normalized and portable"
        )
    return source_key, slug


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "--kind",
        choices=sorted(KIND_DIRECTORIES | FIXED_DOCUMENTS),
        required=True,
    )
    result.add_argument("--title", required=True)
    result.add_argument("--issue", type=positive_issue)
    result.add_argument(
        "--source-document-id",
        help="authoritative spec document_id required by derived document kinds",
    )
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
    fixed = FIXED_DOCUMENTS.get(args.kind)
    source_document_id = None
    if args.kind in {"spec-explainer", "local-work"}:
        source_document_id = args.source_document_id
        source_key, slug = parse_spec_document_id(
            argument_parser, source_document_id, args.issue
        )
        if args.kind == "spec-explainer":
            relative = KIND_DIRECTORIES[args.kind] / f"{source_key}-{slug}.md"
        else:
            relative = (
                KIND_DIRECTORIES[args.kind]
                / f"{source_key}-{slug}"
                / COLLECTION_ENTRYPOINTS[args.kind]
            )
        document_id = f"{args.kind}:{source_key}:{slug}"
    elif args.source_document_id:
        argument_parser.error(
            "--source-document-id is only valid for spec-explainer or local-work"
        )
    elif fixed:
        if args.issue:
            argument_parser.error(
                f"{args.kind} uses a project-wide stable identity; omit --issue"
            )
        source_key = fixed["source_key"]
        document_id = fixed["document_id"]
        relative = fixed["relative_path"]
    else:
        source_key = f"issue-{args.issue}" if args.issue else args.date
        try:
            slug = fit_slug_to_filename(slugify(args.title), source_key)
        except ValueError as error:
            argument_parser.error(str(error))
        if args.kind in COLLECTION_ENTRYPOINTS:
            relative = (
                KIND_DIRECTORIES[args.kind]
                / f"{source_key}-{slug}"
                / COLLECTION_ENTRYPOINTS[args.kind]
            )
        else:
            relative = KIND_DIRECTORIES[args.kind] / f"{source_key}-{slug}.md"
        document_id = f"{args.kind}:{source_key}:{slug}"
    root = pathlib.Path(args.root).expanduser().resolve()
    payload = {
        "absolutePath": str(root / pathlib.Path(*relative.parts)),
        "authority": "repository",
        "documentId": document_id,
        "indexPath": "docs/README.md",
        "kind": args.kind,
        "relativePath": relative.as_posix(),
        "sourceKey": source_key,
        "status": "draft",
    }
    if source_document_id:
        payload["derivedFrom"] = source_document_id
        payload["sourcePath"] = (
            KIND_DIRECTORIES["spec"] / f"{source_key}-{slug}.md"
        ).as_posix()
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
