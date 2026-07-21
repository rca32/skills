---
name: complexity-optimizer
description: Analyze a software codebase for algorithmic complexity and performance hotspots, then propose or implement safe optimizations without breaking behavior. Use when Codex is asked to scan many files, find inefficient loops, nested iteration, repeated scans, costly rendering/recomputation, N+1 queries, avoidable O(n^2) or O(n) operations, or reduce complexity such as O(n^2) to O(n log n) / O(n), while preserving tests, APIs, outputs, and maintainability. Do not use for a general Standards/Spec code review or to diagnose an unexplained performance regression before its symptom and cause are isolated.
---

# Complexity Optimizer

## Core Rule

Optimize only when the current behavior is understood and can be preserved. Prefer a small, proven improvement with tests over a broad rewrite with unclear correctness.

## Default Behavior

When the user asks to analyze, scan, audit, review, or "give me a report" for a codebase, produce the full complexity report automatically. Do not require the user to specify report fields.

Default report contents:

- Scope analyzed and detected stack/test commands.
- Top findings ranked by likely impact.
- File and line for each finding.
- Current pattern and why it may be costly.
- Estimated current complexity.
- Recommended change.
- Estimated complexity after the change.
- Risk level.
- Tests, benchmarks, or manual checks needed.
- Clear statement that no implementation files were modified, plus the authoritative report document or pointer when persistence was explicitly requested.

Only edit code when the user asks to implement, fix, optimize, apply, change, refactor, or otherwise clearly requests code modification. If the user only asks for analysis or a report, do not modify implementation files.

Keep a report in the conversation by default. When the user explicitly asks to save or publish a durable report, use `documenting-work` to resolve its persistence tier, single authority, destination, metadata, index, and write authorization before creating it. Leave tracker publication and any issue-backed evidence pointer to the outer `work-github-issue` workflow.

## Authority and Composition

For an unexplained slow or flaky symptom, use `diagnosing-bugs` to establish a reproducible cause before optimizing. Use `code-review` rather than this skill when the request is to judge a complete change against repository Standards or an originating Spec.

This skill may make a locally authorized optimization, but it never claims or releases an issue, changes tracker state, commits, pushes, opens a pull request, merges, or publishes evidence. For issue-backed edits, do not change files until the outer `work-github-issue` workflow confirms a valid implementation lease for this session. When a validated hotspot shows that consolidating shallow modules or moving a public seam is necessary, use `codebase-design` to recommend the target module shape and obtain the required acceptance before editing. Use `tdd` for the behavior-preserving implementation slice when available, and leave final independent review to `code-review`.

## Workflow

1. Establish the baseline:
   - Identify the language, framework, test command, build command, and performance-sensitive paths.
   - Inspect existing tests before touching code.
   - Run the bundled scanner for a first-pass hotspot list when scanning a repository.

2. Rank opportunities:
   - Prioritize code on hot paths, large input paths, rendering loops, database/API loops, and shared utilities.
   - Separate algorithmic complexity from constant-factor cleanup.
   - Do not patch every warning. Treat scanner output as leads, not proof.
   - For report-only requests, inspect enough surrounding code to estimate current and proposed complexity; do not stop at raw scanner output.

3. Prove behavior:
   - Locate or add focused tests for the function/component being changed.
   - Capture edge cases: empty input, duplicates, ordering stability, null/missing values, errors, permissions, pagination, time zones, and mutation side effects.
   - If tests are absent and behavior is ambiguous, remain read-only and report the exact behavior or test seam that must be resolved before editing.

4. Optimize conservatively:
   - Replace repeated linear lookup with maps/sets when key equality is stable.
   - Replace nested scans with indexing, grouping, two-pointer scans, sweep-line logic, binary search, memoization, batching, or precomputation only when the data shape supports it.
   - In UI code, reduce unnecessary renders with stable props, memoized derived data, virtualization, debounced work, and moving expensive work out of render paths.
   - In data access code, remove N+1 behavior with bulk fetches, joins, preloading, caching, or batching while preserving authorization and filtering.

5. Verify:
   - Run relevant tests and type/lint/build commands.
   - Add a micro-benchmark or measurement when the complexity improvement is non-obvious or performance-critical.
   - Report the original complexity, new complexity, changed files, tests run, and any residual risk.

## First-Pass Scanner

Use the bundled scanner from the skill directory:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/complexity-optimizer/scripts/analyze_complexity.py" /path/to/repo --format markdown
python3 "${CODEX_HOME:-$HOME/.codex}/skills/complexity-optimizer/scripts/analyze_complexity.py" /path/to/repo --format json
```

The scanner flags common patterns in Python, JavaScript, TypeScript, JSX/TSX, Java, Go, C, C++, C#, Ruby, PHP, and Swift files. It intentionally favors readable leads over perfect static analysis.

If the scanner reports nothing, still inspect known hot paths manually. Rendering churn, database query patterns, and framework lifecycle issues often require repository-specific context.

## Optimization Safety Checklist

Before editing:

- Confirm the data sizes are large enough for complexity to matter.
- Confirm the optimization preserves output ordering where callers may rely on it.
- Confirm object identity, mutability, and reference sharing are not part of the public behavior.
- Confirm caches have a valid invalidation strategy.
- Confirm deduplication does not collapse distinct records that share a display label.
- Confirm database batching preserves tenant, permission, soft-delete, pagination, and sorting constraints.

After editing:

- Run the narrow test first, then the broadest relevant test/build command.
- Compare before/after benchmark numbers when a benchmark exists or was added.
- Keep the patch localized. Avoid formatting churn in unrelated files.

## References

- Read [the optimization playbook](references/optimization-playbook.md) for common O(n^2) to O(n log n) / O(n) transformations and framework-specific patterns.
- Read [the report template](references/report-template.md) when preparing the final analysis or audit output.

## Completion Check

A report is complete when it names the inspected scope, ranks supported hotspots, cites the relevant code, estimates before/after complexity, separates measured impact from inference, identifies verification and risk, states that no implementation files changed, and names any authorized durable report document. An implementation is complete only when the public behavior is preserved by focused tests, the relevant surrounding suite and build checks pass, any material performance claim has a repeatable measurement, and the report lists the exact changed files and residual risk.
