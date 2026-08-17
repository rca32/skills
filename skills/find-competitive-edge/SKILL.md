---
name: find-competitive-edge
description: Analyze why a new or existing service, product, organization, network, person, or organism attracts and retains scarce resources, then identify a narrow, defensible combination of competitive strategy vectors and the evidence needed to validate it. Use when planning a new service's competitive positioning, assessing an offering's competitive advantage or moat, comparing rivals, explaining why participants flock to something, or testing how an entity can survive in a crowded landscape. Do not use for general requirements writing, market-size research alone, financial valuation, module design, implementation, or harmful competitive tactics.
---

# Find Competitive Edge

Treat an edge as a causal system, not a collection of flattering labels. A strategy vector counts only when a capability changes participant behavior or competitor economics in a way that helps the subject acquire, retain, or protect a scarce resource.

## Authority and boundaries

Run this as a read-only strategy analysis. Inspect material the user made available and return the result in the conversation by default. Do not edit product artifacts, persist a strategy document, mutate external systems, or start implementation unless an outer authorized workflow owns that action. If durable output is explicitly requested, use the consuming repository's documentation rules or `documenting-work` when available.

Separate observed capabilities and outcomes from proposed ones. A new service can have a defensible hypothesis, but not an evidenced moat. Verify time-sensitive market claims when current evidence is required and tools are available; otherwise mark them as assumptions with a validation method.

Treat hostile vectors such as violence, sabotage, parasitism, espionage, deceptive lures, and coercive litigation as threat-model lenses only. Never turn them into instructions for harm, intrusion, theft, deception, harassment, or unlawful exclusion. Reject a portfolio that depends on those acts and name a lawful, non-deceptive substitute when one exists.

Use an explicitly invoked `first-principles` pass when the product objective or inherited problem framing itself must be challenged. Use market research as evidence input, not as a substitute for the mechanism analysis. Do not let a recommended portfolio silently become product requirements; pass user-accepted decisions to the appropriate specification workflow.

## Frame the arena

Establish the following before selecting vectors:

1. **Subject:** the entity or concept being analyzed and its present maturity.
2. **Participants and objectives:** the people or systems whose choice matters—including users, buyers, suppliers, contributors, distributors, regulators, or allies—and the progress, protection, or reward each seeks.
3. **Contested resource:** what the subject must accumulate or preserve, such as attention, trust, demand, talent, data, distribution, capital, time, territory, or energy.
4. **Alternatives:** direct rivals, substitutes, internal workarounds, and non-consumption.
5. **Arena and horizon:** the relevant geography, segment, constraints, and period over which survival or advantage matters.
6. **Flocking behavior:** the observable action to explain, such as joining, buying, returning, contributing, recommending, integrating, or refusing to switch.

Inspect available evidence before asking for missing context. When the prompt is sparse, choose explicit provisional assumptions and continue; ask only when different answers would materially change the arena.

Framing is complete when the contested choice, resource, alternatives, and time horizon are explicit.

## Build the evidence map

Record only decision-relevant observations:

- **Observed:** supported by provided data, inspected artifacts, behavior, or an authoritative current source.
- **Reported:** asserted by the user or subject but not independently observed.
- **Inferred:** a causal interpretation with named premises.
- **Unknown:** a claim whose absence could reverse the conclusion.

Distinguish acquisition from retention, value creation from value capture, and current advantage from future aspiration. Popularity, revenue, size, longevity, and uniqueness are outcomes or clues; they are not self-proving strategy mechanisms.

## Scan the strategy vectors

Read [references/strategy-vectors.md](references/strategy-vectors.md) before evaluating candidates. Use the catalog as a search space, not a checklist or an exhaustive ontology. When the strongest evidenced mechanism does not fit a listed vector, name it plainly instead of forcing a match.

For every serious candidate, write the mechanism chain:

```text
capability → changed behavior or economics → resource flow → reinforcement → persistence
```

Reject a vector when the chain contains a missing causal step, merely restates the desired outcome, or relies only on resemblance to a catalog example. For retained candidates, assess:

- fit with the arena and participants;
- evidence that the capability exists or can plausibly be built;
- strength and speed of the resource effect;
- reinforcement or compounding behavior;
- imitation, substitution, and bypass cost;
- operating cost, fragility, ethical risk, and likely counter-moves.

Use qualitative ratings with reasons unless the available data supports calibrated numbers. Do not manufacture precision.

## Compose a narrow portfolio

Prefer the smallest combination that explains a meaningful advantage:

- **Anchor vectors:** one or two mechanisms that directly create or protect the edge.
- **Enablers:** only the few vectors necessary to make the anchors work.
- **Defense:** the mechanism that slows imitation, substitution, capture, or decay.

Explain interactions explicitly. A valuable combination should be more defensible together than each vector is alone. Name conflicts and costs, such as luxury versus affordability, predictability versus surprise, centralization versus decentralized resilience, completeness versus simplicity, or speed versus craftsmanship.

For an existing subject, assess the current portfolio before proposing changes. For a new service, compare two or three plausible portfolios and select a provisional thesis. For direct competitor comparison, hold the arena, horizon, evidence bar, and evaluation dimensions constant. For organisms or non-market systems, translate users and revenue into the actual contested resources without forcing business language onto the case.

Portfolio selection is complete when every chosen vector has a role, mechanism, evidence state, complement, and cost—and deleting any vector would change the thesis.

## Stress-test the edge

Test the selected portfolio against these questions:

1. Why would a participant choose, return to, or contribute to this subject rather than the best alternative?
2. Which scarce capability or asset makes that behavior difficult to reproduce?
3. Can a well-resourced rival copy the visible features while bypassing the underlying mechanism?
4. Does usage, scale, learning, reputation, or ecosystem participation strengthen the edge, weaken it, or leave it unchanged?
5. Who captures the created value, and can a supplier, platform, regulator, or complementor appropriate it?
6. What substitute, counter-strategy, constraint, or trust failure collapses the mechanism?
7. What does maintaining the edge continually cost, and what causes it to decay?

Classify the conclusion:

- **Observed edge:** evidence supports the mechanism and at least one material barrier to imitation, substitution, capture, or decay.
- **Provisional edge:** the mechanism is plausible, but named unknowns could reverse it.
- **Temporary advantage:** the mechanism creates value but is readily copied, substituted, or exhausted.
- **No demonstrated edge:** evidence does not support a causal or defensible distinction.

Do not upgrade the result merely because the strategy combination sounds unusual.

## Return the strategy brief

Return the smallest useful brief in the user's language:

1. arena, participants, alternatives, contested resource, and horizon;
2. the flocking or survival mechanism in one causal sentence;
3. current vector portfolio, with evidence states, when an existing subject is analyzed;
4. recommended portfolio: anchors, enablers, defense, and rejected near-matches;
5. interaction logic showing reinforcement and tension among the chosen vectors;
6. moat verdict and the strongest imitation, substitution, capture, and decay risks;
7. the three cheapest discriminating tests or observations, each with the result that would confirm or reject the thesis.

Express the selected portfolio in one compact table with `Role`, `Vector`, `Evidence state`, `Mechanism`, `Reinforcement or defense`, and `Cost or tension`. Keep rejected near-matches outside the table with one-line rejection reasons.

The analysis is complete when the recommendation is narrow, every selected vector has a traceable mechanism, current facts and aspirations remain separate, harmful tactics are excluded, uncertainty is visible, and the next tests could actually change the verdict.
