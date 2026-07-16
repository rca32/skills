---
name: triage
description: Triage incoming GitHub issues and external pull requests by verifying claims, classifying category and readiness, and writing durable briefs. Use when the user asks to inspect, categorize, verify, or move unready tracker work; do not use to claim or implement an already-ready issue.
---

# Issue triage

Turn an unready issue or external pull request into a verified tracker outcome. Triage owns intake, verification, briefing, and authorized readiness-state preparation. `work-github-issue` supplies the tracker contract and later revalidates readiness and dependencies before it owns leases, implementation evidence, completion, and handoff.

## Establish the tracker contract

1. Read repository instructions and tracker documentation before interpreting labels or mutating the tracker.
2. If the repository has no contract, use the contract exposed by `work-github-issue` when it is installed.
3. Keep category and state separate. With the default vocabulary, publish one Korean category (`유형: 버그` or `유형: 개선`) and exactly one Korean state (`상태: 분류 필요`, `상태: 정보 필요`, `상태: 에이전트 작업 가능`, `상태: 사람 검토 필요`, or `상태: 진행하지 않음`). Read `bug`/`enhancement` and the English state role keys as legacy label aliases, not additional labels. Never add both aliases for one role; conflicting recognized categories or states require maintainer direction. Repository mappings override these names.
4. Resolve the human-facing language from repository instructions, then the user's request, and otherwise use Korean. Under the fallback contract, write titles, briefs, questions, and tracker comments in clear Korean while preserving quoted reporter text, code identifiers, machine markers, and links.
5. Do not acquire an implementation lease during triage. If a requested verification would change code or shared artifacts, stop at a reproducible verification plan or route the work through `work-github-issue` first.
6. Treat the issue or pull request as the authoritative home of its agent brief. Use `documenting-work` only when repository policy requires a durable decision document or a pointer; never copy the full brief into a second file.

When the user asks only for an assessment, remain read-only. Apply labels, comments, closure, or other tracker changes only when that mutation is explicitly requested or approved. Before the first authorized mutation, have `work-github-issue` acquire a `planning` lease keyed to this issue. Check that lease before each mutation batch and release it only after labels, comments, state, and closure have been read back from the tracker with no unknown result.

Before applying a label, read the repository label catalog and confirm the selected category and state labels already exist with the expected meaning. Ordinary triage mutation authority does not include repository-wide label creation; if setup is missing, report the exact labels and descriptions required unless label creation was separately authorized.

## Find work needing attention

List these buckets oldest first:

1. unlabeled incoming work;
2. `needs-triage` role work (`상태: 분류 필요` in the fallback);
3. `needs-info` role work (`상태: 정보 필요`) with new reporter activity.

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

- `ready-for-agent` (`상태: 에이전트 작업 가능`): require a complete brief using [the agent brief contract](references/agent-brief.md). Every acceptance criterion must be independently observable and blockers must already be represented by the tracker contract.
- `ready-for-human` (`상태: 사람 검토 필요`): use the same brief and fill the selected tracker contract's Human action block with the request type, exact target, and judgment, permission, access, merge, or manual action that prevents autonomous work. Name where the person responds, the observable completion condition and durable evidence reference, which state follows, and the authorized transition owner.
- `needs-info` (`상태: 정보 필요`): preserve established facts and ask only concrete, answerable questions about an exact target in the Human action block. The person records the answer without editing labels. After a reply, revalidate the brief and blockers before recommending or applying `상태: 에이전트 작업 가능`.
- `wontfix` (`상태: 진행하지 않음`): state whether the request is already implemented, a duplicate, or rejected. Follow repository policy for durable rejected-decision records; if none exists and a durable enhancement rejection is required, resolve one `decision` document through `documenting-work` and link it from the issue.
- `needs-triage` (`상태: 분류 필요`): preserve the partial evidence and the next decision required.

Never mark an item ready merely because the user requested that label. If the brief or verification is incomplete, explain the missing readiness evidence and use the appropriate non-ready state unless the repository contract provides an explicit override mechanism.

## Completion check

Triage is complete when:

- the evidence and search scope are recorded;
- category and state do not conflict;
- any ready item has a durable brief and validated blockers;
- any human-wait item tells the person exactly why, the request type and target, what to do, where to respond, what completion looks like, which state follows, and which skill owns that transition;
- tracker mutations match the user's authorization;
- no implementation lease, code commit, push, or completion evidence was created by this skill.
