#!/usr/bin/env python3
"""Render, install, or verify the managed work-github-issue AGENTS.md contract."""

from __future__ import annotations

import argparse
import base64
import dataclasses
import hashlib
import json
import os
import pathlib
import re
import stat
import subprocess
import sys


START = "<!-- work-github-issue:publication-contract:v1:start -->"
END = "<!-- work-github-issue:publication-contract:v1:end -->"
TEMPLATE = pathlib.Path(__file__).parent.parent / "references" / "consumer-agents-contract.md"
TARGET_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*")
MERGE_METHODS = {
    "merge": "a merge commit",
    "rebase": "rebase merge",
    "squash": "squash merge",
}
SECURE_DIR_FD_SUPPORT = all(
    operation in os.supports_dir_fd for operation in (os.open, os.mkdir, os.rmdir, os.stat)
)


class ContractError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class ContractSnapshot:
    content: str
    exists: bool
    root_identity: tuple[int, int]
    file_identity: tuple[int, int] | None


def emit(status: str, **details: object) -> None:
    print(json.dumps({"status": status, **details}, ensure_ascii=False, sort_keys=True))


def validate_target(value: str) -> str:
    parts = value.split("/")
    if (
        not TARGET_RE.fullmatch(value)
        or ".." in value
        or "//" in value
        or "@{" in value
        or value.endswith("/")
        or any(part.startswith(".") or part.endswith(".lock") for part in parts)
    ):
        raise ContractError("integration target must be an explicit safe branch name")
    result = subprocess.run(
        ["git", "check-ref-format", "--branch", value],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise ContractError("integration target must be a valid Git branch name")
    return value


def render_contract(target: str, merge_method: str) -> str:
    target = validate_target(target)
    template = TEMPLATE.read_text(encoding="utf-8").strip()
    if template.count(START) != 1 or template.count(END) != 1:
        raise ContractError("bundled contract markers are invalid")
    return (
        template.replace("{{INTEGRATION_TARGET}}", target)
        .replace("{{MERGE_METHOD}}", MERGE_METHODS[merge_method])
    )


def validate_repository_target(path: pathlib.Path) -> tuple[int, int]:
    if path.name != "AGENTS.md":
        raise ContractError("target file must be named AGENTS.md")
    current = pathlib.Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise ContractError(f"refusing symlinked path component: {current}")
        if not current.exists() and current != path:
            raise ContractError("AGENTS.md parent directory must already exist")
    if not path.parent.is_dir():
        raise ContractError("AGENTS.md parent directory must already exist")
    root_snapshot = os.stat(path.parent, follow_symlinks=False)
    if not stat.S_ISDIR(root_snapshot.st_mode):
        raise ContractError("Git repository root must be a real directory")
    result = subprocess.run(
        ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise ContractError("AGENTS.md target must be the root of an existing Git repository")
    repository_root = pathlib.Path(result.stdout.strip()).resolve()
    if path.parent != repository_root or path != repository_root / "AGENTS.md":
        raise ContractError("managed contract must target the Git repository root AGENTS.md")
    return root_snapshot.st_dev, root_snapshot.st_ino


def require_secure_open_support() -> None:
    if (
        not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
        or not SECURE_DIR_FD_SUPPORT
    ):
        raise ContractError(
            "secure no-follow installation is unavailable on this platform; use render"
        )


def open_directory_chain(path: pathlib.Path) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open(path.anchor, flags)
    try:
        for part in path.parts[1:]:
            child = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def verify_repository_identity(
    parent_descriptor: int,
    root_descriptor: int,
    root_name: str,
    expected_identity: tuple[int, int],
) -> None:
    opened = os.fstat(root_descriptor)
    try:
        named = os.stat(root_name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError as error:
        raise ContractError("Git repository root was removed during installation") from error
    if (
        not stat.S_ISDIR(named.st_mode)
        or (opened.st_dev, opened.st_ino) != expected_identity
        or (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino)
    ):
        raise ContractError("Git repository root changed during validation")


def open_repository_root(path: pathlib.Path) -> tuple[int, int, str, tuple[int, int]]:
    require_secure_open_support()
    expected_identity = validate_repository_target(path)
    if path.parent == path.parent.parent:
        raise ContractError("refusing to install a managed contract at filesystem root")
    parent_descriptor = open_directory_chain(path.parent.parent)
    root_name = path.parent.name
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        root_descriptor = os.open(root_name, flags, dir_fd=parent_descriptor)
    except BaseException:
        os.close(parent_descriptor)
        raise
    try:
        verify_repository_identity(
            parent_descriptor,
            root_descriptor,
            root_name,
            expected_identity,
        )
        git_entry = os.stat(".git", dir_fd=root_descriptor, follow_symlinks=False)
        if not (stat.S_ISDIR(git_entry.st_mode) or stat.S_ISREG(git_entry.st_mode)):
            raise ContractError("Git repository metadata is not a regular file or directory")
        return root_descriptor, parent_descriptor, root_name, expected_identity
    except BaseException:
        os.close(root_descriptor)
        os.close(parent_descriptor)
        raise


def open_agents_file(
    root_descriptor: int,
    create: bool,
    writable: bool = False,
) -> tuple[int | None, bool]:
    flags = (
        (os.O_RDWR | os.O_APPEND if writable else os.O_RDONLY)
        | os.O_NOFOLLOW
        | os.O_NONBLOCK
    )
    try:
        descriptor = os.open("AGENTS.md", flags, dir_fd=root_descriptor)
        exists = True
    except FileNotFoundError:
        if not create:
            return None, False
        descriptor = os.open(
            "AGENTS.md",
            flags | os.O_CREAT | os.O_EXCL,
            0o644,
            dir_fd=root_descriptor,
        )
        exists = False
    opened = os.fstat(descriptor)
    if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
        os.close(descriptor)
        raise ContractError("AGENTS.md must be one regular, non-hard-linked file")
    return descriptor, exists


def read_descriptor(descriptor: int) -> str:
    os.lseek(descriptor, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while True:
        chunk = os.read(descriptor, 65536)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks).decode("utf-8")


def verify_named_identity(root_descriptor: int, descriptor: int) -> None:
    opened = os.fstat(descriptor)
    try:
        named = os.stat("AGENTS.md", dir_fd=root_descriptor, follow_symlinks=False)
    except FileNotFoundError as error:
        raise ContractError("AGENTS.md was removed during installation") from error
    if (
        not stat.S_ISREG(named.st_mode)
        or named.st_nlink != 1
        or (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino)
    ):
        raise ContractError("AGENTS.md path identity changed during installation")


def read_contract(path: pathlib.Path) -> ContractSnapshot:
    root_descriptor, parent_descriptor, root_name, expected_identity = open_repository_root(path)
    try:
        verify_repository_identity(
            parent_descriptor, root_descriptor, root_name, expected_identity
        )
        descriptor, exists = open_agents_file(root_descriptor, create=False)
        if not exists or descriptor is None:
            return ContractSnapshot("", False, expected_identity, None)
        try:
            value = read_descriptor(descriptor)
            verify_named_identity(root_descriptor, descriptor)
            verify_repository_identity(
                parent_descriptor, root_descriptor, root_name, expected_identity
            )
            opened = os.fstat(descriptor)
            return ContractSnapshot(
                value,
                True,
                expected_identity,
                (opened.st_dev, opened.st_ino),
            )
        finally:
            os.close(descriptor)
    finally:
        os.close(root_descriptor)
        os.close(parent_descriptor)


def content_sha256(value: str, exists: bool) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest() if exists else "absent"


def contract_sha256(block: str) -> str:
    return hashlib.sha256(block.encode("utf-8")).hexdigest()


def snapshot_token(snapshot: ContractSnapshot, block: str) -> str:
    payload = {
        "contentSha256": content_sha256(snapshot.content, snapshot.exists),
        "contractSha256": contract_sha256(block),
        "fileIdentity": list(snapshot.file_identity) if snapshot.file_identity else None,
        "rootIdentity": list(snapshot.root_identity),
        "version": 1,
    }
    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).decode("ascii")
    return encoded.rstrip("=")


def validate_expected_snapshot(value: str) -> str:
    if 20 <= len(value) <= 2048 and re.fullmatch(r"[A-Za-z0-9_-]+", value):
        return value
    raise ContractError("expected snapshot token is malformed")


def managed_span(text: str) -> tuple[int, int] | None:
    starts = [match.start() for match in re.finditer(re.escape(START), text)]
    ends = [match.end() for match in re.finditer(re.escape(END), text)]
    if not starts and not ends:
        return None
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ContractError("AGENTS.md contains duplicate or unmatched managed markers")
    return starts[0], ends[0]


def desired_text(current: str, block: str) -> str:
    span = managed_span(current)
    if span is not None:
        start, end = span
        return current[:start] + block + current[end:]
    if not current:
        return "# Repository agent instructions\n\n" + block + "\n"
    separator = "" if current.endswith("\n\n") else "\n" if current.endswith("\n") else "\n\n"
    return current + separator + block + "\n"


def write_once(descriptor: int, value: str) -> None:
    payload = value.encode("utf-8")
    written = os.write(descriptor, payload)
    if written != len(payload):
        raise ContractError("AGENTS.md write was partial; reconcile the file before retrying")
    os.fsync(descriptor)


def install_contract(path: pathlib.Path, block: str, expected_snapshot: str) -> str:
    expected_snapshot = validate_expected_snapshot(expected_snapshot)
    root_descriptor, parent_descriptor, root_name, expected_identity = open_repository_root(path)
    lock_name = ".AGENTS.md.work-github-issue.lock"
    status: str | None = None
    try:
        verify_repository_identity(
            parent_descriptor, root_descriptor, root_name, expected_identity
        )
        try:
            os.mkdir(lock_name, 0o700, dir_fd=root_descriptor)
        except FileExistsError as error:
            raise ContractError(
                f"installer lock exists; inspect and reconcile before removing it: {path.parent / lock_name}"
            ) from error
        try:
            verify_repository_identity(
                parent_descriptor, root_descriptor, root_name, expected_identity
            )
            descriptor, exists = open_agents_file(
                root_descriptor, create=False, writable=True
            )
            if not exists or descriptor is None:
                current_snapshot = ContractSnapshot("", False, expected_identity, None)
            else:
                current = read_descriptor(descriptor)
                opened = os.fstat(descriptor)
                current_snapshot = ContractSnapshot(
                    current,
                    True,
                    expected_identity,
                    (opened.st_dev, opened.st_ino),
                )
            if snapshot_token(current_snapshot, block) != expected_snapshot:
                if descriptor is not None:
                    os.close(descriptor)
                raise ContractError(
                    "repository contract no longer matches the inspected snapshot; no update was installed"
                )
            if descriptor is None:
                descriptor, exists = open_agents_file(
                    root_descriptor, create=True, writable=True
                )
                if exists and descriptor is not None:
                    reopened_content = read_descriptor(descriptor)
                    reopened = os.fstat(descriptor)
                    reopened_snapshot = ContractSnapshot(
                        reopened_content,
                        True,
                        expected_identity,
                        (reopened.st_dev, reopened.st_ino),
                    )
                    if snapshot_token(reopened_snapshot, block) != expected_snapshot:
                        os.close(descriptor)
                        descriptor = None
                        raise ContractError(
                            "repository contract no longer matches the inspected snapshot; no update was installed"
                        )
            assert descriptor is not None
            try:
                current = read_descriptor(descriptor)
                verify_named_identity(root_descriptor, descriptor)
                opened = os.fstat(descriptor)
                if current_snapshot.exists:
                    before_write_snapshot = ContractSnapshot(
                        current,
                        True,
                        expected_identity,
                        (opened.st_dev, opened.st_ino),
                    )
                    unchanged = (
                        snapshot_token(before_write_snapshot, block)
                        == expected_snapshot
                    )
                else:
                    unchanged = not exists and current == ""
                if not unchanged:
                    raise ContractError(
                        "repository contract changed after validation; no update was installed"
                    )
                desired = desired_text(current, block)
                span = managed_span(current)
                if span is not None:
                    if current == desired:
                        status = "unchanged"
                    else:
                        raise ContractError(
                            "managed contract differs; resolve the existing policy explicitly instead of replacing it"
                        )
                else:
                    addition = desired[len(current) :] if exists else desired
                    verify_repository_identity(
                        parent_descriptor, root_descriptor, root_name, expected_identity
                    )
                    verify_named_identity(root_descriptor, descriptor)
                    write_once(descriptor, addition)
                    verify_named_identity(root_descriptor, descriptor)
                    verify_repository_identity(
                        parent_descriptor, root_descriptor, root_name, expected_identity
                    )
                    observed = read_descriptor(descriptor)
                    observed_span = managed_span(observed)
                    if (
                        observed != desired
                        or observed_span is None
                        or observed[slice(*observed_span)] != block
                    ):
                        raise ContractError(
                            "installed content or concurrent edits did not reconcile exactly; preserve the file and resolve manually"
                        )
                    status = "installed"
            finally:
                os.close(descriptor)
        finally:
            os.rmdir(lock_name, dir_fd=root_descriptor)
        verify_repository_identity(
            parent_descriptor, root_descriptor, root_name, expected_identity
        )
        assert status is not None
        return status
    finally:
        os.close(root_descriptor)
        os.close(parent_descriptor)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)

    def add_policy_options(command: argparse.ArgumentParser) -> None:
        command.add_argument("--integration-target", default="main")
        command.add_argument("--merge-method", choices=sorted(MERGE_METHODS), default="squash")

    render = subparsers.add_parser("render", help="print the managed contract")
    add_policy_options(render)
    for name in ("check", "install"):
        command = subparsers.add_parser(name, help=f"{name} the managed contract")
        command.add_argument("agents_file", type=pathlib.Path)
        if name == "install":
            command.add_argument("--expected-snapshot", required=True)
        add_policy_options(command)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        block = render_contract(args.integration_target, args.merge_method)
        if args.command == "render":
            print(block)
            return 0
        path = pathlib.Path(os.path.abspath(args.agents_file))
        if args.command == "check":
            snapshot = read_contract(path)
            desired = desired_text(snapshot.content, block)
            status = "current" if snapshot.content == desired else "missing-or-stale"
            emit(
                status,
                contract=block,
                contractSha256=contract_sha256(block),
                path=str(path),
                sha256=content_sha256(snapshot.content, snapshot.exists),
                snapshot=snapshot_token(snapshot, block),
            )
            return 0 if status == "current" else 1
        status = install_contract(path, block, args.expected_snapshot)
        emit(status, path=str(path))
        return 0
    except (ContractError, OSError, UnicodeError) as error:
        emit("error", error=str(error))
        return 2


if __name__ == "__main__":
    sys.exit(main())
