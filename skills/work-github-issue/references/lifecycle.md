# Issue lifecycle routing

Use this reference when the issue is not already a ready, unblocked unit of
implementation work. Invoke a named skill when it is available and reachable;
otherwise apply the invariant in the final column directly.

| Situation | Route | Preserved invariant |
| --- | --- | --- |
| Incoming bug or request | `prepare-issue` | Verify before briefing; exactly one category and state role |
| Settled conversation needs a durable PRD | `to-spec` | Domain vocabulary, testing seams, decisions, out-of-scope |
| Approved plan spans sessions | `to-tickets` | Tracer-bullet slices with genuine blocking edges |
| A spec, decision, report, handoff, or artifact may be persisted | `documenting-work` | One authority, repository override, stable identity/path, index and pointers |
| Destination is larger than the visible route | `wayfinder` | Shared map, named tickets, frontier, fog, one ticket per session |
| Ready ticket is being built | Skill's execution step | Test seam, focused implementation, regular checks, final suite |
| Diff is ready to judge | `code-review` | Standards and Spec stay separate |
| Work is ready to publish | resolved repository publish flow | Fixed point, PR/integration targets, separate push/PR/merge authority, checks, completion point |

The selected tracker contract is the single source of truth for state labels,
frontier membership, dependency representation, claim authority, and close
semantics. This reference only selects the lifecycle branch.

## Resume rules

Read the latest durable evidence before resuming. Reuse an active lease only
with its exact session token. For an expired lease, inspect the named branch,
commit/PR links, tests, and handoff comment, then acquire with
`--takeover-expired`. Preserve useful work and record any superseded branch.

## Integration context changed before publication

Enter this branch whenever the live integration-base OID differs from the
pre-work fixed point at initial final verification or moves after review while
the ticket head is unchanged. Keep the pre-work review base immutable. Resolve the
repository's exact merge method, then use a disposable repository, worktree, or
index to construct the effective integration tree for the reviewed ticket head
on the new live integration base. Do not mutate the ticket workspace.

Record the live integration-base OID, merge method, construction command or
provider adapter version, resulting tree OID when available, and a binary-safe
fingerprint plus reconstructable diff of that tree against the live integration
base. Pass this pinned artifact to `code-review`; both axes must inspect its diff
and include it in their review-context identities. Re-resolve applicable scope and authority
identities against the integration context, then rerun every gate or axis whose
behavior, effective diff, authority, or context evidence changed. Carry an axis
forward only with explicit unchanged-context evidence.

Exit only when the artifact still matches the live candidate and integration
base and every affected gate is valid. If the merge result conflicts, the merge
method is unresolved, the artifact cannot be reconstructed, or provider state
changes during inspection, fail closed and return a bounded non-complete outcome.
