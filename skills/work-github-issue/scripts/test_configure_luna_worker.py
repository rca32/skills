#!/usr/bin/env python3
"""Disposable tests for configure_luna_worker.py."""

from __future__ import annotations

import concurrent.futures
import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock


SCRIPT = pathlib.Path(__file__).with_name("configure_luna_worker.py")
sys.path.insert(0, str(SCRIPT.parent))
import configure_luna_worker as configure  # noqa: E402


FAKE_CODEX = r'''#!/usr/bin/env python3
import json
import os
import pathlib
import sys

arguments = sys.argv[1:]
if arguments == ["--version"]:
    print("codex-cli 0.146.0")
    raise SystemExit(0)
if arguments == ["debug", "models"]:
    if os.environ.get("FAKE_MUTATE_TARGET_ON_MODELS"):
        target = pathlib.Path(os.environ["CODEX_HOME"]) / "agents" / "luna-worker.toml"
        target.parent.mkdir(exist_ok=True)
        target.write_text('name = "concurrent"\n', encoding="utf-8")
    models = [] if os.environ.get("FAKE_MODEL_MISSING") else [{
        "slug": "gpt-5.6-luna",
        "supported_reasoning_levels": [] if os.environ.get("FAKE_EFFORT_MISSING") else [{"effort": "max"}],
    }]
    print(json.dumps({"models": models}))
    raise SystemExit(0)
if arguments == ["--strict-config", "doctor", "--json"]:
    if os.environ.get("FAKE_DOCTOR_FAIL"):
        print(json.dumps({"overallStatus": "error"}))
        raise SystemExit(2)
    target = pathlib.Path(os.environ["CODEX_HOME"]) / "agents" / "luna-worker.toml"
    if 'name = "luna_worker"' not in target.read_text(encoding="utf-8"):
        raise SystemExit(2)
    print(json.dumps({
        "codexVersion": "0.146.0",
        "checks": {"config.load": {"status": "ok"}},
    }))
    raise SystemExit(0)
raise SystemExit(2)
'''


class ConfigureLunaWorkerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.codex_home = self.root / ".codex"
        self.codex_home.mkdir(mode=0o700)
        self.config = self.codex_home / "config.toml"
        self.config.write_text('model = "preserve-me"\n', encoding="utf-8")
        self.codex = self.root / "codex"
        self.codex.write_text(textwrap.dedent(FAKE_CODEX), encoding="utf-8")
        self.codex.chmod(0o755)

    def tearDown(self) -> None:
        self.temp.cleanup()

    @property
    def target(self) -> pathlib.Path:
        return self.codex_home / "agents" / configure.FILENAME

    def run_cli(self, command: str, *extra: str, environment: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        values = os.environ.copy()
        if environment:
            values.update(environment)
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                command,
                "--codex-home",
                str(self.codex_home),
                "--codex-bin",
                str(self.codex),
                *extra,
            ],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            env=values,
        )

    def check_payload(self) -> dict[str, object]:
        result = self.run_cli("check")
        self.assertEqual(result.returncode, 1, result.stderr)
        return json.loads(result.stdout)

    def install(self, snapshot: str, environment: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return self.run_cli("install", "--expected-snapshot", snapshot, environment=environment)

    def test_asset_schema_is_complete(self) -> None:
        payload = configure.read_asset()
        self.assertIn(b'name = "luna_worker"', payload)
        self.assertIn(b'model = "gpt-5.6-luna"', payload)
        self.assertIn(b'model_reasoning_effort = "max"', payload)

    def test_check_reports_compatibility_snapshot_and_diff(self) -> None:
        payload = self.check_payload()
        self.assertEqual(payload["status"], "missing")
        self.assertEqual(payload["codex_version"], "codex-cli 0.146.0")
        self.assertEqual(payload["model"], "gpt-5.6-luna")
        self.assertEqual(payload["reasoning_effort"], "max")
        self.assertRegex(str(payload["snapshot"]), r"^[0-9a-f]{64}$")
        self.assertIn("+++", str(payload["diff"]))
        self.assertFalse(self.target.exists())

    def test_diff_is_read_only(self) -> None:
        result = self.run_cli("diff")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("+++", result.stdout)
        self.assertFalse(self.target.exists())

    def test_install_and_verify_preserve_other_config(self) -> None:
        original = self.config.read_bytes()
        snapshot = str(self.check_payload()["snapshot"])
        installed = self.install(snapshot)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        self.assertEqual(json.loads(installed.stdout)["status"], "installed")
        self.assertEqual(self.target.read_bytes(), configure.read_asset())
        self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)
        self.assertEqual(self.config.read_bytes(), original)
        verified = self.run_cli("verify")
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
        self.assertEqual(json.loads(verified.stdout)["status"], "verified")

    def test_current_install_is_idempotent(self) -> None:
        snapshot = str(self.check_payload()["snapshot"])
        self.assertEqual(self.install(snapshot).returncode, 0)
        current = self.run_cli("check")
        self.assertEqual(current.returncode, 0, current.stderr)
        payload = json.loads(current.stdout)
        unchanged = self.install(str(payload["snapshot"]))
        self.assertEqual(unchanged.returncode, 0, unchanged.stdout + unchanged.stderr)
        self.assertEqual(json.loads(unchanged.stdout)["status"], "unchanged")

    def test_conflict_is_never_overwritten(self) -> None:
        self.target.parent.mkdir()
        original = b'name = "different"\n'
        self.target.write_bytes(original)
        checked = self.run_cli("check")
        self.assertEqual(checked.returncode, 2)
        payload = json.loads(checked.stdout)
        installed = self.install(str(payload["snapshot"]))
        self.assertEqual(installed.returncode, 2)
        self.assertIn("refusing to overwrite", installed.stdout)
        self.assertEqual(self.target.read_bytes(), original)

    def test_group_or_other_writable_current_profile_is_a_conflict(self) -> None:
        self.target.parent.mkdir()
        self.target.write_bytes(configure.read_asset())
        self.target.chmod(0o666)
        checked = self.run_cli("check")
        self.assertEqual(checked.returncode, 2)
        payload = json.loads(checked.stdout)
        self.assertEqual(payload["status"], "conflict")
        self.assertEqual(payload["target_kind"], "regular")
        self.assertEqual(payload["compatibility_status"], "not-evaluated")

    def test_stale_snapshot_refuses_write(self) -> None:
        snapshot = str(self.check_payload()["snapshot"])
        self.target.parent.mkdir()
        self.target.write_text('name = "concurrent"\n', encoding="utf-8")
        installed = self.install(snapshot)
        self.assertEqual(installed.returncode, 2)
        self.assertIn("changed after check", installed.stdout)
        self.assertIn("concurrent", self.target.read_text(encoding="utf-8"))

    def test_compatibility_check_drift_refuses_write(self) -> None:
        snapshot = str(self.check_payload()["snapshot"])
        installed = self.install(snapshot, {"FAKE_MUTATE_TARGET_ON_MODELS": "1"})
        self.assertEqual(installed.returncode, 2)
        self.assertIn("changed during compatibility checks", installed.stdout)
        self.assertIn("concurrent", self.target.read_text(encoding="utf-8"))

    def test_symlink_and_hard_link_are_conflicts(self) -> None:
        self.target.parent.mkdir()
        real = self.root / "real.toml"
        real.write_text('name = "real"\n', encoding="utf-8")
        self.target.symlink_to(real)
        symlink = json.loads(self.run_cli("check").stdout)
        self.assertEqual(symlink["status"], "conflict")
        self.assertEqual(symlink["target_kind"], "symlink")
        self.assertIsNone(symlink["diff"])
        self.assertEqual(symlink["diff_status"], "unavailable-target-content-not-read")
        unavailable = self.run_cli("diff")
        self.assertEqual(unavailable.returncode, 2)
        self.assertEqual(json.loads(unavailable.stdout)["target_kind"], "symlink")
        self.target.unlink()
        os.link(real, self.target)
        hard_link = json.loads(self.run_cli("check").stdout)
        self.assertEqual(hard_link["status"], "conflict")
        self.assertEqual(hard_link["target_kind"], "hard-linked")
        self.assertIsNone(hard_link["diff"])

    def test_missing_model_or_effort_fails_before_write(self) -> None:
        missing_model = self.run_cli("check", environment={"FAKE_MODEL_MISSING": "1"})
        self.assertEqual(missing_model.returncode, 2)
        self.assertIn("does not include", missing_model.stdout)
        missing_effort = self.run_cli("check", environment={"FAKE_EFFORT_MISSING": "1"})
        self.assertEqual(missing_effort.returncode, 2)
        self.assertIn("does not support", missing_effort.stdout)
        self.assertFalse(self.target.exists())

    def test_doctor_failure_reports_installed_unverified_without_deleting(self) -> None:
        snapshot = str(self.check_payload()["snapshot"])
        installed = self.install(snapshot, {"FAKE_DOCTOR_FAIL": "1"})
        self.assertEqual(installed.returncode, 2)
        self.assertEqual(json.loads(installed.stdout)["status"], "installed-unverified")
        self.assertEqual(self.target.read_bytes(), configure.read_asset())

    def test_atomic_competitors_reconcile_identical_result(self) -> None:
        agents, identity = configure.ensure_agents_directory(self.codex_home)
        target = agents / configure.FILENAME
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(
                executor.map(
                    lambda _: configure.install_atomic(target, configure.read_asset(), identity),
                    range(2),
                )
            )
        self.assertIn("installed", outcomes)
        self.assertIn("current-after-race", outcomes)
        self.assertEqual(target.read_bytes(), configure.read_asset())

    def test_competing_unsafe_mode_is_not_reconciled_as_current(self) -> None:
        agents, identity = configure.ensure_agents_directory(self.codex_home)
        target = agents / configure.FILENAME

        def install_unsafe_competitor(*args: object, **kwargs: object) -> None:
            target.write_bytes(configure.read_asset())
            target.chmod(0o666)
            raise FileExistsError("synthetic competitor")

        with mock.patch.object(configure.os, "link", side_effect=install_unsafe_competitor):
            with self.assertRaisesRegex(configure.SetupError, "appeared during installation"):
                configure.install_atomic(target, configure.read_asset(), identity)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o666)

    def test_unknown_link_result_reconciles_exact_target(self) -> None:
        agents, identity = configure.ensure_agents_directory(self.codex_home)
        target = agents / configure.FILENAME
        real_link = configure.os.link

        def link_then_error(*args: object, **kwargs: object) -> None:
            real_link(*args, **kwargs)
            raise OSError("unknown result")

        with mock.patch.object(configure.os, "link", side_effect=link_then_error):
            outcome = configure.install_atomic(target, configure.read_asset(), identity)
        self.assertEqual(outcome, "installed-reconciled")
        self.assertEqual(target.read_bytes(), configure.read_asset())

    def test_temporary_cleanup_failure_is_structured_after_reconciliation(self) -> None:
        agents, identity = configure.ensure_agents_directory(self.codex_home)
        target = agents / configure.FILENAME
        real_unlink = configure.os.unlink

        def reject_temporary(path: object, *args: object, **kwargs: object) -> None:
            if str(path).endswith(".tmp"):
                raise PermissionError("synthetic cleanup failure")
            real_unlink(path, *args, **kwargs)

        with mock.patch.object(configure.os, "unlink", side_effect=reject_temporary):
            with self.assertRaisesRegex(configure.SetupError, "target may be installed"):
                configure.install_atomic(target, configure.read_asset(), identity)
        self.assertEqual(target.read_bytes(), configure.read_asset())


if __name__ == "__main__":
    unittest.main()
