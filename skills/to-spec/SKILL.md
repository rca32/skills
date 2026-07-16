---
name: to-spec
description: Synthesize settled decisions in the current conversation into a durable planning and decomposition-ready product or engineering spec. Use when the user asks for a spec or PRD from existing discussion without another discovery interview; publish only when explicitly requested.
---

# Conversation to spec

Convert decisions already present in the conversation and repository into a precise spec. Do not reopen discovery or invent requirements to make the document look complete.

## Authority and boundaries

- Preserve consuming-repository safety, ownership, and architecture instructions. Within those boundaries, explicit user product decisions govern the requested outcome, followed by accepted domain and architecture records as context.
- If product decisions conflict with repository safety or accepted architecture and the conversation does not resolve the conflict, preserve both claims in the open-questions section (`미해결 질문` in the fallback template) and keep the spec in a draft or blocked-on-questions status; never choose silently.
- Separate confirmed decisions from assumptions and unresolved questions.
- Do not interview the user during this workflow. If an unknown materially changes the solution, record it in the open-questions section and make the spec's decomposition readiness conditional.
- Resolve the human-facing language from repository instructions, then the user's request, and otherwise use Korean. Preserve quoted source text, code identifiers, API names, links, and protocol markers exactly.
- Use `documenting-work` to classify the spec as conversation-, tracker-, or repository-authoritative before persistence. Return it in the response when the user asked only for a draft. A destination file authorizes that file plus locally required index entries and in-repository reciprocal links; create or update a tracker item or external pointer only when the user asked to publish it.
- A published spec is a planning or parent item, not an implementation ticket. Never add the `ready-for-agent` role. Resolve labels only from the selected tracker contract. Use the repository's non-frontier planning state; under the fallback contract use `상태: 사람 검토 필요` while approval or decomposition is required, and fill its Human action contract with the request type, exact target, action, response location, completion condition and evidence reference, next state, and transition owner.
- Let `documenting-work` own repository path, document identity, metadata, index, and supersession. Before any authorized destination-file or tracker write, have `work-github-issue` acquire a `planning` lease keyed to the source issue. Use repository-wide key `0` only when no source issue exists. If that outer lease is unavailable, keep the result in the response. Check the lease before writes and release only after operation-specific readback.

## Process

1. **Collect decisions.** Extract the problem, desired outcome, constraints, safety boundaries, exclusions, and unresolved choices from the conversation.
2. **Inspect current reality.** Read the repository's product synthesis, domain vocabulary, architecture decisions, and relevant public interfaces. Verify claims that can drift as code changes.
3. **Choose test seams.** Prefer the highest existing public seam that observes user-visible behavior. Add a new seam only when no stable seam can express the acceptance criteria. Record the seam and why it is sufficient.
4. **Write the spec.** Use [the spec template](references/spec-template.md). Keep requirements behavioral; avoid file paths, line numbers, and speculative code unless a short type or state-machine shape is itself an approved contract. When persistence is requested without a destination, resolve it through `documenting-work`; do not invent another `specs/` location.
5. **Audit the draft.** Every acceptance criterion must trace to a stated requirement. Every material constraint must have an observable verification path. Mark contradictions and unknowns explicitly.
6. **Persist if authorized.** For a repository document, follow the resolved `documenting-work` contract, fingerprint the destination, check the planning lease, apply only the spec change, locally required index entries, and in-repository reciprocal links, then read them back. Add a tracker comment, issue edit, or other external pointer only under separate mutation authorization. Stop if the file changed between inspection and write. Before tracker publication, read the repository label catalog and confirm every label this spec will use exists with the selected tracker meaning; ordinary spec-publication authority does not create repository-wide labels. If setup is missing, stop with the selected contract's exact labels and descriptions unless label creation was separately authorized. For tracker publication, choose a stable non-secret key: prefer the source issue identifier, otherwise use a normalized approved title. Include `<!-- to-spec:v1 key=<key> -->` in the issue body. Search for that marker before create: reuse exactly one match and stop on duplicates. After create or update, read back the marker, body, source links, planning state, and any required Human action block. Preserve authorized links to the conversation or source issue and leave implementation decomposition to `to-tickets`. Never duplicate the full body across file and tracker; the non-authoritative side contains a pointer only when that write is authorized. Never retry an unknown file or update result until its authoritative field classifies it as present exactly once or absent. For an ambiguous issue create, an empty marker search or paginated issue enumeration does not prove absence; retry only when a durable provider response, request identifier, or transport record proves the original request was rejected before creation. Otherwise preserve the unknown key and planning lease and stop publication.

## Completion check

The result is complete when it distinguishes decisions, assumptions, and unknowns; defines current and desired behavior; names verification seams; includes measurable acceptance criteria and exclusions; identifies one authoritative location when persisted; and cannot be mistaken for a claimable implementation issue.
