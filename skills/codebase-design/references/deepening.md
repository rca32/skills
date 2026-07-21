# Deepening an Existing Cluster

Read this guide when several shallow modules or repeated caller responsibilities appear to belong behind one interface. Use the vocabulary in [the core skill](../SKILL.md).

## Assess the candidate

1. Map the current modules, callers, duplicated policy, pass-through calls, and tests.
2. Apply the deletion test. A useful candidate causes hidden complexity to reappear across callers when removed; a pass-through layer merely disappears.
3. State the proposed external seam and the behavior that would move behind it.
4. Classify every dependency before choosing adapters or a test strategy.

Do not recommend a merge merely because the code runs in one process. Preserve independent lifecycle, security, transactional, concurrency, ownership, or deployment constraints defined by the consuming repository.

## Classify dependencies

### In-process

Pure computation or in-memory state with no I/O is usually a strong deepening candidate. Test the proposed module directly through its external interface. Add no adapter unless behavior actually varies.

### Local-substitutable

Use a faithful local stand-in, such as an embedded database or in-memory filesystem, when the repository already supports one or its adoption is an accepted design choice. Keep this seam internal when callers do not need to choose the dependency.

### Remote but owned

For an owned service across a network boundary, define a port at the internal seam. Keep policy in the deep module and inject a production transport adapter plus a faithful local adapter for tests. Preserve protocol, failure, retry, and consistency semantics in the interface.

Recommendation shape:

> Define a port at the seam, use a transport adapter in production and a faithful local adapter in tests, and keep caller-facing policy in one deep module.

### True external

For a third-party system, inject the external capability through a narrow port. Use a controlled fake or mock adapter in tests and make external errors, idempotency, limits, and reconciliation behavior explicit in the module interface.

## Keep seam discipline

- Treat one adapter as a hypothetical seam. Justify at least two adapters or real behavior variants before adding indirection.
- Keep test-only internal seams private. Do not expose them through the external interface merely because tests use them.
- Count the production transport and a behaviorally faithful test adapter only when both exercise a meaningful variation at the seam.

## Plan replacement, not layering

Recommend a migration that leaves one authoritative behavior surface:

1. Add tests for required behavior at the proposed deep module interface.
2. Move behavior behind that interface in an order that keeps the repository green.
3. Migrate callers without creating a second editable policy path.
4. Remove obsolete shallow interfaces and their implementation-coupled tests only after replacement coverage is green and removal is authorized.

Implementation belongs to `tdd` or another authorized implementation workflow. This guide produces the target interface, migration order, replacement test surface, and risks; it does not edit code.

The deepening recommendation is complete when every current responsibility and dependency has a destination, caller migration is explicit, and the final state contains one external interface rather than a new layer over the old cluster.
