---
name: work-github-issue
description: Coordinate collision-safe GitHub issue implementation and planning mutations through readiness, remote session leases, review, evidence, and resolution. Use before starting, resuming, publishing planning state, handing off, or finishing issue-backed work when agents may share one account. Also use to inspect or initialize a consuming repository's execution, publication, and bundled tracker-label setup; repository initialization requires explicit policy and remote-label mutation authority.
---

# Work GitHub Issue

Treat an issue as a **leased unit of work**. The GitHub assignee shows the human
owner; the remote lease ref elects exactly one active agent session even when
every session uses the same account.

Read the repository's configured issue-tracker document before the first
tracker write. If none exists, use
[references/tracker-contract.md](references/tracker-contract.md). Read
[references/lifecycle.md](references/lifecycle.md) only when the issue is not
already in the configured `ready-for-agent` role, belongs to a Wayfinder map, or must be split,
prepared, handed off, or resolved into a parent.

Read [references/workspace-cleanup.md](references/workspace-cleanup.md) only
when an implementation session used a ticket branch or worktree and is ready to
record its final outcome. It defines the bundled cleanup default and the safe
removal checks.

Use `documenting-work` whenever a workflow proposes a durable file, report, or
artifact outside the tracker. The issue comment remains authoritative for agent
briefs, implementation evidence, and issue-backed handoffs unless the consuming
repository explicitly assigns that authority elsewhere.

Minimize human intervention within resolved authority. Continue without asking
for confirmation when repository evidence, applicable instructions, and an
existing standing authorization determine the next safe action. Escalate only
for genuinely missing requirements or authority, unavailable access, a safety
decision outside the ticket, or an external write that cannot be reconciled.

When a consuming repository lacks an execution and publication contract, remain
read-only for publication-dependent work. If the user asks to inspect or
initialize the bundled repository setup, read the
[repository-initialization workflow](references/repository-contract.md) and the exact
[managed contract template](references/consumer-agents-contract.md). Treat its
`AGENTS.md` policy and GitHub tracker labels as one user-facing initialization,
while using their separate deterministic installers and readbacks. Never insert
standing merge authority or create repository-wide labels without explicit
authority for the corresponding mutation class; complete initialization requires
both.

## 0. Preflight and serialize planning writes

Before the first real lease in a repository, verify that Git is available, the
configured remote resolves to the intended canonical GitHub `owner/name`, `gh`
is authenticated to the expected account, the tracker contract and state-label
mapping are known and recognized by the lease helper or repository adapter, and
the account may push atomic refs to the remote. Under the bundled fallback,
publish Korean state labels and accept the legacy English aliases only for
existing issues; never attach both aliases for one role. A claim fails closed
when these prerequisites are absent.

When the applicable repository contract prohibits GitHub Actions, verify before
claim that Actions are disabled for the canonical repository and that no branch
rule requires an Actions-hosted status check, external approving review, or
restriction the lease-owning agent cannot satisfy autonomously. If any state
conflicts or cannot be read reliably, do not claim publication-dependent work:
pushing a branch or opening a pull request could trigger a prohibited service or
lead to an unavoidable human wait.

Resolve the human-facing tracker language before claim. The lease helper
defaults new claim/release projection comments to Korean and records that
choice in the lease; pass `--display-language en` when the selected repository
contract requires English. Keep protocol markers unchanged in either language.

Read-only issue preparation, drafting, and graph design need no lease. Before `prepare-issue`,
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

- Route raw incoming reports through `prepare-issue`.
- Route a settled multi-session plan through `to-spec` and `to-tickets`.
- Route a huge foggy effort through `wayfinder` when it is installed; otherwise
  keep the issue non-ready and report the missing shared map, named ticket,
  frontier, or fog decision required before implementation.
- Apply the configured tracker document's readiness, frontier, dependency, and
  override contract before selecting implementation work.

Before an implementation claim, resolve the execution and publication contract
from explicit user instructions, then applicable repository instructions and one
unambiguous configured publish flow. Record:

- the ticket base and pre-work fixed point;
- when the current worktree is eligible and where an isolated worktree may be
  created otherwise;
- the authorized delivery surface: local commit, pushed branch, pull request,
  or merge;
- the pull-request target and, when integration or direct merge is in scope, the
  integration target;
- merge authority and strategy, required checks, and the repository-defined
  completion point when publication is in scope;
- which branch and worktree already existed, which ones this session may create,
  and any repository or user cleanup override.

When no higher authority defines cleanup, use the bundled default: after a
`completed` implementation, remove an eligible linked worktree created by this
session and delete its eligible session-created local ticket branch. Retain
pre-existing or shared workspaces, all `blocked|handoff` workspaces, and remote
branches. This default resolves local cleanup policy; deleting a remote branch
or a pre-existing local artifact still requires explicit repository or user
authority.

Do not select a merge target merely because it is the remote default branch or
because a nearby pull request used it. A local-only request may mark publication
fields `not authorized` only when the user explicitly scopes the outcome to local
work; the configured tracker contract still owns its release outcome. If a field
required for the requested outcome is missing or two authorities conflict,
remain read-only and report the exact decision required instead of claiming.
Do not ask the user to restate a field already resolved by a valid applicable
repository contract.

Completion criterion: the issue snapshot satisfies the tracker contract and its
requested outcome plus acceptance criteria are present in the body or an
identified brief/spec; the execution contract is resolved; and every publication
field required by the requested outcome is either resolved or explicitly out of
scope. Workspace provenance and the applicable cleanup policy are also recorded.

## 2. Acquire the implementation lease

Run the claim before implementation exploration or any implementation-related
local/external write. Read-only investigation required to prepare, verify,
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

After the claim, create or select a ticket branch from the resolved fixed point.
Before creating either artifact, capture `git worktree list --porcelain`, the
relevant local and remote refs, and the intended canonical path. Mark each
selected branch and worktree as pre-existing or created by this session; never
infer ownership from its name later.

Use the current worktree only when all of these are true:

- it is already on the ticket branch; creating or selecting a different ticket
  branch uses a linked worktree instead of changing this checkout;
- every staged, unstaged, and untracked change is verified as part of this ticket;
- no other active session or user task shares the directory;
- the work needs no revision switching or destructive experiment.

Otherwise create a separate worktree without cleaning, stashing, resetting, or
switching the user's active checkout. Inspect `git worktree list` before choosing
the branch. If the intended ticket branch is already checked out in an ineligible
worktree, do not force it into another worktree: reuse it only after it becomes
eligible and exclusive, or create an authorized distinct continuation branch at
its durable committed HEAD and record the relationship. If relevant uncommitted
state remains there or a continuation branch is not authorized, stop before
editing, preserve both workspaces, and apply the configured tracker contract's
non-complete outcome.

A separate worktree uses the same issue lease and a branch that isolates the
ticket. From the selected execution workspace, renew the lease so its branch and
source HEAD projection describe the actual ticket workspace, then verify
ownership before editing.

Follow the repository owner boundaries and any skill the user explicitly
invoked. If the ticket still requires a module-interface or architectural-seam
decision, use `codebase-design` before the first implementation edit. Resume
only when the recommendation is resolved under that skill's acceptance
contract. If it exceeds or changes approved behavior,
architecture, ticket boundaries, dependencies, or another approval-gated
contract, stop and return to the planning workflow rather than widening the
ticket. At the agreed highest test seam, make behavior changes test-first where
practical. Run typechecking and focused tests regularly, then the full relevant
suite once. Keep the ticket a tracer bullet: deliver its end-to-end acceptance
criteria without absorbing adjacent tickets.

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

Completion criterion: the execution workspace is isolated at the recorded fixed
point; its branch and HEAD match the current lease projection; each acceptance
criterion maps to a changed behavior, test, or named evidence artifact; the
focused and final suites are green; and `check` returns `status=owned` for this
session.

## 4. Review and publish evidence

Create or amend the final ticket commit before final verification and review,
then require a clean execution workspace. Renew from that workspace and check
ownership so the lease projection names the exact branch and ticket-head OID.
Record the live integration-base OID used to build that candidate and require
the candidate to incorporate that base. Run the final local verification for
that `(integration-base OID, ticket-head OID)` pair and record it as the
candidate reviewed-and-tested pair.

Review the pre-work fixed point through that candidate pair independently on both
Standards and Spec, using `code-review` when available. Do not expose one
reviewer's conclusions to the other before both reports are complete. Address
every blocker/high finding and every medium finding that affects safety,
ownership, invocation, or predictable completion. Any finding-driven file or
commit change creates a new candidate pair and invalidates local verification
and both pair-bound reviews, regardless of which axis found it. A changed live
integration base has the same effect: incorporate the new base, create the new
ticket-head OID, and repeat every gate. Continue until one unchanged pair passes.

Push, open a pull request, or merge only to the extent authorized by the user or
active repository workflow, and include only the ticket's files. An
implementation claim authorizes required tracker projection and evidence writes;
it does not by itself authorize code publication. A pushed branch does not
authorize a pull request, and pull-request creation does not authorize merge.

Apply the resolved publication contract rather than inventing a target or merge
method. Before each consequential write, recheck the lease and the target. Read
back operation-specific state:

- after push, the remote branch points to the intended commit;
- after pull-request create or update, its head, base, state, and required checks
  match the contract;
- after merge, the configured integration target contains the published change
  and required checks remain satisfied.

When the applicable repository contract grants standing autonomous merge
authority, do not pause for redundant human approval after local tests and both
independent reviews satisfy its gates. Before merge, inspect the pull request and
every included commit message plus the selected merge message for a closing
keyword targeting the leased issue. Remove an authorized pull-request-body
keyword and read back that edit. Rewrite a commit or merge message only within
explicit publication authority and rerun invalidated verification and reviews;
stop if any source could still close the issue before cleanup and final evidence.
Re-read the live pull request head OID, live remote ticket ref, base, state,
review result, and integration ref. Require the PR head and remote ticket ref to
equal the reviewed ticket-head OID and the live integration ref to equal the
reviewed integration-base OID. Any mismatch invalidates the pair; incorporate
the new base or head and repeat local verification plus both reviews. Perform
the authorized merge only when a provider-side rule or operation atomically
rejects either a stale expected head or a stale expected integration base. On
GitHub, pass the merge API's `sha` head precondition and require a branch rule or
other recorded provider mechanism that rejects an out-of-date base without
GitHub Actions. An unguarded merge, or a provider that cannot enforce both
preconditions, is not authorized. Treat a mismatch as a stale-pair stop, not a
retry with newly observed OIDs. Then verify that the pull request reports merged
from the reviewed ticket-head OID and the live integration ref
contains the reported integration commit. Record both OIDs; squash and rebase
merge need not preserve the ticket head as an ancestor. A contract that
prohibits GitHub Actions makes hosted Actions and required Actions checks
unavailable rather than optional: run its local verification and stop on
conflicting branch rules instead of enabling, triggering, rerunning, or bypassing
Actions.

An unknown publication result remains unresolved. Keep the lease, inspect the
remote branch, pull request, or integration target, and classify the operation
as present exactly once or absent before retrying. If tracker writes are
prohibited, remain read-only and do not claim.
If merge unexpectedly closes the leased issue before cleanup and final evidence,
reconcile it back to open while the implementation lease is still owned and
verify that state before continuing. Treat an unknown reopen result like any
other unresolved tracker mutation.

Once the acceptance criteria and resolved repository completion point establish
that implementation is publishable, including every publication readback
required by that outcome, verify that the final commit is recoverable from a
live remote ref or the integration ref. Then perform the applicable cleanup from
a retained control worktree while the implementation lease is still owned. Follow
[references/workspace-cleanup.md](references/workspace-cleanup.md), recheck the
lease immediately before removal, and read back each worktree or ref deletion.
Do not apply the bundled deletion default to `blocked` or `handoff` outcomes.
When a cleanup precondition fails, preserve the exact path or ref and record the
failed condition plus next safe action; never force removal.

Post the configured tracker document's structured evidence comment only after
the cleanup result or safe preservation disposition is settled. Include both
independent review results, the ticket-head and integration OIDs, the live
ticket-head recovery ref, and cleanup disposition. Use the contract's
human-facing language. Under the bundled fallback, use the Korean evidence
headings while preserving the protocol marker; legacy English headings remain
read-compatible.
Link any repository document or artifact selected by `documenting-work`; do not
copy its full body into the evidence comment.

Read back every implementation tracker write as well. Reconcile an evidence
comment by the exact `rca-issue-evidence:v1` session/outcome marker: reuse exactly
one match, create only when no match exists, and stop on duplicates or an unknown
search result. Verify labels, parent state, and closure from their exact tracker
fields. Never repeat an ambiguous tracker mutation before this readback.

Completion criterion: the reviewed diff contains only the ticket's scope; every
authorized publication and tracker step has an exact readback; and the issue
comment names the fixed point, branch, exact local or published commit, pull
request or merge state when applicable, commands and results, evidence paths,
cleanup result or preserved workspace, limitations, and safety outcome. When the
requested completion point requires publication but that publication is not
authorized, proceed to the configured tracker contract's non-complete outcome;
an explicitly resolved local completion point remains eligible for `completed`.

## 5. Resolve or hand off

Apply `Session work outcomes` from the configured tracker document. Pass its
durable evidence pointer and matching `completed|blocked|handoff` outcome to the
lease release:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/work-github-issue/scripts/issue_lease.py" \
  release <issue> --session <session> --outcome completed \
  --evidence <issue-evidence-comment-url>
```

Use `completed` only when every acceptance criterion holds and the resolved
repository completion point has been reached. For every non-complete session,
apply the configured tracker contract's state and `blocked|handoff` mapping; do
not substitute the fallback vocabulary when the repository defines another
outcome. When the bundled fallback contract is active, apply its human-wait and
continuation rules directly. Before releasing `blocked` in `needs-info` or
`ready-for-human`, verify the authoritative issue body or latest comment tells
the person why intervention is required, the exact action, where to respond,
the observable completion condition, durable evidence reference, and the next
state plus transition owner. For `ready-for-human`, also include one copy-ready
suggested comment tailored to that response location. Name the exact target,
then follow the selected tracker contract's exact suggested-comment shape with
distinct concrete results and editable rationale and evidence-reference slots,
without pretending the action already happened. The person
edits and posts it only after performing the requested review, approval, or
manual action; the suggested comment never substitutes for that action.
The person records the requested answer or action evidence but does not edit
the state directly: authorized `prepare-issue` owns revalidation and open-state
transitions, while this skill owns evidence-backed completion and closure. Do
not release with a generic request to review or provide information.

Cleanup is a separate, read-backed operation completed before the final evidence
and lease release; the release command itself never deletes workspaces. After
release readback, do not start an automatic cleanup pass because a successor may
already be acquiring the issue. Report every artifact preserved by policy or a
failed safety check.

Completion criterion: `status <issue>` returns `status=unclaimed` and the issue,
parent map, repository completion point, publication state, and evidence match
the tracker-defined outcome; no eligible session-created workspace remains, and
every intentionally preserved path or ref and its next safe action are reported.

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
