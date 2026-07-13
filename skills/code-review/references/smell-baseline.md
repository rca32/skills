# Design smell baseline

Use this catalogue as a secondary review heuristic, not as repository law. A
documented repository rule always wins, and every smell remains a judgement call.
Report one only when it appears in the reviewed change and has a concrete cost.

- **Mysterious Name** — A function, variable, or type does not reveal its purpose.
  Prefer a revealing name; inability to name it may indicate a muddled design.
- **Duplicated Code** — The same logic shape appears in multiple changed places.
  Consolidate the shared behavior when that reduces divergent maintenance.
- **Feature Envy** — A method works more with another object's state than its own.
  Consider moving the behavior toward the state it uses.
- **Data Clumps** — The same group of values repeatedly travels together. Consider
  introducing a type that names and validates the concept.
- **Primitive Obsession** — A primitive or string represents a domain concept with
  behavior or invariants. Consider a small domain type.
- **Repeated Switches** — The same conditional dispatch recurs for the same cases.
  Centralize dispatch or use an appropriate polymorphic boundary.
- **Shotgun Surgery** — One logical change requires scattered edits across many
  modules. Move the volatile decision behind one owned interface.
- **Divergent Change** — One module changes for several unrelated reasons. Split
  responsibilities only when the change demonstrates distinct owners.
- **Speculative Generality** — Abstraction, parameters, or hooks serve no current
  requirement. Remove or inline them until an evidenced need appears.
- **Message Chains** — A caller navigates a long object chain and becomes coupled
  to its structure. Hide the navigation behind an owning method.
- **Middle Man** — A type or function mainly delegates without adding policy,
  translation, or protection. Consider calling the real owner directly.
- **Refused Bequest** — A subtype ignores or defeats much of the inherited
  contract. Prefer a narrower interface or composition.

## False-positive controls

- Do not flag code outside the review scope unless the change makes it newly
  reachable or worsens it.
- Do not flag repetition merely because two small expressions look alike; require
  a shared reason to change.
- Do not recommend a new type or abstraction without a demonstrated invariant,
  coupling, or maintenance cost.
- Do not flag generated code, fixtures, migrations, or compatibility adapters
  when repository policy intentionally permits the shape.
- Do not duplicate a tooling diagnostic. Cite the actual tool failure if it is
  relevant to the review.
