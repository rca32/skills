---
name: apply-architecture-playbook
description: Apply a user-authored dictionary of preferred architecture patterns to a concrete system, distinguish taste from evidence and hard constraints, select fitting defaults and explicit exceptions, and produce a preference brief for later design or specification. Use only when the user explicitly invokes $apply-architecture-playbook or explicitly asks to apply their personal architecture playbook before designing a new system, evaluating an existing architecture, or comparing approved technology directions. Do not use as universal best practice, for module-interface or seam design, requirements invention, implementation, or completed-change review.
---

# Apply Architecture Playbook

Treat every entry as an explicit owner preference, not a claim of universal optimality. Use a preference to choose a default only after it fits the system's actual constraints; expose deviations instead of forcing the preferred shape.

## Authority and composition

Run this as a read-only preference application workflow. Inspect authorized context and return a brief in the conversation by default. Do not edit architecture documents, code, tracker state, or the dictionary itself; do not commit, push, or publish.

Apply authority in this order:

1. law, safety requirements, and consuming-repository instructions;
2. current explicit user direction within that user's decision authority;
3. accepted product behavior, architecture decisions, and operational constraints not explicitly superseded by their owning authority;
4. observed workload and system evidence;
5. this playbook's applicable preferences;
6. generic convention or popularity.

When authorities conflict, name the conflict and keep the preference unapplied unless the authority that owns the decision accepts a change. Do not convert an explicit invocation into blanket permission to replace an accepted architecture.

An explicit user choice may override the playbook's ranking, but it cannot override evidence labeling. Record a knowingly chosen mismatch as a user-mandated deviation rather than calling it a fit.

- Use an explicitly invoked `first-principles` pass when the problem framing or inherited constraint itself must be challenged.
- Pass the resulting preference brief to `codebase-design` when module interfaces or architectural seams remain open; that skill owns their comparison and recommendation.
- Pass only accepted architecture decisions to `to-spec`. A playbook match is not acceptance by itself.
- Use `documenting-work` when the user explicitly asks to persist an accepted architecture decision.

Time-sensitive claims about libraries, extensions, supported versions, managed services, or operational maturity are evidence, not preferences. Revalidate them against primary sources before an adoption decision. If verification is unavailable, keep the affected match conditional.

## Frame the system

Record only the context that can change entry selection:

- system purpose, maturity, and existing architecture;
- workload shape, scale, latency, consistency, and availability needs;
- data ownership and transaction boundaries;
- synchronous, asynchronous, scheduled, and long-running work;
- failure recovery, idempotency, checkpoint, and audit needs;
- deployment platform, database privileges, extension limits, and operational capacity;
- team skills, delivery constraints, dependencies, and required integrations;
- accepted decisions and the authority allowed to change them.

Inspect available artifacts before asking questions. When context is sparse, state provisional assumptions and continue only to a conditional result.

Framing is complete when hard constraints, important unknowns, and the architectural decision being influenced are explicit.

## Dictionary index

Load only entries whose `Use when` conditions plausibly match the framed system.

| ID | Kind | Entry | Default status |
| --- | --- | --- | --- |
| 001 | Base | [Rust + PostgreSQL layered monolith](references/001-rust-postgres-layered-monolith.md) | Preferred |
| 002 | Overlay | [PostgreSQL-native durable workflows](references/002-postgres-durable-workflows.md) | Conditional; maturity-sensitive |

A base entry supplies the starting system shape. An overlay changes one concern without replacing the base. Multiple entries may compose only when their ownership and operational costs do not conflict.

Treat component and layer names in entries as conceptual responsibility roles. Do not turn them into mandatory packages, interfaces, or seams; leave that concrete mapping to `codebase-design`.

## Match entries

For each candidate entry:

1. Check every hard prerequisite and disqualifier.
2. Trace the preference to the concrete concern it simplifies or protects.
3. Separate established fit from assumed fit and current product facts.
4. Identify the cost transferred to the database, application, deployment, operators, or future migration.
5. Apply its escape triggers: name the evidence that would cause extraction, replacement, or a different default.
6. Check interaction with the selected base, overlays, accepted architecture, and external dependencies.

Do not select an entry because its stack resembles the prompt. A match must explain why its operating model fits. Do not invent a new preference to fill a catalog gap; report the gap plainly.

Choose one result for each candidate:

- **Apply:** prerequisites and evidence support the preferred default.
- **Apply conditionally:** the preference fits if named assumptions or current technology facts hold.
- **Defer:** missing evidence prevents a responsible choice.
- **Deviate:** a hard constraint, measured mismatch, or lower-complexity option defeats the preference.

Entry matching is complete when every result names its evidence, assumptions, costs, and reversal trigger.

## Compose the preferred shape

Start with at most one base entry, then add only overlays that solve a present requirement. Keep components out until a named need earns their operational and cognitive cost.

For an existing system, prefer the smallest compatible application of an entry. State migration pressure without treating a rewrite as the default. For a new system, select the smallest preferred starting shape and defer scale-driven components until their trigger is observable. When no entry fits, return `No playbook match` rather than disguising generic advice as owner preference.

The composed shape is a preference proposal. Mark it `accepted` only when current user or repository authority explicitly accepts that choice; otherwise mark it `proposed` or `conditional`.

## Return the preference brief

Return the smallest brief that later design work can consume:

1. decision in scope, hard constraints, and material unknowns;
2. selected base and overlays with `Apply`, `Apply conditionally`, `Defer`, or `Deviate` results;
3. preferred system shape and conceptual responsibility allocation, without fixing concrete module interfaces or seams;
4. preference-versus-evidence ledger, including time-sensitive facts;
5. deliberate deviations, operational costs, and escape triggers;
6. unresolved interface, seam, requirement, or acceptance questions and their owning workflow;
7. resolution state: `accepted`, `proposed`, `conditional`, or `No playbook match`.

Write in the user's language and preserve established project terminology.

The brief is complete when another workflow can tell exactly which choices came from owner taste, which came from evidence or authority, what was deliberately excluded, and what would reverse the selection.

## Extend the dictionary

Treat dictionary changes as skill maintenance, not as runtime application. Add an entry only from an explicit user-authored or user-approved preference. Give it a stable ID, kind, status, one-line default, use and avoid conditions, preferred shape, responsibility boundaries, costs, escape triggers, interactions, and dated facts requiring revalidation. Add one directly disclosed reference and one index row; do not duplicate the entry body elsewhere. Use the repository's skill-authoring and validation workflow for every change.
