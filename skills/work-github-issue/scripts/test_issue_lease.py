#!/usr/bin/env python3
"""Integration tests for issue_lease.py against a disposable bare remote."""

from __future__ import annotations

import concurrent.futures
import json
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock


SCRIPT = pathlib.Path(__file__).with_name("issue_lease.py")
sys.path.insert(0, str(SCRIPT.parent))
import issue_lease  # noqa: E402


SUGGESTED_REVIEW_COMMENT = (
    "PR #42 권한 변경 — 결과: [승인 | 수정 요청]. "
    "판단 근거: [작성]. 완료 증거: [PR #42 리뷰 URL 붙여넣기]."
)
SUGGESTED_REVIEW_COMMENT_WITHOUT_RATIONALE = (
    "PR #42 권한 변경 — 결과: [승인 | 수정 요청]. "
    "완료 증거: [PR #42 리뷰 URL 붙여넣기]."
)
MISLEADING_COMPLETED_REVIEW_COMMENT = (
    "PR #42 검토 결과: 승인. 판단 근거: 요구사항 충족. "
    "리뷰 링크: https://example.invalid/reviews/42."
)
PRECOMPLETED_REVIEW_COMMENT = (
    "PR #42 권한 변경을 검토하고 승인 완료했습니다. "
    + SUGGESTED_REVIEW_COMMENT
)
GENERIC_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "선택 1 | 선택 2"
)
DUPLICATE_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "승인 | 승인"
)
SUBSTRING_EVIDENCE_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "PR #42 리뷰 URL 붙여넣기", "catalog"
)
LETTERED_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "선택 A | 선택 B"
)
PUNCTUATION_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "— | 승인"
)
UNRELATED_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "PostgreSQL | MySQL"
)
DISGUISED_UNRELATED_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "PostgreSQL 승인 | MySQL 승인"
)
BARE_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "A | R"
)
SUBSTRING_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "commentary | approvedly"
)
TRUNCATED_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "approve | quest"
)
INCOMPLETE_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "승인 | 요청"
)
GENERIC_CONTROLLED_RESULT_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "승인 | 수정 요청", "의견 | 검토 결과"
)
GENERIC_EVIDENCE_REVIEW_COMMENT = SUGGESTED_REVIEW_COMMENT.replace(
    "PR #42 리뷰 URL 붙여넣기", "링크 붙여넣기"
)
VALID_HUMAN_ACTION_BODY = "\n".join(
    [
        "## 사람에게 필요한 도움",
        "**필요한 이유:** 보안 승인이 있어야 안전하게 계속할 수 있습니다.",
        "**요청 종류:** 검토",
        "**대상:** PR #42 권한 변경",
        "### 해 주실 일",
        "- [ ] PR #42 권한 변경을 검토하고 승인 또는 수정 요청을 PR #42 리뷰에 남겨 주세요.",
        "**답변/결과를 남길 곳:** 이슈 #53 댓글 (실제 검토는 PR #42 리뷰)",
        "**완료 조건:** 승인 또는 구체적인 수정 요청이 리뷰로 등록됨",
        "**완료 증거:** PR #42 승인 또는 수정 요청 리뷰 링크",
        "**완료 후 상태:** 상태: 에이전트 작업 가능",
        "**전환 담당:** prepare-issue",
        f"**추천 댓글:** {SUGGESTED_REVIEW_COMMENT}",
    ]
)
HUMAN_ACTION_WITHOUT_SUGGESTED_COMMENT = VALID_HUMAN_ACTION_BODY.replace(
    f"\n**추천 댓글:** {SUGGESTED_REVIEW_COMMENT}", ""
)


def command(args: list[str], cwd: pathlib.Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(f"command failed: {args}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


class IssueLeaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.temp.name)
        self.remote = root / "remote.git"
        self.repo = root / "repo"
        command(["git", "init", "--bare", str(self.remote)], root)
        command(["git", "init", "-b", "main", str(self.repo)], root)
        command(["git", "config", "user.name", "Lease Test"], self.repo)
        command(["git", "config", "user.email", "lease@example.invalid"], self.repo)
        (self.repo / "seed.txt").write_text("seed\n", encoding="utf-8")
        command(["git", "add", "seed.txt"], self.repo)
        command(["git", "commit", "-m", "seed"], self.repo)
        command(["git", "remote", "add", "origin", str(self.remote)], self.repo)
        command(["git", "push", "-u", "origin", "main"], self.repo)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def lease(self, *args: str, check: bool = True) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = command(
            ["python3", str(SCRIPT), *args, "--no-github-sync", "--actor", "test-agent"],
            self.repo,
            check=check,
        )
        payload = json.loads(result.stdout.strip())
        return result, payload

    def test_claim_renew_check_and_release(self) -> None:
        _, claimed = self.lease("claim", "42", "--session", "session-a123")
        self.assertEqual(claimed["status"], "acquired")
        lease_tree = command(
            [
                "git",
                f"--git-dir={self.remote}",
                "ls-tree",
                "-r",
                "refs/notes/rca-issue-leases/42",
            ],
            self.repo,
        )
        self.assertEqual(lease_tree.stdout, "")

        conflict, payload = self.lease(
            "claim", "42", "--session", "session-b123", check=False
        )
        self.assertEqual(conflict.returncode, 3)
        self.assertEqual(payload["lease"]["session"], "session-a123")

        _, checked = self.lease("check", "42", "--session", "session-a123")
        self.assertEqual(checked["status"], "owned")
        _, renewed = self.lease("renew", "42", "--session", "session-a123")
        self.assertEqual(renewed["status"], "renewed")
        self.assertNotEqual(renewed["remoteSha"], claimed["remoteSha"])

        wrong, wrong_payload = self.lease(
            "release",
            "42",
            "--session",
            "session-b123",
            "--outcome",
            "handoff",
            "--evidence",
            "local-test:handoff",
            check=False,
        )
        self.assertEqual(wrong.returncode, 5)
        self.assertEqual(wrong_payload["status"], "error")

        _, released = self.lease(
            "release",
            "42",
            "--session",
            "session-a123",
            "--outcome",
            "completed",
            "--evidence",
            "local-test:complete",
        )
        self.assertEqual(released["status"], "released")
        _, status = self.lease("status", "42")
        self.assertEqual(status["status"], "unclaimed")

    def test_planning_claim_serializes_tracker_writes_without_evidence(self) -> None:
        _, claimed = self.lease(
            "claim",
            "0",
            "--purpose",
            "planning",
            "--session",
            "session-plan-a",
        )
        self.assertEqual(claimed["status"], "acquired")
        self.assertEqual(claimed["lease"]["purpose"], "planning")

        conflict, payload = self.lease(
            "claim",
            "0",
            "--purpose",
            "planning",
            "--session",
            "session-plan-b",
            check=False,
        )
        self.assertEqual(conflict.returncode, 3)
        self.assertEqual(payload["lease"]["session"], "session-plan-a")

        _, checked = self.lease("check", "0", "--session", "session-plan-a")
        self.assertEqual(checked["status"], "owned")
        _, released = self.lease("release", "0", "--session", "session-plan-a")
        self.assertEqual(released["status"], "released")
        self.assertEqual(released["purpose"], "planning")
        _, status = self.lease("status", "0")
        self.assertEqual(status["status"], "unclaimed")

    def test_expired_lease_requires_explicit_takeover(self) -> None:
        self.lease(
            "claim",
            "43",
            "--session",
            "session-old1",
            "--ttl-minutes",
            "0.001",
        )
        time.sleep(0.08)
        expired, payload = self.lease(
            "claim", "43", "--session", "session-new1", check=False
        )
        self.assertEqual(expired.returncode, 4)
        self.assertEqual(payload["lease"]["session"], "session-old1")

        _, takeover = self.lease(
            "claim",
            "43",
            "--session",
            "session-new1",
            "--takeover-expired",
        )
        self.assertTrue(takeover["takeover"])
        self.assertEqual(takeover["lease"]["session"], "session-new1")
        old_session = command(
            [
                "git",
                "ls-remote",
                "--refs",
                "origin",
                "refs/notes/rca-agent-sessions/session-old1",
            ],
            self.repo,
        )
        self.assertEqual(old_session.stdout, "")

    def test_concurrent_claim_has_one_winner(self) -> None:
        def contender(session: str) -> subprocess.CompletedProcess[str]:
            return command(
                [
                    "python3",
                    str(SCRIPT),
                    "claim",
                    "44",
                    "--session",
                    session,
                    "--no-github-sync",
                    "--actor",
                    "test-agent",
                ],
                self.repo,
                check=False,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(contender, ("session-race-a", "session-race-b")))
        self.assertEqual(sorted(result.returncode for result in results), [0, 3])
        winner = json.loads(next(result.stdout for result in results if result.returncode == 0))
        _, status = self.lease("status", "44")
        self.assertEqual(status["lease"]["session"], winner["lease"]["session"])

    def test_concurrent_planning_claim_has_one_winner(self) -> None:
        def contender(session: str) -> subprocess.CompletedProcess[str]:
            return command(
                [
                    "python3",
                    str(SCRIPT),
                    "claim",
                    "55",
                    "--purpose",
                    "planning",
                    "--session",
                    session,
                    "--no-github-sync",
                    "--actor",
                    "test-agent",
                ],
                self.repo,
                check=False,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(contender, ("session-plan-race-a", "session-plan-race-b"))
            )
        self.assertEqual(sorted(result.returncode for result in results), [0, 3])
        winner = json.loads(
            next(result.stdout for result in results if result.returncode == 0)
        )
        self.assertEqual(winner["lease"]["purpose"], "planning")

    def test_concurrent_planning_and_implementation_claim_have_one_winner(self) -> None:
        def contender(purpose: str) -> subprocess.CompletedProcess[str]:
            command_args = [
                "python3",
                str(SCRIPT),
                "claim",
                "56",
                "--purpose",
                purpose,
                "--session",
                f"session-mixed-{purpose}",
                "--no-github-sync",
                "--actor",
                "test-agent",
            ]
            return command(command_args, self.repo, check=False)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(contender, ("planning", "implementation")))
        self.assertEqual(sorted(result.returncode for result in results), [0, 3])
        winner = json.loads(
            next(result.stdout for result in results if result.returncode == 0)
        )
        self.assertIn(winner["lease"]["purpose"], {"planning", "implementation"})

    def test_active_session_cannot_change_lease_purpose(self) -> None:
        self.lease(
            "claim",
            "57",
            "--purpose",
            "planning",
            "--session",
            "session-purpose",
        )
        conflict, payload = self.lease(
            "claim",
            "57",
            "--purpose",
            "implementation",
            "--session",
            "session-purpose",
            check=False,
        )
        self.assertEqual(conflict.returncode, 3)
        self.assertEqual(payload["lease"]["purpose"], "planning")

    def test_one_session_cannot_claim_two_issues(self) -> None:
        self.lease("claim", "45", "--session", "session-single")
        conflict, payload = self.lease(
            "claim", "46", "--session", "session-single", check=False
        )
        self.assertEqual(conflict.returncode, 3)
        self.assertEqual(payload["lease"]["issue"], 45)
        _, second_status = self.lease("status", "46")
        self.assertEqual(second_status["status"], "unclaimed")

    def test_concurrent_same_session_claims_only_one_issue(self) -> None:
        def contender(issue: str) -> subprocess.CompletedProcess[str]:
            return command(
                [
                    "python3",
                    str(SCRIPT),
                    "claim",
                    issue,
                    "--session",
                    "session-one-ticket",
                    "--no-github-sync",
                    "--actor",
                    "test-agent",
                ],
                self.repo,
                check=False,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(contender, ("48", "49")))
        self.assertEqual(sorted(result.returncode for result in results), [0, 3])
        statuses = [self.lease("status", issue)[1]["status"] for issue in ("48", "49")]
        self.assertEqual(sorted(statuses), ["active", "unclaimed"])

    def test_expired_owner_cannot_renew(self) -> None:
        self.lease(
            "claim",
            "47",
            "--session",
            "session-expired",
            "--ttl-minutes",
            "0.001",
        )
        time.sleep(0.08)
        renewal, payload = self.lease(
            "renew", "47", "--session", "session-expired", check=False
        )
        self.assertEqual(renewal.returncode, 5)
        self.assertIn("expired", payload["error"])


class GitHubContractTest(unittest.TestCase):
    def test_claim_and_release_comments_explain_the_lease_in_korean(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False,
            issue=50,
            repo="octo-org/example-repo",
            evidence="https://github.com/octo-org/example-repo/issues/50#issuecomment-1",
        )
        metadata = {
            "session": "session-korean",
            "branch": "agent/korean",
            "headSha": "a" * 40,
            "expiresAt": "2030-01-01T00:00:00Z",
            "displayLanguage": "ko",
        }
        completed = subprocess.CompletedProcess([], 0, "", "")
        with mock.patch.object(
            issue_lease, "run", return_value=completed
        ) as invoked:
            issue_lease.github_claim(args, metadata, False)
            claim_command = invoked.call_args.args[0]
            claim_body = claim_command[claim_command.index("--body") + 1]
            self.assertIn("에이전트 세션 lease를 획득했습니다.", claim_body)
            self.assertIn("- 세션:", claim_body)

            issue_lease.github_release(args, "blocked", metadata["session"], "ko")
            release_command = invoked.call_args.args[0]
            release_body = release_command[release_command.index("--body") + 1]
            self.assertIn("차단됨", release_body)
            self.assertIn("증거:", release_body)

            english = dict(metadata)
            english["displayLanguage"] = "en"
            issue_lease.github_claim(args, english, False)
            claim_command = invoked.call_args.args[0]
            claim_body = claim_command[claim_command.index("--body") + 1]
            self.assertIn("Agent session lease acquired.", claim_body)

            issue_lease.github_release(args, "blocked", metadata["session"], "en")
            release_command = invoked.call_args.args[0]
            release_body = release_command[release_command.index("--body") + 1]
            self.assertIn("released with outcome `blocked`", release_body)

    def test_remote_url_binds_repository_identity(self) -> None:
        urls = (
            "https://github.com/octo-org/example-repo.git",
            "git@github.com:octo-org/example-repo.git",
            "ssh://git@github.com/octo-org/example-repo.git",
        )
        for url in urls:
            completed = subprocess.CompletedProcess([], 0, f"{url}\n", "")
            with mock.patch.object(issue_lease, "run", return_value=completed):
                self.assertEqual(
                    issue_lease.github_repo_from_remote("origin"),
                    "octo-org/example-repo",
                )

        args = issue_lease.argparse.Namespace(
            no_github_sync=False, remote="origin", repo="other/repository"
        )
        completed = subprocess.CompletedProcess(
            [], 0, "https://github.com/octo-org/example-repo.git\n", ""
        )
        with mock.patch.object(issue_lease, "run", return_value=completed):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.bind_github_repo(args)

    def test_readiness_and_open_blockers_gate_claim(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False,
            issue=50,
            repo="octo-org/example-repo",
            allow_unready=False,
            allow_shared_assignee=False,
            takeover_expired=False,
        )
        base = {
            "state": "OPEN",
            "assignees": [],
            "url": "https://github.com/octo-org/example-repo/issues/50",
            "labels": [],
            "blockedBy": [],
            "comments": [],
            "parent": None,
        }
        with mock.patch.object(issue_lease, "github_issue_snapshot", return_value=base):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_precheck(args, "octocat")

        blocked = dict(base)
        blocked["labels"] = [{"name": "ready-for-agent"}]
        blocked["blockedBy"] = [
            {
                "number": 49,
                "title": "Open prerequisite",
                "url": "https://github.com/octo-org/example-repo/issues/49",
                "state": "OPEN",
            }
        ]
        with mock.patch.object(issue_lease, "github_issue_snapshot", return_value=blocked):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_precheck(args, "octocat")

    def test_korean_ready_label_allows_claim(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False,
            issue=50,
            repo="octo-org/example-repo",
            allow_unready=False,
            allow_shared_assignee=False,
            takeover_expired=False,
        )
        ready = {
            "state": "OPEN",
            "assignees": [],
            "url": "https://github.com/octo-org/example-repo/issues/50",
            "labels": [{"name": "상태: 에이전트 작업 가능"}],
            "blockedBy": [],
            "comments": [],
            "parent": None,
        }
        with mock.patch.object(issue_lease, "github_issue_snapshot", return_value=ready):
            self.assertEqual(issue_lease.github_precheck(args, "octocat"), ready)

    def test_ready_body_marker_allows_claim_without_custom_labels(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False,
            issue=50,
            repo="octo-org/example-repo",
            allow_unready=False,
            allow_shared_assignee=False,
            takeover_expired=False,
        )
        ready = {
            "state": "OPEN",
            "assignees": [],
            "url": "https://github.com/octo-org/example-repo/issues/50",
            "labels": [],
            "body": "<!-- work-github-issue:state role=ready-for-agent -->",
            "blockedBy": [],
            "comments": [],
            "parent": None,
        }
        with mock.patch.object(issue_lease, "github_issue_snapshot", return_value=ready):
            self.assertEqual(issue_lease.github_precheck(args, "octocat"), ready)

        conflicting = dict(ready)
        conflicting["labels"] = [{"name": "needs-info"}]
        with mock.patch.object(
            issue_lease, "github_issue_snapshot", return_value=conflicting
        ):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_precheck(args, "octocat")

    def test_claim_rejects_multiple_state_labels_and_aliases(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False,
            issue=50,
            repo="octo-org/example-repo",
            allow_unready=False,
            allow_shared_assignee=False,
            takeover_expired=False,
        )
        base = {
            "state": "OPEN",
            "assignees": [],
            "url": "https://github.com/octo-org/example-repo/issues/50",
            "blockedBy": [],
            "comments": [],
            "parent": None,
        }
        conflicts = (
            ["상태: 에이전트 작업 가능", "상태: 정보 필요"],
            ["ready-for-agent", "상태: 에이전트 작업 가능"],
        )
        for labels in conflicts:
            snapshot = dict(base)
            snapshot["labels"] = [{"name": label} for label in labels]
            with mock.patch.object(
                issue_lease, "github_issue_snapshot", return_value=snapshot
            ):
                with self.assertRaises(issue_lease.LeaseFailure):
                    issue_lease.github_precheck(args, "octocat")

    def test_planning_precheck_and_reconcile_do_not_project_a_claim(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False,
            issue=50,
            repo="octo-org/example-repo",
            purpose="planning",
            allow_unready=False,
            allow_shared_assignee=False,
            takeover_expired=False,
        )
        snapshot = {
            "state": "OPEN",
            "assignees": [{"login": "another-account"}],
            "url": "https://github.com/octo-org/example-repo/issues/50",
            "labels": [{"name": "needs-triage"}],
            "blockedBy": [{"number": 49, "state": "OPEN"}],
            "comments": [],
            "parent": None,
        }
        metadata = {
            "purpose": "planning",
            "session": "session-plan-c",
            "actor": "octocat",
        }
        with (
            mock.patch.object(
                issue_lease,
                "github_issue_snapshot",
                side_effect=[snapshot, snapshot],
            ),
            mock.patch.object(issue_lease, "run") as invoked,
        ):
            self.assertEqual(issue_lease.github_precheck(args, "octocat"), snapshot)
            issue_lease.github_reconcile_claim(args, metadata, False)
        invoked.assert_not_called()

    def test_missing_projection_is_repaired(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False, issue=51, repo="octo-org/example-repo"
        )
        snapshot = {
            "state": "OPEN",
            "assignees": [],
            "url": "https://github.com/octo-org/example-repo/issues/51",
            "labels": [{"name": "ready-for-agent"}],
            "blockedBy": [],
            "comments": [],
            "parent": None,
        }
        metadata = {
            "session": "session-repair",
            "actor": "octocat",
            "branch": "agent/repair",
            "headSha": "a" * 40,
            "expiresAt": "2030-01-01T00:00:00Z",
        }
        projected = dict(snapshot)
        projected["assignees"] = [{"login": "octocat"}]
        projected["comments"] = [
            {"body": issue_lease.claim_marker("session-repair")}
        ]
        completed = subprocess.CompletedProcess([], 0, "", "")
        with (
            mock.patch.object(
                issue_lease,
                "github_issue_snapshot",
                side_effect=[snapshot, projected],
            ),
            mock.patch.object(issue_lease, "run", return_value=completed) as invoked,
        ):
            issue_lease.github_reconcile_claim(args, metadata, False)
        commands = [call.args[0] for call in invoked.call_args_list]
        self.assertTrue(any(command[1:3] == ["issue", "edit"] for command in commands))
        self.assertTrue(any(command[1:3] == ["issue", "comment"] for command in commands))

    def test_production_actor_override_is_rejected(self) -> None:
        args = issue_lease.argparse.Namespace(
            actor="spoofed-user", no_github_sync=False
        )
        with self.assertRaises(issue_lease.LeaseFailure):
            issue_lease.github_actor(args)

    def test_post_claim_gate_drift_is_rejected(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False, issue=52, repo="octo-org/example-repo"
        )
        ready = {
            "state": "OPEN",
            "assignees": [{"login": "octocat"}],
            "url": "https://github.com/octo-org/example-repo/issues/52",
            "labels": [{"name": "ready-for-agent"}],
            "blockedBy": [],
            "comments": [],
            "parent": None,
        }
        drifted = dict(ready)
        drifted["comments"] = [
            {"body": issue_lease.claim_marker("session-drift")}
        ]
        drifted["blockedBy"] = [
            {
                "number": 51,
                "title": "New blocker",
                "url": "https://github.com/octo-org/example-repo/issues/51",
                "state": "OPEN",
            }
        ]
        metadata = {
            "session": "session-drift",
            "actor": "octocat",
            "branch": "agent/drift",
            "headSha": "b" * 40,
            "expiresAt": "2030-01-01T00:00:00Z",
            "readinessOverride": False,
        }
        completed = subprocess.CompletedProcess([], 0, "", "")
        with (
            mock.patch.object(
                issue_lease,
                "github_issue_snapshot",
                side_effect=[ready, drifted],
            ),
            mock.patch.object(issue_lease, "run", return_value=completed),
        ):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_reconcile_claim(args, metadata, False)

    def test_release_outcome_requires_matching_issue_state(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False,
            issue=53,
            repo="octo-org/example-repo",
            outcome="completed",
        )
        opened = {
            "state": "OPEN",
            "assignees": [{"login": "octocat"}],
            "url": "https://github.com/octo-org/example-repo/issues/53",
            "labels": [{"name": "ready-for-agent"}],
            "blockedBy": [],
            "comments": [],
            "parent": None,
        }
        with mock.patch.object(issue_lease, "github_issue_snapshot", return_value=opened):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_release_precheck(args)

        args.outcome = "blocked"
        with mock.patch.object(issue_lease, "github_issue_snapshot", return_value=opened):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_release_precheck(args)

        needs_info = dict(opened)
        needs_info["labels"] = [{"name": "needs-info"}]
        needs_info["comments"] = [
            {
                "body": HUMAN_ACTION_WITHOUT_SUGGESTED_COMMENT
                + "\n**추천 댓글:** 답변을 남겨 주세요."
            }
        ]
        with mock.patch.object(
            issue_lease, "github_issue_snapshot", return_value=needs_info
        ):
            issue_lease.github_release_precheck(args)

        marker_only = dict(opened)
        marker_only["labels"] = []
        marker_only["body"] = (
            "<!-- work-github-issue:state role=needs-info -->"
        )
        marker_only["comments"] = needs_info["comments"]
        with mock.patch.object(
            issue_lease, "github_issue_snapshot", return_value=marker_only
        ):
            issue_lease.github_release_precheck(args)

        for korean_state, human_action in (
            ("상태: 정보 필요", HUMAN_ACTION_WITHOUT_SUGGESTED_COMMENT),
            ("상태: 사람 검토 필요", VALID_HUMAN_ACTION_BODY),
        ):
            localized = dict(opened)
            localized["labels"] = [{"name": korean_state}]
            localized["comments"] = [{"body": human_action}]
            with mock.patch.object(
                issue_lease, "github_issue_snapshot", return_value=localized
            ):
                issue_lease.github_release_precheck(args)

        conflicting = dict(opened)
        conflicting["labels"] = [
            {"name": "ready-for-agent"},
            {"name": "needs-info"},
        ]
        with mock.patch.object(
            issue_lease, "github_issue_snapshot", return_value=conflicting
        ):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_release_precheck(args)

        duplicate_aliases = dict(opened)
        duplicate_aliases["labels"] = [
            {"name": "needs-info"},
            {"name": "상태: 정보 필요"},
        ]
        with mock.patch.object(
            issue_lease, "github_issue_snapshot", return_value=duplicate_aliases
        ):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_release_precheck(args)

    def test_blocked_human_wait_requires_actionable_human_contract(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False,
            issue=53,
            repo="octo-org/example-repo",
            outcome="blocked",
        )
        base = {
            "state": "OPEN",
            "assignees": [],
            "url": "https://github.com/octo-org/example-repo/issues/53",
            "labels": [{"name": "상태: 사람 검토 필요"}],
            "blockedBy": [],
            "comments": [],
            "parent": None,
            "body": "",
        }
        vague = dict(base)
        vague["comments"] = [
            {
                "body": "\n".join(
                    [
                        "## 사람에게 필요한 도움",
                        "**필요한 이유:** 확인이 필요합니다.",
                        "**요청 종류:** 검토",
                        "**대상:** 변경 사항",
                        "### 해 주실 일",
                        "- [ ] 검토해 주세요.",
                        "**답변/결과를 남길 곳:** 이슈 댓글",
                        "**완료 조건:** 확인 완료",
                        "**완료 증거:** 이슈 댓글",
                        "**완료 후 상태:** 상태 변경",
                        "**전환 담당:** 사람",
                    ]
                )
            }
        ]
        paraphrased_vague = dict(base)
        paraphrased_vague["comments"] = [
            {
                "body": "\n".join(
                    [
                        "## 사람에게 필요한 도움",
                        "**필요한 이유:** 안전한 진행을 위해 사람의 판단이 필요합니다.",
                        "**요청 종류:** 검토",
                        "**대상:** 적절한 처리",
                        "### 해 주실 일",
                        "- [ ] 적절한 처리를 검토한 뒤 처리해 주세요.",
                        "**답변/결과를 남길 곳:** 이슈 댓글",
                        "**완료 조건:** 처리 결과가 댓글로 등록됨",
                        "**완료 증거:** 이슈 댓글",
                        "**완료 후 상태:** 상태: 에이전트 작업 가능",
                        "**전환 담당:** prepare-issue",
                    ]
                )
            }
        ]
        unknown_state = dict(base)
        unknown_state["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    "상태: 에이전트 작업 가능", "상태: 나중에 결정"
                )
            }
        ]
        imprecise = dict(base)
        imprecise["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    "PR #42 권한 변경을 검토하고 승인 또는 수정 요청을 PR #42 리뷰에 남겨 주세요.",
                    "PR #42를 봐 주세요.",
                ).replace(
                    "승인 또는 구체적인 수정 요청이 리뷰로 등록됨",
                    "처리가 끝남",
                ).replace(
                    "PR #42 승인 또는 수정 요청 리뷰 링크",
                    "처리 완료",
                )
            }
        ]
        missing_owner = dict(base)
        missing_owner["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    "\n**전환 담당:** prepare-issue", ""
                )
            }
        ]
        wrong_owner = dict(base)
        wrong_owner["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    "**전환 담당:** prepare-issue", "**전환 담당:** 사람"
                )
            }
        ]
        missing_suggested_comment = dict(base)
        missing_suggested_comment["comments"] = [
            {"body": HUMAN_ACTION_WITHOUT_SUGGESTED_COMMENT}
        ]
        unhelpful_suggested_comment = dict(base)
        unhelpful_suggested_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    SUGGESTED_REVIEW_COMMENT_WITHOUT_RATIONALE,
                )
            }
        ]
        misleading_completed_comment = dict(base)
        misleading_completed_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    MISLEADING_COMPLETED_REVIEW_COMMENT,
                )
            }
        ]
        precompleted_comment = dict(base)
        precompleted_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    PRECOMPLETED_REVIEW_COMMENT,
                )
            }
        ]
        generic_result_comment = dict(base)
        generic_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    GENERIC_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        duplicate_result_comment = dict(base)
        duplicate_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    DUPLICATE_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        substring_evidence_comment = dict(base)
        substring_evidence_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    SUBSTRING_EVIDENCE_REVIEW_COMMENT,
                )
            }
        ]
        lettered_result_comment = dict(base)
        lettered_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    LETTERED_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        punctuation_result_comment = dict(base)
        punctuation_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    PUNCTUATION_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        unrelated_result_comment = dict(base)
        unrelated_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    UNRELATED_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        disguised_unrelated_result_comment = dict(base)
        disguised_unrelated_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    DISGUISED_UNRELATED_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        bare_result_comment = dict(base)
        bare_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    BARE_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        substring_result_comment = dict(base)
        substring_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    SUBSTRING_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        truncated_result_comment = dict(base)
        truncated_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    TRUNCATED_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        incomplete_result_comment = dict(base)
        incomplete_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    INCOMPLETE_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        generic_controlled_result_comment = dict(base)
        generic_controlled_result_comment["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    GENERIC_CONTROLLED_RESULT_REVIEW_COMMENT,
                )
            }
        ]
        self_referential_response = dict(base)
        self_referential_response["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    "이슈 #53 댓글 (실제 검토는 PR #42 리뷰)",
                    "PR #42 리뷰",
                )
            }
        ]
        implicit_review_self_response = dict(base)
        implicit_review_self_response["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    "승인 또는 수정 요청을 PR #42 리뷰에 남겨 주세요.",
                    "승인 또는 수정 요청을 남겨 주세요.",
                ).replace(
                    "이슈 #53 댓글 (실제 검토는 PR #42 리뷰)",
                    "PR #42 리뷰",
                )
            }
        ]
        completion_evidence_self_response = dict(base)
        completion_evidence_self_response["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    SUGGESTED_REVIEW_COMMENT,
                    GENERIC_EVIDENCE_REVIEW_COMMENT,
                ).replace(
                    "이슈 #53 댓글 (실제 검토는 PR #42 리뷰)",
                    "PR #42 리뷰",
                )
            }
        ]
        conflicting_destination = dict(base)
        conflicting_destination["comments"] = [
            {
                "body": VALID_HUMAN_ACTION_BODY.replace(
                    "상태: 에이전트 작업 가능",
                    "상태: 에이전트 작업 가능 또는 상태: 정보 필요",
                )
            }
        ]
        for index, snapshot in enumerate((
            base,
            vague,
            paraphrased_vague,
            unknown_state,
            imprecise,
            missing_owner,
            wrong_owner,
            missing_suggested_comment,
            unhelpful_suggested_comment,
            misleading_completed_comment,
            precompleted_comment,
            generic_result_comment,
            duplicate_result_comment,
            substring_evidence_comment,
            lettered_result_comment,
            punctuation_result_comment,
            unrelated_result_comment,
            disguised_unrelated_result_comment,
            bare_result_comment,
            substring_result_comment,
            truncated_result_comment,
            incomplete_result_comment,
            generic_controlled_result_comment,
            self_referential_response,
            implicit_review_self_response,
            completion_evidence_self_response,
            conflicting_destination,
        )):
            with self.subTest(invalid_snapshot=index):
                with mock.patch.object(
                    issue_lease, "github_issue_snapshot", return_value=snapshot
                ):
                    with self.assertRaises(issue_lease.LeaseFailure):
                        issue_lease.github_release_precheck(args)

        english = dict(base)
        english["body"] = "\n".join(
            [
                "## Human action required",
                "**Why this is needed:** A maintainer must approve the security boundary.",
                "**Request type:** Review",
                "**Target:** PR #42",
                "### What to do",
                "- [ ] Review PR #42 and submit an approval or specific change request.",
                "**Where to respond:** issue #53 comment after the PR #42 review",
                "**Completion condition:** An approval or actionable change request is recorded.",
                "**Completion evidence:** PR #42 approval or change-request review link",
                "**State after completion:** ready-for-agent",
                "**Transition owner:** prepare-issue",
                "**Suggested comment:** PR #42 — Result: [approved | changes requested]. Rationale: [write]. Evidence: [paste the PR #42 review URL].",
            ]
        )
        with mock.patch.object(
            issue_lease, "github_issue_snapshot", return_value=english
        ):
            issue_lease.github_release_precheck(args)

        english_truncated_result = dict(english)
        english_truncated_result["body"] = english["body"].replace(
            "approved | changes requested", "approve | quest"
        )
        with mock.patch.object(
            issue_lease,
            "github_issue_snapshot",
            return_value=english_truncated_result,
        ):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_release_precheck(args)

        english_incomplete_result = dict(english)
        english_incomplete_result["body"] = english["body"].replace(
            "approved | changes requested", "approve | request"
        )
        with mock.patch.object(
            issue_lease,
            "github_issue_snapshot",
            return_value=english_incomplete_result,
        ):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_release_precheck(args)

        english_generic_controlled_result = dict(english)
        english_generic_controlled_result["body"] = english["body"].replace(
            "approved | changes requested", "comment | review outcome"
        )
        with mock.patch.object(
            issue_lease,
            "github_issue_snapshot",
            return_value=english_generic_controlled_result,
        ):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.github_release_precheck(args)

        legacy_owner = dict(base)
        legacy_owner["body"] = VALID_HUMAN_ACTION_BODY.replace(
            "**전환 담당:** prepare-issue", "**전환 담당:** triage"
        )
        with mock.patch.object(
            issue_lease, "github_issue_snapshot", return_value=legacy_owner
        ):
            issue_lease.github_release_precheck(args)

        closure = dict(base)
        closure["body"] = VALID_HUMAN_ACTION_BODY.replace(
            "상태: 에이전트 작업 가능", "완료 증거와 함께 종료"
        ).replace("**전환 담당:** prepare-issue", "**전환 담당:** work-github-issue")
        with mock.patch.object(
            issue_lease, "github_issue_snapshot", return_value=closure
        ):
            issue_lease.github_release_precheck(args)

    def test_suggested_comment_supports_human_request_types(self) -> None:
        cases = (
            (
                "검토",
                "릴리스 후보",
                "릴리스 후보를 검토하고 승인 또는 거절 결과를 남겨 주세요.",
                "릴리스 후보 — 결과: [승인 | 거절]. 판단 근거: [작성]. 완료 증거: [검토 댓글 링크].",
            ),
            (
                "결정",
                "데이터베이스 엔진",
                "데이터베이스 엔진을 PostgreSQL 또는 MySQL로 결정하고 근거를 남겨 주세요.",
                "데이터베이스 엔진 — 결과: [PostgreSQL | MySQL]. 판단 근거: [작성]. 완료 증거: [결정 댓글 링크].",
            ),
            (
                "권한 부여",
                "운영 계정",
                "운영 계정의 배포 권한 부여 또는 거절을 결정하고 근거를 남겨 주세요.",
                "운영 계정 — 결과: [권한 부여 | 권한 거절]. 판단 근거: [작성]. 완료 증거: [감사 로그 링크].",
            ),
            (
                "수동 작업",
                "프로덕션 재시작",
                "프로덕션 재시작을 실행하고 성공 또는 실패 결과를 남겨 주세요.",
                "프로덕션 재시작 — 결과: [성공 | 실패]. 판단 근거: [작성]. 완료 증거: [운영 로그 링크].",
            ),
        )
        for request_type, target, action, suggested_comment in cases:
            body = "\n".join(
                [
                    "## 사람에게 필요한 도움",
                    "**필요한 이유:** 사람이 직접 판단하거나 실행해야 안전하게 계속할 수 있습니다.",
                    f"**요청 종류:** {request_type}",
                    f"**대상:** {target}",
                    "### 해 주실 일",
                    f"- [ ] {action}",
                    "**답변/결과를 남길 곳:** 이슈 #53 댓글",
                    "**완료 조건:** 요청한 결과와 근거가 이슈 댓글에 등록됨",
                    "**완료 증거:** 이슈 #53 결과 댓글 링크",
                    "**완료 후 상태:** 상태: 에이전트 작업 가능",
                    "**전환 담당:** prepare-issue",
                    f"**추천 댓글:** {suggested_comment}",
                ]
            )
            self.assertTrue(
                issue_lease.human_action_contract_is_complete(
                    body, require_suggested_comment=True
                ),
                request_type,
            )

    def test_invalid_display_language_does_not_delete_the_lease(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=True,
            issue=53,
            evidence="local-test:blocked",
            outcome="blocked",
            display_language=None,
            remote="origin",
        )
        metadata = {
            "session": "session-language",
            "purpose": "implementation",
            "displayLanguage": "invalid",
        }
        with (
            mock.patch.object(
                issue_lease,
                "require_owned",
                return_value=("a" * 40, metadata),
            ),
            mock.patch.object(issue_lease, "delete_lease") as deleted,
        ):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.command_release(args)
        deleted.assert_not_called()

    def test_production_evidence_must_be_existing_issue_comment(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False, issue=54, repo="octo-org/example-repo"
        )
        with self.assertRaises(issue_lease.LeaseFailure):
            issue_lease.validate_evidence(
                args, "not-durable", "session-evidence", "completed"
            )

        url = "https://github.com/octo-org/example-repo/issues/54#issuecomment-12345"
        comment = {
            "html_url": url,
            "issue_url": "https://api.github.com/repos/octo-org/example-repo/issues/54",
            "body": "\n".join(
                [
                    "<!-- rca-issue-evidence:v1 session=session-evidence outcome=completed -->",
                    "## Outcome",
                    "complete",
                    "## Changes",
                    "commit abc",
                    "## Verification",
                    "tests green",
                    "## Limitations",
                    "none",
                    "## Safety",
                    "no mutation",
                ]
            ),
        }
        completed = subprocess.CompletedProcess([], 0, json.dumps(comment), "")
        with mock.patch.object(issue_lease, "run", return_value=completed):
            self.assertEqual(
                issue_lease.validate_evidence(
                    args, url, "session-evidence", "completed"
                ),
                url,
            )

        claim_comment = dict(comment)
        claim_comment["body"] = issue_lease.claim_marker("session-evidence")
        completed = subprocess.CompletedProcess([], 0, json.dumps(claim_comment), "")
        with mock.patch.object(issue_lease, "run", return_value=completed):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.validate_evidence(
                    args, url, "session-evidence", "completed"
                )

        empty_sections = dict(comment)
        empty_sections["body"] = "\n".join(
            [
                "<!-- rca-issue-evidence:v1 session=session-evidence outcome=completed -->",
                "## Outcome",
                "## Changes",
                "## Verification",
                "## Limitations",
                "## Safety",
            ]
        )
        completed = subprocess.CompletedProcess([], 0, json.dumps(empty_sections), "")
        with mock.patch.object(issue_lease, "run", return_value=completed):
            with self.assertRaises(issue_lease.LeaseFailure):
                issue_lease.validate_evidence(
                    args, url, "session-evidence", "completed"
                )

    def test_production_evidence_accepts_korean_sections(self) -> None:
        args = issue_lease.argparse.Namespace(
            no_github_sync=False, issue=54, repo="octo-org/example-repo"
        )
        url = "https://github.com/octo-org/example-repo/issues/54#issuecomment-12345"
        comment = {
            "html_url": url,
            "issue_url": "https://api.github.com/repos/octo-org/example-repo/issues/54",
            "body": "\n".join(
                [
                    "<!-- rca-issue-evidence:v1 session=session-evidence outcome=blocked -->",
                    "## 결과",
                    "사람의 승인을 기다립니다.",
                    "## 변경 사항",
                    "커밋 abc를 준비했습니다.",
                    "## 검증",
                    "테스트가 통과했습니다.",
                    "## 제한 사항",
                    "아직 병합되지 않았습니다.",
                    "## 안전",
                    "원격 병합은 수행하지 않았습니다.",
                    "## 다음 행동",
                    "유지보수자가 PR을 검토하고 승인 여부를 댓글로 알려 주세요.",
                ]
            ),
        }
        completed = subprocess.CompletedProcess([], 0, json.dumps(comment), "")
        with mock.patch.object(issue_lease, "run", return_value=completed):
            self.assertEqual(
                issue_lease.validate_evidence(
                    args, url, "session-evidence", "blocked"
                ),
                url,
            )


if __name__ == "__main__":
    unittest.main()
