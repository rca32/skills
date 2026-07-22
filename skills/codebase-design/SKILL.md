---
name: codebase-design
description: Analyze and recommend deep module interfaces and seams. Use when the user asks to deepen a cluster of shallow modules, compare materially different interface designs, decide where a module seam belongs, or recommend an architectural seam choice before specification or test-first implementation. Do not use for generic implementation, unknown-cause diagnosis, performance-hotspot discovery, or completed-change review.
---

# Codebase Design

Choose a module shape that puts substantial behavior behind a small interface at a clean seam. Optimize for leverage for callers, locality for maintainers, and testability through the same interface callers use.

## Authority and composition

Treat this as a read-only design workflow. Inspect code, tests, and architecture material; return a recommendation in the conversation by default. Do not edit implementation files, claim an issue, change tracker state, persist a design, commit, push, or review a completed change from this skill.

- Before `to-spec`, use this skill when the module interface or architectural seam is not settled. Pass the recommendation and its resolution status to `to-spec`; let that skill record a resolved decision or keep an unresolved recommendation open.
- During issue-backed implementation, use this skill only after the outer `work-github-issue` workflow reports an already-held valid implementation lease. If no lease is held, return control without claiming one. Enter after a diagnosis or validated hotspot establishes that module reshaping is needed and before `tdd` when the ticket still needs a module-shape recommendation.
- If the recommendation would change approved behavior, an accepted architecture decision, ticket boundaries, or dependencies, stop implementation and return the recommendation to the planning workflow before editing.
- Treat private, in-bounds implementation structure as delegated to the implementer by default when it preserves approved behavior, public interfaces, accepted architecture, ticket boundaries, and dependencies. Require explicit acceptance only when the recommendation changes one of those contracts or another approval-gated decision. Do not present an out-of-bounds agent preference as accepted.
- Use `tdd` to implement the selected interface through observable behavior. Let `code-review` assess the result only against repository Standards and the originating Spec, not against an unapproved recommendation from this skill.
- When the user explicitly requests a durable design decision, use `documenting-work` to resolve its authority, destination, metadata, and write authorization, then leave the actual write to the authorized outer workflow.

A recommendation is **resolved** when existing authority fixes it, it is a private in-bounds implementation choice, an accepted source delegates it within named limits, or explicit user or repository authority accepts it. Other recommendations remain **proposed**.

Consuming-repository instructions and accepted domain language override this vocabulary. Use the terms below for design reasoning, but preserve existing identifiers, quoted contracts, and domain terms rather than renaming them mechanically.

## Inputs and framing

1. Read the request, applicable repository instructions, accepted architecture decisions, relevant callers, current interfaces, tests, and dependencies.
2. Name the candidate module and the caller behavior it must support. Record invariants, ordering constraints, error modes, configuration, performance expectations, compatibility constraints, and dependencies that may vary.
3. Identify whether the decision is still open. When an approved contract fixes the interface or seam, design within it. Treat private in-bounds structure as resolved implementation discretion. When the recommendation changes public behavior, architecture, ticket boundaries, dependencies, or another approval-gated contract, name who may accept it and keep it proposed. Report missing information only when it materially changes one of those contracts.

The framing is complete when the candidate, callers, constraints, current authority, and permissible design space are explicit.

## Glossary

**Module** — anything with an interface and an implementation. Deliberately scale-agnostic: a function, class, package, or tier-spanning slice.

**Interface** — everything a caller must know to use the module correctly: the type-level surface plus invariants, ordering constraints, error modes, required configuration, and performance characteristics.

**Implementation** — what is inside a module. Use **adapter** instead when the role at a seam is the subject.

**Depth** — leverage at the interface: the amount of behavior a caller or test can exercise per unit of interface it must learn. A module is **deep** when substantial behavior sits behind a small interface and **shallow** when callers must understand nearly as much complexity as the implementation contains.

**Seam** — a place where behavior can vary without editing the caller at that place; the location at which a module's interface lives. Seam placement is a separate decision from what goes behind it.

**Adapter** — a concrete implementation that satisfies an interface at a seam. It describes the role a thing fills, not its substance.

**Leverage** — the capability callers gain per unit of interface they learn. One implementation pays back across many callers and tests.

**Locality** — the concentration of change, bugs, knowledge, and verification in one module instead of across its callers.

## Design principles

- **Depth belongs to the interface.** A deep module may contain small internal parts and internal seams without exposing them to callers.
- **Use the deletion test.** Imagine deleting the module. If complexity vanishes, it was likely pass-through indirection. If the complexity reappears across callers, the module was earning its place.
- **Use the interface as the test surface.** Callers and tests should cross the same seam. A need to test past it is evidence that the module may have the wrong shape.
- **Require real variation.** One adapter makes a seam hypothetical; introduce a seam when at least two justified adapters or behaviors vary across it.
- **Keep the surface small.** Reduce methods and parameters, move policy behind the interface, and make the common caller path easy without hiding material constraints.

## Choose a branch

### Deepen an existing cluster

Enter this branch when several shallow modules or repeated caller responsibilities appear to belong behind one interface. Read [the deepening guide](references/deepening.md), classify the dependencies, and recommend the replacement module, external seam, migration order, and test surface.

### Explore materially different interfaces

Enter this branch when the user asks for alternatives or when two or more credible seam choices would materially change the public contract, architecture, or test cost. Read [Design It Twice](references/design-it-twice.md), generate distinct alternatives, compare them, and make one recommendation.

### Recommend one constrained design

Use this branch when repository authority or caller constraints leave one credible module shape. State the interface, seam, hidden behavior, dependency strategy, and tests directly. Do not manufacture alternatives merely to make the report look thorough.

## Evaluate the recommendation

Check every candidate against:

- **Depth:** how much caller-visible capability the interface provides for what callers must learn;
- **Locality:** whether policy, change, and verification concentrate behind the seam;
- **Seam placement:** whether the seam follows real behavioral variation rather than test-only convenience;
- **Testability:** whether callers and tests can observe the required behavior through the same interface;
- **Compatibility:** whether the design respects accepted contracts and provides a safe migration when callers must move;
- **Dependency fit:** whether in-process, local-substitutable, remote-owned, and true-external dependencies receive an appropriate strategy.

Reject a recommendation that achieves a smaller type signature by hiding required ordering, errors, performance costs, or configuration from callers. That information remains part of the interface.

## Completion and handoff

Return:

1. the selected module and seam;
2. the proposed interface, including invariants, ordering, error modes, configuration, and performance expectations;
3. the behavior hidden behind it;
4. the dependency and adapter strategy;
5. how callers and tests use the interface;
6. alternatives considered and the decisive trade-offs;
7. compatibility, migration, and unresolved risks;
8. resolution status: fixed by existing authority, private in-bounds implementation discretion, delegated within named limits, explicitly accepted, or proposed with the accepting authority named;
9. the next owner: `to-spec` for unsettled planning, `tdd` for a resolved and authorized implementation, or the outer issue workflow when scope must be renegotiated.

The design is complete when a caller can understand the full interface without reading the implementation, the recommendation is justified by depth, locality, seam placement, and testability, and the next workflow can proceed without silently making another architectural choice.
