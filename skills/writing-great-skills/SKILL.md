---
name: writing-great-skills
description: Design, rewrite, or audit Codex skills for predictable invocation and execution. Use when the user asks to create or improve a SKILL.md, reduce skill overlap or context load, clarify branches and completion gates, or pressure-test whether skill instructions change agent behavior.
---

# Writing great skills

A skill exists to wrangle predictability from a stochastic system: the agent should take the same justified process across runs even though wording and intermediate reasoning vary.

## Start with the behavioral delta

Before writing prose, state:

- **Purpose:** the one outcome this skill owns;
- **Trigger:** observable request shapes that should invoke it;
- **Inputs:** context or artifacts required to proceed;
- **Branches:** materially different paths through the workflow;
- **Completion:** evidence that distinguishes done from plausible-looking progress;
- **Non-ownership:** adjacent actions or state mutations owned elsewhere.

If these cannot fit in a short paragraph, split the concept before drafting the skill.

## Choose invocation deliberately

A model-invoked skill is discoverable from its frontmatter description and costs context on every eligible turn. Use it only when the agent or another skill must reach it autonomously. The description should lead with the action, name one trigger per real branch, and state negative scope where a neighboring skill could also fire.

An explicit skill is remembered and invoked by the user. Set `policy.allow_implicit_invocation: false` in `agents/openai.yaml`; keep valid `name` and `description` frontmatter for packaging and human discovery. Use explicit invocation for durable external mutations, rare expert procedures, or flows whose surprise cost is high.

When explicit skills become hard to remember, add one small router over the actual installed catalog rather than making every procedure implicit.

## Build the information hierarchy

Put information at the highest tier that needs it and no higher:

1. **In-skill step:** an ordered action every run needs now. End meaningful steps with a checkable completion criterion.
2. **In-skill reference:** a compact rule or definition consulted across most branches.
3. **Disclosed reference:** branch-specific detail in `references/`, reached by a direct pointer whose wording says when to read it.
4. **Executable script:** fragile, repetitive, or concurrent mechanics that are safer to execute and test than regenerate.
5. **Asset:** material copied into output, not instructions the agent must read.

Progressive disclosure is a branch decision, not a license to hide the core workflow. Keep a concept's rule, caveats, and completion evidence co-located. Do not add resource directories that the skill never references.

## Write predictable steps

- Use leading words with strong pretrained meaning, such as `red-green-refactor`, `frontier`, `lease`, or `reconcile`, to collapse repeated explanation.
- State positive target behavior first. Reserve prohibitions for hard safety boundaries and pair them with the safe alternative.
- Prefer public contracts and observable outcomes over file paths, line numbers, or current implementation trivia.
- Make authorization branches explicit: read-only analysis, local edits, external writes, publication, and destructive actions are different permissions.
- Define unknown-result recovery before retry behavior for external mutations.
- Give each state transition an entry condition, an operation, a readback, and an exit condition.

## Prune aggressively

Keep each meaning in one source of truth. For every sentence, ask whether removing it would change agent behavior. Delete no-ops, stale sediment, duplicated cautions, and generic advice already supplied by the host agent.

Watch for these failure modes:

- **Premature completion:** the next step attracts attention before the current gate is actually satisfied. Sharpen the gate; split the sequence only if the pressure remains.
- **Duplication:** one rule appears in several skills and drifts. Assign an owner and link to it.
- **Sprawl:** every line is relevant but too much loads at once. Disclose by branch or split by independently useful invocation.
- **Trigger overlap:** adjacent descriptions fire on the same request. Distinguish unknown-cause diagnosis from known behavior change, or analysis from mutation.
- **No-op:** prose sounds careful but changes nothing. Replace it with a binary observation, concrete authority boundary, or remove it.

## Package with skill-creator

For a new skill, run the installed `skill-creator` initializer before manual scaffolding. Keep `SKILL.md` below 500 lines and use only supported frontmatter. In `agents/openai.yaml`, quote strings, keep the short description within the validator's limit, and make the default prompt explicitly name `$skill-name`.

Do not place credentials, private data, project-only absolute paths, or unrelated setup assumptions in a reusable skill.

## Pressure-test before publishing

Create realistic prompts without embedding the intended answer. Include at least:

- a normal successful path;
- a neighboring trigger that should select a different skill;
- missing or ambiguous authorization;
- partial or unknown external failure;
- concurrent actors when state is shared;
- dirty or changing local state when files are inspected.

Observe the chosen steps, mutations, stop conditions, and completion claim. Repair the instruction that allowed an unsafe or unpredictable choice; do not merely document the bad outcome.

Then run structural validation, every bundled deterministic test, and separate Standards and Spec reviews. Use isolated reviewers when available. Otherwise run the axes sequentially in the current context, keep their evidence and findings separate, and disclose that they were not independent; unavailable delegation alone does not block validation. A skill is ready only when its trigger is distinct, every branch reaches an observable terminal condition, resources are reachable, mutations match authority, and the consuming repository's publication gate is satisfied.
