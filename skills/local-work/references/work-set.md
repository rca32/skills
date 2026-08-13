# Local-work document set

Use these shapes only after `documenting-work` resolves repository persistence from an authoritative repository spec ID. Follow an established consuming-repository format when it differs.

## Contents

- [Work entry point](#work-entry-point)
- [Work item](#work-item)

## Work entry point

```markdown
---
document_id: "local-work:<source-key>:<slug>"
kind: "local-work"
title: "<spec title> — local work"
status: "draft"
authority: "repository"
normative: false
derived_from: "spec:<source-key>:<slug>"
source: "<authoritative spec path>"
source_fingerprint: "to-spec-body-v1:<sha256>"
fixed_point: "<HEAD OID>"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---

# <Spec title> — local work

> This set controls local execution order and progress only.
> Product behavior comes from `derived_from`, never from these files.

## Current

- [W001 — <work item>](items/W001-<slug>.md) — pending

## Remaining

- [W002 — <work item>](items/W002-<slug>.md) — pending

## Completed

- <none>

## Blocked

- <none>

## Source coverage

- REQ-001, AC-001 → W001

## Final convergence

- Implementation candidate: <HEAD plus implementation tracked-diff and implementation-scope untracked fingerprints>
- Excluded coordination paths: <this local-work document set and index-only projections>
- Coordination checkpoint: <completed item states and final block read back; no recursive self-fingerprint>
- Source identity: <derived_from and source_fingerprint>
- Verification: `<command>` — <outcome>
- Standards review: <review mode, reviewer identity, authority identity, candidate identity, finding counts>
- Spec review: <review mode, reviewer identity, authority identity, candidate identity, finding counts>
- Review-mode disclosure: <isolated reviewers, or separated single-context fallback>
- Carried forward: <axis, prior clean candidate, and unchanged-context rationale; otherwise none>
```

Keep item detail out of `work.md`. During item execution, update links and one-line status only. Populate `Final convergence` only after all items complete; keep it bounded to identities, excluded paths, commands, outcomes, provenance, counts, and carry-forward rationale rather than review prose or raw logs. The implementation candidate excludes this document set and index-only projections, so the final evidence write cannot invalidate or recursively fingerprint itself; validate those coordination files by schema and readback instead.

## Work item

```markdown
---
document_id: "local-work-item:<source-key>:<spec-slug>:W001"
kind: "local-work-item"
title: "<observable outcome>"
status: "pending"
normative: false
work: "local-work:<source-key>:<slug>"
derived_from: "spec:<source-key>:<slug>"
source_fingerprint: "to-spec-body-v1:<sha256>"
predecessors: []
requirements: ["REQ-001"]
acceptance: ["AC-001"]
updated: "YYYY-MM-DD"
---

# <Observable outcome>

## Outcome and seam

<Short execution outcome and the public seam where the source spec verifies it.>

## Writable scope

- <path or component allowed for this item>

## Excluded scope

- <nearby work intentionally excluded>

## Verification

- <focused command or evidence class>

## Evidence

- <command> — <pass, fail, or blocked summary>

## Blocker

<Exact missing requirement, decision, authority, or failing condition; empty unless blocked.>
```

Items reference source IDs instead of copying requirement prose. The ordinary lifecycle is `pending → in-progress → completed|blocked`; preflight overlap may also transition `pending → blocked` before any code edit. A blocked item returns to `pending` only after its named resume condition is satisfied and read back.
