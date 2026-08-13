---
name: domain-modeling
description: Actively develop and sharpen a project's domain model during design. Use when work must challenge ambiguous domain terms, test concepts with examples and edge cases, or settle changes to domain language, invariants, relationships, state transitions, or boundaries. Do not invoke merely to read an existing domain document for vocabulary, and do not use for module-interface design, requirements invention, implementation, or document-placement decisions.
---

# Domain Modeling

Make the domain model precise enough that later specifications, interfaces, and tests can use the same concepts without silently choosing another meaning. Treat examples and edge cases as tests of the model, not as accepted requirements.

## Authority and composition

Inspect authorized repository material and actively analyze the model in the conversation. Classify every changed term, rule, or boundary as `established`, `proposed`, or `unresolved`; mark it `established` only when repository authority or an authorized decision maker settles it.

- Read the existing domain document as a routine prerequisite when another skill only needs its vocabulary. That consumption alone does not invoke this skill.
- Use `codebase-design` for module interfaces and architectural seams. A domain boundary may constrain a module seam, but this skill does not design the module.
- Pass established behavior and domain decisions to `to-spec`. Do not turn a plausible scenario into a requirement merely because it makes the model cleaner.
- Use `documenting-work` before persisting a domain-model change. Let it resolve authority, path, identity, metadata, index, lifecycle, and write authorization; keep ownership of domain content here.
- Leave implementation to `tdd`, issue and tracker lifecycle to `work-github-issue`, and completed-change assessment to `code-review`.

A request to inspect, discuss, challenge, or draft is read-only: return proposed domain-model changes in the response and create no file. When the user or repository explicitly authorizes repository persistence, update only the destination and locally required index or reciprocal links selected by `documenting-work`, with destination fingerprint and dirty-worktree protection. Do not edit code, mutate a tracker, commit, push, publish, or delete an existing document from this skill.

## Frame the model change

1. Read applicable repository instructions, the authoritative domain model or glossary, accepted specifications and decisions, and the smallest relevant implementation evidence.
2. Name the ambiguity or model pressure: conflicting terms, missing distinction, unclear identity, invalid state, uncertain relationship, or boundary leakage.
3. Identify affected concepts, actors, events, invariants, lifecycle states, and contexts. Preserve accepted language unless evidence or authority justifies a change.
4. State who or what can settle the change. Keep the work read-only when that authority or persistence authorization is absent.

Framing is complete when the current meaning, observed pressure, affected model surface, source authority, and decision authority are explicit.

## Stress-test the current model

Construct only scenarios that discriminate between meanings. For each material concept, use the smallest relevant set of:

- a canonical example and a near-miss non-example;
- boundary values, empty states, and invalid combinations;
- identity, equality, ownership, and lifecycle questions;
- ordering, duplication, retry, cancellation, and late-event cases;
- actor, permission, jurisdiction, tenant, or time-context changes;
- a counterexample that would break the proposed invariant.

Label each scenario as observed, required by an authoritative source, or hypothetical. A hypothetical scenario may expose ambiguity but cannot establish product behavior by itself. Stop expanding scenarios when additional cases no longer distinguish a term, invariant, relationship, state transition, or boundary.

The stress test is complete when every proposed model change names the case the old model mishandles and no decisive scenario is presented as accepted without authority.

## Sharpen the model

For each concept that survives the stress test, record only the fields that change shared understanding:

- **Term:** one preferred name, precise meaning, aliases to search for, and misleading uses to avoid.
- **Examples:** representative examples and non-examples that define the boundary.
- **Identity and lifecycle:** what makes an instance the same, when it begins and ends, and valid state transitions.
- **Relationships and invariants:** cardinality, ownership, dependencies, and rules that must always hold.
- **Context boundary:** where the meaning applies and how a similarly named concept in another context differs or translates.
- **Decision:** rationale, source authority, rejected meanings, consequences, and status.

Prefer domain language over current class, table, endpoint, or file names. Cite implementation identifiers only as evidence or migration impact. Split concepts that carry incompatible meanings; merge synonyms only when their invariants and lifecycle are genuinely the same.

## Settle and persist

1. Present the smallest coherent model delta and the scenarios that support it.
2. Resolve each item as `established`, `proposed`, or `unresolved`. Name the accepting authority and missing evidence for anything not established.
3. When persistence is not authorized, return a patch-shaped proposal in the conversation and stop without creating or editing a document.
4. When repository persistence is authorized, invoke `documenting-work` and follow the destination, identity, and lifecycle it resolves, including any fixed-document behavior. Do not select or duplicate a destination here.
5. Persist established material as the operative glossary and model. Keep proposed or unresolved material visibly labeled so readers cannot mistake it for the current contract.
6. Read back the affected terms, decisions, metadata, index, links, and Git status. Stop if the destination changed after inspection or if two documents claim authority for the same model surface.

If an issue-backed implementation lease is already active, respect it around the repository write. Tracker comments or external pointers require separate authorization and the outer workflow's lease; do not create them merely because the domain document changed.

## Completion and handoff

Return:

1. the model pressure and inspected authority;
2. changed terms, examples, invariants, relationships, states, and boundaries;
3. the discriminating scenarios and whether each is observed, authoritative, or hypothetical;
4. the status and accepting authority of every change;
5. unresolved questions and the smallest evidence that would settle them;
6. persistence result: conversation proposal or the authoritative document resolved by `documenting-work`;
7. downstream effects for specifications, module design, implementation, tests, and migration.

Complete the work only when later workflows can distinguish the established model from proposals, every accepted change survives its named edge cases, no scenario has silently become a requirement, and any authorized document update has exactly one authoritative home.
