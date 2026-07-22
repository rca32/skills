#!/usr/bin/env python3
"""Tests for configure_tracker_labels.py with synthetic GitHub state."""

from __future__ import annotations

import contextlib
import io
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = pathlib.Path(__file__).with_name("configure_tracker_labels.py")
sys.path.insert(0, str(SCRIPT.parent))
import configure_tracker_labels as labels  # noqa: E402


def current_catalog() -> list[dict[str, str]]:
    return [
        {
            "name": item.name,
            "description": item.description,
            "color": item.color,
        }
        for item in labels.LABELS
    ]


class ConfigureTrackerLabelsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_inspect_reports_missing_conflict_and_ignores_color_drift(self) -> None:
        catalog = current_catalog()
        catalog.pop()
        catalog[0]["description"] = "다른 의미"
        catalog[1]["color"] = "000000"
        observed = labels.inspect(catalog)
        self.assertEqual(observed[0]["status"], "conflict")
        self.assertEqual(observed[1]["status"], "current")
        self.assertTrue(observed[1]["colorDrift"])
        self.assertEqual(observed[-1]["status"], "missing")

    def test_snapshot_binds_repository_and_relevant_label_state(self) -> None:
        observed = labels.inspect(current_catalog())
        first = labels.snapshot_token("owner/repo", observed)
        self.assertEqual(first, labels.snapshot_token("owner/repo", observed))
        self.assertNotEqual(first, labels.snapshot_token("owner/other", observed))
        changed = current_catalog()
        changed[0]["description"] = "changed"
        self.assertNotEqual(first, labels.snapshot_token("owner/repo", labels.inspect(changed)))

    def test_install_creates_only_missing_labels_and_preserves_dirty_file(self) -> None:
        catalog = current_catalog()[:-2]
        dirty = self.root / "user-change.txt"
        dirty.write_text("preserve\n", encoding="utf-8")
        expected = labels.snapshot_token("owner/repo", labels.inspect(catalog))

        def create(_root: pathlib.Path, _repository: str, spec: labels.LabelSpec):
            catalog.append(
                {"name": spec.name, "description": spec.description, "color": spec.color}
            )
            return subprocess.CompletedProcess([], 0, "{}", "")

        with (
            mock.patch.object(labels, "fetch_catalog", side_effect=lambda *_: list(catalog)),
            mock.patch.object(labels, "check_planning_lease") as lease_check,
            mock.patch.object(labels, "create_label", side_effect=create) as create_mock,
        ):
            status, created = labels.install_labels(
                self.root, "origin", "owner/repo", "session-1", expected
            )

        self.assertEqual(status, "initialized")
        self.assertEqual(created, [item.name for item in labels.LABELS[-2:]])
        self.assertEqual(create_mock.call_count, 2)
        self.assertEqual(lease_check.call_count, 2)
        self.assertEqual(dirty.read_text(encoding="utf-8"), "preserve\n")

    def test_install_is_idempotent_when_every_label_exists(self) -> None:
        catalog = current_catalog()
        expected = labels.snapshot_token("owner/repo", labels.inspect(catalog))
        with (
            mock.patch.object(labels, "fetch_catalog", return_value=catalog),
            mock.patch.object(labels, "check_planning_lease") as lease_check,
            mock.patch.object(labels, "create_label") as create_mock,
        ):
            status, created = labels.install_labels(
                self.root, "origin", "owner/repo", "session-1", expected
            )
        self.assertEqual((status, created), ("unchanged", []))
        lease_check.assert_not_called()
        create_mock.assert_not_called()

    def test_install_rejects_changed_snapshot_before_mutation(self) -> None:
        checked = current_catalog()[:-1]
        changed = current_catalog()
        expected = labels.snapshot_token("owner/repo", labels.inspect(checked))
        with (
            mock.patch.object(labels, "fetch_catalog", return_value=changed),
            mock.patch.object(labels, "create_label") as create_mock,
        ):
            with self.assertRaisesRegex(labels.LabelError, "inspected snapshot"):
                labels.install_labels(
                    self.root, "origin", "owner/repo", "session-1", expected
                )
        create_mock.assert_not_called()

    def test_install_stops_on_conflicting_meaning(self) -> None:
        catalog = current_catalog()
        catalog[0]["description"] = "conflicting meaning"
        expected = labels.snapshot_token("owner/repo", labels.inspect(catalog))
        with (
            mock.patch.object(labels, "fetch_catalog", return_value=catalog),
            mock.patch.object(labels, "create_label") as create_mock,
        ):
            with self.assertRaisesRegex(labels.LabelError, "conflict"):
                labels.install_labels(
                    self.root, "origin", "owner/repo", "session-1", expected
                )
        create_mock.assert_not_called()

    def test_lease_collision_stops_before_remote_mutation(self) -> None:
        catalog = current_catalog()[:-1]
        expected = labels.snapshot_token("owner/repo", labels.inspect(catalog))
        with (
            mock.patch.object(labels, "fetch_catalog", return_value=catalog),
            mock.patch.object(
                labels,
                "check_planning_lease",
                side_effect=labels.LabelError("not owned"),
            ),
            mock.patch.object(labels, "create_label") as create_mock,
        ):
            with self.assertRaisesRegex(labels.LabelError, "not owned"):
                labels.install_labels(
                    self.root, "origin", "owner/repo", "session-1", expected
                )
        create_mock.assert_not_called()

    def test_unknown_create_result_is_not_retried(self) -> None:
        catalog = current_catalog()[:-1]
        expected = labels.snapshot_token("owner/repo", labels.inspect(catalog))
        failed = subprocess.CompletedProcess([], 1, "", "network failure")
        with (
            mock.patch.object(labels, "fetch_catalog", return_value=catalog),
            mock.patch.object(labels, "check_planning_lease"),
            mock.patch.object(labels, "create_label", return_value=failed) as create_mock,
        ):
            with self.assertRaises(labels.UnknownMutation) as caught:
                labels.install_labels(
                    self.root, "origin", "owner/repo", "session-1", expected
                )
        self.assertEqual(caught.exception.created, [])
        create_mock.assert_called_once()

    def test_post_timeout_is_reconciled_when_label_exists(self) -> None:
        catalog = current_catalog()[:-1]
        expected = labels.snapshot_token("owner/repo", labels.inspect(catalog))

        def timeout_after_create(
            _root: pathlib.Path, _repository: str, spec: labels.LabelSpec
        ):
            catalog.append(
                {"name": spec.name, "description": spec.description, "color": spec.color}
            )
            raise subprocess.TimeoutExpired(["gh", "api"], 30)

        with (
            mock.patch.object(labels, "fetch_catalog", side_effect=lambda *_: list(catalog)),
            mock.patch.object(labels, "check_planning_lease"),
            mock.patch.object(labels, "create_label", side_effect=timeout_after_create),
        ):
            status, created = labels.install_labels(
                self.root, "origin", "owner/repo", "session-1", expected
            )
        self.assertEqual(status, "initialized")
        self.assertEqual(created, [labels.LABELS[-1].name])

    def test_catalog_timeout_is_normalized_for_reconciliation(self) -> None:
        with mock.patch.object(
            labels,
            "run",
            side_effect=subprocess.TimeoutExpired(["gh", "api"], 30),
        ):
            with self.assertRaisesRegex(labels.LabelError, "timed out"):
                labels.fetch_catalog(self.root, "owner/repo")

    def test_catalog_os_error_is_normalized_for_reconciliation(self) -> None:
        with mock.patch.object(labels, "run", side_effect=OSError("gh disappeared")):
            with self.assertRaisesRegex(labels.LabelError, "failed"):
                labels.fetch_catalog(self.root, "owner/repo")

    def test_partial_failure_reports_confirmed_creates(self) -> None:
        catalog = current_catalog()[:-2]
        expected = labels.snapshot_token("owner/repo", labels.inspect(catalog))
        calls = 0

        def create(_root: pathlib.Path, _repository: str, spec: labels.LabelSpec):
            nonlocal calls
            calls += 1
            if calls == 1:
                catalog.append(
                    {"name": spec.name, "description": spec.description, "color": spec.color}
                )
                return subprocess.CompletedProcess([], 0, "{}", "")
            return subprocess.CompletedProcess([], 1, "", "transport failure")

        with (
            mock.patch.object(labels, "fetch_catalog", side_effect=lambda *_: list(catalog)),
            mock.patch.object(labels, "check_planning_lease"),
            mock.patch.object(labels, "create_label", side_effect=create) as create_mock,
        ):
            with self.assertRaises(labels.UnknownMutation) as caught:
                labels.install_labels(
                    self.root, "origin", "owner/repo", "session-1", expected
                )
        self.assertEqual(caught.exception.created, [labels.LABELS[-2].name])
        self.assertEqual(create_mock.call_count, 2)

    def test_readback_timeout_preserves_confirmed_creates(self) -> None:
        catalog = current_catalog()[:-2]
        expected = labels.snapshot_token("owner/repo", labels.inspect(catalog))
        fetches = 0

        def fetch(*_args: object) -> list[dict[str, str]]:
            nonlocal fetches
            fetches += 1
            if fetches == 3:
                raise labels.LabelError("GitHub label catalog read timed out or failed")
            return list(catalog)

        def create(_root: pathlib.Path, _repository: str, spec: labels.LabelSpec):
            catalog.append(
                {"name": spec.name, "description": spec.description, "color": spec.color}
            )
            return subprocess.CompletedProcess([], 0, "{}", "")

        with (
            mock.patch.object(labels, "fetch_catalog", side_effect=fetch),
            mock.patch.object(labels, "check_planning_lease"),
            mock.patch.object(labels, "create_label", side_effect=create),
        ):
            with self.assertRaises(labels.UnknownMutation) as caught:
                labels.install_labels(
                    self.root, "origin", "owner/repo", "session-1", expected
                )
        self.assertEqual(caught.exception.created, [labels.LABELS[-2].name])

    def test_post_create_os_error_reports_unknown_state(self) -> None:
        catalog = current_catalog()[:-1]
        expected = labels.snapshot_token("owner/repo", labels.inspect(catalog))
        fetches = 0

        def fetch(*_args: object) -> list[dict[str, str]]:
            nonlocal fetches
            fetches += 1
            if fetches == 2:
                raise OSError("readback process failed")
            return list(catalog)

        with (
            mock.patch.object(labels, "fetch_catalog", side_effect=fetch),
            mock.patch.object(labels, "check_planning_lease"),
            mock.patch.object(
                labels,
                "create_label",
                return_value=subprocess.CompletedProcess([], 0, "{}", ""),
            ) as create_mock,
        ):
            with self.assertRaises(labels.UnknownMutation) as caught:
                labels.install_labels(
                    self.root, "origin", "owner/repo", "session-1", expected
                )
        self.assertEqual(caught.exception.created, [])
        create_mock.assert_called_once()

    def test_check_command_is_read_only_and_reports_missing(self) -> None:
        catalog = current_catalog()[:-1]
        output = io.StringIO()
        with (
            mock.patch.object(labels, "repository_root", return_value=self.root),
            mock.patch.object(labels, "resolve_repository", return_value="owner/repo"),
            mock.patch.object(labels, "fetch_catalog", return_value=catalog),
            contextlib.redirect_stdout(output),
        ):
            result = labels.main(["check", str(self.root)])
        self.assertEqual(result, 1)
        self.assertIn('"status": "missing"', output.getvalue())

    def test_remote_parser_accepts_canonical_forms_and_rejects_others(self) -> None:
        self.assertEqual(
            labels.parse_github_remote("https://github.com/owner/repo.git"),
            "owner/repo",
        )
        self.assertEqual(labels.parse_github_remote("git@github.com:owner/repo.git"), "owner/repo")
        self.assertEqual(
            labels.parse_github_remote("ssh://git@github.com/owner/repo.git"),
            "owner/repo",
        )
        with self.assertRaises(labels.LabelError):
            labels.parse_github_remote("https://example.com/owner/repo.git")


if __name__ == "__main__":
    unittest.main()
