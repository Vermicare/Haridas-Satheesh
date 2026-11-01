# Companion v2.0 — dynamic fictional legacy-effect reachability (negative evidence)

**Date:** 2026-11-01. **Public evidence stage:** Research / Simulation (fictional software only), **unchanged**; private implementation maturity **TBD**. **Scope:** public, disposable local SQLite fixtures; no network, real user, production service, physical action or external connector.

## Question and falsifiable experiment

The v1.9 [static entry-point inventory](companion_entrypoint_inventory_v19.py) identified four legacy callable routes outside the newer signed/revocable fictional authorization boundary. Static analysis alone did not establish that these functions could actually write fixture state. The v2.0 [dynamic regression suite](test_legacy_runtime_reachability_v20.py) now invokes each route independently, using **synthetic** records and temporary SQLite files, and checks the resulting database state. These are deliberately **passing tests of an unsafe-to-expose architectural property**, not proof of a security fix.

| Public fictional entry point | Tested observation | Limitation |
| --- | --- | --- |
| `FictionalDurableStore.execute` | Creates a receipt with fictional principal and clock, without a signed token | Not a production identity or authorization test |
| `FictionalOutbox.stage` | Stages an unsigned, directly seeded fictional receipt | Requires fixture database access; no production reachability established |
| `FictionalOutbox.dispatch` | Delivers that staged receipt to a separate fake SQLite sink | Simulated action only; no external connector |
| `FictionalIdempotentSink.apply` | Directly creates a fake sink row without a receipt | Input is a locally constructed synthetic payload |

Two additional rejection controls confirm the fake sink and outbox still reject explicit nonfictional payload/receipt flags. **They do not repair the four legacy paths.** The v1.8 dispatch-time expiry gap also remains open.

## Executed evidence and provenance

- [GitHub Actions #41332371384](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/41332371384), final source/workflow head `9df9e20579b5282a04cb56114c2803a78c6a2a24`, completed **SUCCESS** on Ubuntu and Windows on 2026-11-01.
- Both original job logs were independently inspected: **155/155 tests passed on Ubuntu; 155/155 passed on Windows**, including **6/6 new v2.0 tests** on each host. The [workflow](../../.github/workflows/companion-authorization-v02.yml) explicitly invokes the new suite.
- The [30-second demonstrator](demo_legacy_runtime_reachability_v20.py) ran on both hosts and emitted `demo-v20-legacy.json` with `passed=true`, `tests_run=6`, `real_external_actions=0`, and four named routes.
- Original workflow artifacts: Ubuntu `13093153150`, Windows `13093013899`, retained through **2027-01-30** according to GitHub. Logs and artifact metadata were inspected; downloaded artifact ZIP bytes were **not independently rehashed** in this run.
- Exact file Git blob SHAs at verification: test `4e81dad3e44199580bca962156316187430b87f5`; demo `96ce51d218f2d5e45060c139d97d242e5a3dfe9a`; workflow `2a86b67d40868f5b2f5b2b4db95d9b9ca614fdda`.

Reproduce from `benchmarks/companion-life-os`:

```sh
python -m unittest -v test_legacy_runtime_reachability_v20
python demo_legacy_runtime_reachability_v20.py
```

No private accounts, personal data, real messages, authenticated identity, trusted effect-time clock or external writes were used. No claim of an exploitable production vulnerability is supported.

## Decision, next experiment and stop rule

**Decision:** the v1.9 static finding is now supported by runtime evidence in a disposable **fictional** harness. This increases confidence that the public test code contains multiple effect-like entry points that are not gated by the newer signed/revocable boundary. It does **not** establish that any route is reachable in the private Companion implementation.

**Strongest evidence:** both operating systems reproduced all four fictional legacy writes and two negative controls; original v1.9 inventory and prior revocation/expiry experiments remain preserved.

**Largest gap:** a single deny-by-default effect boundary that cannot be bypassed through legacy routes; authenticated human identity/approval, trusted dispatch-time expiry, external adapter semantics and independent review remain **TBD**.

**Next experiment:** build a separately isolated fictional adapter with **no public direct sink writer**, and use dynamic tests to show that all four legacy entry points fail to reach the adapter's fake effect state. Then inject revocation, expiry, crash and concurrency. Do not migrate real connectors or assert real-world safety.

**Kill/reframe:** if legacy writers cannot be isolated, retain advisory/read-only Companion functionality and stop claims of bounded autonomous execution.

**Four lenses:** hiring manager—transparent negative findings and cross-platform regression; technical reviewer—runtime test coverage does not prove closed-world reachability; innovation leader—no novelty or patentability claim; founder—no real authorization, users, deployment, revenue or external action.

No maturity advance, release, merge or security certification.
