# Companion v1.0 — fictional signed-issuer sandbox experiment (prospective protocol)

**Scope:** draft PR #10 only; synthetic task due-date update, no external connector, human authentication, employer data, or private Life OS code. Existing v0.1–v0.9 artifacts and verified CI must remain intact.

**Question:** Does separating a test-harness identity attestation from a scenario-bound approval attestation reject impersonation, token tampering, wrong connector/scope, expiry, and scenario mutation before the existing SQLite v0.3 simulated receipt path?

**Frozen fixture:** committed `scenario.json` plus the v0.3 store. Public test-only HMAC-SHA256 keys, distinct for identity and approval. Exact canonical JSON bytes are signed; duplicate claim keys and noncanonical base64url are rejected. Both signed claims carry an explicit fictional audience and time window. Approval binds SHA-256 of the complete fictional scenario, decision, nonce, connector, scope, principal and expiry. The verifier derives the principal from the signed identity claim rather than accepting a caller-provided string. A fake test clock is supplied by the harness.

**Predeclared controls:** valid first simulated receipt; replay after SQLite reopen; 12 concurrent attempts yield exactly one stored receipt; unsigned/altered identity or approval; alternate signed identity; modified scope, scenario or connector; identity/approval expiry; wrong signing key; duplicate JSON claim key. All rejections must occur before inserting a receipt.

**Metrics:** unit-test pass/fail, simulated receipt count, duplicate simulated effects (expected zero), external actions (expected zero). Human reviewer burden, real authentication, clock trust, power-loss safety, security guarantees and production performance: **TBD**.

**Advance only if:** source, tests, demo and cross-platform logs are preserved; negative controls pass on both OS targets and an independent reviewer accepts the threat-model boundary. Even then this remains a fictional software-contract result, not a product-stage upgrade.

**Kill/reframe:** if an invalid signed claim reaches the simulated store, if concurrent attempts produce more than one new receipt, or if identity/clock assumptions are misrepresented, retain read-only advisory behavior and fix the contract before further integration.

**Threat boundary:** HMAC is symmetric and both public keys are deliberately test-only. The fixture issuer can mint arbitrary fictional subjects and the verifier possesses signing secrets. This is **not** human authentication, independent identity proof, trusted time, real consent, tamper-proof storage, exactly-once external delivery, or evidence of a deployed Life OS.

**Provenance:** planned on 2026-10-27 against draft PR #10 head `c77705cfbc47b5fa4f928e7fc2a0c173995591bf`; executable and CI results remain **TBD until independently published and verified**.
