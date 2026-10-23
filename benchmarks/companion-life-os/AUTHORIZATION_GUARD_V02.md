# Companion Intelligence — authorization negative controls v0.2

**Evidence boundary:** Synthetic, standalone, standard-library contract tests only. No authenticated human, real connector, private Life OS code, durable store, real consent, or external action. **Maturity remains In Progress / private implementation.**

## Why this experiment exists

The committed [v0.1 validator](validator.py) accepts a grant when its authorization ID, decision ID and requested scope match. It does **not** inspect the grant's `approved_by` value or remember whether it was previously used. Two executable **negative controls** in [the regression tests](test_authorization_guard_v02.py) demonstrate that a fictional attacker-named grant and a second use of the same grant both return `True` from v0.1 `can_execute`. These are contract gaps in a synthetic demo, **not** evidence of an exploit in the private implementation.

The new [v0.2 guard](authorization_guard_v02.py) additionally requires a caller-supplied trusted fictional principal, a machine-readable decision scope, matching evidence approvals, a bounded validity interval, and a nonce that has not yet been consumed in this Python process. The original v0.1 validator and fixture remain unchanged. The test builds its extended fixture in memory.

## Reproduce in 30–90 seconds

Python 3.10+ standard library only. From `benchmarks/companion-life-os/`:

```bash
python -m unittest -v test_authorization_guard_v02
python demo_authorization_guard_v02.py > demo-v02.json
```

Local execution on 2026-10-24, CPython 3.13.5 / Linux: **16/16 tests passed**; fictional one-time action accepted, replay/spoof/expiry cases **3/3 blocked**. GitHub-hosted CI: **TBD until observed**. Output includes `external_actions: 0`; it is a hardcoded design property, not a measurement of a real connector.

## Provenance / experiment registry

- Baseline: [`validator.py`](validator.py), Git blob `ca0a3dbd2fba2ab1a7f55d978a13d7202f56cda0`.
- Fixture: [`scenario.json`](scenario.json), Git blob `c703e17ccccf11c76867d2e5c2e4c7e9d0f8d40f`.
- Method: deterministic fictional scenario; no RNG/seed, no external dataset, no dependency beyond Python.
- Question: can a proposed simulation gate reject replay, actor mismatch, expired grants and changed scopes while preserving the original baseline's negative evidence?
- Metrics: 16 unit checks; 3 demonstration rejection cases; simulated external actions.
- Result: 16/16 local tests passed, 3/3 fictional demonstration cases rejected, 0 real actions.
- Unknown: identity authentication, atomic nonce persistence, crash recovery, concurrency, production latency, correction/reversal effectiveness, user trust, security review = **TBD**.

## Failure/learning and stage decision

The baseline's `can_execute` returns `True` for spoofed `approved_by` and replay because those properties were not part of its contract. The new guard's `trusted_principals` is **caller-supplied**, not an identity provider; both the fictional approval and its timestamp can be forged. The nonce set is process-local, non-atomic and resets after restart. Natural-language decision intent is not cryptographically bound. This is not a secure authorization system.

**Decision: retain as Simulation / contract testing; no maturity upgrade or release.** Advance only after independent review and an authenticated, durable sandbox adapter demonstrates identity binding, atomic one-time consumption, expiry, idempotency, interrupted execution recovery and correction receipts. Reframe if these boundaries cannot be enforced without disproportionate review/operational cost.

## Four reviewer lenses

- **Hiring manager:** runnable adversarial tests; no claim of deployed governance.
- **Technical reviewer:** exact failure modes and reproducible contracts; real identity, storage and concurrency are absent.
- **Innovation leader:** reusable bounded-action pattern across Companion, CORTEX and EPMO; no proven integration.
- **Founder:** potential governance primitive, but users, costs, liability, buyer demand and operational value remain **TBD**.

No private outreach tracking, employer information, personal records or production credentials are included.
