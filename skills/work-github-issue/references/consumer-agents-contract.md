<!-- work-github-issue:publication-contract:v1:start -->
## Autonomous issue implementation

This block is the repository's standing execution and publication contract for
`work-github-issue`.

- Minimize human intervention. Continue autonomously when repository evidence,
  existing instructions, and this standing authority determine the next safe
  action. Ask a person only for genuinely missing requirements or authority,
  unavailable credentials or access, an unresolved safety decision, or an
  external write whose result cannot be reconciled.
- Use a pull request targeting `{{INTEGRATION_TARGET}}`; do not push
  implementation commits directly to `{{INTEGRATION_TARGET}}`.
- Run the repository-defined focused and full tests, lint, typechecking, and
  builds in the owned local execution workspace. Observe existing GitHub Actions
  and other required hosted checks, but do not create, edit, enable, disable, or
  rerun workflows unless separately authorized.
- Create or amend the final ticket commit before final verification and review,
  require a clean workspace, and record its ticket-head OID plus the live
  integration-base OID used for integration checks. Run final local verification,
  then separate Standards and Spec reviews from the pinned pre-work fixed point.
  Use isolated reviewers when available; otherwise disclose a separated
  single-context fallback.
  Resolve every blocker/high finding and every safety-, ownership-, or
  completion-relevant medium finding. Any finding-driven file or commit change
  creates a new candidate and invalidates the checks and reviews that cover the
  changed behavior.
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
  merge diff and run risk-relevant integration checks; repeat Spec review only
  when behavior or the effective diff changes, and Standards only when ticket
  files change. Require the pull request to be open and mergeable with its
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
- Post and read back final evidence including local verification, both reviews,
  the ticket-head and integration OIDs, merge state, recovery ref, and cleanup
  disposition. If the issue remains open, close it after that evidence and
  cleanup disposition are settled, then release the implementation lease.
  Remote branch deletion remains unauthorized unless a separate repository rule
  grants it.
<!-- work-github-issue:publication-contract:v1:end -->
