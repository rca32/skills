# Fallback development-document contract

Use this contract only when the consuming repository has no applicable documentation convention. Repository instructions and established indexes override it.

## Authority matrix

| Kind | Default persistence | Repository fallback when durability is requested |
| --- | --- | --- |
| Project domain model | Repository when settled domain knowledge must guide later work | `docs/domain.md` |
| Product or engineering spec | Tracker when the project manages PRDs as issues; otherwise repository | `docs/specs/<name>.md` |
| Plain-language spec explainer | Conversation by default; repository only as a fingerprint-bound derivative of a named authoritative spec | `docs/spec-explainers/<name>.md` |
| Architecture or product decision | Repository | `docs/decisions/<name>.md` |
| Durable research synthesis | Repository | `docs/research/<name>.md` |
| Bug diagnosis | Conversation; issue comment when issue-backed | `docs/reports/diagnostics/<name>.md` only when explicitly requested |
| Code review | Conversation; PR review when PR-backed | `docs/reports/reviews/<name>.md` only when explicitly requested |
| Agent brief and implementation tickets | Tracker | No duplicate local body |
| Completion evidence and issue handoff | Tracker | No duplicate local body |
| Logs, traces, screenshots, benchmarks | Artifact store | Follow repository artifact and retention rules |
| Non-issue session handoff | Conversation or configured session store | Do not commit by default |

When a tracker-backed spec also needs a repository pointer, the file contains metadata, a short summary, and the tracker URL—not the full spec. When a repository spec creates implementation tickets, each ticket links to the spec and the spec index links to the ticket parent.

## Fallback naming

Use the resolver's deterministic names:

- project domain model: fixed `docs/domain.md` with `document_id: "domain:project"`; update it in place and do not create issue- or date-named copies;
- spec explainer: require the authoritative `spec:<source-key>:<slug>` ID and derive the explainer's key, slug, path, and `document_id: "spec-explainer:<source-key>:<slug>"` from it; never derive them independently from the explainer title;
- issue-linked: `issue-<number>-<slug>.md`;
- not issue-linked: `YYYY-MM-DD-<slug>.md` using the creation date in UTC;
- lowercase Unicode slug, normalized with NFKC, punctuation collapsed to `-`, maximum 80 characters, with the complete filename shortened at a UTF-8 boundary to at most 240 bytes;
- stable path for updates to the same `document_id`; do not rename merely because the title wording changes.

The fallback directories are:

```text
docs/
  README.md
  domain.md
  specs/
  spec-explainers/
  decisions/
  research/
  reports/
    diagnostics/
    reviews/
```

Create only the directories needed by the selected document. Do not pre-create the whole tree.

Treat `docs/domain.md` as the stable project-wide glossary and model entry point, not as permission to invent or settle domain content. A modeling workflow supplies established terms, invariants, relationships, states, boundaries, and decisions; this contract only places and maintains the document. If a consuming repository splits the model by bounded context, follow its map and identities instead of forcing the fallback singleton.

## Fallback metadata

Use YAML frontmatter when the repository has no metadata convention:

```yaml
---
document_id: "spec:issue-42:payment-retry-policy"
kind: "spec"
title: "Payment retry policy"
status: "draft"
authority: "repository"
source: "https://github.com/owner/repo/issues/42"
created: "2026-07-13"
updated: "2026-07-13"
supersedes: null
---
```

Rules:

- quote string values;
- use ISO `YYYY-MM-DD` UTC dates;
- use one stable `document_id` for the document's lifetime;
- set `source` to the issue, PR, conversation artifact, or decision that caused the document;
- set `supersedes` to the replaced document ID or `null`;
- add repository-required fields without copying volatile runtime data into frontmatter.

For a non-authoritative pointer file, set `authority: "tracker"` or `"artifact"`, make `source` the authoritative URL/path, and keep the body to a concise pointer.

For a repository-backed spec explainer, use the ordinary metadata plus:

```yaml
kind: "spec-explainer"
authority: "repository"
source: "docs/specs/issue-42-payment-retry-policy.md"
derived_from: "spec:issue-42:payment-retry-policy"
source_fingerprint: "to-spec-body-v1:<sha256>"
normative: false
```

`authority` identifies where the explainer itself is versioned; `normative: false` prevents it from becoming development authority. Require `derived_from` to resolve exactly one spec and require `source_fingerprint` to match that spec's exact current body before claiming the explainer is current. Never infer requirements from the explainer, edit it independently, or preserve it as current after the spec changes.

## Fallback index

Use `docs/README.md` as the document map when no other index exists. Create or update one section per kind with:

```markdown
## Specs

- [Payment retry policy](specs/issue-42-payment-retry-policy.md) — draft; source #42
```

Keep one row per `document_id`. Update status and title in place. Do not delete superseded entries; label them and link to the replacement. Sort active documents by title unless the repository already uses chronological ordering.

Use one `Domain model` entry for `domain:project`. Update `docs/domain.md` in place as its meaning evolves; use repository history and explicit internal decision status rather than replacing the project identity with dated documents.

Index spec explainers in a separate `Spec explainers` section. Each entry links first to the explainer and names its authoritative spec; do not list an explainer under `Specs` or make it look decomposition-ready.

## Update and supersession

- **Fixed domain-model update:** keep `domain:project` and `docs/domain.md` when glossary entries, invariants, relationships, states, boundaries, or decisions change, including an incompatible change to one of those entries. Preserve the prior meaning and rationale in the document's decision history when required and rely on repository history; do not create a second authoritative domain-model body.
- **Fixed domain-model replacement:** supersede the fallback singleton only when the consuming repository adopts another authoritative domain-document convention or splits authority by bounded context. At that point the fallback no longer selects identities; follow the new convention and leave the required reciprocal pointer from `docs/domain.md` rather than inventing fallback context IDs.
- **Spec-explainer update:** retain the explainer identity while its source spec identity remains the same, but regenerate the complete explainer and replace `source_fingerprint` from the exact source readback. If the source changes and regeneration is not authorized or does not complete, report the explainer stale; never treat its old prose as current.
- **Spec-explainer supersession:** when the normative spec is superseded, supersede its explainer and generate a new explainer identity only from the replacement spec. Keep reciprocal pointers without copying either body.
- **Update:** for other documents, edit the existing path and `updated` date when knowledge and identity remain the same.
- **Supersede:** for other documents, when a new authority or incompatible decision replaces the old meaning, create a new ID, mark the old document `superseded`, and add reciprocal links.
- **Archive:** still authoritative history but no longer active; retain the path unless repository policy says otherwise.
- **Delete:** only duplicates, accidental generated output, or material covered by an explicit retention decision, and only with explicit destructive authorization.

Before create or rename, search for the intended ID, source issue, title concept, and index entry. A matching concept with a different ID requires reconciliation, not another file.
