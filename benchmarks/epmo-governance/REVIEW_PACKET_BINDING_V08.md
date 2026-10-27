# EPMO — reviewer packet/oracle binding v0.8 (fictional)

**Date:** 2026-10-26. **Stage:** Research / Simulation. **Human results:** TBD. **External actions:** 0.

## Failure hypothesis and before-fix negative control

The v0.7 private scorer checked the packet's **case IDs** against the private gold key, but did not check the evidence attached to those IDs. An edited candidate actor, context scope, or reviewer instruction could therefore be scored against the original answer key without any mismatch. This is an **integrity gap in a fictional research evaluation**, not a production authentication vulnerability. A regression-test commit (`e897f67cb69116f4f9ab37d2a2d450d830113de9`) introduced three failing-intent tests on v0.7; no CI failure is claimed until its logs are inspected.

## Isolated v0.8 correction

The original [v0.7 generator](blinded_review_preflight_v07.py), tests, results and prior CI evidence are preserved. The new [v0.8 generator/scorer](blinded_review_preflight_v08.py) adds two SHA-256 fingerprints to the **private** gold key, one for each complete review packet (including every context event, candidate, order, instructions and arm). The scorer refuses missing, swapped or mismatched bindings and malformed label types before calculating scores.

[Adversarial v0.8 tests](test_blinded_review_preflight_v08.py) include edits to a candidate actor, historical context scope, instruction text, missing/swapped packet binding and a non-boolean gold label. The binding catches accidental and unilateral packet mutation; because the public code and private key are not signed or externally attested, a party able to alter both packet and gold can forge a consistent pair. **Do not claim cryptographic authenticity.**

## Reproduction (standard library only)

From `benchmarks/epmo-governance`:

```sh
python -B -m unittest -v test_blinded_review_preflight_v07 test_blinded_review_preflight_v08
python -B blinded_review_preflight_v08.py --out /path/outside/repo/new_private_packet_dir
```

For private scoring use `blinded_review_preflight_v08.py --score --packet ... --gold ... --response ...`. Never commit `PRIVATE_gold.json`, response files, participant identifiers or outreach history. The v0.8 key and packets must be generated together; old v0.7 keys are intentionally incompatible.

## Predeclared gate and limitations

**Pass:** v0.8 tests pass on Linux and Windows, both arms have matching immutable key hashes, deliberate evidence mutations fail closed, and the old v0.7 test suite still passes. **Fail:** any changed packet is silently scored, private key schema is ambiguous, or prior v0.7 behavior regresses.

The two v0.8 packets still differ mainly in order and arm label; they do **not** constitute experimentally differentiated manual-vs-structured review treatments. Any claim that structure reduces review burden would be invalid until distinct interventions, independent assignment, learning/carryover controls and consenting human observations are specified. Reviewer time, false-approval rates, intervention effect, employer ROI and deployment remain **TBD**.

**Next highest-value experiment:** preregister genuinely different review aids and randomized independent reviewer assignment, then obtain consented blinded observations with protected response storage. Separately pursue [Issue #14](https://github.com/Vermicare/Haridas-Satheesh/issues/14) for trusted identity/time/outbox safety. No merge, release, external action or maturity advancement is justified by this change.
