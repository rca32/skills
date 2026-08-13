#!/usr/bin/env python3
"""Tests for the fallback development-document path resolver."""

from __future__ import annotations

import json
import pathlib
import subprocess
import unittest


SCRIPT = pathlib.Path(__file__).with_name("resolve_document_path.py")


class ResolveDocumentPathTest(unittest.TestCase):
    def resolve(self, *args: str) -> dict[str, str]:
        result = subprocess.run(
            ["python3", str(SCRIPT), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_issue_linked_spec_has_stable_path_and_id(self) -> None:
        value = self.resolve(
            "--kind",
            "spec",
            "--title",
            "Payment Retry Policy",
            "--issue",
            "42",
            "--date",
            "2026-07-13",
        )
        self.assertEqual(
            value["relativePath"],
            "docs/specs/issue-42-payment-retry-policy.md",
        )
        self.assertEqual(value["documentId"], "spec:issue-42:payment-retry-policy")
        self.assertEqual(value["indexPath"], "docs/README.md")
        self.assertEqual(value["authority"], "repository")

    def test_domain_model_has_project_wide_stable_path_and_id(self) -> None:
        value = self.resolve(
            "--kind",
            "domain",
            "--title",
            "Checkout domain model",
            "--date",
            "2026-07-13",
        )
        self.assertEqual(value["relativePath"], "docs/domain.md")
        self.assertEqual(value["documentId"], "domain:project")
        self.assertEqual(value["sourceKey"], "project")
        self.assertEqual(value["indexPath"], "docs/README.md")

    def test_domain_model_rejects_issue_specific_identity(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--kind",
                "domain",
                "--title",
                "Checkout domain model",
                "--issue",
                "42",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("project-wide stable identity", result.stderr)

    def test_issue_linked_spec_explainer_mirrors_source_key_and_slug(self) -> None:
        value = self.resolve(
            "--kind",
            "spec-explainer",
            "--title",
            "A title that no longer matches the spec",
            "--issue",
            "42",
            "--source-document-id",
            "spec:issue-42:payment-retry-policy",
        )
        self.assertEqual(
            value["relativePath"],
            "docs/spec-explainers/issue-42-payment-retry-policy.md",
        )
        self.assertEqual(
            value["documentId"],
            "spec-explainer:issue-42:payment-retry-policy",
        )
        self.assertEqual(value["derivedFrom"], "spec:issue-42:payment-retry-policy")
        self.assertEqual(
            value["sourcePath"],
            "docs/specs/issue-42-payment-retry-policy.md",
        )

    def test_spec_explainer_rejects_missing_source_spec(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--kind",
                "spec-explainer",
                "--title",
                "Orphan",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --source-document-id", result.stderr)

    def test_spec_explainer_rejects_issue_mismatch(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--kind",
                "spec-explainer",
                "--title",
                "Mismatch",
                "--issue",
                "41",
                "--source-document-id",
                "spec:issue-42:payment-retry-policy",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must match", result.stderr)

    def test_decision_map_uses_collection_entrypoint(self) -> None:
        value = self.resolve(
            "--kind",
            "decision-map",
            "--title",
            "Checkout redesign",
            "--date",
            "2026-08-13",
        )
        self.assertEqual(
            value["relativePath"],
            "docs/decision-maps/2026-08-13-checkout-redesign/map.md",
        )
        self.assertEqual(
            value["documentId"], "decision-map:2026-08-13:checkout-redesign"
        )

    def test_local_work_derives_collection_from_source_spec(self) -> None:
        value = self.resolve(
            "--kind",
            "local-work",
            "--title",
            "A renamed work set",
            "--source-document-id",
            "spec:issue-42:payment-retry-policy",
        )
        self.assertEqual(
            value["relativePath"],
            "docs/local-work/issue-42-payment-retry-policy/work.md",
        )
        self.assertEqual(
            value["documentId"], "local-work:issue-42:payment-retry-policy"
        )
        self.assertEqual(value["derivedFrom"], "spec:issue-42:payment-retry-policy")
        self.assertEqual(
            value["sourcePath"],
            "docs/specs/issue-42-payment-retry-policy.md",
        )

    def test_local_work_rejects_missing_source_spec(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--kind",
                "local-work",
                "--title",
                "Orphan work",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --source-document-id", result.stderr)

    def test_unlinked_report_uses_date_and_kind_directory(self) -> None:
        value = self.resolve(
            "--kind",
            "diagnosis",
            "--title",
            "Intermittent Checkout Timeout",
            "--date",
            "2026-07-13",
        )
        self.assertEqual(
            value["relativePath"],
            "docs/reports/diagnostics/2026-07-13-intermittent-checkout-timeout.md",
        )
        self.assertEqual(
            value["documentId"],
            "diagnosis:2026-07-13:intermittent-checkout-timeout",
        )

    def test_unicode_title_remains_readable_and_portable(self) -> None:
        value = self.resolve(
            "--kind",
            "decision",
            "--title",
            "주문 재시도 정책",
            "--date",
            "2026-07-13",
        )
        self.assertEqual(
            value["relativePath"],
            "docs/decisions/2026-07-13-주문-재시도-정책.md",
        )

    def test_long_multibyte_title_fits_portable_filename_limit(self) -> None:
        value = self.resolve(
            "--kind",
            "decision",
            "--title",
            "장" * 80,
            "--issue",
            "42",
            "--date",
            "2026-07-13",
        )
        filename = pathlib.PurePosixPath(value["relativePath"]).name
        self.assertLessEqual(len(filename.encode("utf-8")), 240)
        self.assertTrue(filename.endswith(".md"))
        self.assertNotIn("�", filename)

    def test_path_like_title_cannot_escape_document_directory(self) -> None:
        value = self.resolve(
            "--kind",
            "research",
            "--title",
            "../../private/token notes",
            "--date",
            "2026-07-13",
        )
        self.assertEqual(
            value["relativePath"],
            "docs/research/2026-07-13-private-token-notes.md",
        )
        self.assertNotIn("..", value["relativePath"])

    def test_non_positive_issue_is_rejected(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--kind",
                "spec",
                "--title",
                "Example",
                "--issue",
                "0",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("positive", result.stderr)


if __name__ == "__main__":
    unittest.main()
