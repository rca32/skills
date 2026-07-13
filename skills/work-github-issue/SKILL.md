---
name: work-github-issue
description: Coordinate collision-safe GitHub issue implementation and planning mutations through readiness, remote session leases, review, evidence, and resolution. Use before starting, resuming, publishing planning state, handing off, or finishing issue-backed work when agents may share one account.
---

# Work GitHub Issue

Treat an issue as a **leased unit of work**. The GitHub assignee shows the human
owner; the remote lease ref elects exactly one active agent session even when
every session uses the same account.

Read the repository's configured issue-tracker document before the first
tracker write. If none exists, use
[references/tracker-contract.md](references/tracker-contract.md). Read
[references/lifecycle.md](references/lifecycle.md) only when the issue is not
already `ready-for-agent`, belongs to a Wayfinder map, or must be split,
triaged, handed off, or resolved into a parent.

Use `documenting-work` whenever a workflow proposes a durable file, report, or
artifact outside the tracker. The issue comment remains authoritative for agent
briefs, implementation evidence, and issue-backed handoffs unless the consuming
repository explicitly assigns that authority elsewhere.

## 0. Preflight and serialize planning writes

Before the first real lease in a repository, verify that Git is available, the
configured remote resolves to the intended canonical GitHub `owner/name`, `gh`
is authenticated to the expected account, the tracker contract and state-label
mapping are known, and the account may push atomic refs to the remote. A claim
fails closed when these prerequisites are absent.

Read-only triage, drafting, and graph design need no lease. Before `triage`,
`to-spec`, or `to-tickets` performs authorized tracker writes, acquire a short
planning lease through this skill. Use the source or parent issue as the key; use
key `0` only when creating a repository-level planning item with no source issue:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  claim <issue-or-0> --purpose planning --ttl-minutes 10
```

Capture the returned session, run `check <key> --session <session>` before each
mutation batch, and renew around long publication. The planning lease uses the
same atomic issue/session refs as implementation, so planning and implementation
cannot race on one key. It does not assign or comment on the issue.

After every external write has an operation-specific readback and no result is
unknown, release without an implementation outcome or evidence:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  release <issue-or-0> --session <session>
```

Do not release while a write result is unknown. Preserve the session/key and
reconcile tracker state first; an expired planning lease may be taken over only
after inspecting markers and partial tracker state.

## 1. Establish readiness

Fetch the full issue body, comments, labels, assignees, state, parent, and open
blocking dependencies. Resolve bare issue numbers as the tracker document
requires.

- Route raw incoming reports through `triage`.
- Route a settled multi-session plan through `to-spec` and `to-tickets`.
- Route a huge foggy effort through `wayfinder`.
- Apply the configured tracker document's readiness, frontier, dependency, and
  override contract before selecting implementation work.

Completion criterion: the issue snapshot satisfies the tracker contract and its
requested outcome plus acceptance criteria are present in the body or an
identified brief/spec.

## 2. Acquire the implementation lease

Run the claim before implementation exploration or any implementation-related
local/external write. Read-only investigation required to triage, verify,
de-duplicate, or determine blockers remains part of readiness and precedes the
lease:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  claim <issue> --purpose implementation --ttl-minutes 30
```

Capture the returned `session` value in the working context. The command
atomically creates `refs/notes/rca-issue-leases/<issue>` and then assigns/comments
on the issue. If another active session owns the lease, report its public
metadata and choose another frontier ticket. If the lease expired, inspect the
issue, branch, and latest comment before using `--takeover-expired`.
Apply the tracker document's legacy ambiguous-claim rule before using
`--allow-shared-assignee`.

Completion criterion: claim returns `status=acquired|already-owned`, the issue
is assigned, and the returned lease is unexpired and owned by this session.

## 3. Execute one ticket

Create or select a branch that isolates this ticket. Follow the repository owner
boundaries and any skill the user explicitly invoked. At the agreed highest
test seam, make behavior changes test-first where practical. Run typechecking
and focused tests regularly, then the full relevant suite once. Keep the ticket
a tracer bullet: deliver its end-to-end acceptance criteria without absorbing
adjacent tickets.

Renew before the TTL expires and before a long unattended operation:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  renew <issue> --session <session> --ttl-minutes 30
```

Before commit, push, issue edits, release actions, or any other consequential
external write, assert ownership:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  check <issue> --session <session>
```

If check fails, stop writes, preserve local evidence, and report the current
lease owner. Resume only after reacquiring or receiving an explicit handoff.

Completion criterion: each acceptance criterion maps to a changed behavior,
test, or named evidence artifact; the focused and final suites are green; and
`check` returns `status=owned` for this session.

## 4. Review and publish evidence

Review the pre-work fixed point on both Standards and Spec, using `code-review`
when available.
Address actionable findings, run the final relevant suite, and commit only the
ticket's files. Publish only when the user or active workflow authorizes it.
The real-issue claim authorizes its required tracker projection and evidence
writes; if tracker writes are prohibited, remain read-only and do not claim.

Post the configured tracker document's structured evidence comment.
Link any repository document or artifact selected by `documenting-work`; do not
copy its full body into the evidence comment.

Completion criterion: the issue comment names the exact local or published
commit, commands and results, evidence paths, limitations, and safety outcome;
the reviewed diff contains only the ticket's scope. Without publication
authorization, proceed to the tracker-defined handoff outcome.

## 5. Resolve or hand off

Apply `Session work outcomes` from the configured tracker document. Pass its
durable evidence pointer and matching `completed|blocked|handoff` outcome to the
lease release:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  release <issue> --session <session> --outcome completed \
  --evidence <issue-evidence-comment-url>
```

Completion criterion: `status <issue>` returns `status=unclaimed` and the issue,
parent map, publication state, and evidence match the tracker-defined outcome.

## Lease guardrails

- Use the remote ref as session authority; assignee and comments are projections.
- Use one ref namespace for both `planning` and `implementation`; purpose changes
  require release and reacquisition, never an in-place interpretation change.
- Treat the session id as an ownership token, not a secret or user identity.
- Renew by compare-and-swap; release only the exact SHA this session observed.
- Take over only an expired lease after inspecting durable work evidence.
- Keep the atomic issue ref and session ref pair as the enforced one-issue per
  session and one-session per issue invariant.
- Use `--no-github-sync` only for isolated tests against a disposable remote.

For command fields, exit codes, stale recovery, and failure behavior, read
[references/lease-protocol.md](references/lease-protocol.md) when a lease
command fails or recovery is required.

Prefix commands with any proxy required by the consuming repository.
