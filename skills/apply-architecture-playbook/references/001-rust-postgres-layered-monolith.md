# 001 — Rust + PostgreSQL layered monolith

**Kind:** Base

**Status:** Preferred

**Tags:** Rust, Tokio, Axum, Tower, rustls, tracing, SQLx, PostgreSQL, layered monolith, simplicity

## Default

Start a medium-sized transactional backend as stateless Rust application replicas around one PostgreSQL system of record. Keep delivery, business policy, and data access in distinct layers, and add infrastructure only after an observed requirement earns it.

```text
Tokio + Axum + Tower + rustls + tracing
                  │
         HTTP / scheduler / worker
                  │
               Service
                  │
              Repository
                  │
          SQLx + PostgreSQL
```

## Use when

- The service is primarily transactional HTTP with roughly tens to low hundreds of endpoints.
- Correctness, maintainability, explicit SQL, and predictable operations matter more than the fastest prototype.
- Most durable state shares one ownership and transaction boundary.
- The team can operate PostgreSQL and stateless application replicas.
- Independent service deployment and heterogeneous data stores are not established requirements.

## Preferred responsibilities

### Delivery layer

- Let HTTP handlers, schedulers, and workers translate transport input into service calls and service results into transport output.
- Keep framework-specific behavior thin so transport changes remain local.
- Use Tower-style middleware for cross-cutting transport concerns and tracing for structured observability.

### Service layer

- Own authorization, validation, business invariants, transaction orchestration, cache policy, and background-work initiation.
- Present use-case-oriented operations rather than exposing database mechanics to delivery code.

### Repository layer

- Own SQL and data access only.
- Keep business rules, caches, and external API calls out of repositories.
- Prefer explicit SQL through SQLx over an ORM that hides query behavior.

### PostgreSQL and application process

- Use PostgreSQL first for transactional data, simple coordination, and scheduler leader election through advisory locks when appropriate.
- For short idempotent background work, prefer a small jobs table with `FOR UPDATE SKIP LOCKED` before adding a queue service.
- Put local in-memory caching behind service policy before adopting a distributed cache.
- Serve a colocated web application and static assets from the same service when that materially simplifies deployment and avoids a needless cross-origin boundary.

## Scaling preference

Scale stateless application replicas before splitting services. Extract a service or infrastructure component only when evidence shows a distinct ownership boundary, independent release or reliability need, incompatible scaling profile, security isolation need, or measured bottleneck.

## Avoid or deviate when

- Accepted boundaries require independent deployment, data ownership, or failure isolation.
- Workloads need a specialized store or compute system that PostgreSQL cannot economically serve.
- Ultra-low-latency, extreme write scale, regional autonomy, or regulatory segregation contradicts the shared database shape.
- The team cannot safely operate the required Rust or PostgreSQL stack.
- A simpler language or managed platform better satisfies an unusually small or short-lived system.

## Costs and escape triggers

- Rust compilation and type-level rigor can slow early delivery; reconsider when learning cost dominates the system's expected lifetime.
- PostgreSQL becomes a concentrated dependency; add capacity, replicas, partitioning, or extraction only from observed load and recovery evidence.
- A local cache is replica-local and may be stale; adopt shared caching only when measured reuse and invalidation needs justify it.
- Layering becomes ceremony when a layer only forwards calls. Collapse pass-through code, while preserving the responsibility boundary that keeps transport, policy, and SQL from leaking into each other.

## Interactions

- Add entry 002 only for multi-step, recoverable background workflows; do not replace simple SQL or a small idempotent queue by default.
- Use `codebase-design` to decide concrete module interfaces and seams inside this component-level shape.
