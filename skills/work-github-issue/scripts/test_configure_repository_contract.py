#!/usr/bin/env python3
"""Tests for configure_repository_contract.py using disposable AGENTS.md files."""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = pathlib.Path(__file__).with_name("configure_repository_contract.py")
sys.path.insert(0, str(SCRIPT.parent))
import configure_repository_contract as configure  # noqa: E402

START = "<!-- work-github-issue:publication-contract:v1:start -->"
END = "<!-- work-github-issue:publication-contract:v1:end -->"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )


def checked_snapshot(path: pathlib.Path, *args: str) -> str:
    checked = run("check", str(path), *args)
    try:
        return str(json.loads(checked.stdout)["snapshot"])
    except (json.JSONDecodeError, KeyError):
        return "invalid-snapshot-token"


def install(
    path: pathlib.Path,
    *args: str,
    expected: str | None = None,
) -> subprocess.CompletedProcess[str]:
    expected = expected or checked_snapshot(path, *args)
    return run("install", str(path), "--expected-snapshot", expected, *args)


class ConfigureRepositoryContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.agents = self.root / "AGENTS.md"
        subprocess.run(
            ["git", "init", "-q", str(self.root)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_render_uses_explicit_policy_values(self) -> None:
        result = run("render", "--integration-target", "release/stable", "--merge-method", "rebase")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("`release/stable`", result.stdout)
        self.assertIn("using rebase merge", result.stdout)
        self.assertIn("ticket-head OID", result.stdout)
        self.assertIn("reported integration", result.stdout)
        self.assertIn("remote ticket ref to equal", result.stdout)
        self.assertIn("invalidates local verification plus both reviews", result.stdout)
        self.assertIn("integration-base OID", result.stdout)
        self.assertIn("atomically rejects", result.stdout)
        self.assertIn("external approving", result.stdout)
        self.assertNotIn("{{", result.stdout)

    def test_install_creates_then_remains_idempotent(self) -> None:
        first = install(self.agents)
        self.assertEqual(first.returncode, 0, first.stderr)
        original = self.agents.read_text(encoding="utf-8")
        self.assertEqual(original.count(START), 1)
        self.assertEqual(original.count(END), 1)

        second = install(self.agents)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(json.loads(second.stdout)["status"], "unchanged")
        self.assertEqual(self.agents.read_text(encoding="utf-8"), original)

    def test_install_preserves_unmanaged_content_and_refuses_managed_replacement(self) -> None:
        self.agents.write_text("# Existing\n\nKeep this rule.\n", encoding="utf-8")
        initial = install(self.agents)
        self.assertEqual(initial.returncode, 0, initial.stderr)
        initial_value = self.agents.read_text(encoding="utf-8")
        updated = install(
            self.agents,
            "--integration-target",
            "stable",
            "--merge-method",
            "merge",
        )
        self.assertEqual(updated.returncode, 2, updated.stderr)
        self.assertIn("resolve the existing policy explicitly", updated.stdout)
        value = self.agents.read_text(encoding="utf-8")
        self.assertTrue(value.startswith("# Existing\n\nKeep this rule.\n"))
        self.assertEqual(value, initial_value)
        self.assertIn("targeting `main`", value)
        self.assertEqual(value.count(START), 1)

    def test_check_reports_missing_and_current(self) -> None:
        missing = run("check", str(self.agents))
        self.assertEqual(missing.returncode, 1)
        missing_payload = json.loads(missing.stdout)
        self.assertEqual(missing_payload["status"], "missing-or-stale")
        self.assertEqual(missing_payload["sha256"], "absent")
        self.assertEqual(install(self.agents).returncode, 0)
        current = run("check", str(self.agents))
        self.assertEqual(current.returncode, 0, current.stderr)
        current_payload = json.loads(current.stdout)
        self.assertEqual(current_payload["status"], "current")
        self.assertRegex(current_payload["sha256"], r"^[0-9a-f]{64}$")

    def test_check_accepts_read_only_agents_file(self) -> None:
        self.assertEqual(install(self.agents).returncode, 0)
        self.agents.chmod(0o444)
        current = run("check", str(self.agents))
        self.assertEqual(current.returncode, 0, current.stderr)
        self.assertEqual(json.loads(current.stdout)["status"], "current")

    def test_malformed_markers_fail_without_modification(self) -> None:
        original = f"# Existing\n{START}\nfirst\n{START}\nsecond\n{END}\n"
        self.agents.write_text(original, encoding="utf-8")
        block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(configure.read_contract(self.agents), block)
        result = install(self.agents, expected=expected)
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate or unmatched", result.stdout)
        self.assertEqual(self.agents.read_text(encoding="utf-8"), original)

    def test_rejects_unsafe_target_and_non_agents_filename(self) -> None:
        unsafe = run("render", "--integration-target", "../main")
        self.assertEqual(unsafe.returncode, 2)
        invalid_git = run("render", "--integration-target", "main.")
        self.assertEqual(invalid_git.returncode, 2)
        self.assertIn("valid Git branch name", invalid_git.stdout)
        unsafe_at = run("render", "--integration-target", "@")
        self.assertEqual(unsafe_at.returncode, 2)
        self.assertIn("explicit safe branch name", unsafe_at.stdout)
        wrong_name = install(self.root / "policy.md")
        self.assertEqual(wrong_name.returncode, 2)

    def test_rejects_symlink_without_changing_its_target(self) -> None:
        real = self.root / "real.md"
        real.write_text("keep\n", encoding="utf-8")
        self.agents.symlink_to(real)
        result = install(self.agents)
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlinked", result.stdout)
        self.assertEqual(real.read_text(encoding="utf-8"), "keep\n")

    def test_rejects_hard_linked_agents_file(self) -> None:
        self.agents.write_text("# Existing\n", encoding="utf-8")
        linked = self.root / "AGENTS.backup"
        linked.hardlink_to(self.agents)
        result = install(self.agents)
        self.assertEqual(result.returncode, 2)
        self.assertIn("non-hard-linked", result.stdout)
        self.assertEqual(linked.read_text(encoding="utf-8"), "# Existing\n")

    def test_fifo_agents_is_rejected_without_blocking(self) -> None:
        self.agents.unlink(missing_ok=True)
        self.agents.parent.mkdir(parents=True, exist_ok=True)
        configure.os.mkfifo(self.agents)
        result = run("check", str(self.agents))
        self.assertEqual(result.returncode, 2)
        self.assertIn("regular", result.stdout)

    def test_rejects_symlinked_parent_and_non_root_target(self) -> None:
        alias = self.root / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        symlinked_parent = install(alias / "AGENTS.md")
        self.assertEqual(symlinked_parent.returncode, 2)
        self.assertIn("symlinked path component", symlinked_parent.stdout)

        nested = self.root / "nested"
        nested.mkdir()
        non_root = install(nested / "AGENTS.md")
        self.assertEqual(non_root.returncode, 2)
        self.assertIn("repository root AGENTS.md", non_root.stdout)

    def test_target_symlink_swap_is_rejected_without_touching_target(self) -> None:
        self.agents.write_text("# Existing\n", encoding="utf-8")
        outside = self.root.parent / f"{self.root.name}-outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(configure.read_contract(self.agents), block)
        real_open = configure.os.open
        swapped = False

        def swap_before_open(
            target: str | bytes | int,
            flags: int,
            mode: int = 0o777,
            *,
            dir_fd: int | None = None,
        ) -> int:
            nonlocal swapped
            if target == "AGENTS.md" and dir_fd is not None and not swapped:
                swapped = True
                self.agents.unlink()
                self.agents.symlink_to(outside)
            return real_open(target, flags, mode, dir_fd=dir_fd)

        try:
            with mock.patch.object(configure.os, "open", side_effect=swap_before_open):
                with self.assertRaises(OSError):
                    configure.install_contract(
                        self.agents,
                        block,
                        expected,
                    )
            self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")
        finally:
            outside.unlink(missing_ok=True)

    def test_parent_symlink_swap_is_rejected_before_repository_open(self) -> None:
        parent = self.root.parent
        saved = parent / f"{self.root.name}-saved"
        outside = parent / f"{self.root.name}-outside"
        outside.mkdir()
        block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(configure.read_contract(self.agents), block)
        real_open = configure.os.open
        swapped = False

        def swap_parent(
            target: str | bytes | int,
            flags: int,
            mode: int = 0o777,
            *,
            dir_fd: int | None = None,
        ) -> int:
            nonlocal swapped
            if target == self.root.name and dir_fd is not None and not swapped:
                swapped = True
                self.root.rename(saved)
                self.root.symlink_to(outside, target_is_directory=True)
            return real_open(target, flags, mode, dir_fd=dir_fd)

        try:
            with mock.patch.object(configure.os, "open", side_effect=swap_parent):
                with self.assertRaises(OSError):
                    configure.install_contract(
                        self.agents,
                        block,
                        expected,
                    )
        finally:
            if self.root.is_symlink():
                self.root.unlink()
            if saved.exists():
                saved.rename(self.root)
            outside.rmdir()

    def test_repository_directory_swap_is_rejected_by_pinned_identity(self) -> None:
        parent = self.root.parent
        saved = parent / f"{self.root.name}-saved"
        replacement = parent / f"{self.root.name}-replacement"
        subprocess.run(
            ["git", "init", "-q", str(replacement)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(configure.read_contract(self.agents), block)
        real_open = configure.os.open
        swapped = False

        def swap_repository(
            target: str | bytes | int,
            flags: int,
            mode: int = 0o777,
            *,
            dir_fd: int | None = None,
        ) -> int:
            nonlocal swapped
            if target == self.root.name and dir_fd is not None and not swapped:
                swapped = True
                self.root.rename(saved)
                replacement.rename(self.root)
            return real_open(target, flags, mode, dir_fd=dir_fd)

        try:
            with mock.patch.object(configure.os, "open", side_effect=swap_repository):
                with self.assertRaisesRegex(configure.ContractError, "root changed"):
                    configure.install_contract(
                        self.agents,
                        block,
                        expected,
                    )
        finally:
            if swapped and self.root.exists():
                self.root.rename(replacement)
            if saved.exists():
                saved.rename(self.root)
            if replacement.exists():
                shutil.rmtree(replacement)

    def test_repository_swap_after_open_is_rejected_before_policy_write(self) -> None:
        parent = self.root.parent
        saved = parent / f"{self.root.name}-saved"
        replacement = parent / f"{self.root.name}-replacement"
        subprocess.run(
            ["git", "init", "-q", str(replacement)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(configure.read_contract(self.agents), block)
        real_mkdir = configure.os.mkdir
        swapped = False

        def swap_during_lock(
            target: str | bytes,
            mode: int = 0o777,
            *,
            dir_fd: int | None = None,
        ) -> None:
            nonlocal swapped
            if target == ".AGENTS.md.work-github-issue.lock" and not swapped:
                swapped = True
                self.root.rename(saved)
                replacement.rename(self.root)
            real_mkdir(target, mode, dir_fd=dir_fd)

        try:
            with mock.patch.object(configure.os, "mkdir", side_effect=swap_during_lock):
                with self.assertRaisesRegex(configure.ContractError, "root changed"):
                    configure.install_contract(
                        self.agents,
                        block,
                        expected,
                    )
            self.assertFalse((self.root / "AGENTS.md").exists())
            self.assertFalse((saved / "AGENTS.md").exists())
        finally:
            if swapped and self.root.exists():
                self.root.rename(replacement)
            if saved.exists():
                saved.rename(self.root)
            if replacement.exists():
                shutil.rmtree(replacement)

    def test_regular_file_replacement_fails_expected_snapshot_without_writing(self) -> None:
        original = "# Inspected policy\n"
        replacement = "# Concurrent replacement policy\n"
        self.agents.write_text(original, encoding="utf-8")
        swap_file = self.root / "replacement.md"
        swap_file.write_text(replacement, encoding="utf-8")
        block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(configure.read_contract(self.agents), block)
        real_open = configure.os.open
        swapped = False

        def replace_before_open(
            target: str | bytes | int,
            flags: int,
            mode: int = 0o777,
            *,
            dir_fd: int | None = None,
        ) -> int:
            nonlocal swapped
            if target == "AGENTS.md" and dir_fd is not None and not swapped:
                swapped = True
                swap_file.replace(self.agents)
            return real_open(target, flags, mode, dir_fd=dir_fd)

        with mock.patch.object(configure.os, "open", side_effect=replace_before_open):
            with self.assertRaisesRegex(configure.ContractError, "inspected snapshot"):
                configure.install_contract(
                    self.agents,
                    block,
                    expected,
                )
        self.assertEqual(self.agents.read_text(encoding="utf-8"), replacement)
        self.assertNotIn(START, replacement)

    def test_same_inode_edit_after_snapshot_check_fails_before_write(self) -> None:
        original = "# Inspected policy\n"
        concurrent = "# Concurrent same-inode edit\n"
        self.agents.write_text(original, encoding="utf-8")
        block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(configure.read_contract(self.agents), block)
        real_read = configure.read_descriptor
        reads = 0

        def edit_after_first_read(descriptor: int) -> str:
            nonlocal reads
            value = real_read(descriptor)
            reads += 1
            if reads == 1:
                with self.agents.open("a", encoding="utf-8") as handle:
                    handle.write(concurrent)
            return value

        with mock.patch.object(
            configure, "read_descriptor", side_effect=edit_after_first_read
        ):
            with self.assertRaisesRegex(configure.ContractError, "changed after validation"):
                configure.install_contract(self.agents, block, expected)
        self.assertEqual(self.agents.read_text(encoding="utf-8"), original + concurrent)
        self.assertNotIn(START, self.agents.read_text(encoding="utf-8"))

    def test_missing_file_with_stale_expected_hash_remains_absent(self) -> None:
        block = configure.render_contract("main", "squash")
        self.agents.write_text("# Previously inspected\n", encoding="utf-8")
        stale = configure.snapshot_token(configure.read_contract(self.agents), block)
        self.agents.unlink()
        result = install(self.agents, expected=stale)
        self.assertEqual(result.returncode, 2)
        self.assertIn("inspected snapshot", result.stdout)
        self.assertFalse(self.agents.exists())

    def test_between_command_repository_replacement_fails_snapshot(self) -> None:
        parent = self.root.parent
        original = parent / f"{self.root.name}-original"
        replacement = parent / f"{self.root.name}-replacement"
        block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(configure.read_contract(self.agents), block)
        subprocess.run(
            ["git", "init", "-q", str(replacement)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.root.rename(original)
        replacement.rename(self.root)
        try:
            with self.assertRaisesRegex(configure.ContractError, "inspected snapshot"):
                configure.install_contract(self.agents, block, expected)
            self.assertFalse(self.agents.exists())
        finally:
            self.root.rename(replacement)
            original.rename(self.root)
            shutil.rmtree(replacement)

    def test_between_command_same_content_file_replacement_fails_snapshot(self) -> None:
        content = "# Inspected policy\n"
        self.agents.write_text(content, encoding="utf-8")
        block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(configure.read_contract(self.agents), block)
        replacement = self.root / "replacement.md"
        replacement.write_text(content, encoding="utf-8")
        replacement.replace(self.agents)
        with self.assertRaisesRegex(configure.ContractError, "inspected snapshot"):
            configure.install_contract(self.agents, block, expected)
        self.assertEqual(self.agents.read_text(encoding="utf-8"), content)
        self.assertNotIn(START, content)

    def test_between_command_contract_change_fails_snapshot(self) -> None:
        inspected_block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(
            configure.read_contract(self.agents), inspected_block
        )
        changed_block = inspected_block.replace("squash merge", "a merge commit")
        with self.assertRaisesRegex(configure.ContractError, "inspected snapshot"):
            configure.install_contract(self.agents, changed_block, expected)
        self.assertFalse(self.agents.exists())

    def test_rejects_missing_parent_and_non_repository(self) -> None:
        missing_parent = install(self.root / "missing" / "AGENTS.md")
        self.assertEqual(missing_parent.returncode, 2)
        self.assertFalse((self.root / "missing").exists())

        with tempfile.TemporaryDirectory() as raw:
            non_repository = install(pathlib.Path(raw) / "AGENTS.md")
        self.assertEqual(non_repository.returncode, 2)
        self.assertIn("existing Git repository", non_repository.stdout)

    def test_concurrent_append_is_preserved_without_replacement(self) -> None:
        original = "# Existing\n"
        concurrent = "# Concurrent user edit\n"
        self.agents.write_text(original, encoding="utf-8")
        block = configure.render_contract("main", "squash")
        expected = configure.snapshot_token(configure.read_contract(self.agents), block)
        real_write = configure.os.write

        def change_during_write(descriptor: int, payload: bytes) -> int:
            with self.agents.open("a", encoding="utf-8") as handle:
                handle.write(concurrent)
            return real_write(descriptor, payload)

        with mock.patch.object(configure.os, "write", side_effect=change_during_write):
            with self.assertRaisesRegex(configure.ContractError, "concurrent edits"):
                configure.install_contract(
                    self.agents,
                    block,
                    expected,
                )
        value = self.agents.read_text(encoding="utf-8")
        self.assertIn(original, value)
        self.assertIn(concurrent, value)
        self.assertIn(block, value)

    def test_existing_installer_lock_fails_without_writing(self) -> None:
        lock = self.root / ".AGENTS.md.work-github-issue.lock"
        lock.mkdir()
        result = install(self.agents)
        self.assertEqual(result.returncode, 2)
        self.assertIn("installer lock exists", result.stdout)
        self.assertFalse(self.agents.exists())


if __name__ == "__main__":
    unittest.main()
