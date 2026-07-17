---
owner: P_authority / repository maintainer
status: accepted
candidate: 3156cf8869563b9683f5c3ff67b4104d95dc1b40
last_verified: 2026-07-16
review_trigger: New component/dependency, score 4, three scores at 3+, new state/concurrency boundary, or changed public claim
---

# Complexity and risk register

Scores are `0` (trivial) through `4` (highest review need). They prioritize control work and are not quality scores.

| ID | Area | Kind | Score | Trigger | Treatment | Test/evidence | Owner |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| CX-001 | Partner policy evolution | necessary | 3 | New/unknown rule or semantic change | Strict schema, fail closed, versioned compatibility | TEST-POLICY-CONTRACT / EVID-POL-STRICT | P_reliability |
| CX-002 | Cross-process session cap | necessary | 4 | Two callers contend for final slot | One SQLite transaction; single-machine boundary | TEST-BUDGET-CROSSPROCESS / EVID-BUDGET-RACE | P_reliability |
| CX-003 | Duplicate adapter/model paths | accidental | 3 | Wrong factory bypasses hardening | Protect constructed clients; contract tests; defer broad refactor | TEST-UPSTREAM-REST, TEST-UPSTREAM-MCP | P_reliability |
| CX-004 | Per-process circuit state | necessary | 3 | Dependency flaps or half-open race | Frozen state machine, one probe, metrics | TEST-HALFOPEN-RACE / EVID-REL-CIRCUIT | P_reliability |
| CX-005 | Candidate-bound portfolio chain | accidental | 3 | Evidence/render/claim built from different candidate | Hash chain and parity validator | TEST-PORTFOLIO-CLAIMS | P_portfolio |
| CX-006 | Rollback with live SQLite | necessary | 3 | Code regression or corrupt state | Preserve volume; snapshot WAL set; separate restore | TEST-ROLLBACK-STATE | P_operations |

| Dimension | Score | Basis and required control |
| --- | ---: | --- |
| Domain rules | 2 | Exclusion and nullable cap are small but interacting |
| Component coupling | 2 | Two public surfaces share service and contracts |
| Data/state | 3 | Durable TTL/LRU SQLite state requires explicit rollback semantics |
| Concurrency | 4 | Cross-process final-slot correctness is safety-critical |
| Integration | 3 | Two untrusted, separately failing upstreams |
| Security/authority | 2 | Member context and tenant policy; v0 lacks production auth |
| Deployment | 2 | One container target and bind-mounted state |
| Operability | 3 | New metrics, alerts, circuit state, rollback drill |
| Performance | 2 | Two sequential upstream reads with explicit budgets |
| Reimplementation | 3 | Toolchain/evidence render chain must be reproducible |

Because concurrency scores `4`, `IFACE-BUDGET-001`, its failure model, cross-process test, and rollback semantics are mandatory gates.

## Risk register

| ID | Risk | Likelihood | Impact | Trigger/signal | Prevention | Contingency | Owner | Residual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-001 | Partner policy unavailable or untrusted | M | H | timeout/429/5xx/schema failure | strict timeout/circuit/schema; no retry | explicit 502, recover through half-open probe | P_reliability | M |
| RISK-002 | Partner/member IDs disagree | M | H | returned partner differs from policy key | resolve policy only from validated member; audit partner | fail request and investigate upstream contract | P_reliability | L |
| RISK-003 | Policy adds unknown rule | M | H | `additionalProperties` failure | compatibility window and contract test | fail closed; deploy support before activation | P_reliability | L |
| RISK-004 | Two processes exceed session cap | M | H | final-slot test grants two | `BEGIN IMMEDIATE` atomic reserve | stop traffic, retain DB/evidence, forward-fix | P_reliability | L in one-file topology |
| RISK-005 | SQLite volume lost/corrupt | L | H | integrity check or missing `.data` | durable bind, stop-and-snapshot WAL set | restore corruption snapshot; counts may be conservatively unavailable | P_operations | M |
| RISK-006 | Session cardinality/TTL assumptions fail | M | M | 10k saturation, eviction/churn | bounded cardinality and metrics | lower TTL, raise measured capacity, or redesign shared state | P_operations | M |
| RISK-007 | Metrics expose identifiers | L | H | unbounded labels or raw IDs | contract tests and network restriction | disable endpoint, rotate access, remove data | P_operations | L |
| RISK-008 | Range/tag dependency drift | H | H | clean install/image differs | lockfile and immutable digests before runtime evidence | invalidate evidence, repin, rebuild candidate | P_integration | M until locked |
| RISK-009 | Presentation invents unsupported claims | M | H | parity/claim validator failure | exact diagram authority and evidence ceiling | reject/regenerate derivative; keep exact render visible | P_portfolio | L |
| RISK-010 | Dirty README content is overwritten | M | H | portfolio work starts from wrong base | record existing modification and assign sole owner | stop, diff against baseline/user content, reconcile manually | P_portfolio | L |
| RISK-011 | Single-replica v0 is scaled | M | Critical | replicas > 1 or non-shared SQLite | compose/deployment guard and docs | remove extra replicas; do not claim cap correctness | P_operations | L |
| RISK-012 | D5/E6 claimed prematurely | M | H | homepage exceeds evidence index | claim checker; explicit D4/E4 baseline | remove claim and retain failed review event | P_integration | L |

