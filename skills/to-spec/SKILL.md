---
name: to-spec
description: Synthesize settled decisions in the current conversation into a durable planning and decomposition-ready product or engineering spec. Use when the user asks for a spec or PRD from existing discussion without another discovery interview; publish only when explicitly requested.
---

# Conversation to spec

Convert decisions already present in the conversation and repository into a precise spec. Do not reopen discovery or invent requirements to make the document look complete.

## Authority and boundaries

- Preserve consuming-repository safety, ownership, and architecture instructions. Within those boundaries, explicit user product decisions govern the requested outcome, followed by accepted domain and architecture records as context.
- If product decisions conflict with repository safety or accepted architecture and the conversation does not resolve the conflict, preserve both claims under `Open questions` and keep the spec `draft` or `blocked on open questions`; never choose silently.
- Separate confirmed decisions from assumptions and unresolved questions.
- Do not interview the user during this workflow. If an unknown materially changes the solution, record it under `Open questions` and make the spec's decomposition readiness conditional.
- Return the draft in the response unless the user named a durable destination. A destination file authorizes that file write only; create or update a tracker item only when the user asked to publish it.
- A published spec is a planning or parent item, not an implementation ticket. Never add `ready-for-agent`. Use the repository's non-frontier planning state; under the default state vocabulary use `ready-for-human` while approval or decomposition is required.
- Before any authorized destination-file or tracker write, have `work-github-issue` acquire a `planning` lease keyed to the source issue. Use repository-wide key `0` only when no source issue exists. If that outer lease is unavailable, keep the result in the response. Check the lease before writes and release only after operation-specific readback.

## Process

1. **Collect decisions.** Extract the problem, desired outcome, constraints, safety boundaries, exclusions, and unresolved choices from the conversation.
2. **Inspect current reality.** Read the repository's product synthesis, domain vocabulary, architecture decisions, and relevant public interfaces. Verify claims that can drift as code changes.
3. **Choose test seams.** Prefer the highest existing public seam that observes user-visible behavior. Add a new seam only when no stable seam can express the acceptance criteria. Record the seam and why it is sufficient.
4. **Write the spec.** Use [the spec template](references/spec-template.md). Keep requirements behavioral; avoid file paths, line numbers, and speculative code unless a short type or state-machine shape is itself an approved contract.
5. **Audit the draft.** Every acceptance criterion must trace to a stated requirement. Every material constraint must have an observable verification path. Mark contradictions and unknowns explicitly.
6. **Persist if authorized.** For a named file, record its current identity/content fingerprint, check the planning lease, apply only the spec change without overwriting unrelated edits, then read back the file. Stop if the file changed between inspection and write. For tracker publication, choose a stable non-secret key: prefer the source issue identifier, otherwise use a normalized approved title. Include `<!-- to-spec:v1 key=<key> -->` in the issue body. Search for that marker before create: reuse exactly one match and stop on duplicates. After create or update, read back the marker, body, source links, and planning state. Preserve links to the conversation or source issue and leave implementation decomposition to `to-tickets`. Never retry an unknown file, create, or update result until readback classifies it as present exactly once or absent.

## Completion check

The result is complete when it distinguishes decisions, assumptions, and unknowns; defines current and desired behavior; names verification seams; includes measurable acceptance criteria and exclusions; and cannot be mistaken for a claimable implementation issue.
