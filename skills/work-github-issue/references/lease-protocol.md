# Session lease protocol

The authoritative lock is an atomic ref pair on the configured Git remote:
`refs/notes/rca-issue-leases/<issue>` and
`refs/notes/rca-agent-sessions/<session>`. The notes namespace keeps lease
traffic out of branch/tag CI and the branch list. Both refs point to one commit
containing `rca.issue-lease.v1` JSON with the issue, session, actor, branch,
source HEAD, creation/renewal time, and expiry.

## Commands

```bash
# Acquire; generates and returns a session id when omitted.
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" claim 42

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
```

Use `--remote <name>`, `--repo owner/name`, and `--ttl-minutes <n>` when the
defaults are not correct. `--no-github-sync --actor <name>` is reserved for
disposable test remotes. That mode ignores `--repo` and validates only the Git
lease lifecycle; it cannot prove issue readiness, assignment, or comments.

An issue already assigned to the same shared account without a lease is
ambiguous. Inspect its comments and branches, then use
`--allow-shared-assignee` only with an explicit handoff or confirmation that no
session is active. An expired valid lease uses `--takeover-expired` instead.

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
