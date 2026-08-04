---
name: work-github-issue
description: Coordinate collision-safe GitHub issue implementation and planning mutations through readiness, remote session leases, review, evidence, and resolution. Use before starting, resuming, publishing planning state, handing off, or finishing issue-backed work when agents may share one account, and when a persistent goal selects one or more issues for fresh workers. Also use to inspect or initialize a consuming repository's bundled tracker labels, or when explicitly asked to check or install its personal Luna worker profile; setup mutations require explicit authority. Do not use it to install repository publication authority.
---

# Work GitHub Issue

Treat an issue as a **leased unit of work**. The GitHub assignee shows the human
owner; the remote lease ref elects exactly one active agent session even when
every session uses the same account.

Read the configured issue-tracker document before the first tracker write; if
none exists, use [references/tracker-contract.md](references/tracker-contract.md).
Read [references/lifecycle.md](references/lifecycle.md) only when the issue is not
already in the configured `ready-for-agent` role, belongs to a Wayfinder map, or must be split,
prepared, handed off, resolved into a parent, or the integration target advances
from the pre-work fixed point before or after review.

When explicitly asked to check or install the personal `luna_worker`, follow [references/luna-worker-setup.md](references/luna-worker-setup.md); never run this user-level mutation as an implicit issue preflight.

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

Resolve execution and publication authority from the consuming repository and
the user's current request. If an operation lacks that authority, remain
read-only for that operation and report the exact missing decision; never install
standing publication authority into repository instructions. If the user asks
to inspect or initialize the bundled GitHub tracker labels, read the
[tracker-label setup workflow](references/tracker-label-setup.md). Label setup is
optional and requires explicit repository-wide label mutation authority.

## Goal and implementation context boundary

When a persistent goal-owning thread selects any issue, keep that thread as a
lightweight **coordinator**. It may read tracker state, select the next ready
frontier, create a bounded worker brief, and collect the outcome. It must
not claim an implementation lease on behalf of a worker, edit the ticket
workspace, run implementation verification, or retain raw command and test
logs.

Run each issue in one context-isolated implementation worker without inherited conversation history (for example, Codex `fork_turns: "none"`).
When `luna_worker` is discovered, select it for bounded analysis, validation, or
small implementation work matching its description. Otherwise use another
context-isolated worker and disclose why; never weaken this section's boundaries.
The brief contains only the canonical repository, issue identifier, readiness
and dependency evidence, fixed point, acceptance/spec authority, execution and
publication constraints, and any known dirty-worktree exclusions. The worker
rereads the repository instructions and this skill, then owns readiness
revalidation, lease claim, implementation, review, publication, cleanup,
evidence, and release end to end.

A session invoked directly and dedicated to one named issue may itself be the
implementation worker only when it is not also acting as a goal coordinator and
does not carry another issue's implementation transcript. It still owns exactly
one issue and the complete lease lifecycle below.

Do not reuse an implementation worker for another issue, use a review or design
agent as the worker, or hand a lease between parent and child sessions. After
release, return only a bounded outcome containing the issue state, ticket and
integration OIDs, PR/evidence pointers, verification and review summaries,
preserved artifacts, and next blocker or frontier signal. The coordinator then
starts a new worker for the next issue. If no context-isolated worker mechanism
is available, the coordinator must not implement the issue. Return the bounded
brief as a handoff, stop before claim or mutation, and require a separately
started implementation session to resume that one issue.

Completion criterion: the coordinator carries only goal-level decisions and
bounded outcomes; every implementation worker owns exactly one issue and one
lease lifecycle, and no next issue inherits the previous issue's transcript or
review contexts.

## 0. Preflight and serialize planning writes

Before the first real lease in a repository, verify that Git is available, the
configured remote resolves to the intended canonical GitHub `owner/name`, `gh`
is authenticated to the expected account, the tracker contract and state-label
mapping are known and recognized by the lease helper or repository adapter, and
the account may push atomic refs to the remote. Under the bundled fallback,
prefer existing Korean state labels and accept legacy English aliases on
existing issues. When custom labels are unavailable, use the fallback issue-body
state marker. A claim fails closed only when the tracker role is missing or
conflicting, not merely because a label is absent.

Before claim, inspect required checks, reviews, and branch restrictions that
apply to the publication target. Treat existing GitHub Actions and other hosted
checks as repository gates: observe their results, but do not create, edit,
enable, disable, or rerun workflows unless separately authorized. A gate the
lease owner cannot satisfy does not authorize a bypass; record the expected
human or external action in the resolved publication contract.

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

Do not release while a write result is unknown. Reconcile tracker state with at
most three complete reads over no more than 60 seconds. If the provider still
cannot classify the write, preserve the recovery key and partial state, stop
writes, and stop renewing indefinitely; let the lease expire so a successor can
inspect and take over rather than blocking the planning key forever.

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

Before an implementation claim, resolve only the execution contract needed to
edit safely. Record:

- the ticket base and pre-work fixed point;
- when the current worktree is eligible and where an isolated worktree may be
  created otherwise;
- local implementation authority and whether a local commit is allowed;
- which branch and worktree already existed, which ones this session may create,
  and any repository or user cleanup override.

When no higher authority defines cleanup, use the bundled default: after a
`completed` implementation, remove an eligible linked worktree created by this
session and delete its eligible session-created local ticket branch. Retain
pre-existing or shared workspaces, all `blocked|handoff` workspaces, and remote
branches. This default resolves local cleanup policy; deleting a remote branch
or a pre-existing local artifact still requires explicit repository or user
authority.

Resolve publication progressively. Before push, resolve the remote ticket branch
and push authority. Before opening a pull request, resolve its target; when no
instruction conflicts and exactly one remote default branch exists, use it as
the PR target. Before merge, resolve integration target, merge authority and
method, required checks, completion point, and cleanup. A default branch never
grants merge or remote-deletion authority. Missing later publication fields do
not block an authorized local implementation; stop only before the operation
that needs the missing field and report the exact decision required.

Completion criterion: the issue snapshot satisfies the tracker contract and its
requested outcome plus acceptance criteria are present in the body or an
identified brief/spec and the execution contract is resolved. Workspace
provenance is recorded; publication and cleanup fields may remain deferred until
their first consequential operation.

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
metadata and return a bounded non-claim outcome; do not select or claim another
issue in this worker. A goal coordinator may then select another frontier issue
and start a fresh worker. If the lease expired, inspect the issue, branch, and
latest comment before using `--takeover-expired`.
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
practical. Keep a verification ledger keyed to the candidate OID or worktree
fingerprint: command, covered behavior, result, and reusable build artifact. A
clean committed candidate uses its OID. A WIP fingerprint binds `HEAD`, the
fixed review base, all three tracked-diff layers required by `code-review`, and
each in-scope untracked path's type, mode, and payload or symlink target. It is
valid only inside the current worker while every component remains unchanged.
Never carry WIP evidence across a worker, restart, or candidate change;
candidate-to-candidate carry-forward requires clean committed OIDs. Recompute
the local fingerprint before reusing same-candidate ledger evidence.
Run typechecking and focused tests while developing, then each repository-required
full relevant suite at most once for the final behavior-affecting candidate unless
repository policy explicitly requires another run. Batch deterministic checks and reuse safe
compiled artifacts. For long commands, prefer one bounded execution and the
runtime's longest practical wait interval over repeated short model-visible
polls. Keep the ticket a tracer bullet: deliver its end-to-end acceptance
criteria without absorbing adjacent tickets.

When the user explicitly invokes `quality-gauntlet` and the authorized ticket
or request supplies an inspectable comparative bar, run it as an inner loop
after the behavior and inspection seam are resolved and before final review.
Keep its improvement cells ephemeral rather than turning them into tracker
tickets. The comparative bar cannot widen acceptance criteria or replace final
tests and `code-review`.

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
criterion maps to a changed behavior, test, or named evidence artifact; every
required gate has green evidence valid for the final candidate; and `check`
returns `status=owned` for this session.

## 4. Review and publish evidence

Create or amend the final ticket commit before final verification and review,
then require a clean execution workspace. Renew from that workspace and check
ownership so the lease projection names the exact branch and ticket-head OID.
Record the live integration-base OID used for final integration checks. Run the
final local verification for the behavior-affecting ticket-head OID against that
base and record the reviewed-and-tested candidate. If that base differs from the
pre-work fixed point, first follow the integration-context branch in
[references/lifecycle.md](references/lifecycle.md).

Review the pre-work fixed point through that candidate on separate Standards and
Spec axes using the required catalog companion `code-review`; pass both the
immutable review-base OID and current integration-base OID. If that skill is
unavailable, stop before publication and report the missing required package;
do not substitute an incomplete review or mark the issue completed. Route through
the selected tracker contract and section 5: set `blocked|handoff`, preserve the
workspace, post and read back structured evidence plus its handoff pointer, then
release the lease only through the non-complete outcome protocol.
Address every blocker/high finding and every medium finding that affects safety,
ownership, invocation, or predictable completion. Any finding-driven file or
commit change creates a new candidate. Compare that change with the verification
ledger and invalidate only the commands, integration assumptions, and review
axes whose evidence it could affect. Rerun the full relevant suite only when the
change crosses its covered behavior or the repository explicitly makes every
candidate rerun mandatory; documentation, evidence, or metadata-only corrections
use their matching validators unless they bind executable bytes or runtime
behavior. Apply `code-review`'s re-review contract: use fresh candidate-scoped
reviewers when isolation is available; otherwise inspect each affected axis anew
under its disclosed separated single-context fallback. Do not describe the
fallback as a fresh-reviewer result. Continue until one unchanged ticket head
passes every affected gate.

When evidence is carried forward after a non-behavioral candidate change, the
final ledger and handoff must name the tested prior candidate, the final
candidate, the unaffected-scope rationale, and the targeted validator run on the
final candidate. Never state that a carried-forward full suite ran at the final
ticket head.

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
review axes satisfy its gates. A closing keyword may close the issue as
part of the authorized merge. Provider-side closure alone is not session
completion: retain the lease and finish cleanup, evidence, and release whether
the issue is open or closed. Re-read the live pull request head OID, live remote
ticket ref, base, state, mergeability, required checks, review result, and
integration ref. Require the PR head and remote ticket ref to equal the reviewed
ticket-head OID. A changed head invalidates the candidate and requires relevant
verification and review again. If only the integration base advanced, inspect
the target-advance branch in [references/lifecycle.md](references/lifecycle.md).
Retain the immutable review base and merge only after that branch pins an
effective-integration artifact and validates every affected gate and axis. When the pull request is open, mergeable, and
its required repository gates pass, perform the authorized merge using every
expected-head precondition the provider supports. On GitHub, pass the merge
API's `sha` head precondition. A separate branch rule that atomically pins the
integration-base OID is optional, not a prerequisite. Then verify that the pull
request reports merged from the reviewed ticket-head OID and the live
integration ref contains the reported integration commit. Record both OIDs;
squash and rebase merge need not preserve the ticket head as an ancestor.

An unknown publication result remains unresolved. Keep the lease, inspect the
remote branch, pull request, or integration target, and classify the operation
as present exactly once or absent before retrying. If tracker writes are
prohibited, remain read-only and do not claim.

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
review-axis results with each axis's explicit review-context identity, reviewed
candidate, final candidate, resolved base, exact path scope, authority
identities, and any carry-forward rationale or single-context fallback
disclosure. Include any effective-integration construction method or adapter,
tree OID, fingerprint, and reconstructable diff or a durable artifact pointer
resolved through `documenting-work`. Also include the ticket-head and integration
OIDs, the live ticket-head recovery ref, and cleanup disposition. For every required
verification gate, record the command, result, tested candidate, covered
behavior or artifact, and relevant integration/base assumptions. For a carried
gate, additionally record its final candidate, unaffected-scope rationale, and
targeted-validator result from the final candidate. For a hosted gate, record
its check name, provider run/status URL or immutable ID, and observed head OID.
Use the contract's
human-facing language. Under the bundled fallback, use the Korean evidence
headings while preserving the protocol marker; legacy English headings remain
read-compatible.
Link any repository document or artifact selected by `documenting-work`; do not
copy its full body into the evidence comment.

Read back every implementation tracker write as well. Reconcile an evidence
comment by the exact `rca-issue-evidence:v1` session/outcome marker: reuse exactly
one match, create only when no match exists, and stop on duplicates or an unknown
search result. Verify labels, parent state, and closure from their exact tracker
fields. For a completed outcome, close the issue only if it remains open after
publication and evidence. Never repeat an ambiguous tracker mutation before this
readback.

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
- Keep one implementation worker thread to one issue even after release; a goal
  coordinator selects every issue, including the first or only one, and starts a
  fresh worker.
- Use `--no-github-sync` only for isolated tests against a disposable remote.

For command fields, exit codes, stale recovery, and failure behavior, read
[references/lease-protocol.md](references/lease-protocol.md) when a lease
command fails or recovery is required.

Prefix commands with any proxy required by the consuming repository.
