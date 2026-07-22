---
name: tdd
description: Implement already-defined behavior or an already-diagnosed fix test-first through small red-green-refactor slices. Use when the target outcome is known and the user asks for TDD, regression or integration tests, or a test-first change; diagnose unexplained failures before using this skill.
---

# Test-Driven Development

Build one observable behavior at a time through a public seam. Keep every cycle small enough that the failing test explains the next production change.

## Respect the outer workflow

This inner skill never claims or releases an issue, changes tracker state, commits, pushes, or publishes evidence. For issue-backed work, follow the authoritative lifecycle in `work-github-issue`.

Treat every repository change made to satisfy an issue as issue-backed, including tests, fixtures, docs, and generated artifacts. Read-only seam discovery may happen before a lease, but no issue-backed file may change until the outer workflow reports a fresh successful ownership check for this session. Let the outer workflow recheck and renew around long cycles. If it reports lost or uncertain ownership, stop writing and return control to it.

## Establish the seam

1. Read the request, repository instructions, nearby tests, and domain or architecture documents relevant to the change.
2. Name the public seam through which a caller observes the behavior: a public function, command, HTTP endpoint, event, rendered interaction, or another stable contract.
3. Derive the seam from the existing contract when it is clear. When two or more materially different module seams would change a public API, accepted architecture, ticket boundaries, dependencies, or material test cost, use `codebase-design` before the first Red. Proceed with a resolved private in-bounds choice; return to planning only for an unresolved contract change.
4. State the seam and first observable behavior before editing.

Test behavior through that seam, not private methods or incidental call order. Read [references/tests.md](references/tests.md) when selecting assertions and [references/mocking.md](references/mocking.md) when the behavior crosses system boundaries.

## Run one vertical slice

Repeat this complete cycle for each behavior:

### Red or characterize

1. Add the smallest test that specifies one externally observable behavior. For existing behavior being protected before refactoring, run a characterization test and record its baseline-green result instead of forcing an artificial failure.
2. Use an expected value independent of the implementation: a specification example, known literal, protocol contract, or established oracle.
3. Run the narrowest relevant test command.
4. Confirm it fails for the missing or incorrect behavior. A syntax error, fixture failure, or unrelated failure is not a valid red.

### Green

1. Make the smallest production change that can satisfy this test.
2. Do not anticipate later slices or widen the public contract without evidence.
3. Re-run the narrow test and confirm it passes.

### Refactor

1. Improve names, duplication, or structure only where the completed slice revealed a concrete need.
2. Add no behavior during refactoring.
3. Keep the focused test green after each change, then run the relevant surrounding suite.

Start the next slice only after this one is green and coherent. Do not write a horizontal batch of speculative tests followed by a batch of implementation.

## Test quality rules

- Prefer stable public interfaces and behavior-oriented names.
- Avoid tautological expectations that recompute the result with the same algorithm.
- Mock external systems, time, randomness, or destructive boundaries when necessary; prefer real internal collaborators.
- Make failures deterministic. Pin clocks and seeds, isolate mutable state, and use disposable or non-production boundaries by default. Real payments, orders, messages, destructive writes, or production traffic require separate explicit authorization plus rollback or reconciliation controls; ordinary test authorization is not enough.
- Preserve repository conventions before introducing a new framework, helper, fixture style, or golden format.

## Exit criteria

Report the seam, behaviors covered, and exact commands run. The slice is complete only when:

- every new behavior or regression test was observed failing for the intended reason before implementation, while characterization tests were observed baseline-green before refactoring;
- focused tests pass after the implementation and refactor;
- the risk-appropriate surrounding suite passes;
- no unrelated behavior, tracker state, lease, commit, push, or publication was changed by this skill.
