---
name: documenting-work
description: Resolve the authority, durability, location, name, metadata, index, and lifecycle of development documents and controlled document sets or derived representations. Use when Codex or another skill is about to create, save, or publish a spec, non-normative spec explainer, decision map, local-work set, domain model, decision, research note, diagnosis, code-review report, handoff, or evidence artifact, especially when the repository does not state where that document belongs.
---

# Documenting development work

Give every document one authoritative home. Persist only information that must outlive the conversation; use pointers instead of maintaining the same content in GitHub, Markdown, and generated artifacts.

## 1. Classify the persistence tier

Choose one tier before writing:

- **Conversation:** analysis, draft, diagnosis, or review needed only for the current interaction. Return it in the response; create no file.
- **Tracker:** issue brief, ticket graph, implementation evidence, or issue-backed handoff whose lifecycle is owned by GitHub. Store it in the issue, PR, comment, or native relationship.
- **Repository:** approved knowledge or local coordination state that must be reviewed and versioned with the code, such as a domain model, spec, decision map, local-work set, decision, durable research result, or explicitly controlled derivative.
- **Artifact store:** generated logs, traces, screenshots, benchmark output, or run evidence. Use the repository's artifact system and retention policy; do not turn raw output into product documentation.

A request to inspect, explain, review, or draft selects `Conversation` unless the user or repository contract requests persistence. A request to save, record, publish, or create a named repository document authorizes that document plus locally required index entries and in-repository reciprocal links. Tracker comments, issue edits, and other external pointers require separate mutation authorization.

## 2. Resolve the repository contract

Apply this precedence:

1. consuming-repository safety, ownership, and documentation instructions;
2. an explicit user destination that is compatible with those instructions;
3. an existing same-kind convention and index in the repository;
4. the fallback contract in [references/document-contract.md](references/document-contract.md).

Inspect repository instructions, documentation roots and indexes, issue-tracker configuration, neighboring documents, and ignore rules. Do not infer a standard from one stray file. If two live conventions conflict, report the conflict and remain at `Conversation` until authority is resolved.

## 3. Declare one authority

Name the authority as `conversation`, `tracker`, `repository`, or `artifact`. A pointer representation contains only a title, status, authoritative link/path, and enough context to follow it. Never copy the full authoritative body into a second system “for convenience.”

Two bundled controlled projections are permitted:

- A spec explainer is separately loadable, declares `kind: "spec-explainer"` and `normative: false`, identifies the authoritative spec with `derived_from`, binds to its exact body with `source_fingerprint`, and adds no normative meaning. It is never an implementation, ticket, test, or review authority.
- A local-work set declares `kind: "local-work"` or `local-work-item`, `normative: false`, one `derived_from` repository spec, and the exact `source_fingerprint`. It may control execution order, writable scope, progress, and evidence while behavior remains authoritative only in the spec.

A decision map is not a duplicated projection: its entry point is an index and each decision document is the sole authority for that decision. Other richer document kinds require a consuming-repository contract or an explicit contract change; do not generalize these exceptions ad hoc.

Use stable identity:

- reuse an existing `document_id` when updating the same knowledge;
- search paths, frontmatter, tracker markers, and indexes before creating;
- stop on two matches or on a path occupied by a different identity;
- create a new identity only for genuinely distinct knowledge or an explicit superseding revision.

## 4. Resolve fallback repository paths

Use the bundled resolver only after choosing `Repository` and confirming that the consuming repository has no applicable location convention:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/documenting-work/scripts/resolve_document_path.py" \
  --kind <domain|spec|spec-explainer|decision-map|local-work|decision|research|diagnosis|review> \
  --title "<title>" [--issue <number>] [--date YYYY-MM-DD] [--root <repo>] \
  [--source-document-id "spec:<source-key>:<slug>"]
```

The command returns the stable document ID, relative path, and fallback index. For `domain`, it returns the project-wide identity `domain:project` and `docs/domain.md`; omit `--issue`. It does not create files or override an established convention. Read the fallback matrix and metadata contract before writing.
Add `decision-map` or `local-work` to `--kind` for those collection entry points. For `spec-explainer` and `local-work`, `--source-document-id` is required; the resolver derives their identity and path from that spec ID rather than their title. For `decision-map`, it returns a stable collection directory with `map.md` as the entry point.

## 5. Persist safely

1. Confirm persistence and external-write authorization.
2. For tracker comments, external pointers, or other shared external writes, have `work-github-issue` acquire the appropriate `planning` or `implementation` lease. An authorized repository-document edit uses the local destination fingerprint and dirty-worktree checks without requiring GitHub; when an implementation lease is already active, continue to respect it.
3. Record the destination's identity, content fingerprint, index entry, and Git status before editing.
4. Create or update one authoritative document, one contract-defined document set, or its contract-authorized derived representation. Within a set, keep each body authoritative for only its declared role and use the entry point as an index. Preserve unrelated edits and repository formatting.
5. Add or update the nearest authoritative index. When the fallback contract is active, use `docs/README.md`.
6. Put pointers—not duplicated bodies—in the source issue, parent spec, superseded document, or report as required.
7. Read back the document, metadata, links, and index. Recheck any applicable external lease and the working-tree fingerprint around consequential writes.

An unknown write result is unresolved. Reconcile identity, content, and index state before retrying or releasing the lease.

## 6. Maintain the lifecycle

Use only states defined by the selected document contract. The fallback uses ordinary `draft|active|completed|stale|superseded|archived` states, adds `blocked|ready-for-spec` for a decision-map entry point, `open|resolved|out-of-scope` for its decision children, and `pending|in-progress|completed|blocked` for local-work items. Update `updated` whenever meaning or controlled state changes. When replacing a non-fixed document, mark the old one `superseded`, link both directions, and keep the old decision readable. For a fixed living document such as the fallback `domain:project`, follow its in-place lifecycle exception in the fallback contract. Never update a spec explainer independently: regenerate it from the exact authoritative spec readback, or report it stale when its fingerprint differs. Mark a local-work set stale on source fingerprint drift and reconcile or regenerate it before execution; never silently rebind its items. Update a decision map and its decision documents in place according to their separate index/detail roles; a resolved decision's `map_projection: pending` is a durable incomplete-update signal. Archive only under repository lifecycle and retention policy. Deleting an existing document additionally requires explicit destructive authorization, even when retention policy permits deletion.

## Completion check

Report:

- document kind and persistence tier;
- authoritative path or tracker/artifact pointer;
- stable document ID and status when repository-backed;
- source and supersession links;
- derived representation, source fingerprint match, and normative status when one exists;
- index updated or the repository rule that makes an index unnecessary;
- readback, collision, authorization, and lease result.

Completion requires exactly one authoritative body for each meaning or declared set role, no unresolved identity collision, no derived representation that can be mistaken for product authority, and no unrequested document or artifact.
