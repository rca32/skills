# Agent brief contract

An agent brief is the durable behavioral contract attached before an issue or pull request becomes implementation-ready. Prefer interfaces and behavior over file paths and line numbers that can go stale.

```markdown
## Agent brief

**Category:** bug | enhancement
**Summary:** one-line outcome

### Current behavior

What happens now, including the verified failure or product gap.

### Desired behavior

What must happen after the change, including edge cases and failure behavior.

### Key contracts

- Public interface or domain concept — required behavioral change
- Data or configuration shape — compatibility expectations

### Acceptance criteria

- [ ] Independently observable criterion
- [ ] Regression or compatibility criterion
- [ ] Required verification succeeds

### Blockers

- Native dependency references, or `None`

### Out of scope

- Adjacent behavior that this issue must not change

### Verification evidence

- Reproduction, inspection, or command and its result
```

For a pull request, describe the current state of the diff and the remaining gaps. Do not rewrite the request as if no code exists.

A brief is incomplete when it relies on phrases such as “works correctly,” gives only implementation steps, omits negative or compatibility behavior, or cannot be verified without guessing the intended result.
