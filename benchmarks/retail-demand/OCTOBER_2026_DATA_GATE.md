# Retail — October 2026 public-data integrity gate

**Stage: Research / Architecture. Real-data decision uplift: TBD.**

Local-only packages (`retail_freshretail_preflight_v02_2026-10-21.zip`, `retail_atomic_acquisition_gate_v04_2026-10-21.zip`) report software tests of hourly stock-status consistency and atomic acquisition safeguards. These are **not** results from an independently reproduced public dataset benchmark. The reported check expects a stock-count field covering hours 6–21 to agree with those 16 hourly flags; verify against the pinned dataset schema before treating this as a data-quality rule.

**Next:** acquire and hash a licensed public dataset snapshot, pin a chronological split, compare seasonal-naive and stockout-aware baselines on predeclared forecast and decision metrics. **Reframe** if correction does not beat simpler baselines or censoring is unidentifiable.
