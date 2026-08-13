---
name: quality-gauntlet
description: Orchestrate an explicitly requested, multi-agent quality-convergence loop over an authorized artifact using an inspectable bar, isolated builders and critics, and repeated evidence-backed improvement. Use when the user invokes this skill to improve code, a UI, writing, research, or another artifact against a reference, benchmark, rubric, or measurable target. Do not use for ordinary test-first implementation, unknown-cause diagnosis, a one-pass completed-change review, or tracker and publication work.
---

# Quality Gauntlet

Converge against a bar the evaluator can inspect. Freeze the real artifact for
each judgment, keep every critic read-only and independent from the builder, and
never let a builder's explanation substitute for evidence.

## Respect authority and adjacent owners

This is an explicit, potentially expensive inner workflow. Invocation authorizes
the requested multi-agent evaluation work, but it does not expand mutation
authority.

- Treat a request to plan or explain a gauntlet as read-only. Return a run-ready
  brief without changing the artifact.
- Edit only when the user or an active outer workflow authorized improvement of
  the artifact. Preserve unrelated and dirty worktree state.
- For issue-backed edits, proceed only while `work-github-issue` reports that the
  current session holds a valid implementation lease. This skill never claims,
  renews, or releases a lease.
- Use `diagnosing-bugs` when the cause of incorrect or slow behavior is unknown,
  `codebase-design` when a material module seam is unresolved, `tdd` for known
  behavior changes, and `complexity-optimizer` for a validated performance
  hotspot.
- Keep final Standards and Spec assessment with `code-review`. A gauntlet critic
  judges comparative quality; it does not certify repository compliance or
  requirement completeness.
- A document declaring `kind: "spec-explainer"`, `normative: false`, or an
  equivalent warning cannot define mandatory requirements or a quality bar for
  another artifact. Resolve and use its authoritative `derived_from` source.
  The explainer may itself be evaluated, but a builder must not edit it
  independently. Any accepted candidate must be regenerated from the frozen
  authority through the `to-spec` explainer and fingerprint lifecycle; its
  prose still cannot change product behavior.
- Do not commit, push, open or merge a pull request, mutate a tracker, publish
  evidence, or create a durable progress document. Use `documenting-work` when
  the user explicitly requests a persistent progress surface or report.

If the requested bar would change approved behavior, architecture, ticket
boundaries, dependencies, safety policy, or another approval-gated contract,
stop at a recommendation and name the accepting authority.

## Establish a runnable gauntlet

Resolve these inputs before the first builder changes the artifact:

1. **Goal:** the desired outcome, non-negotiable requirements, constraints, and
   exclusions.
2. **Artifact:** the actual files, rendered product, running behavior, finished
   prose, benchmark result, or other output to improve.
3. **Inspection seam:** the repeatable way a critic observes that artifact.
4. **Quality bar:** a reference, threshold, rubric, or comparison that can win or
   lose on stated dimensions.
5. **Mutation scope:** writable paths or artifact regions, workspace ownership,
   and any outer lease status.
6. **Execution envelope:** the available time, token or compute ceiling, agent
   capacity, and user stop signal.

Separate mandatory gates from the comparative bar. Tests, safety constraints,
required behavior, data integrity, and other hard requirements must pass in
every candidate; a visual or qualitative win cannot trade them away.

When the user supplied a bar, preserve it. When the user delegated bar selection,
choose the strongest concrete comparison that the inspection seam can evaluate
and state why it is discriminating. When neither is true, propose a bar and stop
before editing. A reference may define quality dimensions, but it cannot silently
invent product requirements or authorize copying protected expression.

The gauntlet is runnable only when the artifact can be inspected repeatedly, the
bar distinguishes improvement, the mutation scope is authorized, and at least
one fresh critic context is available. If an isolated critic cannot be started,
report `blocked` rather than relabeling self-review as a gauntlet.

## Decompose into temporary improvement cells

Have the lead agent choose the smallest cells that can be changed and judged
independently without breaking end-to-end behavior. For each cell record:

- identifier and artifact region;
- inspection seam and relevant bar facet;
- mandatory gates and success signal;
- writable paths or output ownership;
- dependencies and integration risks.

Cells are ephemeral execution state, not tracker tickets. Do not use them to
replace the vertical, independently deliverable tickets owned by `to-tickets`.

Keep one **accepted candidate** and treat every builder result as a **trial
candidate** until an independent critic and mandatory gates accept it. Prefer an
isolated scratch copy, alternate output, or session-owned patch so a rejected
trial never overwrites the accepted artifact. When the artifact must be edited
in place, capture exact path-scoped recovery material for every authorized
writable path and fingerprint unrelated state before editing. Never use a broad
reset, checkout, clean, or stash as recovery. If the accepted candidate cannot
be restored without touching unrelated state, stop before the builder runs.

Run read-heavy exploration and independent critics in parallel when useful.
Allow parallel writers only when their writable outputs are disjoint, their
integration seam is stable, and no shared generated file or mutable environment
can race. Otherwise serialize builders. Never let two agents edit an overlapping
artifact at the same time.

## Route capability by role

Use semantic roles instead of hard-coding a model generation:

- Give the lead and whole-artifact integrator the strongest available capability
  justified by ambiguity and consequence.
- Give clear, bounded builders the lowest-cost capability that passes
  representative evaluations for that role.
- Use efficient critics for objective rubrics and stronger critics for
  ambiguous, holistic, security-sensitive, or architecture-sensitive judgment.
- Increase reasoning effort only after a representative task shows a material
  quality gain. Prefer cost per successful, verified cell over price per token.
- Use a stronger or otherwise diverse checkpoint critic periodically to reduce
  correlated blind spots in a homogeneous fleet.

If the runtime cannot select models or reasoning effort, use the available
isolated contexts and disclose that routing limitation. Model diversity never
replaces fresh context, artifact inspection, or final verification.

## Run the builder-critic loop

Repeat one complete round at a time:

1. **Pin the incumbent.** Pause writers, fingerprint the accepted candidate and
   unrelated state, capture the mandatory-gate baseline, and establish the
   path-scoped rejection method for the next trial.
2. **Build.** Give one builder the goal, its cell, the applicable bar facet,
   constraints, writable boundary, and success signal. Let it inspect and edit
   a trial copy or the recoverable in-place artifact. Require focused
   verification before it returns.
3. **Freeze.** Stop writes, re-run the cell's mandatory gates, and pin the new
   trial candidate. When a mandatory gate fails, reject it through the
   pre-recorded recovery method and read back the accepted fingerprint before
   continuing. Do not ask a critic to judge a moving workspace.
4. **Critique independently.** Start a fresh read-only critic with the goal,
   mandatory gates, bar, inspection seam, pinned accepted candidate, and pinned
   trial candidate. Do not include the builder's reasoning, history,
   self-assessment, or proposed defense.
5. **Return one verdict.** Require:
   - `meets-bar`, `advances`, `no-material-gain`, `regresses`,
     `incomparable`, or `invalid-candidate`;
   - direct evidence comparing the actual trial to the bar and incumbent;
   - the largest meaningful eligible gap;
   - a measurable success signal and correction boundary;
   - confidence and material limits.
6. **Promote or reject.** Recheck the trial fingerprint and mandatory gates.
   Only `meets-bar` or `advances` may enter two-phase promotion: apply the exact
   trial bytes, then re-run the applicable gates and read back the applied
   fingerprint. Update the accepted identity only after both checks pass. Reject
   every other verdict, and any failed provisional promotion, through the
   pre-recorded path-scoped recovery method; then verify the prior accepted
   fingerprint and unrelated state.
7. **Gate the finding.** Verify that the remaining gap is real, in scope,
   compatible with mandatory requirements, and worth another round inside the
   remaining envelope. Send only that gap back to a builder. Escalate rather
   than editing when correction needs a new requirement or approval.
8. **Invalidate stale judgments.** If the accepted or trial fingerprint changes
   during critique, promotion, or rejection, discard every verdict that covered
   the old candidate. Stop `blocked` when exact recovery cannot be read back.

Apply the same rejection protocol on every interruption before promotion,
including builder failure, critic unavailability, environment failure, user
steering, or an unknown tool result. Halt writers and classify whether the trial
is isolated, applied, or uncertain. Before any recovery write, recheck that
mutation authority and any required outer lease remain valid. When they do,
attempt the recorded path-scoped recovery and read back both the accepted and
unrelated fingerprints.

When mutation authority or lease ownership is lost or uncertain, perform no
recovery write. Capture only read-only fingerprints, report `blocked` with the
exact residual trial state and recovery material, and return control to the
authorized outer owner. In every failed or unknown recovery, do not imply that
the accepted candidate is current.

Blind the incumbent and trial identities when possible without losing relevant
context, then compare the winner with the bar. Otherwise disclose that the
comparison was not blind.

After a wave changes multiple cells, run a fresh whole-artifact integration
critic. It should identify conflicts, inconsistency, or local improvements that
hurt the whole. Apply any smoothing fix through one serialized builder, then
repeat mandatory gates and whole-artifact inspection.

## Stop predictably

Do not pick an arbitrary number of rounds. Before starting another round, ensure
the remaining envelope can finish a build, independent critique, verification,
and report. On a user stop, halt new work and apply the common rejection
protocol. Return `user-stopped` only when no unverified trial remains; otherwise
return the protocol's `blocked` residual-state handoff.

Before returning any outcome other than `bar-met`, apply the common rejection
protocol to every unpromoted trial. Report whether the accepted candidate was
restored exactly, recovery writes were prohibited by lost authority, or residual
state makes the run `blocked`.

Finish with exactly one outcome:

- **`bar-met`** — every mandatory gate passes and a fresh whole-artifact critic
  finds that the pinned artifact meets or beats the declared bar.
- **`budget-exhausted`** — preserve the accepted candidate and name the
  highest-value remaining gap; do not claim the bar was met.
- **`user-stopped`** — preserve the accepted candidate and report the active or
  next gap without claiming the bar was met.
- **`no-authorized-gap`** — the bar is not met, but every remaining material gap
  would exceed the approved scope or change a protected contract.
- **`blocked`** — a required artifact, inspection seam, independent critic,
  safe environment, exact candidate recovery, outer lease, or authority is
  unavailable or uncertain.

For code, a `bar-met` gauntlet still requires the applicable final test/build
gate and separate `code-review` before an outer workflow may claim completion.

## Report the evidence

Return:

- goal, mandatory gates, bar, and inspection seam;
- final candidate identity and changed artifact regions;
- cells and waves completed;
- critic verdicts with direct evidence and whether comparisons were blind;
- commands, tests, benchmarks, renders, or other checks run;
- capability routing and any isolation or model-selection limitation;
- final outcome and stop reason;
- largest remaining gaps and the next workflow owner.

Keep progress in normal session updates by default. A live page, workbench, log,
screenshot set, or other durable progress surface is an execution artifact and
must follow the consuming repository's artifact and retention contract.
