# Session lease protocol

The `rca.*` schema, marker, and ref prefixes below are stable version-1 wire
identifiers retained for compatibility with existing leases. They do not bind
the skill to an RCA project. Do not rename them without a migration that checks
both old and new namespaces; otherwise sessions using different installed
versions could both believe they own the same issue.

The authoritative lock is an atomic ref pair on the configured Git remote:
`refs/notes/rca-issue-leases/<issue>` and
`refs/notes/rca-agent-sessions/<session>`. The notes namespace keeps lease
traffic out of branch/tag CI and the branch list. Both refs point to one commit
containing `rca.issue-lease.v1` JSON with the issue, session, actor, branch,
source HEAD, creation/renewal time, expiry, purpose, and optional display
language. Readers treat a missing display language as the legacy English
projection behavior.

## Commands

```bash
# Acquire; generates and returns a session id when omitted.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" claim 42

# Serialize authorized planning writes without assignment/comment projection.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  claim 42 --purpose planning

# Use key 0 only for a repository-level planning item with no source issue.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  claim 0 --purpose planning

# Inspect without mutating.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" status 42

# Assert current ownership before consequential writes.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" check 42 --session <id>

# Extend from the exact current lease tip.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" renew 42 --session <id>

# Acquire an expired lease after inspecting durable evidence.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" claim 42 \
  --takeover-expired

# Delete only the observed lease tip and project the outcome to GitHub.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" release 42 \
  --session <id> --outcome handoff --evidence <issue-comment-url>

# A fully reconciled planning lease releases without implementation evidence.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  release 42 --session <id>
```

Use `--remote <name>`, `--repo owner/name`, and `--ttl-minutes <n>` when the
defaults are not correct. New leases use Korean GitHub projection comments by
default; pass `--display-language en` at claim when repository instructions
require English. The selected language is stored in the lease and reused for
release; legacy leases without this field retain English compatibility.
`--no-github-sync --actor <name>` is reserved for
disposable test remotes. That mode ignores `--repo` and validates only the Git
lease lifecycle; it cannot prove issue readiness, assignment, or comments.

An issue already assigned to the same shared account without a lease is
ambiguous. Inspect its comments and branches, then use
`--allow-shared-assignee` only with an explicit handoff or confirmation that no
session is active. An expired valid lease uses `--takeover-expired` instead.

Legacy version-1 lease records without a `purpose` field are interpreted as
`implementation`. A session cannot change an active lease's purpose in place.
Planning claims bypass implementation readiness and assignee projection, but
still require an open source issue when the key is nonzero.

## Exit codes

| Code | Meaning | Response |
| --- | --- | --- |
| `0` | Operation completed | Continue using returned metadata |
| `2` | Invalid input, repository, issue state, or lease record | Repair the stated contract |
| `3` | Another session won or owns the lease | Stop writes and select/handoff |
| `4` | Lease is expired and requires inspected takeover | Inspect, then claim with takeover |
| `5` | Caller does not own the current lease | Stop writes; never release or renew it |
| `6` | GitHub projection failed after lease mutation | Inspect ref and issue; reconcile explicitly |

## Recovery

- A failed create/renew push means another compare-and-swap won. Re-read status.
- A missing ref means no session owns the issue, regardless of stale comments.
- A mismatched or missing half of the issue/session ref pair is invalid and
  requires reconciliation before work.
- An expired ref remains evidence until a successful takeover or owner release.
- Claim, renew, takeover, and release update both refs with one atomic push.
  Exact `--force-with-lease=<ref>:<observed-sha>` expectations prevent an older
  session from replacing or deleting a newer lease.
- GitHub assignment/comments improve visibility but never override the ref.
