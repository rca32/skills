# Design It Twice

Read this guide when the user asks for alternative interfaces or when multiple credible seam choices would materially change the public contract, architecture, or test cost. Use the vocabulary in [the core skill](../SKILL.md) and the dependency categories in [the deepening guide](deepening.md).

## 1. Frame the problem space

Before generating designs, show the user:

- the caller behaviors and constraints every interface must satisfy;
- the dependencies and their categories;
- accepted architecture decisions and compatibility requirements;
- a small illustrative sketch that grounds the constraints without presenting a preferred proposal.

Proceed when the framing distinguishes fixed constraints from open design choices. If an approved Spec or architecture decision already closes the choice, stop and report that authority instead of creating competing designs.

## 2. Generate distinct alternatives

When independent sub-agents are available, start at least three in parallel. Give each the same raw technical brief and applicable repository or domain vocabulary, but do not expose another candidate or an intended winner. Assign different constraints:

- minimize the interface to one to three entry points and maximize leverage;
- maximize extension across justified caller use cases;
- optimize the most common caller path;
- when remote-owned dependencies matter, optimize seam placement around ports and adapters.

If independent sub-agents are unavailable, produce at least three alternatives sequentially under those constraints and disclose that they were not independently generated. Keep each draft separate until all are complete.

Do not assume one conventional filename for domain context. Read the consuming repository's documented domain vocabulary when one exists; otherwise preserve terminology from the request and current code.

Each alternative must include:

1. the interface, including types, methods, invariants, ordering, error modes, configuration, and performance expectations;
2. a caller usage example;
3. the behavior hidden behind the seam;
4. the dependency and adapter strategy;
5. compatibility and migration impact;
6. where leverage is high and where the interface remains shallow.

## 3. Compare and recommend

Present each design separately, then compare them by depth, locality, seam placement, testability, compatibility, and dependency fit. Identify any constraint a candidate fails instead of averaging incompatible designs into a compromise.

Recommend one design and explain the decisive trade-offs. Propose a hybrid only when its combined interface remains coherent and smaller than the knowledge it hides. Mark the recommendation proposed until the user or applicable repository architecture authority accepts it, unless an existing authority already fixes the choice or explicitly delegates this in-bounds design decision.

This branch is complete when the alternatives are materially different, all satisfy the same fixed constraints or are explicitly rejected, one recommendation and its resolution status are clear, and the next workflow will not choose or implement an unresolved interface implicitly.
