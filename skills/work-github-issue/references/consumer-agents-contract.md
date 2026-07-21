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
- Do not create, enable, trigger, rerun, or depend on GitHub Actions. Run the
  repository-defined focused and full tests, lint, typechecking, and builds in
  the owned local execution workspace.
- Create or amend the final ticket commit before final verification and review,
  require a clean workspace, and record its ticket-head OID plus the live
  integration-base OID it incorporates. Run all final local verification for
  that OID pair, then run independent Standards and Spec reviews from the pinned
  pre-work fixed point through the same pair. Do not share either
  reviewer's conclusions with the other before both reports are complete.
  Resolve every blocker/high finding and every safety-, ownership-, or
  completion-relevant medium finding. Any finding-driven file or commit change
  creates a new pair and invalidates local verification plus both reviews. A
  changed live integration base does the same: incorporate it, create the new
  ticket-head OID, and repeat all three gates until one unchanged pair passes.
- The lease-owning agent has standing authority to push its ticket branch,
  create or update its pull request, and merge that pull request into
  `{{INTEGRATION_TARGET}}` using {{MERGE_METHOD}} after all gates above pass.
  No additional human pull-request approval is required by this contract.
  Immediately before merge, verify that the pull-request body, every included
  commit message, and the selected merge message cannot close the leased issue
  through a closing keyword. Remove an authorized pull-request-body keyword and
  read back the edit. Rewrite a commit or merge message only within explicit
  publication authority and rerun invalidated verification and reviews; stop if
  any source could still close the issue prematurely.
- Immediately before merge, require the live pull request head OID and live
  remote ticket ref to equal the reviewed ticket-head OID and the live target ref
  to equal the reviewed integration-base OID. If any differs, incorporate the new
  base or head and repeat local verification plus both isolated reviews. Submit
  the merge only through a provider-side rule or operation that atomically rejects
  either a stale expected head or stale expected integration base. On GitHub,
  pass the merge API's `sha` head precondition and require a branch rule or other
  recorded provider mechanism that rejects an out-of-date base without GitHub
  Actions. Never issue an unguarded merge or retry with newly observed OIDs.
  Treat publication as complete only when the pull request reports merged from
  the reviewed ticket-head OID and the live
  `{{INTEGRATION_TARGET}}` contains the reported integration commit. Record both
  ticket-head and integration OIDs; squash and rebase merge need not preserve
  the ticket head as an ancestor of the integration ref. Branch rules or another
  applicable instruction that requires GitHub-hosted checks, external approving
  reviews, or restrictions the lease owner cannot satisfy autonomously conflicts
  with this contract; stop instead of bypassing those rules.
- Before closing the issue, verify that every session-created worktree is clean,
  no nested repository or submodule state would be lost, and the ticket-head OID
  remains recoverable from a live remote ticket ref or another verified durable
  ref. Remove an eligible session-created linked worktree from a retained control
  worktree, then delete its eligible local ticket branch with ordinary safe
  deletion. Never force cleanup. Preserve and report any artifact that fails a
  safety check.
- Post and read back final evidence including local verification, both reviews,
  the ticket-head and integration OIDs, merge state, recovery ref, and cleanup
  disposition. Close the issue only after that evidence and cleanup disposition
  are settled, then release the implementation lease. If an unexpected merge
  side effect closes the issue early, reconcile it back to open while the lease
  is owned before continuing; stop if that mutation is unknown. Remote branch
  deletion remains unauthorized unless a separate repository rule grants it.
<!-- work-github-issue:publication-contract:v1:end -->
