#!/usr/bin/env python3
"""Check, diff, install, or verify the bundled personal Luna worker profile."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import pathlib
import secrets
import shutil
import stat
import subprocess
import sys
import time
from dataclasses import dataclass


ASSET = pathlib.Path(__file__).parent.parent / "assets" / "luna-worker.toml"
FILENAME = "luna-worker.toml"
AGENT_NAME = "luna_worker"
MODEL = "gpt-5.6-luna"
REASONING_EFFORT = "max"
MAX_PROFILE_BYTES = 1_000_000
ASSET_SHA256 = "c125dc713fc2247948c78c612e9df78052004286ef6107686738d45865c45665"


class SetupError(RuntimeError):
    pass


@dataclass(frozen=True)
class TargetState:
    kind: str
    content: bytes | None
    identity: tuple[int, int] | None
    mode: int | None
    links: int | None


def emit(status: str, **details: object) -> None:
    print(json.dumps({"status": status, **details}, ensure_ascii=False, sort_keys=True))


def read_asset() -> bytes:
    payload = ASSET.read_bytes()
    try:
        payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise SetupError("bundled Luna worker asset is not valid UTF-8") from error
    if hashlib.sha256(payload).hexdigest() != ASSET_SHA256:
        raise SetupError("bundled Luna worker asset does not match its reviewed package digest")
    return payload


def resolve_codex_home(value: str | None) -> pathlib.Path:
    raw = value or os.environ.get("CODEX_HOME")
    path = pathlib.Path(raw).expanduser() if raw else pathlib.Path.home() / ".codex"
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as error:
        raise SetupError("CODEX_HOME must already exist") from error
    snapshot = os.stat(resolved, follow_symlinks=False)
    if not stat.S_ISDIR(snapshot.st_mode):
        raise SetupError("CODEX_HOME must resolve to a directory")
    if resolved == pathlib.Path(resolved.anchor):
        raise SetupError("refusing filesystem root as CODEX_HOME")
    return resolved


def target_path(codex_home: pathlib.Path) -> pathlib.Path:
    return codex_home / "agents" / FILENAME


def read_target(path: pathlib.Path) -> TargetState:
    try:
        named = os.stat(path, follow_symlinks=False)
    except FileNotFoundError:
        return TargetState("missing", None, None, None, None)
    if stat.S_ISLNK(named.st_mode):
        return TargetState("symlink", None, (named.st_dev, named.st_ino), named.st_mode, named.st_nlink)
    if not stat.S_ISREG(named.st_mode):
        return TargetState("non-regular", None, (named.st_dev, named.st_ino), named.st_mode, named.st_nlink)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino):
            raise SetupError("Luna worker target changed while reading")
        if opened.st_nlink != 1:
            return TargetState("hard-linked", None, (opened.st_dev, opened.st_ino), opened.st_mode, opened.st_nlink)
        if opened.st_size > MAX_PROFILE_BYTES:
            return TargetState("oversized", None, (opened.st_dev, opened.st_ino), opened.st_mode, opened.st_nlink)
        with os.fdopen(os.dup(descriptor), "rb") as handle:
            content = handle.read(MAX_PROFILE_BYTES + 1)
        after = os.fstat(descriptor)
        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (
            opened.st_dev,
            opened.st_ino,
            opened.st_size,
            opened.st_mtime_ns,
        ):
            raise SetupError("Luna worker target changed while reading")
        return TargetState("regular", content, (opened.st_dev, opened.st_ino), opened.st_mode, opened.st_nlink)
    finally:
        os.close(descriptor)


def directory_identity(path: pathlib.Path) -> tuple[str, tuple[int, int] | None]:
    try:
        snapshot = os.stat(path, follow_symlinks=False)
    except FileNotFoundError:
        return "missing", None
    if stat.S_ISLNK(snapshot.st_mode) or not stat.S_ISDIR(snapshot.st_mode):
        return "unsafe", (snapshot.st_dev, snapshot.st_ino)
    return "directory", (snapshot.st_dev, snapshot.st_ino)


def snapshot_token(codex_home: pathlib.Path, asset: bytes, state: TargetState) -> str:
    home = os.stat(codex_home, follow_symlinks=False)
    agents_kind, agents_identity = directory_identity(codex_home / "agents")
    payload = {
        "target": str(target_path(codex_home)),
        "asset_sha256": hashlib.sha256(asset).hexdigest(),
        "home": [home.st_dev, home.st_ino],
        "agents_kind": agents_kind,
        "agents_identity": agents_identity,
        "target_kind": state.kind,
        "target_identity": state.identity,
        "target_mode": state.mode,
        "target_links": state.links,
        "target_sha256": hashlib.sha256(state.content).hexdigest() if state.content is not None else None,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def classify(asset: bytes, state: TargetState) -> str:
    if state.kind == "missing":
        return "missing"
    if (
        state.kind == "regular"
        and state.content == asset
        and state.mode is not None
        and stat.S_IMODE(state.mode) & 0o022 == 0
    ):
        return "current"
    return "conflict"


def render_diff(asset: bytes, state: TargetState, target: pathlib.Path) -> str | None:
    if state.kind not in {"missing", "regular"}:
        return None
    before = state.content.decode("utf-8", errors="replace").splitlines(keepends=True) if state.content else []
    after = asset.decode("utf-8").splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            before,
            after,
            fromfile=str(target) if state.content is not None else "/dev/null",
            tofile=str(target),
        )
    )


def resolve_codex_binary(value: str | None) -> str:
    if value:
        path = shutil.which(value) if os.path.sep not in value else value
    else:
        path = shutil.which("codex")
    if not path or not pathlib.Path(path).is_file():
        raise SetupError("installed Codex CLI was not found")
    return str(path)


def run_codex(arguments: list[str], codex_bin: str, codex_home: pathlib.Path, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["CODEX_HOME"] = str(codex_home)
    try:
        return subprocess.run(
            [codex_bin, *arguments],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise SetupError(f"Codex validation command failed: {' '.join(arguments)}") from error


def validate_codex(codex_bin: str, codex_home: pathlib.Path) -> dict[str, str]:
    version = run_codex(["--version"], codex_bin, codex_home)
    if version.returncode != 0 or not version.stdout.strip():
        raise SetupError("unable to read installed Codex version")
    catalog = run_codex(["debug", "models"], codex_bin, codex_home)
    if catalog.returncode != 0:
        raise SetupError("installed Codex cannot render its model catalog")
    try:
        models = json.loads(catalog.stdout)["models"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise SetupError("installed Codex returned an invalid model catalog") from error
    selected = next((model for model in models if model.get("slug") == MODEL), None)
    if selected is None:
        raise SetupError(f"installed Codex model catalog does not include {MODEL}")
    efforts = {
        item.get("effort")
        for item in selected.get("supported_reasoning_levels", [])
        if isinstance(item, dict)
    }
    if REASONING_EFFORT not in efforts:
        raise SetupError(f"{MODEL} does not support reasoning effort {REASONING_EFFORT}")
    return {"codex_version": version.stdout.strip(), "model": MODEL, "reasoning_effort": REASONING_EFFORT}


def validate_doctor(codex_bin: str, codex_home: pathlib.Path) -> str:
    result = run_codex(["--strict-config", "doctor", "--json"], codex_bin, codex_home, timeout=60)
    if result.returncode != 0:
        raise SetupError("Codex strict doctor rejected the installed configuration")
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise SetupError("Codex doctor returned invalid JSON") from error
    config = report.get("checks", {}).get("config.load", {})
    if config.get("status") != "ok":
        raise SetupError("Codex doctor did not confirm config.load")
    return str(report.get("codexVersion", "unknown"))


def inspect(codex_home: pathlib.Path, asset: bytes) -> tuple[pathlib.Path, TargetState, str, str]:
    target = target_path(codex_home)
    agents_kind, _ = directory_identity(target.parent)
    if agents_kind == "unsafe":
        raise SetupError("refusing unsafe CODEX_HOME/agents path")
    state = read_target(target)
    return target, state, classify(asset, state), snapshot_token(codex_home, asset, state)


def ensure_agents_directory(
    codex_home: pathlib.Path,
    expected_kind: str | None = None,
    expected_identity: tuple[int, int] | None = None,
) -> tuple[pathlib.Path, tuple[int, int]]:
    agents = codex_home / "agents"
    kind, _ = directory_identity(agents)
    if expected_kind is not None and kind != expected_kind:
        raise SetupError("CODEX_HOME/agents changed after check")
    if kind == "directory" and expected_identity is not None:
        current = os.stat(agents, follow_symlinks=False)
        if (current.st_dev, current.st_ino) != expected_identity:
            raise SetupError("CODEX_HOME/agents changed after check")
    if kind == "missing":
        try:
            os.mkdir(agents, 0o700)
        except FileExistsError as error:
            raise SetupError("CODEX_HOME/agents appeared during installation") from error
        kind, _ = directory_identity(agents)
    if kind != "directory":
        raise SetupError("CODEX_HOME/agents must be a real directory")
    snapshot = os.stat(agents, follow_symlinks=False)
    return agents, (snapshot.st_dev, snapshot.st_ino)


def install_atomic(target: pathlib.Path, asset: bytes, expected_directory: tuple[int, int]) -> str:
    agents = target.parent
    descriptor = os.open(agents, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    temporary = f".{FILENAME}.{secrets.token_hex(8)}.tmp"
    temporary_exists = False

    def cleanup_temporary() -> None:
        nonlocal temporary_exists
        if not temporary_exists:
            return
        try:
            os.unlink(temporary, dir_fd=descriptor)
        except FileNotFoundError:
            pass
        except OSError as error:
            raise SetupError(
                f"Luna worker target may be installed, but temporary cleanup failed for {temporary}"
            ) from error
        temporary_exists = False

    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != expected_directory:
            raise SetupError("CODEX_HOME/agents changed during installation")
        temp_fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=descriptor)
        temporary_exists = True
        try:
            with os.fdopen(temp_fd, "wb", closefd=False) as handle:
                handle.write(asset)
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            os.close(temp_fd)
        try:
            os.link(temporary, FILENAME, src_dir_fd=descriptor, dst_dir_fd=descriptor, follow_symlinks=False)
            outcome = "installed"
        except FileExistsError:
            current = read_target(target)
            for _ in range(100):
                if current.kind != "hard-linked":
                    break
                time.sleep(0.01)
                current = read_target(target)
            if classify(asset, current) == "current":
                outcome = "current-after-race"
            else:
                raise SetupError("Luna worker target appeared during installation")
        except OSError as error:
            try:
                named_target = os.stat(FILENAME, dir_fd=descriptor, follow_symlinks=False)
                named_temporary = os.stat(temporary, dir_fd=descriptor, follow_symlinks=False)
                linked_ours = (
                    stat.S_ISREG(named_target.st_mode)
                    and (named_target.st_dev, named_target.st_ino)
                    == (named_temporary.st_dev, named_temporary.st_ino)
                )
            except OSError:
                linked_ours = False
            current = read_target(target) if not linked_ours else None
            if linked_ours or (current is not None and classify(asset, current) == "current"):
                outcome = "installed-reconciled"
            else:
                raise SetupError("Luna worker installation result is unknown") from error
        cleanup_temporary()
        final = read_target(target)
        if classify(asset, final) != "current" or final.links != 1:
            raise SetupError("installed Luna worker failed exact readback")
        return outcome
    finally:
        if temporary_exists:
            try:
                os.unlink(temporary, dir_fd=descriptor)
            except OSError:
                pass
        os.close(descriptor)


def command_check(args: argparse.Namespace) -> int:
    asset = read_asset()
    home = resolve_codex_home(args.codex_home)
    target, state, status, snapshot = inspect(home, asset)
    diff = render_diff(asset, state, target)
    common = {
        "target": str(target),
        "target_kind": state.kind,
        "snapshot": snapshot,
        "diff": diff,
        "diff_status": "available" if diff is not None else "unavailable-target-content-not-read",
    }
    if status == "conflict":
        emit(status, compatibility_status="not-evaluated", **common)
        return 2
    codex = resolve_codex_binary(args.codex_bin)
    compatibility = validate_codex(codex, home)
    emit(status, **common, **compatibility)
    return 0 if status == "current" else 1


def command_diff(args: argparse.Namespace) -> int:
    asset = read_asset()
    home = resolve_codex_home(args.codex_home)
    target, state, _, snapshot = inspect(home, asset)
    diff = render_diff(asset, state, target)
    if diff is None:
        emit(
            "conflict",
            target=str(target),
            target_kind=state.kind,
            snapshot=snapshot,
            diff=None,
            diff_status="unavailable-target-content-not-read",
        )
        return 2
    sys.stdout.write(diff)
    return 0


def command_install(args: argparse.Namespace) -> int:
    asset = read_asset()
    home = resolve_codex_home(args.codex_home)
    target, state, status, snapshot = inspect(home, asset)
    if snapshot != args.expected_snapshot:
        raise SetupError("Luna worker target or prerequisites changed after check")
    if status == "conflict":
        raise SetupError("refusing to overwrite an existing Luna worker profile")
    codex = resolve_codex_binary(args.codex_bin)
    compatibility = validate_codex(codex, home)
    target, state, status, revalidated_snapshot = inspect(home, asset)
    if revalidated_snapshot != args.expected_snapshot:
        raise SetupError("Luna worker target or prerequisites changed during compatibility checks")
    if status == "current":
        doctor_version = validate_doctor(codex, home)
        emit("unchanged", target=str(target), snapshot=snapshot, doctor_version=doctor_version, **compatibility)
        return 0
    agents_kind, agents_before = directory_identity(target.parent)
    _, agents_identity = ensure_agents_directory(home, agents_kind, agents_before)
    outcome = install_atomic(target, asset, agents_identity)
    try:
        doctor_version = validate_doctor(codex, home)
    except SetupError as error:
        emit("installed-unverified", target=str(target), error=str(error), **compatibility)
        return 2
    _, final_state, final_status, final_snapshot = inspect(home, asset)
    if final_status != "current" or final_state.content != asset:
        raise SetupError("Luna worker changed after Codex validation")
    emit(outcome, target=str(target), snapshot=final_snapshot, doctor_version=doctor_version, **compatibility)
    return 0


def command_verify(args: argparse.Namespace) -> int:
    asset = read_asset()
    home = resolve_codex_home(args.codex_home)
    target, _, status, snapshot = inspect(home, asset)
    if status != "current":
        emit(status, target=str(target), snapshot=snapshot)
        return 1 if status == "missing" else 2
    codex = resolve_codex_binary(args.codex_bin)
    compatibility = validate_codex(codex, home)
    doctor_version = validate_doctor(codex, home)
    emit("verified", target=str(target), snapshot=snapshot, doctor_version=doctor_version, **compatibility)
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)
    for name in ("check", "diff", "verify"):
        command = subparsers.add_parser(name)
        command.add_argument("--codex-home")
        command.add_argument("--codex-bin")
    install = subparsers.add_parser("install")
    install.add_argument("--codex-home")
    install.add_argument("--codex-bin")
    install.add_argument("--expected-snapshot", required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        return {
            "check": command_check,
            "diff": command_diff,
            "install": command_install,
            "verify": command_verify,
        }[args.command](args)
    except SetupError as error:
        emit("error", error=str(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
