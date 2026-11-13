# QHAP-TRADER — caller-manifest completeness and February 2021 exception
*Research-only repair, 13 November 2026*

**Verdict: NO_TRADE. No new data was fetched. No licensed market bars, broker
fills, strategy advantage, account entitlements or live order capability are
established by this code.**

## Defect addressed

Before this repair, \`replayBook()\` checked for duplicate dates *that were
actually supplied*, but it could not detect a session absent from the
sourceFiles array. If a researcher omitted an expected losing, interrupted or
missing-data session, the remaining fully populated dates could be described
as technically \`certified:true\` without explaining the incomplete date
coverage. This could mislead downstream research reporting.

The **new optional** \`expectedSessionDays\` contains only
\`"01"\`–\`"28"\` February 2021 day strings for the legacy offline engine.
When provided, it is checked **before any simulated trade evaluation**.
Invalid/duplicate/extra dates raise an explicit error. Missing expected
days produce **zero trade records**, \`knownRealizedPnl:null\`,
\`finalEquity:null\`, \`certified:false\`, and
\`lockedReason:"MISSING_EXPECTED_SESSION"\`; the complete sorted list of
missing dates is retained.

Matching a caller-supplied manifest returns only
\`certificationScope:"CALLER_MANIFEST_MATCHED_UNVERIFIED"\`, even when the
synthetic technical replay reports \`certified:true\`. Without a declared
manifest, the backward-compatible technical scope is explicitly
\`SUPPLIED_DAYS_ONLY\`. Every result explicitly says
\`exchangeCalendarIndependentlyVerified:false\` and
\`sourceDataEntitlementIndependentlyVerified:false\`.
A user-controlled list **cannot authenticate** that NSE was open, that
unusual sessions were included, or that market-data use is permitted.

Existing February 2021 inspected 12-day development runs do **not** pass a
full-month external coverage test, and should **never** be reclassified as
fresh untouched holdout evidence. Existing untouched-holdout plans remain
unfulfilled and the historical P&L conclusions remain unchanged.

## February 2021 special-session falsification

This test-only \`feb2021_calendar_gate.test.mjs\` separately inspects a
**provisional 20-weekday** February 2021 candidate list. The
[NSE original 2021 Capital Market holiday schedule,
CMTR/46623](https://archives.nseindia.com/content/circulars/CMTR46623.pdf)
lists no February weekday trading holiday. The
[SEBI February 25, 2021 press release, PR 9/2021](https://www.sebi.gov.in/media/press-releases/feb-2021/trading-halt-at-nse-on-february-24-2021_49287.html)
documents NSE's **February 24 intraday halt**, not a full-day market
holiday. Thus February 2 and 19 remain provisional weekday candidates,
and February 24 must be included in a candidate-day manifest **and
explicitly flagged as an exception**. The existing legacy replayDay
already refuses to simulate Feb 24 as an ordinary continuous session.

The separate calendar test's output is **always HALT_UNKNOWN**, even when
all 20 provisional dates and the outage flag are present. This is
deliberate: subsequent exchange amendments, original source documents,
precise reopening/auction phases, data completeness, source timestamp
authenticity, storage rights and fill certainty have **not** been checked.
The provisional candidate list and a self-declared exception flag cannot
turn a trading-data outage into a normal backtest.

## Validation

Run with Node 22, without credentials or network access:

\`\`\`bash
node --test projects/qhap-trader/experiments/test_costed_intraday_pilot.mjs
node --test projects/qhap-trader/experiments/test_guarded_paper_replay.mjs
node --test projects/qhap-trader/experiments/feb2021_calendar_gate.test.mjs
\`\`\`

The existing read-only GitHub Actions workflow
\`.github/workflows/qhap-trader-offline-tests.yml\` includes the new
exception tests, while the pinned historical-replay workflow must
separately reproduce previously known development-sample results without
regression. A passing synthetic CI is **not** an exchange-data licence or
a positive trading recommendation.

## Actual next research dependency

A *fully covered, independent, legally permitted, pre-frozen* unseen
market-data set with exchange-correct session calendars, corporate actions,
execution chronology and dated cost schedule. The prior examined February
2021 sample is not an acceptable holdout. No trading/funds/orders until
independent financial, licensing, broker and operational review.
