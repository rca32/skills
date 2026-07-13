#!/usr/bin/env python3
"""Atomic Git-ref leases for same-account GitHub issue workers."""

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
STATE_ROLES = {
    "needs-triage",
    "needs-info",
    "ready-for-agent",
    "ready-for-human",
    "wontfix",
}


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
    fields = "state,assignees,url,labels,blockedBy,comments,parent"
    result = run(
        gh_args(args, "issue", "view", str(args.issue), "--json", fields)
    )
    return json.loads(result.stdout)


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
    if "ready-for-agent" not in labels and not allow_unready:
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


def github_release(args: argparse.Namespace, outcome: str, session: str) -> None:
    if args.no_github_sync:
        return
    if outcome != "completed":
        run(gh_args(args, "issue", "edit", str(args.issue), "--remove-assignee", "@me"))
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
        state_roles = labels & STATE_ROLES
        if len(state_roles) != 1:
            raise LeaseFailure(
                "blocked release requires exactly one triage state role",
                2,
                {"stateRoles": sorted(state_roles), "issueUrl": value["url"]},
            )
        if not open_blockers and state_roles.isdisjoint({"needs-info", "ready-for-human"}):
            raise LeaseFailure(
                "blocked release requires an open blocker, needs-info, or ready-for-human state",
                2,
                {"labels": sorted(labels), "issueUrl": value["url"]},
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
        "## Outcome",
        "## Changes",
        "## Verification",
        "## Limitations",
        "## Safety",
    }
    if outcome in {"blocked", "handoff"}:
        required_sections.add("## Next action")
    section_content = {section: [] for section in required_sections}
    current_section: str | None = None
    for line in body.splitlines():
        if line.startswith("## "):
            current_section = line if line in section_content else None
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
        "readinessOverride": args.allow_unready,
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
    args.evidence = validate_evidence(
        args, args.evidence, metadata["session"], args.outcome
    )
    github_release_precheck(args)
    delete_lease(args.remote, args.issue, metadata["session"], sha)
    try:
        github_release(args, args.outcome, metadata["session"])
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
    common.add_argument("issue", type=int, help="positive GitHub issue number")
    common.add_argument(
        "--remote", default="origin", help="Git remote that stores the lease ref"
    )
    common.add_argument("--repo", help="GitHub owner/name; inferred by gh when omitted")
    common.add_argument(
        "--no-github-sync",
        action="store_true",
        help="test only: skip issue readiness, assignment, and comments; --repo is ignored",
    )
    common.add_argument("--actor", help="actor projection; normally inferred from gh")
    commands = result.add_subparsers(dest="command", required=True)

    claim = commands.add_parser("claim", parents=[common])
    claim.add_argument("--session")
    claim.add_argument("--ttl-minutes", type=float, default=30.0)
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
        required=True,
        help="durable issue comment, commit, PR, artifact, or handoff pointer",
    )
    release.add_argument(
        "--outcome",
        choices=("completed", "handoff", "blocked"),
        required=True,
    )
    release.set_defaults(handler=command_release)
    return result


def main() -> None:
    args = parser().parse_args()
    try:
        ensure_repo()
        if args.issue <= 0:
            raise LeaseFailure("issue must be a positive integer")
        bind_github_repo(args)
        args.handler(args)
    except LeaseFailure as error:
        fail(error)


if __name__ == "__main__":
    main()
