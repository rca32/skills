---
name: to-spec
description: "Synthesize settled decisions into two separate outputs: a compact authoritative product or engineering spec for decomposition, implementation, testing, and review, plus a short plain-language explainer that is fingerprint-bound to the spec and cannot affect development. Use when the user explicitly asks for a spec or PRD from existing discussion without another discovery interview; publish only when explicitly requested."
---

# Conversation to spec

Produce one precise development authority and one separately loadable human explanation. Optimize the spec for compactness, traceability, and unambiguous execution; optimize the explainer for quick understanding. Never let the explainer become a second source of requirements.

## Authority and boundaries

- Preserve consuming-repository safety, ownership, documentation, and architecture instructions. Within those boundaries, explicit user product decisions govern the requested outcome, followed by accepted domain and architecture records.
- Separate confirmed decisions from assumptions and unresolved questions. If product decisions conflict with repository safety or accepted architecture, preserve both claims and keep the spec draft or blocked; never choose silently.
- Do not reopen discovery or interview the user during this workflow. Record a material unknown in the authoritative spec and make decomposition readiness conditional.
- When the effort is too large or foggy to state its route-defining questions and settled decisions, stop and recommend `decision-map`; consume its resolved decision documents only after that map is `ready-for-spec`.
- Resolve the output language from repository instructions, then the user's request, and otherwise use Korean. Preserve quoted sources, identifiers, API names, links, and protocol markers exactly.
- Treat only the spec as normative. The explainer must declare `kind: "spec-explainer"`, `normative: false`, `derived_from`, and `source_fingerprint`; it cannot be an input to `to-tickets`, `tdd`, or the Spec axis of `code-review`.
- Apply the plain-language invariant directly: preserve meaning and important details while adding no fact, requirement, advice, decision, or interpretation. Do not invoke `bro`, whose contract covers the last message rather than a source document.
- Use `documenting-work` to resolve persistence tier, path, identity, metadata, index, and lifecycle for both outputs. Keep exactly one normative body even when the explainer is durable.
- A request to draft returns two independently addressable conversation artifacts and creates no file. When the host cannot create separate response artifacts, return two canonical length-delimited envelopes with distinct IDs; only the complete spec envelope may be copied into a development handoff. An explicit request to persist a repository spec includes its declared paired explainer and locally required index or reciprocal links unless the user or repository forbids derived documents. Tracker publication, comments, and other external writes still require their own authorization.
- A published tracker spec is a planning or parent item, not an implementation ticket. Never add the `ready-for-agent` role. Use the selected tracker contract for state and Human action fields.
- Let `work-github-issue` own planning leases. Before tracker or other shared external writes, acquire a `planning` lease keyed to the source issue or key `0` when none exists. If unavailable, keep publication in the response.

## Process

1. **Collect settled input.** Extract the problem, desired outcome, constraints, safety boundaries, exclusions, decisions, and unresolved choices from the conversation and named authorities.
2. **Inspect current reality.** Read product synthesis, authoritative domain vocabulary, accepted architecture decisions, and relevant public interfaces. Verify claims that may have drifted.
3. **Resolve active design pressure.** Reuse accepted domain vocabulary without invoking `domain-modeling`. When domain meaning would materially change specified behavior, return the pressure to `domain-modeling`; resume only from an established model or an explicitly unresolved choice. Use `codebase-design` when a new module interface or architectural seam remains unsettled. Keep decomposition conditional while either decision is unresolved.
4. **Write the authoritative spec.** Read [the spec template](references/spec-template.md). Use stable IDs, direct behavioral statements, references instead of repeated prose, and only the detail needed for decomposition, implementation, testing, and review. Do not optimize this body as an onboarding narrative.
5. **Audit the spec.** Trace every acceptance criterion to a requirement, every material constraint to an authority, and every requirement to an observable verification path. Remove repeated background and empty sections. The spec must stand alone without its explainer.
6. **Probe explainability.** Read [the explainer template](references/spec-explainer-template.md) after the spec audit. Use only its prose rules to render a disposable candidate without metadata, identity, or fingerprint. Add nothing to make the explanation flow: if the probe exposes a gap, update and re-audit the spec, then discard the probe. Do not persist or hand off the probe.
7. **Finalize by persistence branch.** Freeze the exact final authority body with `python3 "${CODEX_HOME:-$HOME/.codex}/skills/to-spec/scripts/fingerprint_spec.py" -`: pass exact in-memory bytes on stdin for conversation and tracker branches, and replace `-` with the readback file path only for a repository branch. Then regenerate the explainer from scratch from that frozen body. Explain why the change exists, what changes, the shortest meaningful flow, exclusions, and material unresolved questions. Omit implementation contracts, verification mechanics, protocol metadata, and repeated detail unless a human needs them to understand the outcome. Reconcile every write before retrying.

## Persistence branches

### Conversation

Assign a response-scoped lowercase ASCII key using only letters, digits, `.`, `_`, or `-`, then freeze the exact audited spec body. The body begins at its title and ends at its last normative section; artifact labels, IDs, fingerprints, envelopes, and reporting text are outside the hashed bytes. Fingerprint that body, then produce:

- `conversation-spec:<key>`: a canonical spec artifact containing only the frozen normative body;
- `conversation-spec-explainer:<key>`: a separate artifact with `authority: "conversation"`, `derived_from: "conversation-spec:<key>"`, and the matching fingerprint.

Use host-level response artifacts when available. Otherwise pass each exact in-memory content body on stdin to `python3 "${CODEX_HOME:-$HOME/.codex}/skills/to-spec/scripts/envelope_artifact.py" encode --id <artifact-id>`; the omitted path selects stdin and creates no file. Never calculate or transcribe `content_bytes` manually. The script emits this canonical envelope, where `content_bytes` is the UTF-8 byte length of the exact content following the `---CONTENT---` newline:

```text
---BEGIN CODEX CONVERSATION ARTIFACT---
id: <exact artifact ID>
content_bytes: <decimal byte count>
---CONTENT---
<read exactly content_bytes bytes>
---END CODEX CONVERSATION ARTIFACT---
```

The byte count, not the end marker, determines the content boundary, so marker-like content is harmless. Use the same installed script with `validate` or `extract` on a copied envelope; stop on any mismatch or trailing data. State that downstream work must extract and load only the `conversation-spec:<key>` envelope. A response-scoped ID is not a durable locator: when the handoff crosses a response or session and no host artifact locator exists, copy the complete exact spec envelope together with its ID. Do not call the whole response a spec, and do not include either artifact inside the other. Create no file.

### Repository-authoritative spec

1. Resolve both destinations through `documenting-work`; under the fallback use `docs/specs/<name>.md` and `docs/spec-explainers/<name>.md`.
2. Record both destination fingerprints, identities, index entries, and Git status before editing. Stop on collisions or changing in-scope files.
3. Write and read back the spec first. Compute `source_fingerprint` from that exact readback.
4. Generate the explainer from the readback, write its required derived metadata and warning, then read back both files and the index. Never copy the full spec body into the explainer.
5. If the spec write succeeds but the explainer write is missing, stale, or unknown, preserve the authoritative spec, report `explainer-pending`, and reconcile the explainer identity before retrying. Do not roll back or weaken the spec to make the pair look complete.

### Tracker-authoritative spec

Publish and read back the normative spec only under the authorized planning lease. Compute the fingerprint from the exact issue-body bytes returned by readback, including stable markers and planning fields but excluding provider chrome. Return the derived explainer as a conversation artifact by default, with `authority: "conversation"` and `derived_from` set to the stable tracker identity; do not add it to the issue body or a comment, because implementation workflows load that surface. Persist it to a repository only under separate authorization and the resolved `documenting-work` contract.

For tracker publication, choose a stable non-secret key, keep the stable `<!-- to-spec:v1 key=<key> -->` marker, search before create, and reuse exactly one match. After a create or update, read back the marker, body, source links, planning state, and Human action block. Never duplicate the normative body across tracker and repository. Reconcile an ambiguous create with exactly three complete marker/catalog reads over no more than 60 seconds and require the final two reads to agree. If the marker is absent, no provider request remains pending, and absence is stable, retry once with the same marker. If the retry is unknown or uniqueness cannot be established, preserve the recovery key, stop writes, and stop renewing the planning lease indefinitely so a later takeover can reconcile it.

## Completion check

Report the normative authority and identity, spec fingerprint, explainer location or conversation status, and persistence/readback results. Completion requires:

- a compact spec that independently distinguishes decisions, assumptions, unknowns, requirements, verification, and exclusions;
- a separate explainer whose `derived_from` and `source_fingerprint` match that exact spec revision;
- no explainer statement that adds or changes normative meaning;
- no development handoff that names the explainer as its source;
- no unresolved identity, authorization, collision, lease, or write result.

For a repository-authoritative spec, name the next execution path without starting it: `local-work` for sequential low-overhead local implementation, or `to-tickets` when shared GitHub tracking, claims, dependencies, or remote handoff are required.
