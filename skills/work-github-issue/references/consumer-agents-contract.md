<!-- work-github-issue:publication-contract:v1:start -->
## Issue-backed autonomous implementation only

This block is the repository's standing execution and publication contract for
`work-github-issue`.

This block is dormant unless all of these activation conditions are true:

- the current task is explicitly backed by a GitHub issue;
- `work-github-issue` is active for that issue;
- the session holds a valid implementation lease for that issue.

It does not apply to ad-hoc maintenance, documentation-only changes, or ordinary
Git operations authorized directly by the user. Outside those activation
conditions, ignore this block and follow the other applicable repository and
user publication instructions.

- Minimize human intervention. Continue autonomously when repository evidence,
  existing instructions, and this standing authority determine the next safe
  action. Ask a person only for genuinely missing requirements or authority,
  unavailable credentials or access, an unresolved safety decision, or an
  external write whose result cannot be reconciled.
- For an active leased issue implementation, use a pull request targeting `{{INTEGRATION_TARGET}}`;
  do not push its implementation commits directly to `{{INTEGRATION_TARGET}}`.
- Run repository-defined focused checks while developing and the required full
  relevant tests, lint, typechecking, and builds once for the final
  behavior-affecting candidate in the owned local execution workspace. After a
  candidate changes, rerun only the gates whose evidence the changed behavior,
  artifact, or integration assumption can affect unless repository policy
  explicitly requires a complete rerun. When carrying evidence forward after a
  non-behavioral change, record the tested prior candidate, final candidate,
  unaffected-scope rationale, and targeted validator run on the final candidate.
  Observe existing GitHub Actions and other required hosted checks, but do not
  create, edit, enable, disable, or rerun workflows unless separately authorized.
- Create or amend the final ticket commit before final verification and review,
  require a clean workspace, and record its ticket-head OID plus the live
  integration-base OID used for integration checks. Run final local verification,
  then separate Standards and Spec reviews from the pinned pre-work fixed point.
  Pass both the immutable review-base OID and current integration-base OID.
  If those bases differ, first pin and inspect the effective integration result
  as required by the target-advance branch below.
  Apply the required catalog companion `code-review` and its fresh
  candidate-scoped context boundary; use its disclosed separated single-context
  fallback only when reviewer isolation is unavailable. If the skill itself is
  unavailable, stop before publication, report the missing required package,
  apply the tracker contract's `blocked|handoff` state, preserve the workspace,
  post and read back structured evidence plus its handoff pointer, and release
  the lease only after that readback; never report completed.
  Resolve every blocker/high finding and every safety-, ownership-, or
  completion-relevant medium finding. Any finding-driven file or commit change
  creates a new candidate and invalidates every check and review axis whose
  evidence the changed behavior, artifact, integration assumption, or files
  could affect.
- The lease-owning agent has standing authority to push its ticket branch,
  create or update its pull request, and merge that pull request into
  `{{INTEGRATION_TARGET}}` using {{MERGE_METHOD}} after all gates above pass.
  No additional human pull-request approval is required by this contract. A
  closing keyword may close the issue as part of the authorized merge; retain
  the lease and finish cleanup, evidence, and release whether the issue is open
  or closed.
- Immediately before merge, require the live pull request head OID and live
  remote ticket ref to equal the reviewed ticket-head OID. A changed head
  invalidates the candidate. If only the target advanced, inspect the effective
  integration result in a disposable workspace using the resolved merge method.
  Retain the immutable review base; pin the live integration-base OID, merge
  method, effective tree/diff fingerprint, and reconstructable diff, then pass
  that artifact to both review axes. Re-resolve scope and authority identities,
  rerun every affected gate or axis, and fail closed if the result cannot be
  reconstructed. Require the pull request to be open and mergeable with its
  required repository gates satisfied, then use every expected-head precondition
  the provider supports. On GitHub, pass the merge API's `sha` head precondition.
  A branch rule that also pins the integration base is optional, not a
  prerequisite.
  Treat publication as complete only when the pull request reports merged from
  the reviewed ticket-head OID and the live
  `{{INTEGRATION_TARGET}}` contains the reported integration commit. Record both
  ticket-head and integration OIDs; squash and rebase merge need not preserve
  the ticket head as an ancestor of the integration ref. Satisfy applicable
  branch rules and required checks; if an external approval or restriction
  remains unsatisfied, request that exact action instead of bypassing the rule.
- Before finalizing the issue outcome, verify that every session-created
  worktree is clean, no nested repository or submodule state would be lost, and
  the ticket-head OID remains recoverable from a live remote ticket ref or
  another verified durable ref. Remove an eligible session-created linked
  worktree from a retained control worktree, then delete its eligible local
  ticket branch with ordinary safe deletion. Never force cleanup. Preserve and
  report any artifact that fails a safety check.
- Post and read back final evidence including local verification, both reviews
  with each axis's explicit review-context identity, candidate, base, path scope,
  authority provenance, and any carry-forward rationale, plus the ticket-head
  and integration OIDs, merge state, recovery ref, and cleanup disposition.
  Preserve any effective-integration construction method or adapter, tree OID,
  fingerprint, and reconstructable diff or a durable artifact pointer.
  Record every required verification gate's command, result, tested candidate,
  covered scope or artifact, and integration/base assumptions; for carried
  evidence also record the final candidate, rationale, and final targeted-validator
  result. For a hosted gate, record its check name, provider run/status URL or
  immutable ID, and observed head OID. If the issue remains open, close it after that evidence and cleanup
  disposition are settled, then release the implementation lease.
  Remote branch deletion remains unauthorized unless a separate repository rule
  grants it.
<!-- work-github-issue:publication-contract:v1:end -->
