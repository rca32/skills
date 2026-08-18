# 002 — PostgreSQL-native durable workflows

**Kind:** Overlay on entry 001

**Status:** Conditional preference; maturity-sensitive

**Tags:** PostgreSQL, pg_durable, durable execution, workflow, checkpoint, retry, scheduling, fan-out, fan-in

## Default

When application state already lives in PostgreSQL and background work becomes multi-step, expensive to restart, or recovery-sensitive, prefer evaluating a PostgreSQL-native durable execution layer before building retry, checkpoint, dependency, scheduling, and crash-recovery machinery in application code.

```text
Rust / Axum service
      ├─ Repository ───── application data ─┐
      └─ Workflow trigger                   │
                                           ▼
                                      PostgreSQL
                                      ├─ app data
                                      └─ pg_durable
                                         ├─ workflow state
                                         ├─ checkpoints
                                         ├─ retry / scheduling
                                         └─ fan-out / fan-in
```

Keep CPU-heavy or SDK-heavy work in external Rust, AI, or specialized workers. Let PostgreSQL own orchestration and durable state only when the workflow maps cleanly to the extension's execution model.

## Use when

- A workflow has several ordered or parallel steps and completed intermediate work is expensive.
- Restart, retry, checkpoint, scheduling, progress, dependency, or audit behavior is a first-class requirement.
- Data locality and one operational state model are valuable.
- The workflow is SQL-shaped or can cross to external work through a supported, explicit boundary.
- The deployment permits the extension, its background worker, required PostgreSQL configuration, and an appropriate privilege model.

Typical matches include ingestion, document processing, LLM or embedding pipelines, approval flows, publication pipelines, long-running batches, external API workflows, and fan-out/fan-in aggregation.

## Work classification

| Level | Work shape | Preferred mechanism |
| --- | --- | --- |
| 1 | One ordinary database operation | Plain SQL |
| 2 | Short, idempotent, cheap-to-restart asynchronous task | Small PostgreSQL queue using `FOR UPDATE SKIP LOCKED` |
| 3 | Multi-step, expensive, recoverable, scheduled, or dependency-rich workflow | Evaluate `pg_durable` |

Do not promote Level 1 or Level 2 work merely for stack uniformity.

## Responsibility boundaries

- Let the service layer validate the use case and initiate the workflow.
- Let repositories continue to own ordinary application queries; do not hide workflow policy in repositories.
- Let `pg_durable` own supported orchestration state, checkpoints, retry, scheduling, and workflow progress.
- Keep heavy computation and arbitrary application logic outside PostgreSQL, returning durable results through an explicit boundary.
- Treat idempotency, external side effects, cancellation, timeout, access control, monitoring, backup, and recovery as designed responsibilities rather than implied extension features.

## Avoid or deviate when

- The work is a single SQL statement or a sub-millisecond synchronous request.
- The environment cannot install and preload the extension or run its background worker.
- Most workflow steps live across heterogeneous systems and non-HTTP SDKs.
- Rich in-memory control flow or arbitrary application code is central.
- Database resource isolation cannot protect transactional traffic from workflow execution.
- The extension's current maturity, supported PostgreSQL versions, platform packaging, security model, or operational tooling fails the system's acceptance bar.

## Costs and escape triggers

- The database takes on orchestration workload and a larger failure domain. Move execution out when contention, recovery objectives, or operational ownership demand isolation.
- SQL-shaped workflows can become awkward when application behavior dominates. Move to a general-purpose orchestrator when translation cost exceeds consolidation value.
- Extension availability can constrain managed PostgreSQL choices. Prefer an external workflow system when platform portability is more important.
- A preview dependency can change quickly. Pin reviewed versions, test crash and upgrade behavior, and reconsider before production adoption if maturity or support remains below the project's bar.

## Facts to revalidate

As of 2026-08-18, Microsoft's official project describes `pg_durable` as a preview PostgreSQL extension for SQL-defined, checkpointed workflows that resume after failures. Its documented installation, PostgreSQL-version support, privileges, packaging, and limitations are current product facts rather than owner preferences. Re-check the [official repository](https://github.com/microsoft/pg_durable) and [user guide](https://github.com/microsoft/pg_durable/blob/main/USER_GUIDE.md) before recommending adoption or implementation.

## Interactions

- Compose with entry 001 as an overlay; preserve its delivery, service, and repository responsibilities.
- Use `codebase-design` for the application-facing workflow interface and the seam around external compute.
