# Durable Behavior Tests

## Prefer observable contracts

A durable test reads like a caller-facing specification and survives internal refactors.

```typescript
test("a valid cart can be checked out", async () => {
  const cart = createCart([{ sku: "A", price: 10 }]);
  const result = await checkout(cart, approvedPayment());

  expect(result.status).toBe("confirmed");
});
```

Avoid tests whose contract is an internal call:

```typescript
test("checkout invokes the payment helper once", async () => {
  await checkout(cart, payment);
  expect(paymentHelper.process).toHaveBeenCalledTimes(1);
});
```

The second test can fail after a harmless refactor even when checkout behavior is unchanged.

## Verify through the public seam

If the public contract says a created record can be retrieved, verify it through that contract. Querying internal storage directly couples the test to a persistence detail unless storage itself is the seam under test.

## Use independent expectations

Do not reproduce the implementation in the assertion:

```typescript
// Tautological: the expected value repeats the likely algorithm.
const expected = items.reduce((sum, item) => sum + item.price, 0);
expect(calculateTotal(items)).toBe(expected);

// Independent worked example.
expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
```

Prefer specification examples, known literals, protocol fixtures, or an independent trusted oracle.

## Keep one logical behavior per slice

One test may need several assertions to describe a single result, but it should have one reason to fail. Split unrelated behavior into later red-green-refactor cycles.
