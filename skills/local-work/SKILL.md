---
name: local-work
description: "Decompose an authoritative repository spec into small local work documents and implement them sequentially in the current worktree without GitHub issues, leases, per-item branches, or worktrees. Use when the user explicitly chooses the low-overhead local path for one agent or session chain; support plan-only, implement, resume, and finish requests. Do not use when shared tracker visibility, concurrent claims, remote handoff, or issue-backed evidence is required."
---

# Local work

Use local files as a lightweight execution queue. Keep the repository spec as the only behavior authority; local work documents control scope, order, progress, and concise evidence without becoming requirements.

## Authority and selection

- Accept one current repository-authoritative spec whose exact status means approved for implementation under the consuming repository contract and whose material open questions block no referenced requirement, item boundary, seam, or acceptance criterion. Under the bundled `to-spec` vocabulary, require `상태: 승인됨`; `초안` and `미해결 질문으로 차단됨` are not executable. If approval or open-question impact is absent or ambiguous, create nothing and return `status=planning-blocked`, the exact missing approval or decision, `mutations=none`, and `resume_condition=approved-authoritative-spec-read`. On resume, accept a local-work entry point only to resolve and revalidate that source. Reject an explainer, another non-normative projection, a conversation-only artifact, or an unresolved source identity as the behavior source. If `derived_from` resolves exactly once, restart from that spec; otherwise create nothing and return `status=non-normative-source`, the candidate and source identities, `mutations=none`, and `resume_condition=authoritative-repository-spec-read`.
- Bind the work set to the exact complete spec-file fingerprint. If that file changes, mark the work set `stale` and stop before further code edits; regenerate or explicitly reconcile it from the new spec.
- Use `documenting-work` for the work-set identity, fallback path, index, and lifecycle. Under its fallback, use `docs/local-work/<spec-name>/work.md` and `items/WNNN-<slug>.md`.
- Treat `work.md` as an index and each item as a non-normative execution projection. Items may name source requirement and acceptance IDs, writable scope, order, and verification seam, but must not invent or restate product behavior as a new authority.
- Use `tdd` for each already-defined behavior change, `diagnosing-bugs` before fixing an unexplained failure, `codebase-design` for an unresolved material seam, and `code-review` for the final pinned change. Return requirement or domain uncertainty to `to-spec` or `decision-map`.
- If implementation is already issue-backed or its evidence must update a tracker, create nothing and return `status=issue-backed-route`, the issue/spec identity, `mutations=none`, `next_workflow=work-github-issue`, and `resume_condition=issue-readiness-revalidated`; do not create a second local execution lifecycle even for one agent.
- Do not create or mutate GitHub issues, acquire leases, create per-item branches or worktrees, commit, push, open a PR, merge, or publish evidence.

A request to explain, inspect, or draft is read-only. A request to create or plan local work authorizes only the work-set documents and index. A request to implement, resume, continue, or finish with `local-work` authorizes the in-scope code and test changes plus work-set updates. It does not authorize commit, push, publication, destructive cleanup, or unrelated fixes.

## Prepare the work set

1. Read repository instructions, the exact spec file, accepted domain and architecture decisions, the relevant public seams, and current Git status.
2. Compute the source fingerprint with the installed `to-spec` fingerprint script against the exact spec readback. Record the initial `HEAD`, staged/unstaged/untracked paths, and fingerprints for proposed work-set destinations.
3. Pass the decomposition gate. Stop with `planning-blocked` when any item would require a new product behavior, domain meaning, public interface, architecture, dependency, safety policy, or acceptance decision. Name the authority and smallest decision needed.
4. Read [the work-set templates](references/work-set.md). Resolve the `local-work` collection from the source spec ID through `documenting-work`, then create `work.md` and the smallest ordered set of vertical items.
5. Give every item one observable outcome, source `REQ-*` and `AC-*` references, writable and excluded scope, public verification seam, and predecessors. Keep shared setup inside the first item that uses it; do not create horizontal layer tickets or a separate cleanup item.
6. Validate that every source requirement is covered, every item ends in an independently observable green state, predecessors are acyclic, and no item relies on an explainer. Read back the work set and index, then change `work.md` from `draft` to `active` only after all checks pass.

Plan-only completion requires a matching source identity and fingerprint, complete source-to-item traceability, one initial ready item, no unresolved decomposition decision, and no code change.

If the installed `to-spec` fingerprint script or `documenting-work` resolver is unavailable, create nothing and return `status=missing-local-work-prerequisite` with the missing public-catalog skill and `resume_condition=prerequisite-installed`; never substitute an ad hoc fingerprint or path.

## Execute one item

1. Re-read `work.md`, select the first `pending` item whose predecessors are `completed`, and load only that item, its referenced spec sections, named decisions, nearby implementation, and relevant tests. Do not load every item body.
2. Recompute the spec fingerprint and compare the current `HEAD`, Git status, work-set files, and intended writable paths with the last checkpoint. Preserve unrelated user changes. On source drift, write `stale` only when the work-set and index destinations match the last checkpoint and are explicitly owned; preserve all item states and evidence, then return `status=source-drift` with both fingerprints and `resume_condition=work-set-reconciled`. If that checkpoint write is unsafe, leave every document untouched and also return `checkpoint_write=unsafe`. On overlapping ownership or another unexplained in-scope change, make no code change; when the work documents remain safe to edit, mark the selected item `blocked` with that path and return `status=preflight-blocked`, otherwise leave it `pending` and return the same status plus `checkpoint_write=unsafe`. Resume only from an unchanged, explicitly owned path set.
3. Mark the item `in-progress` only after preflight succeeds and read back the state. If resuming an existing `in-progress` item, reconcile its current diff and evidence before deciding whether to continue, complete, or mark it blocked.
4. Invoke `tdd` for the item's referenced behavior through its public seam. Keep changes within the declared writable scope; expand scope only when the spec requires it and record the reason before editing the new path.
5. Run the focused and risk-appropriate surrounding verification. Record only commands, outcomes, and durable evidence pointers in the item; do not paste raw logs.
6. Mark the item `completed` only when its source acceptance IDs are satisfied and the worktree readback matches the recorded result. Otherwise mark it `blocked` with the exact requirement, decision, failure, or authority needed.
7. Update only status and one-line progress in `work.md`, read back both files, and checkpoint the new Git status. Do not commit between items.

If code or tests change but an item or index checkpoint cannot be read back, preserve the code state, report `checkpoint-unknown`, and reconcile the exact diff and work files before another implementation attempt. Do not repeat code edits merely to retry a document update.

Process one item by default. When the user asks to continue or finish, repeat sequentially while each item reaches a terminal checkpoint and no stop condition appears.

## Final convergence

After all items are `completed`:

1. Run the repository's full risk-appropriate verification from the work-set fixed point.
2. Invoke `code-review` on the complete implementation candidate with the original fixed point and exact source spec as Spec authority. Define that candidate as all in-scope implementation, test, and product-document changes while excluding this non-normative local-work document set and its index-only projections. Still Standards-check the work-set documents in their pre-completion form. Keep Standards and Spec reviews separate.
3. Repair authorized findings through the appropriate inner workflow, rerun affected verification, and obtain a fresh review for changed axes.
4. Mark `work.md` `completed` only when verification passes, both final review axes have current provenance, and no blocker or high finding remains. Preserve medium findings that affect safety, ownership, or predictable completion as blockers.

Before completion, write and read back the bounded `Final convergence` block from the work-set template: final implementation candidate identity, the explicitly excluded coordination paths, verification commands and outcomes, separate Standards and Spec review provenance, review mode, authority identities, finding counts, and any carried-forward rationale. Prefer isolated reviewers; when unavailable, use the `code-review` separated single-context fallback and disclose that mode without calling it independent or fresh. Treat this bounded projection and the final `work.md` status change as a post-review coordination checkpoint, not as part of the candidate fingerprint that it records; validate its schema and readback without recursively hashing it into itself. If `HEAD`, implementation tracked diffs, implementation-scope untracked files, source identity, or source fingerprint no longer match that record, implementation evidence is stale and affected verification/review must run again. Later changes to excluded coordination paths require checkpoint reconciliation and readback, but invalidate implementation review only when they change the source identity, candidate scope, or recorded implementation evidence.

Return the source spec and fingerprint, work-set path, completed and blocked items, changed paths, verification and review summaries, and remaining publication action. Completion requires no unresolved `checkpoint-unknown`, source drift, overlapping ownership, or final review blocker. It does not imply commit or push; those occur once, later, only on explicit request.
