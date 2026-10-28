# CORTEX v0.4 — exact-disagreement triage on fictional reviewer pairs

**Date:** 2026-10-28. **Maturity:** Architecture / R&D (unchanged). **Scope:** synthetic-only, local privacy-minimal *triage*, not semantic agreement, annotation accuracy, reviewer independence, measured correction burden, or external validation. **Human participants:** 0. **External actions:** 0.

## Falsifiable gap and negative control

The earlier [v0.3 pair gate](REVIEWER_PAIR_SEMANTIC_GATE_V03.md) correctly checks source/provenance and semantic **field presence** for two reviewer submissions, but deliberately leaves semantic agreement as `TBD`. Two fictional submissions can therefore both be `pair_ready=true` despite carrying different decision statements for the *same source signature*. Structural readiness must not be interpreted as reviewer consensus.

The additive [v0.4 executable](reviewer_pair_exact_disagreement_v04.py) first invokes the **unchanged v0.3 gate**. For a structurally valid pair it compares only *exact* field values for **uniquely matched** (kind, sorted source IDs, predecessor if a decision) signatures. It reports aggregate counts of exact field matches, mismatches, missing signature groups and ambiguous duplicate-source groups. It never emits source IDs, reviewer pseudonyms, statements, archival record IDs or private paths. Different wordings may mean the same thing; identical wordings do not prove independent agreement. Hence `semantic_agreement`, `human_independence`, `adjudicated_gold` and `correction_burden` remain `TBD` even when exact differences are zero.

## Reproduce

From `benchmarks/cortex` on Python 3.13, standard library only:

```sh
python -B -m unittest -v test_reviewer_pair_exact_disagreement_v04.py
python -B demo_reviewer_pair_exact_disagreement_v04.py
```

The demo uses only the existing author-created fictional fixture. For actual voluntary submissions, use the local-only CLI with the frozen case/archive and two **private** JSON paths, and keep all completed reviewer files and reports outside public Git:

```sh
python -B reviewer_pair_exact_disagreement_v04.py check blind_case_20261024.json blind_archive_20261024.json /private/A.json /private/B.json
```

**Predeclared fictional checks:** (1) same source but different statement is flagged without scoring semantic disagreement; (2) identical fields are *not* equated with semantic agreement; (3) one-sided source signatures remain unpaired; (4) duplicates are ambiguous rather than greedily matched; (5) missing semantic fields and invalid provenance fail closed; (6) private strings never appear in output; (7) empty pairs do not fabricate records. The earlier source-only negative control and frozen evaluator are untouched.

## Execution provenance and failures

- The first code-bearing [hosted run #40738440351](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40738440351) succeeded with **201/201 tests on Ubuntu and 201/201 on Windows**, including **12 new v0.4 adversarial tests** per OS. Both job logs were inspected. The new test source blob is `7ca691f0bf3f54ff4ea15e3a72126674ecd3111f`; executable blob `d8e89d7004206893a21e5c960a607b4783f0f0f4`.
- An intermediate workflow change accidentally wrote literal backslash-n characters into the YAML artifact path, producing [failed run #40738524280](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40738524280). This was corrected to a genuine multiline YAML path in commit `263ca66e8eebc3655bb1a7a79ef5f0e3c92c559b`. Do not conceal this failure.
- The corrected code-and-demo [hosted run #40738549357](https://github.com/Vermicare/Haridas-Satheesh/actions/runs/40738549357) passed **201/201 tests on Ubuntu and 201/201 on Windows**; both logs were inspected. Its two artifact ZIPs were independently downloaded and rehashed against GitHub's SHA-256 metadata: Ubuntu `16f3b4038cd582696010a4ef1a115e536f16ee6719977db544054f0c010d7b28`, Windows `118b1f29ea55aa8a37058e862f7ab99bd7c0917934745959d0b845f895925f63`. Both archives contained `cortex-exact-disagreement-v04.json`, independently parsed: 0 human reviewers, 0 external actions, 1 exact matching fictional group, and 1 changed-statement mismatch in the deliberately altered pair. The unchanged synthetic lineage result was also retained. Exact runner image, Python patch version and timing benchmark: **TBD**. No random seed; deterministic fictional inputs.

## Decision and next evidence gate

**No maturity advancement.** This is a reviewer-triage software check, not a human study. The largest gap remains independent, voluntary, blinded annotations of the frozen fictional meeting, source-span adjudication, and actual correction time compared with manual notes ([Issue #12](https://github.com/Vermicare/Haridas-Satheesh/issues/12)). Reframe toward provenance-assisted human review if unsupported records or correction burden exceed manual notes.

**Four lenses:** hiring manager — testable privacy-minimal triage; technical reviewer — exact comparison only, duplicate-signature ambiguity explicit; innovation leader — no novelty or patentability conclusion; founder — zero users, zero deployments, zero measured benefit. Keep draft and unmerged pending independent review.
