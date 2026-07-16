# Section B2 — Required Reasoning Question

| Metadata | Value |
| --- | --- |
| Owner | Repository maintainer |
| Status | Accepted canonical response |
| Baseline candidate | `5b2fc6f80e7714d0af5459fa2b9d3a30b1c28896` |
| Last verified | 2026-07-16 |
| Review trigger | Session-budget transaction, SQLite schema, concurrency test, or rollout-claim change |

A concrete plausible-but-wrong AI implementation in this domain is a split session-budget reservation. The AI first queries how many recommendation slots remain, returns that value to the filtering loop, and later issues a separate query that increments the used count. Each query looks correct in isolation, but the pair is not one transaction.

Suppose a partner cap is three and the session has already used two slots. Request A and request B arrive concurrently. Both read `used = 2`, both conclude that the final slot is available, and both return a recommendation before separately writing `used = 3`. The stored count can still look valid even though the partner received four recommendations. This is especially dangerous because a simple final-database assertion would miss the business-policy violation.

The detection test starts with `used = cap - 1` in a real temporary SQLite file, then launches two independently spawned processes so they do not share an in-process Python lock. A barrier releases both contenders at the same time. Each calls `reserve(..., requested=1)`. The test asserts:

- the sorted grants are exactly `[0, 1]`;
- the persisted `used` value equals the cap;
- the sum of recommendations returned by both contenders is one;
- both processes exit cleanly within a bounded timeout.

The corresponding code-review invariant is that `BEGIN IMMEDIATE` occurs before the row is read and that the remaining calculation, granted calculation, upsert, and commit all remain inside that same transaction. There must be no public `remaining()`-then-`consume()` call sequence in the recommendation path.

The mitigation is a combination of one atomic reservation API, a cross-process regression test, repeatable concurrency evidence, and review language that distinguishes same-machine SQLite coordination from distributed multi-replica consistency. Never build or claim distributed guarantees that have not been engineered and verified.
