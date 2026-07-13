---
name: to-tickets
description: Decompose an approved spec or plan into dependency-safe, vertically complete implementation tickets. Use when the user asks to split settled work into GitHub issues or tracer bullets; publish only when explicitly requested and expose readiness only after validating the entire dependency graph.
---

# Spec to tickets

Turn an approved source into small, verifiable tracer bullets. This skill may create tickets, dependency edges, and readiness labels when publication is authorized. `work-github-issue` supplies the tracker contract, revalidates frontier membership and blockers at claim time, and remains the sole owner of leases, implementation evidence, completion, and handoff.

## Preconditions

1. Read the full approved spec or plan, including comments and linked decisions.
2. Confirm that unresolved questions do not change ticket boundaries or dependencies. Return to `to-spec` when they do.
3. Read repository tracker instructions and domain documentation. The repository contract overrides all label and dependency examples here.
4. Draft only unless the user explicitly requested tracker publication.
5. Before authorized publication, have `work-github-issue` acquire a `planning` lease keyed to the source/parent issue. Check it before every mutation batch, renew around long publication, and release only after all tracker writes have been read back with no unknown result.

## Design the graph

### Prefer vertical tracer bullets

Each ticket should:

- deliver a narrow end-to-end behavior through every necessary layer;
- be independently demonstrable or verifiable;
- fit one fresh agent context;
- state concrete acceptance criteria and explicit exclusions;
- depend only on work that genuinely prevents it from starting.

Do not create separate schema, backend, frontend, and test tickets for one inseparable behavior. Put tests with the behavior they verify.

### Handle wide refactors explicitly

When one mechanical change cannot land green as a vertical slice, use expand-contract:

1. add the new form beside the old;
2. migrate callers in independently green batches;
3. remove the old form only after every migration completes.

Make those edges explicit. Do not disguise a wide refactor as a feature ticket.

### Draft every ticket

Compute a lowercase SHA-256 graph revision fingerprint from the approved source body plus the ordered identifiers and bodies of the specific accepted comments or decision records used for decomposition. Record those source identities; do not include secrets in the fingerprint input or marker. Use [the ticket template](references/ticket-template.md). Assign stable draft keys such as `T1`, `T2`, and express blockers by those keys until real tracker identifiers exist.

When the user asks to draft or review a breakdown, present the proposed graph and wait for approval before publishing. When the user explicitly asks to publish an approved source, that instruction authorizes publication after validation; proceed without a second approval unless a material ambiguity would change scope or dependencies. In either case, call out parallel frontier tickets, the critical path, and any scope that does not fit a single session.

## Validate before publishing

Reject or repair the draft if any of these checks fail:

- every blocker key resolves to a ticket in the graph;
- no ticket blocks itself and the graph has no cycle;
- every edge is a true start blocker, not merely a preferred order;
- every source requirement maps to at least one acceptance criterion;
- every ticket has a user-visible or operationally observable outcome;
- no ticket silently expands the approved source;
- initial frontier tickets can begin without an unrepresented prerequisite.

## Publish in two phases

Only perform these mutations when publication is authorized.

### Phase 1: create an unready graph

1. Assign each draft a stable key and include a non-secret reconciliation marker such as `<!-- to-tickets:v1 source=<parent> revision=<fingerprint> key=T1 -->` in its body. Search before every create for the exact marker and for the broader source/key pair. Reuse exactly one exact-revision match and create only when no source/key match exists. If another revision already uses that key, stop for an explicit supersession or migration decision instead of reusing or duplicating it.
2. Create every child ticket without `ready-for-agent`. Under the default label vocabulary, use `needs-triage` during assembly. Read back the marker and state after each create.
3. Link every ticket to the planning parent when the tracker supports parent/child relationships.
4. Add native blocking relationships. Use a `Blocked by` section only when the tracker lacks native dependencies.
5. Replace draft keys with real tracker identifiers and verify every body update from the tracker, not from the local draft.
6. After each parent link, blocker edge, body replacement, or label change, read the corresponding tracker field and classify the operation as present, absent, or unknown before continuing.

### Phase 2: expose the frontier

1. Re-run all graph checks against published identifiers and states.
2. Confirm each ticket has a complete brief, acceptance criteria, exclusions, and valid blockers.
3. Replace the assembly state with `ready-for-agent` on implementation tickets that satisfy the repository contract.
4. Keep the planning parent out of the implementation frontier and do not close or relabel it unless the user separately requested that action.

If any Phase 1 write fails or returns an ambiguous result, stop further writes. Reconcile creates by marker, parent links by parent field, blocker mutations by the exact dependency set, body changes by content/marker, and labels by the exact state role; never retry an unknown result blindly. Resume with the same keys only after each attempted mutation is classified as present exactly once or confirmed absent. If reconciliation is impossible, keep the planning lease, leave every created ticket unready, and report the partial graph, attempted operations, confirmed identifiers, and next safe action. Never delete successful creates automatically or make a partially linked graph claimable.

## Completion check

Return the source revision fingerprint, source-to-ticket traceability, dependency graph, initial frontier, published links if any, and validation result. Do not claim a ticket, commit code, publish implementation evidence, or close the parent from this skill.
