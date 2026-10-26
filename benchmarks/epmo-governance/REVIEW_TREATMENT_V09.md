# EPMO fictional reviewer-treatment contrast v0.9

**2026-10-26 | Independent public research simulation | Human results: TBD | External actions: 0**

## Why this experiment exists

The v0.8 manual and structured packets contained the same raw case material and differed chiefly by arm label and reversed order. A reviewer-burden difference could not be attributed to a real review aid. v0.9 defines a **single inspectable presentation intervention** while preserving the v0.8 policy oracle, sixteen fictional cases (three valid/thirteen invalid), and previous source and results.

## Predeclared treatments and question

**Question:** Does a derived evidence-comparison worksheet, added to unchanged raw fictional events, reduce false approvals or review time relative to raw event notes? This is a hypothesis, **not a measured effect**.

- **Control — `manual_notes`:** original raw fictional context/candidate events, with instructions to make an accept/reject decision. No precomputed comparison worksheet.
- **Treatment — `structured_packet`:** exactly the same raw events, **same case order and instructions**, plus a deterministic worksheet extracting submission fields, approval fields, prior execution/correction receipts, candidate fields and generic review questions. The worksheet **does not compute a verdict or give a case-specific reason**.
- Both arms share the same policy oracle and case IDs; case ordering is deliberately identical to avoid the v0.8 order/arm confound. The only intended treatment contrast is the additional derived worksheet. More information on screen may itself slow review.
- `review_treatment_v09.py` uses the frozen v0.8 generator/scorer and generates a separate local private gold key bound to the full v0.9 packets. v0.8 artifacts and original evidence remain unchanged.
- Public code and raw cases allow reconstruction of labels. This is **procedural blinding only**, not blinded source code, cryptographic provenance, or independent ground truth.

## Preregistered human-study design — not yet executed

Before collecting responses, freeze an assignment plan, sample-size/power rationale, consent statement, exclusion/missingness policy, stopwatch protocol and analysis script. Assign **independent reviewers between subjects** to exactly one arm using a privately recorded randomized allocation; block by prior governance-review experience where feasible. Do **not** show both arms to the same reviewer or reveal the public oracle/key during review. Keep identities, consent, assignments, case-level responses, times, outreach history and private gold **off GitHub**.

Primary outcome: **false-approval rate per reviewer** among the 13 oracle-negative fictional cases. Secondary: true-approval recall among the three oracle-positive cases; total and median seconds per case; per-case disagreement and missingness. Report arm differences with uncertainty at reviewer level, not case rows treated as independent reviewers. A small convenience sample or zero events cannot justify an efficacy claim. Explicitly report whether the worksheet causes extra time, and keep an `inconclusive` decision available.

**Advance only when** independent, consented human data with preregistered assignment show reproducible benefit and reviewer burden is acceptable. **Reframe** if the worksheet offers no improvement or increases burden; keep a simpler raw-event audit when appropriate. Do not interpret any outcome as production authorization safety, employer productivity, or ROI.

## Reproduce the *software contract*, not a human study

From `benchmarks/epmo-governance`:

```sh
python -B -m unittest -v test_review_treatment_v09
python -B review_treatment_v09.py --demo
python -B review_treatment_v09.py --out /absolute/private/path/outside-any-git-checkout/new-directory
```

The generator rejects an existing output directory or any destination under a Git checkout/worktree. Keep `PRIVATE_gold.json` and all response files private. The public `--demo` prints only treatment counts, hashes, `human_results=TBD`, and `external_actions=0`. Unit-test fabricated perfect/all-denied responses are **scorer arithmetic controls**, never observed reviewers.

## Provenance and gates

- Source: `review_treatment_v09.py`; tests: `test_review_treatment_v09.py`; original oracle: `governance_demo.py` and `blinded_review_preflight_v08.py`.
- Python standard library only; exact hosted Python/OS/commit and CI test counts: **TBD until inspected**.
- Expected deterministic fixture: 16 cases, 3 accepted / 13 rejected by the fictional oracle, identical raw event cases and order across arms, 0 real actions.
- Negative controls: changed raw evidence, changed worksheet, modified instructions, swapped arm, changed gold and duplicate response IDs must fail closed.
- Source authenticity, independent reviewer performance, trusted actor identity, external action receipts and employer ROI: **TBD / not established**.
- Stage remains **Research / Simulation**; draft PR #13 only, no merge, release or deployment.

**Four lenses:** hiring—clear reproducible contrast; technical—check that the aid is derived, not an answer leak; innovation—test human burden rather than assume it; founder—no validated users, adoption, revenue or defensible market claim.

**Next evidence-producing step:** recruit consenting independent reviewers through verified professional routes **only after private Gmail/outreach checks**, freeze sample size and assignment, then privately collect a small preregistered manual-vs-worksheet pilot. Separately complete [Issue #14](https://github.com/Vermicare/Haridas-Satheesh/issues/14) for authenticated sandbox approval safety.
