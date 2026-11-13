# QHAP-CRYPTO — interdependent research agents v0.1

**13 November 2026. Research-only.** BTC-USDT and ETH-USDT spot markets, no leverage, margin, futures, real or fake order submissions, exchange accounts, wallets, model API calls or demonstrated profit. This is an ISOLATED cryptocurrency research lane within QHAP, not an upgrade of the Upstox NSE broker connection.

## Claude news and other source references

Anthropic now documents multiagent orchestration with independently running subagents, coordination and dynamic workflows at https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration . Its experimental Claude Code agent teams (https://code.claude.com/docs/en/agent-teams) can coordinate named agents through messages, but use additional tokens and coordination overhead.

Cross-referenced:
- TauricResearch TradingAgents — https://github.com/TauricResearch/TradingAgents — research analyst, trader and risk roles. Apache 2.0. Its recent release notes explicitly discuss correcting point-in-time and backtest issues.
- Agent4Crypto — https://arxiv.org/abs/2611.12269 — November 9, 2026 preprint: three risk styles and counterfactual weighting. Independent replication required before using reported returns.
- Consensus-Gated Execution — https://doi.org/10.3390/electronics15153453 — adversarial Bull vs Bear with a meta-evaluator; reported average return improvements were not statistically significant.
- Multi-Agent Debate for Explainable Trading — https://arxiv.org/abs/2609.29701 — better agent reasoning did not reliably improve economic trading performance.
- Multiagent Bitcoin panel comparison — https://github.com/sanfernandezf/multiagent-llm-btc-trading — role diversity and single-agent versus 3/5/9 studies.
- A research-grade LangGraph multiagent BTC proposal with cost telemetry — https://github.com/ziyadal/multi-agent-trading-system — still not proof of live profits.

No source code was copied from those projects. No current QHAP code invokes Claude directly. Our pre-existing independent 3-provider plus judge research council is at ../research_council/README.md and remains an OPTIONAL research sidecar only, not a model-generated trading broker. Its online model mode is potentially paid and requires separate explicit user action/approval; this crypto module makes ZERO such requests.

## Implemented v0.1

A Node.js 22+ dependency-free isolated agent network:
- Program: ../live_readiness/crypto_interdependent_agent_network.mjs
- Offline tests: ../live_readiness/test_crypto_interdependent_agent_network.mjs
- Source inputs: locally constructed closed, contiguous one-minute OHLCV candles, or bundled synthetic fixture; the real exchange/rights/feed integration has not been built.
- Typed message graph: SOURCE_INTEGRITY -> five parallel analysis modules (TREND, MEAN_REVERSION, VOLUME/LIQUIDITY PROXY, VOLATILITY, COST) -> ADVERSARIAL_SKEPTIC -> RESEARCH_COORDINATOR -> NON_OVERRIDABLE_RISK_GUARDIAN.
- Every agent publishes a role, evidence family, dependency message IDs, bounded metrics and SHA-256 chain digest. This is an in-process logical interdependent network, NOT nine LLM instances in separate environments. A separate exported verifier checks the graph, hash chain and final non-overrideable veto.
- Skeptic exposes a critical issue: momentum and mean reversion both arise from one candle feed. Multiple votes are NOT independently sourced evidence. Missing order book depth, license, observed fill price, source attestation, and unverified tax/fee conditions are explicit.
- Research WATCH may appear on strongly trending test fixtures, but the output always returns finalDecision NO_TRADE, realOrdersSent 0 and paperOrdersSent 0. There is no trading route, exchange authentication, wallet key, paid AI endpoint, persistence, daemon or fill simulator. This is a *signal research watchdog*, not even a paper portfolio or a running live price monitor.

Simplified dependency graph:

    Local point-in-time OHLCV -> Source Guardian
           |
           +--> Trend researcher ---------+
           +--> Mean-reversion opponent --+--> Adversarial skeptic
           +--> Volume proxy -------------+           |
           +--> Volatility watchdog ------------------+--> Research coordinator
           +--> Fee/slippage auditor -----------------+         |
                                                              v
                                              Mandatory deterministic risk veto
                                                              |
                                                     NO_TRADE (research only)

## Windows PowerShell demonstration

Run after this PR has merged to main:

    cd "$env:USERPROFILE\Downloads\Haridas-Satheesh"
    git pull --ff-only origin main

    node --test --test-reporter=tap .\projects\qhap-trader\live_readiness\test_crypto_interdependent_agent_network.mjs
    node .\projects\qhap-trader\live_readiness\crypto_interdependent_agent_network.mjs --synthetic-demo

The demo outputs exactly nine research messages, their explicit dependencies and digest, while the final decision remains NO_TRADE. All synthetic fixture prices are invented, not a BTC quote and not claimed financial outcomes.

The optional local-only mode accepts an absolute path to a PRIVATE_REPLAY JSON file:

    node .\projects\qhap-trader\live_readiness\crypto_interdependent_agent_network.mjs --private-replay --file "C:\YourPrivatePath\btc-local.json"

For that private JSON, supply market BTC-USDT or ETH-USDT; sourceClass PRIVATE_REPLAY; asOfMs (decision-clock timestamp in Unix milliseconds); candles array of 40–180 contiguous 60-second closed records with fields closeTimeMs, open, high, low, close and volume; and costAssumptions fields feeBpsPerSide, slippageBpsPerSide, spreadRoundTripBps, uncertaintyBps, independentlyVerified (boolean). Keep any data you are entitled to use **only on the user's local disk**; don't commit licensed market candles or wallet secrets to GitHub. The script outputs bounded metrics, not OHLCV bars.

## Next high-value development phases

1. **Data integrity** — compare eligible PUBLIC read-only crypto OHLCV sources and supported geographic jurisdictions, venue fees, time-zone-independent candle close timestamps, stale-feed and exchange outage rules. Choose source with explicit applicable data terms; backfill and live streaming are independent.
2. **Real model sidecars** — reuse QHAP's existing 3-provider research council for independent blind Claude/GPT/Gemini critique of public-only research summaries, with user-approved API costs, no private source price uploads and hard no-order permissions. Compare against 1-model and deterministic-only baselines.
3. **Evidence** — freeze new hypotheses before evaluating untouched permitted BTC/ETH periods; compare 1 vs 3 vs 5 vs 9 agent ensembles, no-trade and buy-hold baselines, costs including actual venue spread, slippage and model token budget; split by time and regimes, block bootstrap, multiple-testing and ablations. An agent network that loses money after costs is rejected regardless of agent count.
4. **Only paper portfolios after independent results** — paper cash balance and unleveraged spot, realistic next-event limit/market fills, ambiguity, partial fills, interruptions, position ledger, restart and close/reconcile controls, no direct exchange order route.
5. **Live feasibility later** — requires separate written venue/API permission where necessary, local tax/jurisdiction review, validated risk and a separate user-approved order integration. Successful research may never automatically enable real money.

**India matters:** Indian Income Tax Department currently describes 30% tax on taxable gains from transfers of Virtual Digital Assets, applicable cess/surcharge, and 1% Section 194S withholding on eligible transfers. The withholding is a payment/cash-flow event, not an exchange trading fee and is subject to statutory conditions. Official source: https://www.incometaxindia.gov.in/w/tds-on-payment-for-the-transfer-of-virtual-digital-assets-vdas- . This code does not calculate a user's Indian tax obligations, tax lots or TDS. Any future net profitability analysis needs venue-specific law and tax review.

**Security and project policies:** QHAP has NO automatic real crypto trading; user had previously authorized only Upstox historical equity research and read-only equity paper—such authorization cannot be silently transplanted to a cryptocurrency venue. No QHAP email sends/replies/forwards/resends without explicit per-message user approval. Other projects' outreach arrangements remain unchanged.
