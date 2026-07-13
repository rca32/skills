# Mocking at Boundaries

Use a mock when a real system boundary would make a focused test destructive, slow, unavailable, or non-deterministic.

Reasonable boundaries include:

- remote APIs and message brokers;
- clocks, randomness, and schedulers;
- payment, email, and other side-effecting services;
- filesystem or database boundaries when a disposable real instance is impractical.

Prefer real code for modules and collaborators owned by the same application. Mocking those internals tends to freeze implementation structure rather than verify behavior.

## Expose narrow boundary interfaces

Inject a purpose-specific capability:

```typescript
async function reserve(order, inventoryClient) {
  return inventoryClient.reserveItems(order.items);
}
```

This is easier to fake faithfully than constructing a global client inside `reserve`, or mocking a generic request function with path-dependent branching.

## Make fakes honest

- Match the real boundary's success, error, and timeout shapes.
- Assert the resulting public behavior, not every internal interaction.
- Keep fake logic simpler than production logic.
- Use contract tests when drift between the fake and real boundary is a material risk.
