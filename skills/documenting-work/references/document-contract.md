# Fallback development-document contract

Use this contract only when the consuming repository has no applicable documentation convention. Repository instructions and established indexes override it.

## Authority matrix

| Kind | Default persistence | Repository fallback when durability is requested |
| --- | --- | --- |
| Product or engineering spec | Tracker when the project manages PRDs as issues; otherwise repository | `docs/specs/<name>.md` |
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

- issue-linked: `issue-<number>-<slug>.md`;
- not issue-linked: `YYYY-MM-DD-<slug>.md` using the creation date in UTC;
- lowercase Unicode slug, normalized with NFKC, punctuation collapsed to `-`, maximum 80 characters, with the complete filename shortened at a UTF-8 boundary to at most 240 bytes;
- stable path for updates to the same `document_id`; do not rename merely because the title wording changes.

The fallback directories are:

```text
docs/
  README.md
  specs/
  decisions/
  research/
  reports/
    diagnostics/
    reviews/
```

Create only the directories needed by the selected document. Do not pre-create the whole tree.

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

## Fallback index

Use `docs/README.md` as the document map when no other index exists. Create or update one section per kind with:

```markdown
## Specs

- [Payment retry policy](specs/issue-42-payment-retry-policy.md) — draft; source #42
```

Keep one row per `document_id`. Update status and title in place. Do not delete superseded entries; label them and link to the replacement. Sort active documents by title unless the repository already uses chronological ordering.

## Update and supersession

- **Update:** same knowledge and identity; edit the existing path and `updated` date.
- **Supersede:** a new authority or incompatible decision replaces the old meaning; create a new ID, mark the old document `superseded`, and add reciprocal links.
- **Archive:** still authoritative history but no longer active; retain the path unless repository policy says otherwise.
- **Delete:** only duplicates, accidental generated output, or material covered by an explicit retention decision, and only with explicit destructive authorization.

Before create or rename, search for the intended ID, source issue, title concept, and index entry. A matching concept with a different ID requires reconciliation, not another file.
