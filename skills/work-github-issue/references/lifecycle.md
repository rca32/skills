# Issue lifecycle routing

Use this reference when the issue is not already a ready, unblocked unit of
implementation work. Invoke a named skill when it is available and reachable;
otherwise apply the invariant in the final column directly.

| Situation | Route | Preserved invariant |
| --- | --- | --- |
| Incoming bug or request | `triage` | Verify before briefing; exactly one category and state role |
| Settled conversation needs a durable PRD | `to-spec` | Domain vocabulary, testing seams, decisions, out-of-scope |
| Approved plan spans sessions | `to-tickets` | Tracer-bullet slices with genuine blocking edges |
| A spec, decision, report, handoff, or artifact may be persisted | `documenting-work` | One authority, repository override, stable identity/path, index and pointers |
| Destination is larger than the visible route | `wayfinder` | Shared map, named tickets, frontier, fog, one ticket per session |
| Ready ticket is being built | Skill's execution step | Test seam, focused implementation, regular checks, final suite |
| Diff is ready to judge | `code-review` | Standards and Spec stay separate |
| Work is ready to publish | repository publish flow | Intentional scope, commit, push/PR authorization |

The selected tracker contract is the single source of truth for state labels,
frontier membership, dependency representation, claim authority, and close
semantics. This reference only selects the lifecycle branch.

## Resume rules

Read the latest durable evidence before resuming. Reuse an active lease only
with its exact session token. For an expired lease, inspect the named branch,
commit/PR links, tests, and handoff comment, then acquire with
`--takeover-expired`. Preserve useful work and record any superseded branch.
