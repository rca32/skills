---
name: decision-map
description: "Turn a large, unclear effort that cannot yet become one reliable spec into a sequential repository map of decision questions. Use when the user explicitly asks to chart or continue a decision map, when important questions emerge only after earlier answers, or when a multi-session effort still has material fog; hand off to to-spec when the route is clear. Do not use for implementation decomposition, GitHub tickets, or code changes."
---

# Decision map

Find the decisions that make a large effort specifiable. Keep a small map as an index and put each question and resolution in one separate document. Work sequentially; this workflow has no claim, lease, assignment, or parallel-agent protocol.

## Authority and boundaries

- Treat the destination as the scope boundary, not as permission to implement it. The map is complete when the route to a spec is clear.
- Keep each decision's detailed question, evidence, resolution, and consequences in its decision document. `map.md` contains only links, status, and one-line gists.
- Use `documenting-work` to resolve persistence, identity, paths, metadata, index, and lifecycle. Under its fallback, use `docs/decision-maps/<name>/map.md` and `decisions/DNNN-<slug>.md`.
- Use `domain-modeling` when a question actively changes domain terms, invariants, states, relationships, or boundaries. Use `codebase-design` for a module interface or architectural seam. Record their established outcome in the decision document; do not duplicate their full analysis.
- Use `to-spec` only after the open decisions and material fog no longer prevent one coherent specification.
- Do not create or mutate tracker issues, implement destination code, claim work, commit, push, publish, or delete documents.

A request to inspect, explain, or draft a possible map is read-only and returns conversation output. A request to create, chart, update, resolve, or continue a named decision map authorizes that repository document set and its required index entry, but not code, prototype files, external writes, or publication. A prototype or prerequisite that changes another artifact requires separate authorization for that artifact.

## Chart a map

1. Read repository instructions, authoritative domain and architecture records, nearby specs or decisions, and the documentation convention.
2. Name the destination in one or two outcome-focused sentences. Identify the decision authority and explicit out-of-scope boundary.
3. Test whether a map is necessary. If the destination and all material decisions already fit one coherent spec, create no map and recommend `to-spec`.
4. Resolve the map identity and destination through `documenting-work`. Record the destination file, index entry, Git status, and existing fingerprints before editing.
5. Read [the map and decision templates](references/document-set.md). Create `map.md`, then create documents only for questions that can be stated precisely now. Keep uncertain areas that cannot yet be phrased as a decision question under `Not yet specified`.
6. Order open decisions by what can clarify the most remaining fog. Mark exactly one as `Current`; later questions remain `Open decisions` and are not worked in parallel.
7. Read back the map, decision metadata, links, index, and Git status. Stop on an identity collision or changing in-scope file. Change the map from `draft` to `active` only after exactly one valid `Current` link and every indexed child resolve correctly.

Charting completes with one repository map authority, at least one precise current question, and no copied decision detail in `map.md`. If no precise question exists, set the map status to `blocked`, record the smallest human input needed to name one, and return `status=map-question-blocked` plus `resume_condition=precise-question-authorized`.

## Resolve decisions sequentially

1. Load `map.md` and only its current decision document. Fetch another decision or authority only when the current question links to it.
2. Recheck the map, current decision, index, and relevant source fingerprints before writing. If another actor changed an in-scope file, reconcile or stop; this skill does not add concurrency machinery.
3. Resolve according to `question_kind`:
   - `research`: inspect authoritative local or external evidence and distinguish fact from inference;
   - `discussion`: obtain the named decision maker's answer; never speak for the human side;
   - `prototype`: create only a cheap artifact that the user separately authorized, then use the reaction as evidence rather than shipping the prototype;
   - `prerequisite`: perform only the authorized enabling action, then record the resulting facts without treating it as destination delivery.
4. Write the resolution, authority, evidence pointers, rejected alternatives, and consequences in the decision document. Use `resolved` only when the named authority settled the question; set its `map_projection` to `pending`. Otherwise retain `open` with `map_projection: not-applicable` and state the missing evidence or answer.
5. For a resolved decision, update `map.md` with one linked gist. Promote newly precise fog into new sequential decision documents, remove only the promoted fog text, and move newly excluded work to `Out of scope` with its reason.
6. Select the next open decision as `Current`, or set the map to `ready-for-spec` when no open decision or material fog blocks the destination. Read back every changed file and link, then update the resolved decision's `map_projection` to `current` and read back that metadata.

If a decision resolution is written but the map or index update fails, preserve its `map_projection: pending`, report `status=map-index-pending`, the decision/map/index identities, known write results, and `resume_condition=projection-reconciled`. Reconcile the links before selecting another decision. Never rewrite the resolution merely to retry the index update.

Resolve one decision by default. Continue through more decisions only when the user explicitly asks to keep going and each prior resolution has been read back before the next begins.

## Completion and handoff

Return the map identity and path, current status, decision resolved this run, remaining open decisions and fog, files changed, and next workflow. A completed map requires:

- a stable destination and scope boundary;
- every route-defining question resolved or explicitly out of scope;
- an empty `Not yet specified` section for material in-scope uncertainty;
- no implementation deliverable disguised as a decision;
- a `to-spec` handoff containing the map path and authoritative decision-document paths, not a new combined summary body;
- no unresolved `map-index-pending`, identity collision, or changing in-scope file.
