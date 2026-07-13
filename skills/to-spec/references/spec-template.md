# Spec template

```markdown
# <Outcome-oriented title>

## Status and sources

- Status: draft | approved | blocked on open questions
- Source conversation or parent issue:
- Relevant domain or architecture decisions:

## Problem

Describe the user-visible or operational problem and evidence that it exists.

## Desired outcome

Describe the successful result without prescribing internal implementation.

## Actors and scenarios

1. As a <specific actor>, I want <behavior>, so that <benefit>.

Include normal, failure, recovery, permission, and compatibility scenarios only when they are relevant.

## Behavioral requirements

- Required behavior and edge cases
- Error, safety, and compatibility behavior
- Data or interface contracts that are already decided

## Implementation decisions

- Approved architectural or ownership decisions
- Constraints that implementations must preserve

## Testing decisions

- Highest public seam:
- Existing test precedent:
- Required negative and regression coverage:

## Acceptance criteria

- [ ] Observable product or system outcome
- [ ] Observable failure or compatibility outcome
- [ ] Required verification evidence

## Out of scope

- Explicitly excluded adjacent work

## Assumptions

- Assumption supported strongly enough to proceed

## Open questions

- Unresolved question — impact if unanswered
```

Omit empty scenario categories, but never omit material unknowns. A long list is not a substitute for traceability or observable criteria.
