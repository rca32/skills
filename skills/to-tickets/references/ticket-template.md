# Ticket template

```markdown
<!-- to-tickets:v1 source=<parent identifier> revision=<source fingerprint> key=<draft key> -->

## Parent

<Planning issue or approved spec reference>

## Outcome

The narrow end-to-end behavior this ticket makes work from a user or operator perspective.

## Acceptance criteria

- [ ] Independently observable behavior
- [ ] Failure, safety, or compatibility behavior where relevant
- [ ] Focused verification that must pass

## Blocked by

- <Draft key or tracker identifier>, or `None`

## Out of scope

- Adjacent work intentionally excluded from this slice

## Source traceability

- Requirement or acceptance criterion from the approved source
```

Ticket titles should describe the delivered outcome, not a layer or activity. Avoid implementation file paths and line numbers. Include a short interface or state-machine shape only when the approved source made it part of the contract.
