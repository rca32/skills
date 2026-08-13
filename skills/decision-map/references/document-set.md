# Decision-map document set

Use these shapes only after `documenting-work` selects repository persistence and a destination. Follow an established consuming-repository format when it differs.

## Map entry point

```markdown
---
document_id: "decision-map:<source-key>:<slug>"
kind: "decision-map"
title: "<map title>"
status: "draft|active|blocked|ready-for-spec"
authority: "repository"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---

# <Map title>

## Destination

<One or two sentences describing the artifact or settled outcome this map must make possible.>

## Current

- [D001 — <decision name>](decisions/D001-<slug>.md)

## Open decisions

- [D002 — <decision name>](decisions/D002-<slug>.md)

## Decisions so far

- [D000 — <decision name>](decisions/D000-<slug>.md) — <one-line gist>

## Not yet specified

- <in-scope area that cannot yet be phrased as a precise question>

## Out of scope

- <excluded area> — <reason>
```

Keep exactly one `Current` link while the map is active. Omit empty lists only when the map status makes their absence unambiguous. Never copy the resolution body into the map.

## Decision document

```markdown
---
document_id: "decision-question:<source-key>:<map-slug>:D001"
kind: "decision-question"
title: "<decision name>"
status: "open"
question_kind: "research|discussion|prototype|prerequisite"
map: "decision-map:<source-key>:<slug>"
map_projection: "not-applicable"
decision_authority: "<person, repository authority, or evidence class>"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---

# <Decision name>

## Question

<One precise question whose answer changes the route to the destination.>

## Why now

<What this answer clarifies or unblocks.>

## Constraints and evidence

- <authoritative pointer or observed fact>

## Resolution

<Settled answer, or the exact missing answer/evidence while still open.>

## Consequences

- <newly clear decision, spec effect, or scope effect>

## Rejected alternatives

- <alternative> — <reason>
```

Use `resolved` only with an explicit authority and evidence pointer. When resolving, first persist `map_projection: "pending"`; change it to `current` only after the map and index updates are read back. This field makes a partial projection failure discoverable by the next session without copying the resolution. Use `out-of-scope` when the question lies beyond the destination; state why and link it from the map's matching section.
