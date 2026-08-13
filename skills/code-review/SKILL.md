---
name: code-review
description: "Review a branch, pull request, commit range, or work-in-progress change from a caller-supplied fixed point along separate repository Standards and originating Spec axes. Use when asked to review changes, re-review a corrected candidate, review since a ref, compare work to an issue or PRD, or assess staged, unstaged, and untracked work before commit or publication."
---

# Code Review

Review the complete change from a pinned base through the current worktree. Keep
**Standards** and **Spec** separate so good conformance cannot hide wrong
behavior, and correct behavior cannot hide a standards violation.

This is a read-only workflow. Do not edit files, mutate an issue or pull request,
claim a lease, commit, or push.

Return the report in the conversation or PR review surface. If the caller requests
a durable repository report, use `documenting-work` to resolve and report the
recommended `review` path and authority, but leave the actual write to an
authorized outer workflow so this review remains read-only.

## Inputs

Accept these from the caller when supplied:

- a fixed point: commit, tag, branch, merge-base target, or explicit base SHA;
- an integration-base OID when merge-context evidence is part of the review;
- a pinned effective-integration artifact: merge method, tree/diff fingerprint,
  and reconstructable read-only diff command or artifact pointer;
- a spec source: issue/PR context, PRD text, acceptance criteria, or file path;
- a narrower path scope or an explicit comparison mode;
- for a re-review, the prior candidate, new candidate, corrected findings, and
  axes whose evidence may have changed.

Do not replace supplied context with an inferred source. Resolve missing context
from the repository when possible; ask only when the choice would materially
change the review. If no authoritative spec exists, still run Standards and mark
Spec `Not evaluated — no authoritative spec supplied or found`.

When an effective-integration artifact is supplied, reconstruct and inspect its
exact diff alongside the ticket diff, include its changed paths in authority
discovery, and require both axes to evaluate integration-only effects. Fail
closed if its method, fingerprint, or diff cannot be reconstructed as supplied.

## 1. Pin the review snapshot

Resolve the fixed point before delegating. If the caller names a target branch or
asks for a pull-request/branch review, compare from its merge-base with `HEAD`.
If the caller explicitly names an exact base, use that commit directly. When no
base is supplied, use the current branch's single configured upstream; if none
exists, use the remote default branch only when exactly one candidate resolves.
If those sources conflict or remain absent, request the fixed point.

Record:

- the requested ref and resolved base SHA;
- `HEAD` SHA and `git status --short`;
- `git log <base>..HEAD --oneline`;
- tracked changes from `<base>` through the current working tree;
- untracked, non-ignored files from `git ls-files --others --exclude-standard`, classified as in-scope or unrelated.

The review target is the current worktree, not merely `HEAD`. Inspect all three
tracked views so one layer cannot hide another:

- `git diff --no-ext-diff <base> --` for the final base-to-worktree result;
- `git diff --no-ext-diff --cached <base> --` for the exact base-to-index result;
- `git diff --no-ext-diff --` for the exact index-to-worktree result.

Inspect untracked files that belong to the requested change, its tests, or an
explicit path scope. List unrelated untracked paths as excluded without hashing
their contents. For large or binary in-scope files, inspect type, size,
provenance, and relevant generated metadata without dumping unbounded contents.
Never expose suspected credentials or secrets; identify the path and redact the
value.

Fingerprint these three diffs and each in-scope untracked file at the start, then
repeat the complete candidate identity, including `HEAD`, before reporting. If an in-scope fingerprint or `HEAD` changed, the
snapshot drifted: identify the drift and restart or clearly limit the review
rather than combining observations from different worktree states. Unrelated
untracked drift does not restart the review. Hashing must be read-only and must
not add objects to the repository.

Define the candidate identity as the `HEAD` SHA plus the three tracked-diff
fingerprints and the sorted `(path, fingerprint)` set for every in-scope
untracked file. Include each untracked path's file type, executable mode, and
payload bytes or symlink target; treat a special file or nested repository that
cannot be inspected safely as unreconstructable. A clean committed candidate
uses its `HEAD` SHA. A WIP fingerprint is only a local drift token for one review
run, not a portable identity: never carry an axis forward from or into a WIP
candidate. Candidate-to-candidate carry-forward is allowed only between clean
committed OIDs whose delta is reconstructable; otherwise start fresh reviewers
for both axes.

Define one review-context identity per axis from the candidate identity,
resolved review-base SHA, any supplied integration-base OID and effective-integration
artifact, exact path scope, and that axis's authority identities. Use
a content fingerprint or immutable version for authority text that is not
pinned by the repository. Carry an axis forward only when its base, path scope,
and authority identity are unchanged and reconstructable; otherwise inspect
that axis anew.

Fail early on an unresolved ref. An empty tracked diff is not an empty review
until the untracked-file list is also empty. If both are empty, report that there
is nothing to review.

## 2. Establish the two authorities

### Standards authority

Discover the instructions that apply to each changed path, including repository
agent instructions, contribution guides, coding standards, architecture rules,
and language- or directory-specific guidance. Respect their documented scope and
precedence. Repository standards are authoritative.

Use [references/smell-baseline.md](references/smell-baseline.md) only as a
secondary heuristic. A repository rule overrides it. Skip formatting, imports,
or other checks already decided reliably by configured tooling unless the tool
actually reports a failure.

### Spec authority

Use caller-supplied issue/spec context first. Otherwise look for read-only evidence
in branch/commit references and nearby repository specs, plans, or acceptance
tests. Record exactly which source is authoritative. Do not infer requirements
from the implementation itself, and do not mutate the tracker while reading
context.

A document declaring `kind: "spec-explainer"`, `normative: false`, or an equivalent non-normative warning is never Spec authority. Read only enough of it to resolve `derived_from`, then inspect the exact authoritative spec and record that identity instead. If the authoritative source is absent, ambiguous, or cannot be fingerprinted as supplied, report Spec `Not evaluated`; do not convert explainer prose into review requirements.

A `local-work` entry point or item may supply the reviewed fixed point, path scope, progress, and verification pointers, but it remains non-normative. Resolve its fingerprint-matched `derived_from` spec and use only that spec for the Spec axis.

## 3. Run separate reviews

Treat reviewer cleanliness as a **context boundary**, not merely a clean
worktree. Delegate Standards and Spec to two fresh subagents in parallel when
capacity allows. Start them without inherited conversation history when the
runtime supports it (for example, Codex `fork_turns: "none"`). Give both the
same pinned scope (base SHA, candidate identity, status, commit list, tracked diff
command, effective-integration artifact, untracked paths, and any path restriction), but give each only its own
authority and brief. Tell both agents to inspect rather than edit.

When isolated reviewers are available, do not reuse an implementer, designer,
test worker, reviewer of another issue, or reviewer of an earlier candidate.
One reviewer evaluates one axis of one candidate and returns one report. If the
candidate changes, retire the old review context and start a fresh reviewer for
every axis whose evidence could have changed. A re-review brief may name the
previous finding and correction, but must not include another reviewer's
conclusions or the caller's expected verdict.

For a re-review, inspect the delta from the prior candidate to the new candidate
before accepting the caller's affected-axis list. An axis may carry forward only
when that delta cannot affect its authority, reviewed files, requirements,
execution path, or other evidence. Record each axis as either freshly reviewed
at the final candidate or carried forward from a named prior candidate with that
rationale. Never present a carried-forward result as though its reviewer
inspected the final candidate. The final gate is coherent only when both axes
have explicit candidate provenance.

If parallel delegation is unavailable but isolated reviewers can be started
sequentially, use separate fresh reviewer contexts. If no isolation mechanism is
available, review Standards first from only its authority, set those findings
aside, then review Spec from only its authority. Label this a separated
single-context fallback rather than an independent review. Keep the two finding
sets and severities separate; unavailable delegation alone never blocks a report.
When isolated reviewers are used, do not show either reviewer the other's
conclusions before both reports are complete.

In the no-isolation fallback, inspect each affected axis anew at the current
candidate in the same context and record that axis as a separated
single-context inspection, never as an independent or fresh-reviewer result.
Prior observations may identify corrected findings but cannot substitute for
this new inspection.

Keep each reviewer bounded to the pinned diff and its authority. Expand into
unchanged code only to trace a dependency or execution path needed to validate
a finding. Do not rerun the caller's full verification suite, wait on long
builds, perform implementation or architectural design, or continue exploring
after the axis can be reported. A reviewer may run a cheap targeted read-only
probe when that probe is necessary to distinguish a supported finding from a
question. Treat the caller's recorded test results as evidence, not as a reason
to reproduce every command.

### Standards brief

Provide all applicable standards files and the smell-baseline path. Ask for only
actionable findings introduced or materially worsened by the reviewed change:

1. direct violations of an applicable documented rule, citing file and rule;
2. concrete design smells, labelled as judgement calls and tied to a changed
   hunk plus a likely maintenance or correctness cost.

The repository wins any conflict with the baseline. A baseline smell by itself
is not a hard violation.

### Spec brief

Provide the authoritative spec text/path and acceptance evidence. Ask for:

1. missing or partial requirements;
2. implemented behavior that contradicts a requirement;
3. unrequested behavior with a concrete cost or risk;
4. requirements that appear implemented but fail on a traceable path or edge.

Every finding must cite the requirement. If no authoritative spec exists, skip
this subagent and report Spec as not evaluated rather than treating it as a pass.

## 4. Gate every finding

Before reporting a finding, verify all of the following:

- it is caused by, exposed by, or materially worsened by this review scope;
- the cited line/hunk and relevant execution or dependency path were inspected;
- repository searches did not reveal an implementation, test, or exception that
  invalidates the claim;
- the authority applies to this file and supports the stated conclusion;
- the impact is concrete and the proposed correction is actionable;
- the confidence is high enough to distinguish a defect from a question.

Do not report pre-existing problems, taste-only preferences, vague future risks,
or lint/type/format guesses that configured tools can settle. When evidence is
incomplete, either verify it, omit it, or place it under `Questions / limits`—not
in the finding count.

Use the same severity vocabulary within each axis:

- **blocker** — unsafe to ship or cannot satisfy the core contract;
- **high** — likely user-visible correctness, security, data, or required-behavior
  failure;
- **medium** — bounded reliability/maintainability failure or partial requirement
  with a concrete impact;
- **low** — real, localized issue worth correcting before completion.

A smell heuristic alone is normally low or medium; raise it only when independent
evidence demonstrates a more severe defect.

## 5. Report without cross-axis reranking

Return:

```markdown
## Review scope
- Requested fixed point / resolved base: ...
- Integration-base OID, when supplied: ...
- Effective-integration merge method, tree/diff fingerprint, and artifact: ...
- Final candidate identity: HEAD + tracked and in-scope untracked fingerprints ...
- Reviewed: commits + staged + unstaged + untracked ...
- Standards sources: ...
- Spec source: ...
- Report authority: conversation | PR | recommended repository path ...

## Standards
- Standards review-context identity: candidate + base + path scope + Standards authorities ...
- Axis provenance: freshly reviewed at <candidate> | separated single-context inspection at <candidate> | carried forward from <candidate>; rationale ...
### [severity] Short title
- Location: path:line
- Authority: standards-file:rule or "smell heuristic"
- Evidence: changed behavior/hunk
- Impact: concrete consequence
- Correction: smallest credible fix

## Spec
- Spec review-context identity: candidate + base + path scope + Spec authorities ...
- Axis provenance: freshly reviewed at <candidate> | separated single-context inspection at <candidate> | carried forward from <candidate>; rationale ...
### [severity] Short title
- Location: path:line
- Requirement: spec-source:line or acceptance criterion
- Evidence: observed mismatch
- Impact: concrete consequence
- Correction: smallest credible fix

## Questions / limits
- ...

## Axis summary
- Standards: N findings; worst severity ...
- Spec: N findings; worst severity ... | Not evaluated ...
```

Order findings by severity, then by file, within each axis. Do not merge duplicate
cross-axis observations, choose a single overall winner, or let one axis change
the other's severity. If an axis has no findings, say `No findings after the
checks above`; this means no supported finding was found, not proof of perfection.
