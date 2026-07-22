#!/usr/bin/env python3
"""Check or initialize the bundled GitHub tracker labels for one repository."""

from __future__ import annotations

import argparse
import base64
import dataclasses
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from collections.abc import Sequence


LEASE_SCRIPT = pathlib.Path(__file__).with_name("issue_lease.py")
REPOSITORY_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
REMOTE_PATTERNS = (
    re.compile(r"https://github\.com/(?P<repo>[^/\s]+/[^/\s]+?)(?:\.git)?/?$"),
    re.compile(r"git@github\.com:(?P<repo>[^/\s]+/[^/\s]+?)(?:\.git)?$"),
    re.compile(r"ssh://git@github\.com/(?P<repo>[^/\s]+/[^/\s]+?)(?:\.git)?/?$"),
)


@dataclasses.dataclass(frozen=True)
class LabelSpec:
    name: str
    description: str
    color: str


LABELS = (
    LabelSpec("상태: 분류 필요", "사실 확인이나 범위 결정이 더 필요함", "D4C5F9"),
    LabelSpec("상태: 정보 필요", "사람이 답할 수 있는 구체적인 정보가 빠져 있음", "FBCA04"),
    LabelSpec("상태: 에이전트 작업 가능", "설명과 blocker가 완전해 에이전트가 구현할 수 있음", "0E8A16"),
    LabelSpec("상태: 사람 검토 필요", "사람이 승인·권한 부여·병합·수동 작업을 해야 함", "B60205"),
    LabelSpec("상태: 진행하지 않음", "중복·기구현·거절로 더 진행하지 않음", "CCCCCC"),
    LabelSpec("유형: 버그", "확인된 잘못된 동작을 수정하는 요청", "D73A4A"),
    LabelSpec("유형: 개선", "새 동작이나 기존 동작 개선 요청", "A2EEEF"),
)


class LabelError(RuntimeError):
    pass


class UnknownMutation(LabelError):
    def __init__(self, message: str, created: Sequence[str]) -> None:
        super().__init__(message)
        self.created = list(created)


def emit(status: str, **details: object) -> None:
    print(json.dumps({"status": status, **details}, ensure_ascii=False, sort_keys=True))


def run(command: Sequence[str], cwd: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )


def repository_root(value: pathlib.Path) -> pathlib.Path:
    candidate = value.resolve()
    result = run(["git", "rev-parse", "--show-toplevel"], candidate)
    if result.returncode != 0:
        raise LabelError("repository path must be an existing Git repository")
    root = pathlib.Path(result.stdout.strip()).resolve()
    if root != candidate:
        raise LabelError("repository path must name the Git repository root")
    return root


def parse_github_remote(value: str) -> str:
    for pattern in REMOTE_PATTERNS:
        match = pattern.fullmatch(value.strip())
        if match:
            repository = match.group("repo")
            if REPOSITORY_RE.fullmatch(repository):
                return repository
    raise LabelError("remote must be a canonical github.com owner/repository URL")


def resolve_repository(root: pathlib.Path, remote: str) -> str:
    result = run(["git", "remote", "get-url", remote], root)
    if result.returncode != 0:
        raise LabelError(f"unable to read canonical Git remote: {remote}")
    requested = parse_github_remote(result.stdout)
    authenticated = run(["gh", "auth", "status", "--hostname", "github.com"], root)
    if authenticated.returncode != 0:
        raise LabelError("gh is not authenticated for github.com")
    viewed = run(
        ["gh", "repo", "view", requested, "--json", "nameWithOwner"],
        root,
    )
    if viewed.returncode != 0:
        raise LabelError("authenticated account cannot read the canonical GitHub repository")
    try:
        observed = json.loads(viewed.stdout)["nameWithOwner"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise LabelError("gh returned an invalid repository identity") from error
    if str(observed).casefold() != requested.casefold():
        raise LabelError("GitHub repository identity does not match the canonical remote")
    return str(observed)


def fetch_catalog(root: pathlib.Path, repository: str) -> list[dict[str, str]]:
    try:
        result = run(
            [
                "gh",
                "api",
                "--paginate",
                "--slurp",
                f"repos/{repository}/labels?per_page=100",
            ],
            root,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise LabelError("GitHub label catalog read timed out or failed") from error
    if result.returncode != 0:
        raise LabelError("unable to read the complete GitHub label catalog")
    try:
        pages = json.loads(result.stdout)
        raw_labels = [item for page in pages for item in page]
        return [
            {
                "name": str(item["name"]),
                "description": str(item.get("description") or ""),
                "color": str(item["color"]).upper(),
            }
            for item in raw_labels
        ]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise LabelError("gh returned an invalid label catalog") from error


def inspect(catalog: Sequence[dict[str, str]]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for spec in LABELS:
        matches = [item for item in catalog if item["name"] == spec.name]
        if not matches:
            result.append({"status": "missing", **dataclasses.asdict(spec)})
            continue
        if len(matches) != 1 or matches[0]["description"] != spec.description:
            result.append(
                {
                    "status": "conflict",
                    **dataclasses.asdict(spec),
                    "observed": matches,
                }
            )
            continue
        result.append(
            {
                "status": "current",
                **dataclasses.asdict(spec),
                "observedColor": matches[0]["color"],
                "colorDrift": matches[0]["color"] != spec.color,
            }
        )
    return result


def snapshot_token(repository: str, observations: Sequence[dict[str, object]]) -> str:
    payload = {
        "labels": list(observations),
        "repository": repository,
        "version": 1,
    }
    digest = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
    ).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def validate_snapshot(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]{43}", value):
        return value
    raise LabelError("expected label snapshot token is malformed")


def check_planning_lease(root: pathlib.Path, remote: str, session: str) -> None:
    result = run(
        [
            sys.executable,
            str(LEASE_SCRIPT),
            "check",
            "0",
            "--remote",
            remote,
            "--session",
            session,
        ],
        root,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise LabelError("planning lease check returned invalid output") from error
    if (
        result.returncode != 0
        or payload.get("status") != "owned"
        or payload.get("lease", {}).get("purpose") != "planning"
    ):
        raise LabelError("repository-wide planning lease is not owned by this session")


def create_label(root: pathlib.Path, repository: str, spec: LabelSpec) -> subprocess.CompletedProcess[str]:
    return run(
        [
            "gh",
            "api",
            "--method",
            "POST",
            f"repos/{repository}/labels",
            "-f",
            f"name={spec.name}",
            "-f",
            f"description={spec.description}",
            "-f",
            f"color={spec.color}",
        ],
        root,
    )


def install_labels(
    root: pathlib.Path,
    remote: str,
    repository: str,
    session: str,
    expected_snapshot: str,
) -> tuple[str, list[str]]:
    expected_snapshot = validate_snapshot(expected_snapshot)
    catalog = fetch_catalog(root, repository)
    observations = inspect(catalog)
    if snapshot_token(repository, observations) != expected_snapshot:
        raise LabelError("tracker labels no longer match the inspected snapshot")
    conflicts = [item for item in observations if item["status"] == "conflict"]
    if conflicts:
        raise LabelError("existing tracker labels conflict with the bundled contract")
    missing = {str(item["name"]) for item in observations if item["status"] == "missing"}
    if not missing:
        return "unchanged", []

    created: list[str] = []
    for spec in LABELS:
        if spec.name not in missing:
            continue
        check_planning_lease(root, remote, session)
        try:
            attempted = create_label(root, repository, spec)
        except (OSError, subprocess.SubprocessError):
            attempted = None
        try:
            refreshed = inspect(fetch_catalog(root, repository))
        except (LabelError, OSError, subprocess.SubprocessError) as error:
            raise UnknownMutation(
                f"label creation result is unknown for {spec.name}: {error}", created
            ) from error
        observed = next(item for item in refreshed if item["name"] == spec.name)
        if observed["status"] == "current":
            created.append(spec.name)
            continue
        if attempted is None or attempted.returncode != 0:
            raise UnknownMutation(
                f"label creation result is unknown for {spec.name}; reconcile before retrying",
                created,
            )
        raise UnknownMutation(
            f"GitHub did not read back the created label {spec.name}; reconcile before retrying",
            created,
        )

    try:
        final = inspect(fetch_catalog(root, repository))
    except (LabelError, OSError, subprocess.SubprocessError) as error:
        raise UnknownMutation(
            f"final tracker label readback is unknown: {error}", created
        ) from error
    if any(item["status"] != "current" for item in final):
        raise UnknownMutation("tracker label initialization did not reconcile exactly", created)
    return "initialized", created


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("check", "install"):
        command = commands.add_parser(name)
        command.add_argument("repository_root", type=pathlib.Path)
        command.add_argument("--remote", default="origin")
        if name == "install":
            command.add_argument("--expected-snapshot", required=True)
            command.add_argument("--lease-session", required=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = repository_root(args.repository_root)
        repository = resolve_repository(root, args.remote)
        if args.command == "check":
            observations = inspect(fetch_catalog(root, repository))
            token = snapshot_token(repository, observations)
            conflicts = [item for item in observations if item["status"] == "conflict"]
            missing = [item for item in observations if item["status"] == "missing"]
            status = "conflict" if conflicts else "missing" if missing else "current"
            emit(status, labels=observations, repository=repository, snapshot=token)
            return 2 if conflicts else 1 if missing else 0
        status, created = install_labels(
            root,
            args.remote,
            repository,
            args.lease_session,
            args.expected_snapshot,
        )
        emit(status, created=created, repository=repository)
        return 0
    except UnknownMutation as error:
        emit("unknown", created=error.created, error=str(error))
        return 3
    except (LabelError, OSError, subprocess.SubprocessError) as error:
        emit("error", error=str(error))
        return 2


if __name__ == "__main__":
    sys.exit(main())
