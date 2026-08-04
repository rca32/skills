---
name: first-principles
description: Reframe a consequential product, engineering, or process decision from first principles by separating observed facts, authoritative constraints, assumptions, inferences, and preferences, then derive the smallest defensible option and the evidence still needed. Use only when the user explicitly invokes $first-principles to challenge inherited framing or convention before design or specification. Do not use for unknown-cause diagnosis, module-interface or seam design, implementation, optimization, or completed-change review.
---

# First Principles

Keep the strength of every conclusion at or below the strength of its evidence. Do not promote a plausible claim into a fact merely because the analysis needs a clean answer.

## Authority and composition

Treat this as a read-only decision-framing workflow. Inspect authorized local material and return the analysis in the conversation by default. Do not edit code or documents, mutate a tracker or external system, claim or release an issue, commit, push, or publish from this skill.

Inspect the current worktree without cleaning, resetting, stashing, switching revisions, or overwriting user changes. When a decisive source changes during analysis, re-read it before concluding or keep the affected claim unresolved and disclose the snapshot limitation. If an earlier external write has an unknown result, do not retry it; pass its recovery identity and uncertainty to the workflow that owns reconciliation.

- Use `diagnosing-bugs` when an incorrect, failing, flaky, or slow behavior has an unknown cause. Evidence from diagnosis may later become an input here, but first-principles reasoning is not a substitute for reproduction and falsification.
- Use `codebase-design` when the open decision is a module interface or architectural seam. Pass it the reframed objective, retained constraints, and unresolved assumptions; let it own the interface recommendation.
- Use `complexity-optimizer` for codebase hotspot discovery or a behavior-preserving optimization after the behavior and cause are understood.
- Pass settled decisions to `to-spec`, authorized implementation to `tdd` within any required outer `work-github-issue` lifecycle, and completed-change assessment to `code-review`.
- When the user explicitly requests a durable decision record, use `documenting-work` to resolve its authority, destination, and write authorization, then leave persistence to the authorized outer workflow.

Existing product decisions, accepted architecture, repository instructions, safety rules, and law are authoritative constraints, not assumptions to discard. When the user asks to challenge an accepted decision, analyze a proposed replacement without treating it as accepted or changing dependent artifacts.

## Frame the decision

1. State the one decision under reconsideration, who or what may decide it, and why it matters now.
2. Express the desired outcome independently of the current solution. Name measurable success criteria, scope, time horizon, and material failure costs.
3. Identify the status quo and the smallest credible alternative. Do not manufacture alternatives when authority or evidence leaves only one feasible path.

Framing is complete when the decision, decision authority, desired outcome, current default, and evaluation boundary are explicit.

## Build the evidence ledger

Classify every claim that could change the decision:

| Class | Required basis | Treatment |
| --- | --- | --- |
| Observed fact | Inspected code, logs, measurements, records, or an authoritative source | Cite the source and observation; preserve its scope and date when relevant. |
| Authoritative constraint | A named user, repository, policy, contract, or safety authority | Apply it within its stated scope; flag conflicts instead of silently choosing. |
| Assumption | A falsifiable claim without sufficient observation or authority | State what evidence would confirm or reject it. |
| Inference | A reasoning step derived from named facts and constraints | Show the premises and keep the confidence proportional to them. |
| Preference | A value judgment or optimization priority | Name whose preference it is; do not present it as fact. |

Inspect available local evidence before asking the user for information. Treat analogy, popularity, precedent, and “best practice” as leads, not proof. Challenge only assumptions whose verdict could materially change the decision.

The ledger is complete when every decision-changing claim has one class, a source or verification method, and no unsupported claim is labeled as fact or fixed constraint.

## Test the framing

For each material assumption:

1. State the decision consequence if the assumption is false.
2. Seek the cheapest safe discriminating observation, calculation, counterexample, or reversible experiment available under the current authorization.
3. Mark the assumption `retained`, `rejected`, `modified`, or `unresolved`. Use the first three states only when the recorded evidence supports them.

Use counterfactuals to expose inherited framing: if the current solution did not exist, what capability would still be required? Use a deletion or substitution test to check whether each proposed component earns its cost. Preserve practical constraints such as migration, compatibility, operations, security, time, and reversibility; theoretical simplicity does not erase them.

When a safe discriminating check requires edits, external writes, production traffic, destructive actions, or new authority, stop at a verification plan. Do not perform the check from this read-only skill.

## Derive options

Build upward only from retained facts, authoritative constraints, explicit preferences, and qualified inferences:

1. Describe the smallest option that satisfies the required outcome.
2. Add a component or constraint only when a named requirement or measured risk justifies it.
3. Compare the status quo and credible alternatives on the same success criteria, including transition and operating costs.
4. Trace each decisive advantage, disadvantage, and risk back to the evidence ledger.
5. Name the evidence that would reverse the ranking and a concrete trigger for revisiting the decision.

Select one result state:

- **Recommended:** current evidence distinguishes one option and the recommendation stays within accepted authority.
- **Provisional:** one option leads, but named unresolved assumptions could reverse it.
- **Unresolved:** evidence does not distinguish the options or the decision requires an authority not present.

Do not convert an unresolved analysis into a recommendation for presentation quality.

## Return the decision brief

Return only the sections needed to make the reasoning inspectable:

1. decision, authority, desired outcome, and success criteria;
2. evidence ledger with sources or verification methods;
3. material assumption tests and their states;
4. derived options and reasoning chain;
5. result state, recommendation if justified, trade-offs, and revisit triggers;
6. smallest missing evidence or next owning workflow.

Write in the user's language. Preserve repository terminology, quoted contracts, identifiers, and source language where translation could change meaning.

The analysis is complete when its decision boundary is explicit, every decisive claim is traceable, uncertainty remains visible, the result state matches the evidence, and the next owner can proceed without mistaking a proposal for an accepted design or implementation authorization.
