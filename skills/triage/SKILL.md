---
name: triage
description: Triage incoming GitHub issues and external pull requests by verifying claims, classifying category and readiness, and writing durable briefs. Use when the user asks to inspect, categorize, verify, or move unready tracker work; do not use to claim or implement an already-ready issue.
---

# Issue triage

Turn an unready issue or external pull request into a verified tracker outcome. Triage owns intake, verification, briefing, and authorized readiness-state preparation. `work-github-issue` supplies the tracker contract and later revalidates readiness and dependencies before it owns leases, implementation evidence, completion, and handoff.

## Establish the tracker contract

1. Read repository instructions and tracker documentation before interpreting labels or mutating the tracker.
2. If the repository has no contract, use the contract exposed by `work-github-issue` when it is installed.
3. Keep category and state separate. With the default vocabulary, use exactly one category (`bug` or `enhancement`) and exactly one state (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, or `wontfix`). Repository mappings override these names.
4. Do not acquire an implementation lease during triage. If a requested verification would change code or shared artifacts, stop at a reproducible verification plan or route the work through `work-github-issue` first.
5. Treat the issue or pull request as the authoritative home of its agent brief. Use `documenting-work` only when repository policy requires a durable decision document or a pointer; never copy the full brief into a second file.

When the user asks only for an assessment, remain read-only. Apply labels, comments, closure, or other tracker changes only when that mutation is explicitly requested or approved. Before the first authorized mutation, have `work-github-issue` acquire a `planning` lease keyed to this issue. Check that lease before each mutation batch and release it only after labels, comments, state, and closure have been read back from the tracker with no unknown result.

## Find work needing attention

List these buckets oldest first:

1. unlabeled incoming work;
2. `needs-triage` work;
3. `needs-info` work with new reporter activity.

Show counts, type (`issue` or `PR`), identifier, and a one-line reason each item needs attention. Follow repository rules for excluding collaborator-owned or automated pull requests.

## Triage one item

### 1. Gather context

Read the body, comments, labels, relationships, author, and dates. For a pull request, also inspect the complete diff and checks. Read relevant repository standards, domain documentation, and durable rejection decisions.

Search by domain concept for:

- an existing implementation;
- a duplicate or superseding issue;
- a prior decision that rejects or constrains the request;
- active work that may already cover it.

Record where you looked. Do not infer absence from a single keyword search.

### 2. Recommend before mutating

Report the proposed category and state, the evidence supporting them, and any conflicting labels. If state labels conflict or the requested transition is unusual, stop and request maintainer direction.

### 3. Verify the claim

- For a bug, reproduce it from the reported steps or provide the smallest repeatable observation that disproves or confirms it. Use a disposable or non-production environment by default. Real orders, payments, messages, destructive writes, or production traffic require separate explicit authorization plus rollback or reconciliation controls; otherwise delegate deeper reproduction to `diagnosing-bugs` after the correct outer lease is held.
- For an enhancement, verify the current behavior and the gap the request would close.
- For a pull request, check whether the diff does what it claims and run the narrowest relevant checks without modifying the contributor's branch.

Classify the result as `confirmed`, `not reproduced`, or `insufficient information`, and attach commands, outputs, or code paths that make the conclusion repeatable.

### 4. Build the outcome

- `ready-for-agent`: require a complete brief using [the agent brief contract](references/agent-brief.md). Every acceptance criterion must be independently observable and blockers must already be represented by the tracker contract.
- `ready-for-human`: use the same brief and state the specific judgment, access, or manual action that prevents autonomous work.
- `needs-info`: preserve established facts and ask only concrete, answerable questions.
- `wontfix`: state whether the request is already implemented, a duplicate, or rejected. Follow repository policy for durable rejected-decision records; if none exists and a durable enhancement rejection is required, resolve one `decision` document through `documenting-work` and link it from the issue.
- `needs-triage`: preserve the partial evidence and the next decision required.

Never mark an item ready merely because the user requested that label. If the brief or verification is incomplete, explain the missing readiness evidence and use the appropriate non-ready state unless the repository contract provides an explicit override mechanism.

## Completion check

Triage is complete when:

- the evidence and search scope are recorded;
- category and state do not conflict;
- any ready item has a durable brief and validated blockers;
- tracker mutations match the user's authorization;
- no implementation lease, code commit, push, or completion evidence was created by this skill.
