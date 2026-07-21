#!/usr/bin/env python3
"""Atomic Git-ref leases for same-account GitHub issue and planning workers."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import uuid
from dataclasses import dataclass
from typing import Any, NoReturn


SCHEMA = "rca.issue-lease.v1"
MARKER = "RCA-ISSUE-LEASE-V1"
SESSION_RE = re.compile(r"^[A-Za-z0-9._-]{8,128}$")
STATE_LABELS_BY_ROLE = {
    "needs-triage": {"needs-triage", "상태: 분류 필요"},
    "needs-info": {"needs-info", "상태: 정보 필요"},
    "ready-for-agent": {"ready-for-agent", "상태: 에이전트 작업 가능"},
    "ready-for-human": {"ready-for-human", "상태: 사람 검토 필요"},
    "wontfix": {"wontfix", "상태: 진행하지 않음"},
}
STATE_ROLE_BY_LABEL = {
    label: role
    for role, labels in STATE_LABELS_BY_ROLE.items()
    for label in labels
}
EVIDENCE_SECTION_ALIASES = {
    "outcome": {"## Outcome", "## 결과"},
    "changes": {"## Changes", "## 변경 사항"},
    "verification": {"## Verification", "## 검증"},
    "limitations": {"## Limitations", "## 제한 사항"},
    "safety": {"## Safety", "## 안전"},
    "next-action": {"## Next action", "## 다음 행동"},
}
EVIDENCE_SECTION_BY_HEADING = {
    heading: section
    for section, headings in EVIDENCE_SECTION_ALIASES.items()
    for heading in headings
}
HUMAN_ACTION_HEADINGS = {
    "## 사람에게 필요한 도움",
    "## Human action required",
}
HUMAN_ACTION_FIELD_ALIASES = {
    "reason": {"**필요한 이유:**", "**Why this is needed:**"},
    "request-type": {"**요청 종류:**", "**Request type:**"},
    "target": {"**대상:**", "**Target:**"},
    "response": {"**답변/결과를 남길 곳:**", "**Where to respond:**"},
    "completion": {"**완료 조건:**", "**Completion condition:**"},
    "completion-evidence": {"**완료 증거:**", "**Completion evidence:**"},
    "next-state": {"**완료 후 상태:**", "**State after completion:**"},
    "transition-owner": {"**전환 담당:**", "**Transition owner:**"},
}
HUMAN_ACTION_SUGGESTED_COMMENT_ALIASES = {
    "**추천 댓글:**",
    "**Suggested comment:**",
}
SUGGESTED_COMMENT_SLOT_ALIASES = {
    "result": {"결과", "Result"},
    "rationale": {"판단 근거", "근거", "Rationale", "Reason"},
    "evidence": {"완료 증거", "증거", "Evidence", "Review link", "리뷰 링크"},
}
HUMAN_ACTION_STEP_HEADINGS = {"### 해 주실 일", "### What to do"}
# Read old issue bodies created before the skill rename; new templates publish only prepare-issue.
OPEN_STATE_TRANSITION_OWNERS = {"prepare-issue", "triage"}
HUMAN_ACTION_REQUEST_TYPES = {
    "질문",
    "결정",
    "승인",
    "권한부여",
    "병합",
    "수동작업",
    "검토",
    "question",
    "decision",
    "approval",
    "accessgrant",
    "merge",
    "manualaction",
    "review",
}
HUMAN_ACTION_RESULT_TOKENS = {
    "질문": {"답변", "제공", "알려", "작성", "나열"},
    "question": {"answer", "provide", "describe", "list"},
    "결정": {"결정", "선택"},
    "decision": {"decide", "choose", "select"},
    "승인": {"승인", "거절", "수정요청"},
    "approval": {
        "approve",
        "approved",
        "approval",
        "reject",
        "rejected",
        "requestchanges",
        "changesrequested",
        "changerequest",
    },
    "권한부여": {"권한부여", "접근허용", "권한변경", "권한거절", "접근거절"},
    "accessgrant": {
        "grantaccess",
        "grantpermission",
        "changepermission",
        "denyaccess",
        "denypermission",
        "accessdenied",
        "permissiondenied",
    },
    "병합": {"병합"},
    "merge": {"merge", "merged"},
    "수동작업": {"실행", "변경", "입력", "업로드", "재시작", "배포", "설정"},
    "manualaction": {"run", "change", "enter", "upload", "restart", "deploy", "configure"},
    "검토": {"승인", "거절", "수정요청", "의견", "검토결과"},
    "review": {
        "approve",
        "approved",
        "approval",
        "requestchanges",
        "changesrequested",
        "changerequest",
        "comment",
        "reviewoutcome",
    },
}
CONTROLLED_SUGGESTED_RESULT_TOKENS = {
    "검토": {"승인", "거절", "수정요청"},
    "review": {
        "approve",
        "approved",
        "approval",
        "reject",
        "rejected",
        "requestchanges",
        "changesrequested",
        "changerequest",
    },
    "승인": {"승인", "거절", "수정요청"},
    "approval": {
        "approve",
        "approved",
        "approval",
        "reject",
        "rejected",
        "requestchanges",
        "changesrequested",
        "changerequest",
    },
}
HUMAN_ACTION_EVIDENCE_TOKENS = {
    "url",
    "id",
    "댓글",
    "리뷰",
    "로그",
    "링크",
    "스크린샷",
    "기록",
    "comment",
    "review",
    "log",
    "link",
    "screenshot",
    "record",
}
GENERIC_SUGGESTED_RESULT_RE = re.compile(
    r"^(?:(?:선택|결과|옵션)(?:\d+|[a-z]|가|나|하나|둘|첫째|둘째)|"
    r"(?:choice|option|result)(?:\d+|[a-z]|one|two|first|second))$",
    re.IGNORECASE,
)
GENERIC_HUMAN_ACTION_TEXT = {
    "검토해주세요",
    "확인해주세요",
    "정보를주세요",
    "확인이필요합니다",
    "확인완료",
    "상태변경",
    "review",
    "please review",
    "more information needed",
    "state change",
    "done",
}
GENERIC_HUMAN_ACTION_PATTERNS = {
    "적절",
    "알아서",
    "필요한조치",
    "asappropriate",
    "asneeded",
    "handleit",
    "takecare",
}
LEASE_PURPOSES = {"implementation", "planning"}
DISPLAY_LANGUAGES = {"en", "ko"}


@dataclass
class LeaseFailure(Exception):
    message: str
    code: int = 2
    details: dict[str, Any] | None = None


def run(
    args: list[str], *, input_text: str | None = None, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise LeaseFailure(f"command failed: {' '.join(args)}: {detail}")
    return result


def emit(status: str, **fields: Any) -> None:
    print(json.dumps({"status": status, **fields}, sort_keys=True))


def fail(error: LeaseFailure) -> NoReturn:
    emit("error", error=error.message, **(error.details or {}))
    raise SystemExit(error.code)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> dt.datetime:
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise LeaseFailure(f"invalid lease timestamp: {value!r}") from error


def ref_for(issue: int) -> str:
    return f"refs/notes/rca-issue-leases/{issue}"


def session_ref_for(session: str) -> str:
    return f"refs/notes/rca-agent-sessions/{session}"


def ensure_repo() -> None:
    run(["git", "rev-parse", "--show-toplevel"])


def remote_sha(remote: str, ref: str) -> str | None:
    result = run(["git", "ls-remote", "--refs", remote, ref])
    line = result.stdout.strip()
    if not line:
        return None
    fields = line.split()
    if len(fields) != 2 or fields[1] != ref:
        raise LeaseFailure(f"unexpected ls-remote result for {ref}")
    return fields[0]


def ensure_object(remote: str, ref: str, sha: str) -> None:
    present = run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], check=False)
    if present.returncode == 0:
        return
    run(["git", "fetch", "--quiet", "--no-tags", remote, ref])


def read_lease(
    remote: str,
    ref: str,
    sha: str,
    *,
    expected_issue: int | None = None,
    expected_session: str | None = None,
) -> dict[str, Any]:
    ensure_object(remote, ref, sha)
    body = run(["git", "show", "-s", "--format=%B", sha]).stdout.strip()
    lines = body.splitlines()
    if len(lines) < 2 or lines[0] != MARKER:
        raise LeaseFailure(f"{ref} is not an RCA issue lease")
    try:
        value = json.loads("\n".join(lines[1:]))
    except json.JSONDecodeError as error:
        raise LeaseFailure(f"{ref} contains invalid lease JSON") from error
    if value.get("schemaVersion") != SCHEMA or not isinstance(value.get("issue"), int):
        raise LeaseFailure(f"{ref} lease identity is invalid")
    if expected_issue is not None and value["issue"] != expected_issue:
        raise LeaseFailure(f"{ref} lease identity does not match issue {expected_issue}")
    if expected_session is not None and value.get("session") != expected_session:
        raise LeaseFailure(f"{ref} lease identity does not match session {expected_session}")
    for field in ("session", "actor", "createdAt", "renewedAt", "expiresAt"):
        if not isinstance(value.get(field), str) or not value[field]:
            raise LeaseFailure(f"{ref} is missing {field}")
    if value.get("purpose", "implementation") not in LEASE_PURPOSES:
        raise LeaseFailure(f"{ref} has an invalid lease purpose")
    if (
        "displayLanguage" in value
        and value["displayLanguage"] not in DISPLAY_LANGUAGES
    ):
        raise LeaseFailure(f"{ref} has an invalid display language")
    return value


def lease_purpose(metadata: dict[str, Any]) -> str:
    """Return the purpose, treating pre-purpose v1 leases as implementation."""
    return str(metadata.get("purpose", "implementation"))


def lease_display_language(
    metadata: dict[str, Any], override: str | None = None
) -> str:
    value = str(metadata.get("displayLanguage") or override or "en")
    if value not in DISPLAY_LANGUAGES:
        raise LeaseFailure("lease has an invalid display language")
    return value


def current_lease(remote: str, issue: int) -> tuple[str, dict[str, Any]] | None:
    issue_ref = ref_for(issue)
    sha = remote_sha(remote, issue_ref)
    if sha is None:
        return None
    metadata = read_lease(remote, issue_ref, sha, expected_issue=issue)
    session_ref = session_ref_for(metadata["session"])
    session_sha = remote_sha(remote, session_ref)
    if session_sha != sha:
        raise LeaseFailure(
            "issue and session lease refs disagree",
            2,
            {
                "issue": issue,
                "issueRef": issue_ref,
                "issueSha": sha,
                "sessionRef": session_ref,
                "sessionSha": session_sha,
            },
        )
    return sha, metadata


def current_session_lease(
    remote: str, session: str
) -> tuple[str, dict[str, Any]] | None:
    ref = session_ref_for(session)
    sha = remote_sha(remote, ref)
    if sha is None:
        return None
    return sha, read_lease(remote, ref, sha, expected_session=session)


def expired(metadata: dict[str, Any], at: dt.datetime | None = None) -> bool:
    return parse_time(metadata["expiresAt"]) <= (at or now_utc())


def branch_name() -> str:
    branch = run(["git", "branch", "--show-current"]).stdout.strip()
    if branch:
        return branch
    sha = run(["git", "rev-parse", "--short=12", "HEAD"]).stdout.strip()
    return f"detached@{sha}"


def create_commit(metadata: dict[str, Any], parent: str | None) -> str:
    # Lease commits carry metadata only. An empty tree prevents a claim from
    # publishing objects reachable only from an unpushed local source commit.
    tree = run(["git", "mktree"], input_text="").stdout.strip()
    command = ["git", "commit-tree", tree]
    if parent:
        command.extend(["-p", parent])
    message = f"{MARKER}\n{json.dumps(metadata, sort_keys=True, separators=(',', ':'))}\n"
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "RCA Issue Lease",
            "GIT_AUTHOR_EMAIL": "issue-lease@local.invalid",
            "GIT_COMMITTER_NAME": "RCA Issue Lease",
            "GIT_COMMITTER_EMAIL": "issue-lease@local.invalid",
        }
    )
    result = subprocess.run(
        command,
        input=message,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        raise LeaseFailure(f"git commit-tree failed: {result.stderr.strip()}")
    return result.stdout.strip()


def push_lease(
    remote: str,
    issue: int,
    session: str,
    sha: str,
    *,
    previous_sha: str | None = None,
    previous_session: str | None = None,
) -> None:
    issue_ref = ref_for(issue)
    session_ref = session_ref_for(session)
    command = ["git", "push", "--porcelain", "--atomic"]
    if previous_sha is not None:
        command.extend(
            [
                f"--force-with-lease={issue_ref}:{previous_sha}",
                f"--force-with-lease={session_ref}:{previous_sha if previous_session == session else ''}",
            ]
        )
    command.extend([remote, f"{sha}:{issue_ref}", f"{sha}:{session_ref}"])
    if previous_session and previous_session != session:
        old_session_ref = session_ref_for(previous_session)
        command.insert(-3, f"--force-with-lease={old_session_ref}:{previous_sha}")
        command.append(f":{old_session_ref}")
    result = run(command, check=False)
    if result.returncode == 0:
        return
    details: dict[str, Any] = {"issue": issue, "issueRef": issue_ref, "sessionRef": session_ref}
    try:
        winner = current_lease(remote, issue)
        if winner:
            details.update({"remoteSha": winner[0], "lease": winner[1]})
    except LeaseFailure as error:
        details["issueLeaseError"] = error.message
    session_winner = current_session_lease(remote, session)
    if session_winner:
        details.update(
            {"sessionRemoteSha": session_winner[0], "sessionLease": session_winner[1]}
        )
    raise LeaseFailure("lease compare-and-swap lost", 3, details)


def delete_lease(
    remote: str, issue: int, session: str, observed_sha: str
) -> None:
    issue_ref = ref_for(issue)
    session_ref = session_ref_for(session)
    result = run(
        [
            "git",
            "push",
            "--porcelain",
            "--atomic",
            f"--force-with-lease={issue_ref}:{observed_sha}",
            f"--force-with-lease={session_ref}:{observed_sha}",
            remote,
            f":{issue_ref}",
            f":{session_ref}",
        ],
        check=False,
    )
    if result.returncode != 0:
        winner = current_lease(remote, issue)
        details: dict[str, Any] = {
            "issue": issue,
            "issueRef": issue_ref,
            "sessionRef": session_ref,
        }
        if winner:
            details.update({"remoteSha": winner[0], "lease": winner[1]})
        raise LeaseFailure("lease release compare-and-swap lost", 3, details)


def rollback_claim(
    remote: str,
    issue: int,
    session: str,
    claimed_sha: str,
    previous_sha: str | None,
    previous_session: str | None,
) -> None:
    if previous_sha is None or previous_session is None:
        delete_lease(remote, issue, session, claimed_sha)
        return
    issue_ref = ref_for(issue)
    session_ref = session_ref_for(session)
    old_session_ref = session_ref_for(previous_session)
    command = [
        "git",
        "push",
        "--porcelain",
        "--atomic",
        f"--force-with-lease={issue_ref}:{claimed_sha}",
        f"--force-with-lease={session_ref}:{claimed_sha}",
    ]
    if previous_session != session:
        command.append(f"--force-with-lease={old_session_ref}:")
    command.extend([remote, f"{previous_sha}:{issue_ref}"])
    if previous_session == session:
        command.append(f"{previous_sha}:{session_ref}")
    else:
        command.extend([f"{previous_sha}:{old_session_ref}", f":{session_ref}"])
    result = run(command, check=False)
    if result.returncode != 0:
        raise LeaseFailure(
            "failed to roll back lease after GitHub projection failure",
            6,
            {"issue": issue, "session": session, "claimedSha": claimed_sha},
        )


def gh_args(args: argparse.Namespace, *parts: str) -> list[str]:
    command = ["gh", *parts]
    if args.repo:
        command.extend(["--repo", args.repo])
    return command


def github_repo_from_remote(remote: str) -> str:
    url = run(["git", "remote", "get-url", remote]).stdout.strip()
    patterns = (
        r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?$",
        r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$",
        r"ssh://git@github\.com/([^/]+)/([^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, url)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
    raise LeaseFailure(
        f"remote {remote!r} is not a canonical GitHub repository URL",
        2,
        {"remoteUrl": url},
    )


def bind_github_repo(args: argparse.Namespace) -> None:
    if args.no_github_sync:
        return
    remote_repo = github_repo_from_remote(args.remote)
    if args.repo and args.repo.casefold() != remote_repo.casefold():
        raise LeaseFailure(
            "--repo does not match the lease remote",
            2,
            {"remoteRepo": remote_repo, "requestedRepo": args.repo},
        )
    args.repo = remote_repo


def github_actor(args: argparse.Namespace) -> str:
    if args.actor:
        if not args.no_github_sync:
            raise LeaseFailure("--actor is valid only with --no-github-sync")
        return args.actor
    if args.no_github_sync:
        return os.environ.get("USER", "local")
    return run(["gh", "api", "user", "--jq", ".login"]).stdout.strip()


def github_issue_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    fields = "state,assignees,url,labels,blockedBy,comments,parent,body"
    result = run(
        gh_args(args, "issue", "view", str(args.issue), "--json", fields)
    )
    return json.loads(result.stdout)


def recognized_state_labels(labels: set[str]) -> dict[str, str]:
    return {
        label: STATE_ROLE_BY_LABEL[label]
        for label in labels
        if label in STATE_ROLE_BY_LABEL
    }


def normalize_human_action_text(value: str) -> str:
    return re.sub(r"[\s.!?。，、]+", "", value).casefold()


def meaningful_human_action_text(value: str) -> bool:
    value = value.strip()
    if len(value) < 4 or "<" in value or ">" in value:
        return False
    normalized = normalize_human_action_text(value)
    if normalized in {
        normalize_human_action_text(item) for item in GENERIC_HUMAN_ACTION_TEXT
    }:
        return False
    return not any(pattern in normalized for pattern in GENERIC_HUMAN_ACTION_PATTERNS)


def suggested_comment_is_useful(
    value: str,
    target: str,
    request_type: str,
    actions: list[str],
    response_location: str,
    completion_evidence: str,
) -> bool:
    target = target.strip()
    if not target:
        return False

    aliases = {
        slot: "|".join(
            re.escape(alias) for alias in sorted(slot_aliases, key=len, reverse=True)
        )
        for slot, slot_aliases in SUGGESTED_COMMENT_SLOT_ALIASES.items()
    }
    match = re.fullmatch(
        rf"\s*{re.escape(target)}\s*(?:—|-)\s*"
        rf"(?:{aliases['result']})\s*:\s*\[([^\[\]\r\n]+)\]\s*\.\s*"
        rf"(?:{aliases['rationale']})\s*:\s*\[([^\[\]\r\n]+)\]\s*\.\s*"
        rf"(?:{aliases['evidence']})\s*:\s*\[([^\[\]\r\n]+)\]\s*\.?\s*",
        value,
        flags=re.IGNORECASE,
    )
    if match is None:
        return False
    slots = {
        "result": match.group(1).strip(),
        "rationale": match.group(2).strip(),
        "evidence": match.group(3).strip(),
    }
    result_choices = [choice.strip() for choice in slots["result"].split("|")]
    if len(result_choices) < 2 or any(not choice for choice in result_choices):
        return False
    normalized_choices = [normalize_human_action_text(choice) for choice in result_choices]
    if len(set(normalized_choices)) != len(normalized_choices):
        return False
    if any(
        len(choice) < 2 or not re.search(r"[0-9a-z가-힣]", choice)
        for choice in normalized_choices
    ):
        return False
    if any(GENERIC_SUGGESTED_RESULT_RE.fullmatch(choice) for choice in normalized_choices):
        return False
    result_tokens = HUMAN_ACTION_RESULT_TOKENS[request_type]
    action_patterns = []
    for choice in result_choices:
        escaped_choice = re.escape(choice.strip()).replace(r"\ ", r"\s+")
        action_patterns.append(
            re.compile(
                rf"(?<![0-9a-z가-힣]){escaped_choice}"
                rf"(?=$|[^0-9a-z가-힣]|(?:으로|은|는|이|가|을|를|로|와|과)"
                rf"(?=$|[^0-9a-z가-힣]))",
                flags=re.IGNORECASE,
            )
        )
    if request_type in CONTROLLED_SUGGESTED_RESULT_TOKENS:
        allowed_results = CONTROLLED_SUGGESTED_RESULT_TOKENS[request_type]
        if any(choice not in allowed_results for choice in normalized_choices):
            return False
    elif any(
        not any(pattern.search(action) for action in actions)
        and choice not in result_tokens
        for choice, pattern in zip(normalized_choices, action_patterns, strict=True)
    ):
        return False
    if any("<" in slot_value or ">" in slot_value for slot_value in slots.values()):
        return False
    evidence = slots["evidence"]
    evidence_reference = bool(re.search(r"https?://\S+|#\d+", evidence))
    evidence_reference = evidence_reference or any(
        token in evidence for token in {"댓글", "리뷰", "로그", "링크", "스크린샷", "기록"}
    )
    evidence_reference = evidence_reference or bool(
        re.search(
            r"(?<![a-z])(?:url|id|comment|review|log|link|screenshot|record)(?![a-z])",
            evidence,
            flags=re.IGNORECASE,
        )
    )
    if not evidence_reference:
        return False

    evidence_text = normalize_human_action_text(
        f"{evidence} {completion_evidence}"
    )
    creates_review_evidence = (
        request_type in {"검토", "review", "승인", "approval"}
        and any(token in evidence_text for token in {"리뷰", "review"})
    )
    if creates_review_evidence:
        response = normalize_human_action_text(response_location)
        if not (
            ("이슈" in response and "댓글" in response)
            or ("issue" in response and "comment" in response)
        ):
            return False
    return True


def human_action_contract_is_complete(
    body: str, *, require_suggested_comment: bool = False
) -> bool:
    lines = body.splitlines()
    heading_indexes = [
        index for index, line in enumerate(lines) if line in HUMAN_ACTION_HEADINGS
    ]
    if len(heading_indexes) != 1:
        return False
    start = heading_indexes[0] + 1
    block: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        block.append(line.strip())
    if sum(line in HUMAN_ACTION_STEP_HEADINGS for line in block) != 1:
        return False
    field_aliases = dict(HUMAN_ACTION_FIELD_ALIASES)
    if require_suggested_comment:
        field_aliases["suggested-comment"] = HUMAN_ACTION_SUGGESTED_COMMENT_ALIASES
    values: dict[str, str] = {}
    for line in block:
        for field, aliases in field_aliases.items():
            for alias in aliases:
                if line.startswith(alias):
                    if field in values:
                        return False
                    values[field] = line[len(alias) :].strip()
    if any(field not in values for field in field_aliases):
        return False
    if any(
        not meaningful_human_action_text(value)
        for field, value in values.items()
        if field != "request-type"
    ):
        return False
    actions = [
        line[6:].strip()
        for line in block
        if line.startswith("- [ ] ") or line.casefold().startswith("- [x] ")
    ]
    if not actions or not all(meaningful_human_action_text(action) for action in actions):
        return False
    request_type = normalize_human_action_text(values["request-type"])
    if request_type not in HUMAN_ACTION_REQUEST_TYPES:
        return False
    target_value = values["target"]
    target = normalize_human_action_text(target_value)
    normalized_actions = [normalize_human_action_text(action) for action in actions]
    if not any(target in action for action in normalized_actions):
        return False
    if not any(
        token in action
        for token in HUMAN_ACTION_RESULT_TOKENS[request_type]
        for action in normalized_actions
    ):
        return False
    suggested_comment = values.get("suggested-comment")
    if suggested_comment is not None and not suggested_comment_is_useful(
        suggested_comment,
        target_value,
        request_type,
        actions,
        values["response"],
        values["completion-evidence"],
    ):
        return False
    evidence_value = values["completion-evidence"]
    completion_evidence = normalize_human_action_text(evidence_value)
    if not (
        re.search(r"https?://\S+", evidence_value)
        or re.search(r"#\d+", evidence_value)
        or any(token in completion_evidence for token in HUMAN_ACTION_EVIDENCE_TOKENS)
    ):
        return False
    next_state = values["next-state"].casefold()
    destinations = [
        label for label in STATE_ROLE_BY_LABEL if label.casefold() in next_state
    ]
    terminal = any(
        phrase in next_state
        for phrase in ("완료 증거와 함께 종료", "close with completion evidence")
    )
    if len(destinations) + int(terminal) != 1:
        return False
    owner = normalize_human_action_text(values["transition-owner"])
    expected_owners = {"work-github-issue"} if terminal else OPEN_STATE_TRANSITION_OWNERS
    return owner in expected_owners


def latest_human_action_contract(value: dict[str, Any]) -> str | None:
    candidates = [str(value.get("body", ""))]
    candidates.extend(str(comment.get("body", "")) for comment in value["comments"])
    matching = [
        body
        for body in candidates
        if any(heading in body for heading in HUMAN_ACTION_HEADINGS)
    ]
    return matching[-1] if matching else None


def validate_issue_gate(
    args: argparse.Namespace,
    value: dict[str, Any],
    actor: str,
    *,
    allow_unready: bool,
) -> None:
    if value["state"] != "OPEN":
        raise LeaseFailure(f"issue {args.issue} is not open")
    labels = {item["name"] for item in value["labels"]}
    state_labels = recognized_state_labels(labels)
    if len(state_labels) > 1:
        raise LeaseFailure(
            f"issue {args.issue} has conflicting state labels",
            2,
            {
                "stateLabels": sorted(state_labels),
                "stateRoles": sorted(set(state_labels.values())),
                "issueUrl": value["url"],
            },
        )
    if not (labels & STATE_LABELS_BY_ROLE["ready-for-agent"]) and not allow_unready:
        raise LeaseFailure(
            f"issue {args.issue} is not ready-for-agent",
            2,
            {"labels": sorted(labels), "issueUrl": value["url"]},
        )
    open_blockers = [
        {"number": item["number"], "title": item["title"], "url": item["url"]}
        for item in value["blockedBy"]
        if item.get("state") != "CLOSED"
    ]
    if open_blockers:
        raise LeaseFailure(
            f"issue {args.issue} has open blockers",
            2,
            {"blockedBy": open_blockers, "issueUrl": value["url"]},
        )
    others = [item["login"] for item in value["assignees"] if item["login"] != actor]
    if others:
        raise LeaseFailure(
            f"issue {args.issue} is assigned to another account",
            3,
            {"assignees": others, "issueUrl": value["url"]},
        )


def github_precheck(args: argparse.Namespace, actor: str) -> dict[str, Any] | None:
    if args.no_github_sync:
        return None
    if getattr(args, "purpose", "implementation") == "planning":
        if args.issue == 0:
            return None
        value = github_issue_snapshot(args)
        if value["state"] != "OPEN":
            raise LeaseFailure(f"issue {args.issue} is not open")
        return value
    value = github_issue_snapshot(args)
    validate_issue_gate(args, value, actor, allow_unready=args.allow_unready)
    same_account = any(item["login"] == actor for item in value["assignees"])
    if same_account and not (args.allow_shared_assignee or args.takeover_expired):
        raise LeaseFailure(
            f"issue {args.issue} is already assigned to the shared account without a session lease",
            3,
            {
                "assignees": [actor],
                "issueUrl": value["url"],
                "action": "inspect comments and use --allow-shared-assignee only after confirming no active work",
            },
        )
    return value


def claim_marker(session: str) -> str:
    return f"<!-- rca-issue-lease:v1 session={session} -->"


def has_claim_projection(value: dict[str, Any], actor: str, session: str) -> bool:
    assigned = any(item["login"] == actor for item in value["assignees"])
    commented = any(claim_marker(session) in item["body"] for item in value["comments"])
    return assigned and commented


def github_reconcile_claim(
    args: argparse.Namespace, metadata: dict[str, Any], takeover: bool
) -> None:
    if args.no_github_sync:
        return
    if lease_purpose(metadata) == "planning":
        if args.issue == 0:
            return
        value = github_issue_snapshot(args)
        if value["state"] != "OPEN":
            raise LeaseFailure(f"issue {args.issue} is not open")
        return
    value = github_issue_snapshot(args)
    actor = metadata["actor"]
    validate_issue_gate(
        args,
        value,
        actor,
        allow_unready=bool(metadata.get("readinessOverride", False)),
    )
    mutated = False
    if not any(item["login"] == actor for item in value["assignees"]):
        run(gh_args(args, "issue", "edit", str(args.issue), "--add-assignee", "@me"))
        mutated = True
    if any(claim_marker(metadata["session"]) in item["body"] for item in value["comments"]):
        projected = github_issue_snapshot(args) if mutated else value
    else:
        github_claim(args, metadata, takeover)
        projected = github_issue_snapshot(args)
    validate_issue_gate(
        args,
        projected,
        actor,
        allow_unready=bool(metadata.get("readinessOverride", False)),
    )
    if not has_claim_projection(projected, actor, metadata["session"]):
        raise LeaseFailure(
            "GitHub claim projection did not converge",
            6,
            {"issueUrl": projected["url"]},
        )


def github_claim(args: argparse.Namespace, metadata: dict[str, Any], takeover: bool) -> None:
    if args.no_github_sync:
        return
    language = lease_display_language(
        metadata, getattr(args, "display_language", None)
    )
    if language == "ko":
        action = "만료된 lease를 인수했습니다." if takeover else "lease를 획득했습니다."
        body = "\n".join(
            [
                claim_marker(metadata["session"]),
                f"에이전트 세션 {action}",
                "",
                f"- 세션: `{metadata['session']}`",
                f"- 브랜치: `{metadata['branch']}`",
                f"- 시작 HEAD: `{metadata['headSha']}`",
                f"- 최초 만료 시각: `{metadata['expiresAt']}`",
                f"- 소유권 기준: `{ref_for(args.issue)}` (갱신하면 만료 시각이 연장될 수 있습니다)",
            ]
        )
    else:
        action = "took over an expired" if takeover else "acquired"
        body = "\n".join(
            [
                claim_marker(metadata["session"]),
                f"Agent session lease {action}.",
                "",
                f"- Session: `{metadata['session']}`",
                f"- Branch: `{metadata['branch']}`",
                f"- Source HEAD: `{metadata['headSha']}`",
                f"- Initial expiry: `{metadata['expiresAt']}`",
                f"- Authority: `{ref_for(args.issue)}` (renewals may extend the expiry)",
            ]
        )
    run(gh_args(args, "issue", "comment", str(args.issue), "--body", body))


def github_release(
    args: argparse.Namespace, outcome: str, session: str, display_language: str
) -> None:
    if args.no_github_sync:
        return
    if outcome != "completed":
        run(gh_args(args, "issue", "edit", str(args.issue), "--remove-assignee", "@me"))
    if display_language == "ko":
        outcome_label = {
            "completed": "완료",
            "blocked": "차단됨",
            "handoff": "인계",
        }[outcome]
        body = "\n".join(
            [
                f"<!-- rca-issue-lease-release:v1 session={session} -->",
                f"에이전트 세션 lease를 `{outcome_label}` 결과로 해제했습니다 (`{outcome}`).",
                f"증거: {args.evidence}",
            ]
        )
    else:
        body = "\n".join(
            [
                f"<!-- rca-issue-lease-release:v1 session={session} -->",
                f"Agent session lease released with outcome `{outcome}`.",
                f"Evidence: {args.evidence}",
            ]
        )
    run(gh_args(args, "issue", "comment", str(args.issue), "--body", body))


def github_release_precheck(args: argparse.Namespace) -> None:
    if args.no_github_sync:
        return
    value = github_issue_snapshot(args)
    expected = "CLOSED" if args.outcome == "completed" else "OPEN"
    if value["state"] != expected:
        raise LeaseFailure(
            f"release outcome {args.outcome} requires issue state {expected.lower()}",
            2,
            {"issueUrl": value["url"], "actualState": value["state"]},
        )
    if args.outcome == "blocked":
        labels = {item["name"] for item in value["labels"]}
        open_blockers = [item for item in value["blockedBy"] if item.get("state") != "CLOSED"]
        state_labels = recognized_state_labels(labels)
        state_roles = set(state_labels.values())
        if len(state_labels) != 1:
            raise LeaseFailure(
                "blocked release requires exactly one recognized state role",
                2,
                {
                    "stateLabels": sorted(state_labels),
                    "stateRoles": sorted(state_roles),
                    "issueUrl": value["url"],
                },
            )
        if not open_blockers and state_roles.isdisjoint({"needs-info", "ready-for-human"}):
            raise LeaseFailure(
                "blocked release requires an open blocker, needs-info, or ready-for-human state",
                2,
                {"labels": sorted(labels), "issueUrl": value["url"]},
            )
        if not state_roles.isdisjoint({"needs-info", "ready-for-human"}):
            human_action = latest_human_action_contract(value)
            require_suggested_comment = "ready-for-human" in state_roles
            if human_action is None or not human_action_contract_is_complete(
                human_action,
                require_suggested_comment=require_suggested_comment,
            ):
                requirement = (
                    "an actionable Human action contract including a useful "
                    "Suggested comment"
                    if require_suggested_comment
                    else "an actionable Human action contract"
                )
                raise LeaseFailure(
                    f"blocked human-wait release requires {requirement}",
                    2,
                    {"stateRoles": sorted(state_roles), "issueUrl": value["url"]},
                )


def validate_session(value: str) -> str:
    if not SESSION_RE.fullmatch(value):
        raise LeaseFailure("session must be 8-128 characters: letters, digits, dot, underscore, hyphen")
    return value


def validate_evidence(
    args: argparse.Namespace, value: str, session: str, outcome: str
) -> str:
    value = value.strip()
    if not 8 <= len(value) <= 500 or "\n" in value:
        raise LeaseFailure("evidence must be one line of 8-500 characters")
    if args.no_github_sync:
        if not value.startswith("local-test:"):
            raise LeaseFailure("test-mode evidence must start with local-test:")
        return value
    owner, repo = args.repo.split("/", 1)
    pattern = re.compile(
        rf"https://github\.com/{re.escape(owner)}/{re.escape(repo)}/issues/"
        rf"{args.issue}#issuecomment-(\d+)"
    )
    match = pattern.fullmatch(value)
    if not match:
        raise LeaseFailure(
            "production evidence must be a comment URL on the leased GitHub issue"
        )
    result = run(
        ["gh", "api", f"repos/{args.repo}/issues/comments/{match.group(1)}"]
    )
    comment = json.loads(result.stdout)
    expected_issue_url = f"https://api.github.com/repos/{args.repo}/issues/{args.issue}"
    body = str(comment.get("body", ""))
    marker = f"<!-- rca-issue-evidence:v1 session={session} outcome={outcome} -->"
    required_sections = {
        "outcome",
        "changes",
        "verification",
        "limitations",
        "safety",
    }
    if outcome in {"blocked", "handoff"}:
        required_sections.add("next-action")
    section_content = {section: [] for section in required_sections}
    current_section: str | None = None
    for line in body.splitlines():
        if line.startswith("## "):
            candidate = EVIDENCE_SECTION_BY_HEADING.get(line)
            current_section = candidate if candidate in section_content else None
        elif current_section and line.strip() and not line.strip().startswith("<!--"):
            section_content[current_section].append(line.strip())
    sections_filled = all(section_content[section] for section in required_sections)
    if (
        comment.get("html_url") != value
        or comment.get("issue_url") != expected_issue_url
        or marker not in body
        or not sections_filled
    ):
        raise LeaseFailure("evidence comment identity, marker, or required sections are invalid")
    return value


def ttl_expiry(minutes: float) -> dt.datetime:
    if not (0 < minutes <= 24 * 60):
        raise LeaseFailure("ttl-minutes must be greater than 0 and at most 1440")
    return now_utc() + dt.timedelta(minutes=minutes)


def command_claim(args: argparse.Namespace) -> None:
    actor = github_actor(args)
    session = validate_session(args.session or uuid.uuid4().hex)
    current = current_lease(args.remote, args.issue)
    parent: str | None = None
    created = iso(now_utc())
    takeover = False
    if current:
        parent, existing = current
        if existing["session"] == session and not expired(existing):
            if lease_purpose(existing) != args.purpose:
                raise LeaseFailure(
                    "session already owns this key for a different purpose",
                    3,
                    {"issue": args.issue, "remoteSha": parent, "lease": existing},
                )
            github_reconcile_claim(args, existing, False)
            emit("already-owned", issue=args.issue, remoteSha=parent, lease=existing)
            return
        if not expired(existing):
            raise LeaseFailure(
                "issue has an active session lease",
                3,
                {"issue": args.issue, "remoteSha": parent, "lease": existing},
            )
        if not args.takeover_expired:
            raise LeaseFailure(
                "issue lease expired; inspect durable evidence before takeover",
                4,
                {"issue": args.issue, "remoteSha": parent, "lease": existing},
            )
        takeover = True
    session_current = current_session_lease(args.remote, session)
    if session_current and (current is None or session_current[1]["issue"] != args.issue):
        raise LeaseFailure(
            "session already owns another issue",
            3,
            {
                "session": session,
                "remoteSha": session_current[0],
                "lease": session_current[1],
            },
        )
    github_precheck(args, actor)
    renewed = iso(now_utc())
    metadata = {
        "schemaVersion": SCHEMA,
        "issue": args.issue,
        "session": session,
        "actor": actor,
        "branch": branch_name(),
        "headSha": run(["git", "rev-parse", "HEAD"]).stdout.strip(),
        "createdAt": created,
        "renewedAt": renewed,
        "expiresAt": iso(ttl_expiry(args.ttl_minutes)),
        "purpose": args.purpose,
        "displayLanguage": args.display_language or "ko",
        "readinessOverride": args.allow_unready if args.purpose == "implementation" else False,
    }
    new_sha = create_commit(metadata, parent)
    push_lease(
        args.remote,
        args.issue,
        session,
        new_sha,
        previous_sha=parent,
        previous_session=existing["session"] if current else None,
    )
    try:
        github_reconcile_claim(args, metadata, takeover)
    except LeaseFailure as error:
        try:
            rollback_claim(
                args.remote,
                args.issue,
                session,
                new_sha,
                parent,
                existing["session"] if current else None,
            )
        except LeaseFailure:
            pass
        raise LeaseFailure(
            f"GitHub projection failed after lease claim: {error.message}",
            6,
            {"issue": args.issue, "session": session, "remoteSha": new_sha},
        ) from error
    emit("acquired", issue=args.issue, remoteSha=new_sha, lease=metadata, takeover=takeover)


def require_owned(args: argparse.Namespace, allow_expired: bool = False) -> tuple[str, dict[str, Any]]:
    session = validate_session(args.session)
    current = current_lease(args.remote, args.issue)
    if current is None:
        raise LeaseFailure("issue has no session lease", 5, {"issue": args.issue})
    sha, metadata = current
    if metadata["session"] != session:
        raise LeaseFailure(
            "current lease belongs to another session",
            5,
            {"issue": args.issue, "remoteSha": sha, "lease": metadata},
        )
    if expired(metadata) and not allow_expired:
        raise LeaseFailure(
            "current session lease is expired",
            5,
            {"issue": args.issue, "remoteSha": sha, "lease": metadata},
        )
    return sha, metadata


def command_status(args: argparse.Namespace) -> None:
    current = current_lease(args.remote, args.issue)
    if current is None:
        emit("unclaimed", issue=args.issue, ref=ref_for(args.issue))
        return
    sha, metadata = current
    emit(
        "expired" if expired(metadata) else "active",
        issue=args.issue,
        remoteSha=sha,
        lease=metadata,
    )


def assert_github_owned(args: argparse.Namespace, metadata: dict[str, Any]) -> None:
    if args.no_github_sync:
        return
    if lease_purpose(metadata) == "planning":
        if args.issue == 0:
            return
        state = github_issue_snapshot(args)
        if state["state"] != "OPEN":
            raise LeaseFailure(
                "planning lease source issue is no longer open",
                5,
                {"issueUrl": state["url"]},
            )
        return
    state = github_issue_snapshot(args)
    validate_issue_gate(
        args,
        state,
        metadata["actor"],
        allow_unready=bool(metadata.get("readinessOverride", False)),
    )
    if not has_claim_projection(state, metadata["actor"], metadata["session"]):
        raise LeaseFailure(
            "owned lease is missing its GitHub assignment or claim comment",
            5,
            {"issueUrl": state["url"]},
        )


def command_check(args: argparse.Namespace) -> None:
    sha, metadata = require_owned(args)
    assert_github_owned(args, metadata)
    emit("owned", issue=args.issue, remoteSha=sha, lease=metadata)


def command_renew(args: argparse.Namespace) -> None:
    sha, metadata = require_owned(args)
    assert_github_owned(args, metadata)
    metadata = dict(metadata)
    metadata["renewedAt"] = iso(now_utc())
    metadata["expiresAt"] = iso(ttl_expiry(args.ttl_minutes))
    metadata["branch"] = branch_name()
    metadata["headSha"] = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    new_sha = create_commit(metadata, sha)
    push_lease(
        args.remote,
        args.issue,
        metadata["session"],
        new_sha,
        previous_sha=sha,
        previous_session=metadata["session"],
    )
    emit("renewed", issue=args.issue, remoteSha=new_sha, lease=metadata)


def command_release(args: argparse.Namespace) -> None:
    sha, metadata = require_owned(args, allow_expired=True)
    purpose = lease_purpose(metadata)
    if purpose == "planning":
        if args.evidence or args.outcome:
            raise LeaseFailure(
                "planning release does not accept implementation evidence or outcome"
            )
        delete_lease(args.remote, args.issue, metadata["session"], sha)
        emit(
            "released",
            issue=args.issue,
            purpose=purpose,
            session=metadata["session"],
        )
        return
    if not args.evidence or not args.outcome:
        raise LeaseFailure(
            "implementation release requires --outcome and --evidence"
        )
    args.evidence = validate_evidence(
        args, args.evidence, metadata["session"], args.outcome
    )
    github_release_precheck(args)
    display_language = lease_display_language(metadata, args.display_language)
    delete_lease(args.remote, args.issue, metadata["session"], sha)
    try:
        github_release(
            args,
            args.outcome,
            metadata["session"],
            display_language,
        )
    except LeaseFailure as error:
        raise LeaseFailure(
            f"GitHub projection failed after lease release: {error.message}",
            6,
            {"issue": args.issue, "session": metadata["session"]},
        ) from error
    emit("released", issue=args.issue, outcome=args.outcome, session=metadata["session"])


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "issue",
        type=int,
        help="GitHub issue number; key 0 is reserved for repository-wide planning",
    )
    common.add_argument(
        "--remote", default="origin", help="Git remote that stores the lease ref"
    )
    common.add_argument(
        "--repo", help="GitHub owner/name; inferred from the canonical remote when omitted"
    )
    common.add_argument(
        "--no-github-sync",
        action="store_true",
        help="test only: skip issue readiness, assignment, and comments; --repo is ignored",
    )
    common.add_argument("--actor", help="actor projection; normally inferred from gh")
    common.add_argument(
        "--display-language",
        choices=sorted(DISPLAY_LANGUAGES),
        help="human-facing GitHub lease comment language; new leases default to ko",
    )
    commands = result.add_subparsers(dest="command", required=True)

    claim = commands.add_parser("claim", parents=[common])
    claim.add_argument("--session")
    claim.add_argument("--ttl-minutes", type=float, default=30.0)
    claim.add_argument(
        "--purpose",
        choices=sorted(LEASE_PURPOSES),
        default="implementation",
        help="implementation claims project to GitHub; planning claims serialize tracker writes only",
    )
    claim.add_argument("--takeover-expired", action="store_true")
    claim.add_argument("--allow-shared-assignee", action="store_true")
    claim.add_argument(
        "--allow-unready",
        action="store_true",
        help="explicit user override for a missing ready-for-agent label; blockers still gate",
    )
    claim.set_defaults(handler=command_claim)

    status = commands.add_parser("status", parents=[common])
    status.set_defaults(handler=command_status)

    check = commands.add_parser("check", parents=[common])
    check.add_argument("--session", required=True)
    check.set_defaults(handler=command_check)

    renew = commands.add_parser("renew", parents=[common])
    renew.add_argument("--session", required=True)
    renew.add_argument("--ttl-minutes", type=float, default=30.0)
    renew.set_defaults(handler=command_renew)

    release = commands.add_parser("release", parents=[common])
    release.add_argument("--session", required=True)
    release.add_argument(
        "--evidence",
        help="durable issue comment, commit, PR, artifact, or handoff pointer",
    )
    release.add_argument(
        "--outcome",
        choices=("completed", "handoff", "blocked"),
    )
    release.set_defaults(handler=command_release)
    return result


def main() -> None:
    args = parser().parse_args()
    try:
        ensure_repo()
        if args.issue < 0:
            raise LeaseFailure("lease key must be zero or a positive issue number")
        if args.command == "claim":
            if args.issue == 0 and args.purpose != "planning":
                raise LeaseFailure("key 0 is reserved for repository-wide planning")
            if args.purpose == "planning" and (
                args.allow_unready or args.allow_shared_assignee
            ):
                raise LeaseFailure(
                    "planning claims do not accept implementation readiness or assignee overrides"
                )
        bind_github_repo(args)
        args.handler(args)
    except LeaseFailure as error:
        fail(error)


if __name__ == "__main__":
    main()
