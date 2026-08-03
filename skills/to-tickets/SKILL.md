---
name: to-tickets
description: Decompose an approved spec or plan into dependency-safe, vertically complete implementation tickets. Use when the user asks to split settled work into GitHub issues or tracer bullets; stop before drafting when decomposition would require a new public behavior, interface, architecture, or dependency decision, publish only when explicitly requested, and expose readiness only after validating the entire dependency graph.
---

# Spec to tickets

Turn an approved source into small, verifiable tracer bullets. This skill may create tickets, dependency edges, and readiness labels when publication is authorized. `work-github-issue` supplies the tracker contract, revalidates frontier membership and blockers at claim time, and remains the sole owner of leases, implementation evidence, completion, and handoff.

## Preconditions

1. Read the full approved spec or plan, including comments and linked decisions.
2. Read repository tracker instructions and domain documentation. The repository contract overrides all label and dependency examples here.
3. Pass the decomposition-readiness gate below before drafting.
4. Resolve the human-facing prose language from repository instructions, then the user's request, and otherwise use Korean. Keep protocol markers, code identifiers, API names, and role keys stable, but write titles, bodies, comments, and human instructions in the resolved language. Resolve label identity only from the selected tracker contract; the bundled fallback publishes Korean labels and accepts legacy English labels only for compatibility. The approved source's language alone is not an output-language request.
5. Draft only unless the user explicitly requested tracker publication.
6. For authorized publication, follow the source revalidation and `planning` lease sequence under **Publish in two phases**. Check the lease before every mutation batch, renew around long publication, and release only after all tracker writes have been read back with no unknown result.
7. Treat the tracker graph as authoritative. If the user requests a local export or pointer, resolve it with `documenting-work`; never maintain a second editable ticket body.

## Gate decomposition readiness

Before drafting, reject any selected source or decision body containing credentials,
tokens, private issue data, or other sensitive material. Do not hash or redact it
ad hoc. Return `status=source-sanitization-required`, the authoritative pointer,
sensitive categories without their values, accepting authority, next workflow,
and resume condition; require a sanitized authoritative revision before retrying.

For safe inputs, compute the current source fingerprint with
[`source_fingerprint.py`](scripts/source_fingerprint.py), then determine whether every
source requirement can become a vertical ticket with a stable acceptance
boundary, verification seam, and true blockers without choosing a new public
behavior or an interface, seam, protocol, architecture, or dependency decision
that establishes or changes an approval-gated/public contract, ticket boundary,
or dependency graph. Private in-bounds
module interfaces and implementation choices that preserve those contracts
remain delegated to the implementation worker and do not block decomposition.

If the answer is yes, continue. If no, do not emit provisional ticket bodies,
create tracker items, or acquire a planning lease. Classify the missing decision:

- route an unsettled module interface or architectural seam that establishes or
  changes an approval-gated contract through `codebase-design`, then `to-spec`
  for resolution and persistence;
- route unsettled product behavior, authority, safety, or acceptance criteria
  to `to-spec` and name the accepting authority;
- route any other unsettled public interface, protocol, or dependency choice to
  `to-spec`; use `codebase-design` first only when it is also a module or
  architectural seam decision;
- repair only graph mapping or dependency errors here when the approved source
  already fixes the required behavior and seams;
- route a conflict between the approved source and current repository reality
  to `to-spec` for revalidation.

Return `status=decomposition-blocked`, the authoritative source pointer and
current fingerprint, affected source requirements, missing decision, boundary
or dependency impact, next workflow, accepting authority, and resume condition. Return control rather than
accepting a recommendation or entering another skill's mutation workflow.
Resume only when the approved source or accepted decision set produces a new
source fingerprint with the decision resolved. Re-read that authority and
decompose from scratch; never carry a provisional graph across revisions.

Completion criterion: either decomposition is demonstrably possible without a
new planning decision, or the workflow stops read-only with a complete,
actionable `decomposition-blocked` handoff.

Whenever publication revalidation finds a safe fingerprint or readiness change,
return `status=publication-source-drift` with the authoritative pointer, old and
new algorithms/fingerprints, affected draft or partial graph, completed
readbacks, lease state, next workflow, required adoption/supersession/migration
decision, accepting authority, and resume condition. Use `none` for graph or
lease fields when drift is caught before they exist. Never migrate a stale graph
in place or resume it under the new revision.

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

Use `scripts/source_fingerprint.py` to compute the lowercase SHA-256 graph revision fingerprint from the exact sanitized source body and the specific accepted comments or decision records used for decomposition. The script owns versioned framing, UTF-8 encoding, decision ordering, and the no-decisions case; do not reproduce or modify its encoding. Record the returned algorithm and ordered source identities. Use [the ticket template](references/ticket-template.md). Assign stable draft keys such as `T1`, `T2`, and express blockers by those keys until real tracker identifiers exist.

Pass the script UTF-8 JSON shaped as `{"source_body":"<exact body>","decisions":[{"id":"<stable id>","body":"<exact body>"}]}` through stdin or a local input file. Include only accepted records actually used for decomposition and pass an empty list when there are none.

Use outcome-first titles and plain language. Explain unavoidable technical terms at first use. When a ticket must wait in the selected tracker contract's `needs-info` or `ready-for-human` role, fill its Human action contract with the exact reason, request type, target, one concrete action, response location, observable completion condition and evidence reference, next state, and authorized transition owner. For `ready-for-human`, also provide a copy-ready suggested comment for recording the person's result, rationale, and evidence link. A generic request to review or provide more information is incomplete.

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
- every human-wait ticket names an actionable request, response location, completion evidence, and next state; every `ready-for-human` ticket also has a copy-ready suggested comment.

## Publish in two phases

Only perform these mutations when publication is authorized.

Immediately before acquiring a planning lease, re-read the authoritative source
and accepted decisions and rerun the readiness gate. The gate checks sensitivity
before computing a safe fingerprint. If the fingerprint differs from the
approved draft or readiness no longer passes, return the applicable blocked or
`publication-source-drift` outcome without acquiring a lease or mutating the
tracker. Otherwise have `work-github-issue` acquire a `planning` lease keyed to
the source/parent issue. Immediately after acquisition, repeat the authoritative
read and gate before comparing fingerprints. On drift or newly sensitive input,
perform no ticket mutation, release the lease after its state is read back, and
return the applicable terminal outcome.

Before Phase 1, read the repository label catalog. Use applicable existing labels, but do not create them without separate authority. Missing optional labels do not block publication; encode each state with the selected tracker contract's body marker and continue.

### Phase 1: create an unready graph

1. Assign each draft a stable key and include the non-secret reconciliation marker `<!-- to-tickets:v2 source=<parent> algorithm=<fingerprint-algorithm> revision=<fingerprint> key=T1 -->` in its body. Search before every create for the exact v2 marker and for the broader source/key pair across v1 and v2 markers. Reuse exactly one exact v2 match and create only when no source/key match exists. Treat a legacy v1 marker as algorithm-unknown: never infer digest equivalence or rewrite it in place. If a legacy marker or another revision already uses that key, stop for an explicit adoption, supersession, or migration decision instead of reusing or duplicating it.
2. Create every child ticket without the `ready-for-agent` role. Under the fallback contract, use an existing `상태: 분류 필요` label or the `needs-triage` body marker during assembly. Read back the reconciliation marker and state after each create.
3. Link every ticket to the planning parent when the tracker supports parent/child relationships.
4. Add native blocking relationships. Under the Korean fallback, use a `먼저 끝나야 하는 작업` section only when the tracker lacks native dependencies.
5. Replace draft keys with real tracker identifiers and verify every body update from the tracker, not from the local draft.
6. After each parent link, blocker edge, body replacement, or label change, read the corresponding tracker field and classify the operation as present, absent, or unknown before continuing.

### Phase 2: expose the frontier

1. Re-read the authoritative source and decisions and rerun the readiness gate,
   which checks sensitivity before computing a safe fingerprint. If the input is
   newly sensitive, or if readiness or the fingerprint differs from Phase 1,
   leave every created ticket unready and perform no further ticket mutation.
   Return `status=source-sanitization-required` for sensitive input; otherwise
   return `status=publication-source-drift`. Include the old algorithm/revision,
   the new algorithm/revision when safely available, partial graph and readback
   state, recovery markers, lease release result, next workflow, required
   adoption/supersession/migration decision, accepting authority, and resume
   condition. Release the lease only after completed writes are read back; do
   not rewrite the old graph into the new revision.
2. Re-run all graph checks against published identifiers and states.
3. Confirm each ticket has a complete brief, acceptance criteria, exclusions, and valid blockers.
4. Replace the assembly state with the `ready-for-agent` role on implementation tickets that satisfy the fallback contract, using an existing label or the body marker. Keep tickets requiring information or human action in the corresponding role with a complete Human action block. Use repository-defined labels or markers when its tracker contract overrides the fallback.
5. Keep the planning parent out of the implementation frontier and do not close or relabel it unless the user separately requested that action.

If any Phase 1 write fails or returns an ambiguous result, stop further writes and reconcile by the authoritative field. For creates, perform exactly three complete marker/catalog reads over no more than 60 seconds and require the final two reads to agree. If the marker remains absent and no provider request is still pending, classify the create as absent and retry once with the same marker. Reconcile parent links, blockers, bodies, and states from their exact fields. If the retry is also unknown, preserve the recovery marker and partial graph, leave created tickets unready, stop writes, and stop renewing the planning lease indefinitely so a later takeover can reconcile it. Never delete successful creates automatically or expose a partially linked graph as claimable.

## Completion check

For a completed graph, return the authoritative source pointer, source revision fingerprint, source-to-ticket traceability, dependency graph, initial frontier, published links if any, and validation result. A `decomposition-blocked`, `source-sanitization-required`, or `publication-source-drift` result is terminal only when it contains every field required by its branch, including partial graph and lease state when publication began. Do not claim a ticket, commit code, publish implementation evidence, close the parent, or create an unindexed duplicate ticket document from this skill.
