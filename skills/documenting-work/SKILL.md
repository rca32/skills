---
name: documenting-work
description: Resolve the authority, durability, location, name, metadata, index, and lifecycle of development documents. Use when Codex or another skill is about to create, save, or publish a spec, decision, research note, diagnosis, code-review report, handoff, or evidence artifact, especially when the repository does not state where that document belongs.
---

# Documenting development work

Give every document one authoritative home. Persist only information that must outlive the conversation; use pointers instead of maintaining the same content in GitHub, Markdown, and generated artifacts.

## 1. Classify the persistence tier

Choose one tier before writing:

- **Conversation:** analysis, draft, diagnosis, or review needed only for the current interaction. Return it in the response; create no file.
- **Tracker:** issue brief, ticket graph, implementation evidence, or issue-backed handoff whose lifecycle is owned by GitHub. Store it in the issue, PR, comment, or native relationship.
- **Repository:** approved knowledge that must be reviewed and versioned with the code, such as a spec, decision, or durable research result.
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

Name the authority as `conversation`, `tracker`, `repository`, or `artifact`. A non-authoritative representation contains only a title, status, authoritative link/path, and enough context to follow it. Never copy the full body into a second system “for convenience.”

Use stable identity:

- reuse an existing `document_id` when updating the same knowledge;
- search paths, frontmatter, tracker markers, and indexes before creating;
- stop on two matches or on a path occupied by a different identity;
- create a new identity only for genuinely distinct knowledge or an explicit superseding revision.

## 4. Resolve fallback repository paths

Use the bundled resolver only after choosing `Repository` and confirming that the consuming repository has no applicable location convention:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/documenting-work/scripts/resolve_document_path.py" \
  --kind <spec|decision|research|diagnosis|review> \
  --title "<title>" [--issue <number>] [--date YYYY-MM-DD] [--root <repo>]
```

The command returns the stable document ID, relative path, and fallback index. It does not create files or override an established convention. Read the fallback matrix and metadata contract before writing.

## 5. Persist safely

1. Confirm persistence and external-write authorization.
2. For tracker comments, external pointers, or other shared external writes, have `work-github-issue` acquire the appropriate `planning` or `implementation` lease. An authorized repository-document edit uses the local destination fingerprint and dirty-worktree checks without requiring GitHub; when an implementation lease is already active, continue to respect it.
3. Record the destination's identity, content fingerprint, index entry, and Git status before editing.
4. Create or update one authoritative document. Preserve unrelated edits and repository formatting.
5. Add or update the nearest authoritative index. When the fallback contract is active, use `docs/README.md`.
6. Put pointers—not duplicated bodies—in the source issue, parent spec, superseded document, or report as required.
7. Read back the document, metadata, links, and index. Recheck any applicable external lease and the working-tree fingerprint around consequential writes.

An unknown write result is unresolved. Reconcile identity, content, and index state before retrying or releasing the lease.

## 6. Maintain the lifecycle

Use `draft`, `active`, `superseded`, or `archived` unless the consuming repository defines another vocabulary. Update `updated` whenever meaning changes. When replacing a document, mark the old one `superseded`, link both directions, and keep the old decision readable. Archive only under repository lifecycle and retention policy. Deleting an existing document additionally requires explicit destructive authorization, even when retention policy permits deletion.

## Completion check

Report:

- document kind and persistence tier;
- authoritative path or tracker/artifact pointer;
- stable document ID and status when repository-backed;
- source and supersession links;
- index updated or the repository rule that makes an index unnecessary;
- readback, collision, authorization, and lease result.

Completion requires exactly one authoritative body, no unresolved identity collision, and no unrequested document or artifact.
