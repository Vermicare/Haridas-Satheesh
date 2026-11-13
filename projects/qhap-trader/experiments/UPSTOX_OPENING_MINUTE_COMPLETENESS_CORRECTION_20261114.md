# QHAP-TRADER — opening-minute completeness correction (2026-11-14)

**Status: SOURCE VALIDATION CORRECTION, NOT A NEW PROFIT OR TRADING MILESTONE.**
**Broker decision: NO_TRADE.** No live or paper broker orders, payments,
credentials, data downloads, outgoing emails or changes to private source
files were involved.

## Root cause

The original Upstox V3 private **one-minute** development importer marked
a day `CANDIDATE_COMPLETE_UNVERIFIED` if **09:16–15:29 IST** existed
(374 timestamps); it did **not** test for the 09:15 opening candle. The
chronology-first intraday replay likewise deliberately operated on
09:16–15:29 signal bars, but incorrectly accepted input CSVs without
the 09:15 source candle. This conflated a strategy warmup/feature boundary
with a full market-source session boundary.

The separate prior public GitHub research sample audit established that
three publicly reachable RELIANCE files (2021-02-01, 2022-01-03 and
2023-01-02) had exactly 374 normal minutes and no 09:15 bar. These files
are **NOT authenticated Upstox data**, and nothing in that observation
proves that previously saved actual Upstox source bars are deficient.
This incident fixes a testable *software acceptance weakness*.

## Exact correction

1. The importer now requires **all 375 timestamps from 09:15 through
   15:29 IST** for any candidate weekday; a missing 09:15 becomes
   `INCOMPLETE_MINUTE_COVERAGE`, `firstMissingRequiredMinute:"09:15"`,
   and it is **removed** from the generated `eligible` manifest.
   Each private per-day audit also records `openingMinutePresent` and
   `expectedRegularSessionMinuteBars:375`.
2. The offline intraday replay validates an existing 09:15 input bar
   for schema, duplicates and OHLCV, and refuses a source lacking it via
   `MISSING_OPENING_MINUTE_09_15`. The previously frozen research
   **strategy features still start at 09:16**: no signal lookback,
   strategy fee formula, simulated fill or stop/target rule was optimized
   on this change. The command-line replay explicitly records opening
   gaps among exclusions instead of treating such dates as passed.
3. New `reaudit_existing_private_upstox.mjs --audit-local` runs
   completely offline on the user's *previously saved* immutable
   `QHAP-TRADER-PRIVATE/manifests/development-*.audit.json` metadata
   and matching private CSVs. It compares preserved SHA-256 hashes and
   rechecks prior *candidate* dates against the stricter session parser.
   It emits **only aggregate counts and affected date labels**, and
   does not overwrite old files, repair missing bars, reprice strategies,
   issue requests, read tokens or certify market rights. A previously
   excluded date is not promoted to candidate by this tool.
4. Unit tests now explicitly challenge 374-bar days missing 09:15,
   duplicates and bad 09:15 OHLCV, structurally complete input,
   legacy stale manifests, modified private-source hashes,
   malformed private audit metadata and read-only output.

## Actual private-data results are unknown until the local check runs

There is **no access to the user's Windows home files from GitHub Actions**.
Therefore `staleCandidateLabels` and
`previouslyLabeledCandidatesPassingFull375Shape` are **unknown**, not
assumed to be zero or positive. The user's previously reported January
2025 five-day sample contained 1,875 candles (375 × 5), which is
consistent with full opening-minute coverage but **not itself proof**
that individual source-day content or hashes pass current checks.
Do not update old signed/hashed research artifacts, call old source
labels certified, or pretend this correction revalidated them.

Run on the Windows host after GitHub merge:

```powershell
cd "$env:USERPROFILE\Downloads\Haridas-Satheesh"
git pull --ff-only origin main
node .\projects\qhap-trader\live_readiness\reaudit_existing_private_upstox.mjs --audit-local
```

No Upstox Analytics Token, Dhan subscription or new acquisition is
required. The output intentionally does **not** inspect the separate
204-day **daily** equity-agent dataset; daily bars do not have the
same missing 09:15 intraday acceptance issue.

## Preserved restrictions

Upstox [Analytics Token](https://upstox.com/developer/api-documentation/analytics-token/)
is officially free and read-only, and its
[Historical Candle V3](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/)
provides one-minute history from January 2022 with one-month request
windows. These API capabilities do not independently authorize
unlicensed redistribution or current-feed paper trading. The user
attests a provider representative verbally approved the proposed
private research; the written provider email status must be
distinguished from any verbal assurance.

The already inspected loss-making RELIANCE daily development evidence
remains negative exploratory research, **never** a newly untouched
historical holdout. True licensed and verified 60+ distinct-date
multi-regime historical holdout, dated transaction costs, 60+ genuine
future sessions, and explicit live-trading compliance still block
production. **No_TRADE** until independently resolved.
