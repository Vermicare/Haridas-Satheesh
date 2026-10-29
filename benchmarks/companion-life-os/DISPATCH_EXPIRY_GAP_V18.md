# Companion v1.8 — pending-work expiry-at-dispatch negative control

**Status (2026-10-29): cross-platform fictional negative control VERIFIED.**
**Maturity:** no advancement. This is a local SQLite simulation, not a real service, authenticated user, or live permission system.

## Question and predeclared decision

Can the v1.4 fictional atomic adapter guarantee that an approval is still unexpired when a previously staged task is dispatched? Its signed boundary checks a test-supplied `now` when creating a receipt and staging work, but `AtomicFictionalDelivery.dispatch(nonce)` accepts neither a clock nor a signed approval. The outbox persists an approval digest, not an authenticated expiry assertion available to the dispatcher.

**Expected negative control:** a fixture whose approval expires at 11:00 UTC is staged at 10:30 UTC; the signed boundary rejects a new execution at 11:00, while the old dispatcher can still insert one *fictional* sink row without observing any dispatch-time clock. The test does **not** wait for a real clock transition; it compares two API contracts using explicitly declared fictional timestamps. This is a missing enforcement mechanism, not a timed physical experiment.

## Reproduction

Run from `benchmarks/companion-life-os`:

```bash
python -m unittest -v test_dispatch_expiry_gap_v18
python demo_dispatch_expiry_gap_v18.py
```

Uses only Python standard library and the repository's fictional fixture. Four controls: new staging at expiry must fail with no receipt; prior staged work still dispatches through v1.4 after a hypothetical expiry; the dispatcher has no time/token parameter; revocation still blocks pending dispatch. All simulated actions remain inside disposable SQLite databases.

## Interpretation and remedy gate

A grant's validity at staging does **not** establish its validity at later dispatch under an expiry-at-effect policy. Before any real connector, freeze the policy (expiry at staging versus expiry at effect), use a separately trusted clock, bind verified expiry and grant identity to durable work, enforce policy at the **actual effect boundary**, and retire/isolate every legacy dispatch and direct-database-write path. A new Python wrapper alone is insufficient; the already verified v1.7 legacy bypass remains.

**Prior art for design comparison, not a claim of compliance:** [RFC 9068 section 4](https://www.rfc-editor.org/rfc/rfc9068.html#section-4) requires OAuth JWT resource servers to validate token expiry at use. The fictional approval here is **not** an OAuth JWT, so this is an analogy for a chosen expiry-at-effect policy, not a normative requirement automatically applicable to this prototype.

**Advancement:** none until independent tests establish an enforced, isolated, fail-closed effect boundary with real authenticated consent and trusted time. **Stop/reframe:** keep advisory-only if legacy writers or effects cannot be isolated. Human reviewer burden, real connector behavior, physical clock and operational safety: **TBD**. No employer data, secrets, human contact, release, patentability or product claim.

## Hosted execution record — October 29, 2026

[Final code-head GitHub Actions #40836954512](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40836954512) completed successfully at commit `1c8afc90c581bf73c185042a64fd8470f7126d1c`. Inspected both job logs: **139/139** regression tests passed on Ubuntu and **139/139** on Windows, including **all four** v1.8 controls on each system. Both independently executed v1.8 JSON demonstrations reported `success=true`, `tests_run=4`, `real_external_actions=0`. Both artifact uploads succeeded ([Ubuntu](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40836954512/artifacts/12881007004), [Windows](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40836954512/artifacts/12880997154)); ZIP bytes were **not** independently downloaded/inspected. This is **negative evidence** about the older adapter, not proof of safe expiry enforcement. The legacy dispatch and direct-database-write bypasses remain.
