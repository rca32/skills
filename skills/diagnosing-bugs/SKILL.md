---
name: diagnosing-bugs
description: Find an unknown root cause of incorrect, failing, flaky, or slow software with a tight evidence-driven loop. Use when the user asks to diagnose, debug, investigate, or explain an unexplained failure or performance regression; use TDD directly when the cause and desired behavior are already established.
---

# Diagnosing Bugs

Turn the reported symptom into a fast pass/fail signal, then use falsifiable experiments to isolate the cause. Evidence precedes explanation.

## Set the authorization boundary

Classify the request before editing:

- **Diagnose only:** reproduce, isolate, and explain the cause. Do not implement the production fix.
- **Diagnose and fix:** diagnosis plus regression protection, the smallest fix, verification, and cleanup is authorized.

If the request is ambiguous, default to diagnose only. Under diagnose-only authorization, keep temporary harnesses and probes outside the repository unless the user separately authorizes repository edits. Any probe must be reversible and disclosed, and existing user changes must never be overwritten or cleaned up.

Do not write issue-backed repository files until the authoritative `work-github-issue` lifecycle holds a valid implementation lease. This inner skill never claims or releases an issue, changes tracker state, commits, pushes, or publishes evidence.

Keep the diagnosis in the response by default. When the user or repository requires a durable diagnosis, use `documenting-work` to resolve whether the issue comment or one `diagnosis` repository document is authoritative. This skill may recommend the destination, but tracker publication remains owned by the outer workflow.

## 1. Define the exact symptom

Record the expected behavior, actual behavior, smallest known trigger, environment, and when it began. Discover missing details from existing logs, tests, configuration, and history first; ask only when the missing fact prevents a safe or discriminating experiment. Read repository instructions, nearby tests, domain documents, and relevant recent history without disturbing unrelated user changes.

For performance reports, define the metric, workload, baseline, and acceptable threshold before explaining the regression.

## 2. Build a tight feedback loop

Choose a non-production, disposable, or explicitly owned environment before exercising the path. Never send real orders, payments, messages, destructive writes, or production traffic merely to reproduce a bug. A live or destructive path requires separate explicit authorization, known rollback or reconciliation behavior, and the repository's safety controls; otherwise replace the boundary with a faithful sandbox, fixture, replay, or fake.

Create one command that exercises the actual behavior path and distinguishes the reported symptom from nearby failures. Prefer, in order:

1. an existing focused test;
2. a new or disposable test harness at the public seam;
3. a CLI, HTTP, or replay script with a precise assertion;
4. a headless UI check;
5. a seeded stress, property, or differential loop;
6. a human-assisted script based on `scripts/hitl-loop.template.sh`.

Run the command. Tighten it until it is specific, deterministic or has a measured high reproduction rate, fast enough to repeat, and runnable without guesswork. For a flaky bug, report trials and failure rate. For a performance bug, capture repeated measurements rather than one timing.

If no valid loop can be built, stop with the attempts made and the smallest missing artifact or access needed. Do not replace missing evidence with a theory.

## 3. Reproduce and minimize

Observe the exact symptom, then remove inputs, configuration, callers, data, and steps one at a time. Re-run after each removal. The minimized case is ready when every remaining element is load-bearing.

Preserve the original scenario; it is needed to detect a fix that only satisfies the minimized harness.

## 4. Rank and falsify hypotheses

List three to five plausible causes, ranked by current evidence. Give each a prediction:

> If X is the cause, changing or observing Y will produce Z.

Test one variable at a time. Prefer debugger or profiler inspection, then narrowly tagged logging. Never add broad logging and search for a story afterward.

For regressions with known good and bad revisions, bisect only in a disposable worktree or equivalent isolated checkout. Never switch revisions, overwrite files, or run destructive setup in the user's active working tree. The bisect command must be unattended, deterministic, and safe for every candidate revision.

The root cause is established only when evidence distinguishes it from the competing hypotheses and explains the observed symptom.

## 5. Stop or fix

### Diagnose-only exit

Do not change production behavior. Report:

- the reproduction command and observed signal;
- the minimized case;
- confirmed root cause with relevant file or component locations;
- evidence that falsified the leading alternatives;
- affected scope and remaining uncertainty;
- the proposed fix and regression-test seam.

### Diagnose-and-fix path

1. Turn the minimized repro into a failing regression test at a public seam when one exists.
2. Confirm the test fails for the diagnosed cause.
3. Apply the smallest fix. When the fix requires a new module interface or a materially different seam, use `codebase-design` to recommend that design without widening the diagnosed scope; obtain the required user or repository acceptance before implementation. Use the `tdd` skill for behavior changes.
4. Confirm the regression test passes.
5. Re-run the original feedback loop and risk-appropriate surrounding tests or benchmarks.

If no correct test seam exists, document that architectural limitation instead of adding a shallow test that cannot catch the real failure.

## 6. Clean up

Remove tagged instrumentation and disposable probes, while preserving an authorized regression test. Verify no debug artifacts or unexpected working-tree changes remain.

Diagnosis is complete only when the exact symptom is reproducible, the cause is supported by a falsifying experiment, the report has one declared authority if persisted, and the diagnose-only report or authorized fix path has met its exit criteria. A fix is complete only when both the minimized regression and original scenario are green and relevant surrounding checks pass.
