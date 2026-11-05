# QHAP-TRADER — Independent Multi-AI Research Council

**Stage:** Research-only software prototype. No market signals, verified profits, real orders, live feed, paid model call or trading authority have been established.

## Purpose

Three distinct AI providers independently critique the **same public research question**. Only after all three replies pass basic validation does a fourth judge review them. It must document agreements, contradictions, missing evidence and a falsification experiment, **not** select a stock to buy. Model consensus is not proof of predictive power.

This differs from using [OpenRouter Fusion](https://openrouter.ai/docs/guides/routing/routers/fusion-router) directly: Fusion can choose whether to invoke its panel. This prototype makes **three independently attributable calls plus one judge** when online mode is manually enabled. It uses [OpenRouter's documented chat-completions API](https://openrouter.ai/docs/api_reference/overview), not a custom trading service.

## Offline demo (default and no cost)

Requires Node.js 22+. No external libraries, account or API key.

    node --test projects/qhap-trader/research_council/test_council.mjs
    node projects/qhap-trader/research_council/council.mjs --demo projects/qhap-trader/research_council/sample_brief.json

**All displayed model answers are synthetic fixtures**, not actual GPT, Claude or Gemini responses, market predictions or profitability results. GitHub Actions runs only this offline test path with no credentials and no billable calls.

## Optional manual online mode — potentially billable

OpenRouter API requests have actual costs determined by model, token use and provider. One run makes **up to four external completion requests**, with no retries, scheduled calls, or broker actions.

Before using online mode: independently create an OpenRouter account, establish a small API-key spending limit, check current model identifiers and prices, and review the public-only brief for confidential information. See [OpenRouter key limits](https://openrouter.ai/docs/api/api-reference/api-keys/create-keys).

Example PowerShell, **only if you explicitly choose and approve the potential charges** (IDs are illustrative and should be verified):

    $env:OPENROUTER_API_KEY = Read-Host "Enter your OpenRouter API key locally"
    $env:QHAP_COUNCIL_MODELS = "anthropic/claude-sonnet-4.6,openai/gpt-5.2,google/gemini-2.5-pro"
    $env:QHAP_COUNCIL_JUDGE = "openai/gpt-5.2"
    $env:QHAP_ENABLE_PAID_COUNCIL = "I_ACCEPT_AI_API_COSTS"
    node projects/qhap-trader/research_council/council.mjs --online projects/qhap-trader/research_council/sample_brief.json "$env:TEMP\qhap-council-private-review.json"
    Remove-Item Env:\OPENROUTER_API_KEY
    Remove-Item Env:\QHAP_ENABLE_PAID_COUNCIL

Keep the key on your device. Use a unique output filename each run; creation refuses overwrite. The command requires an absolute output path and refuses obvious repository directories. **Do not commit the private model-response file or any credentials to GitHub.** This program does not purchase credits, create keys or automatically run online.

## Input and output safety contract

Input JSON explicitly requires a public-only QHAP-TRADER question, real-order execution disabled, private market data disabled, plus optional public HTTPS citations. Checks for pasted secrets are basic safeguards, not guaranteed sanitization; personally review the content before sharing it with vendors.

All URLs, question text and model outputs are untrusted data, not instructions. Judge synthesis is an unverified research hypothesis. SHA-256 fingerprints are local integrity checks—not third-party provenance, correct reasoning, or actual market performance evidence.

The output always states:
- Research classification: UNVERIFIED_RESEARCH_COUNCIL
- Profitable edge verified: false
- Independent market test passed: false
- Trade authorization: false
- Orders submitted: 0

A model's unanimous buy/sell recommendation can never override these fields or place a trade. There is no market-feed, brokerage, bank, trading-execution or project-promotion API in this module.

## Evidence gate

No strategy upgrade until licensed, point-in-time NSE data and sessions, preregistered unseen tests, NO_TRADE and simple baselines, net-of-cost stress, drawdown and fail-closed risk controls have been independently demonstrated. Previous DTT results were negative; no amount of AI consensus can reverse those observed findings. Real-money trading remains outside project scope without future explicit authorization and regulatory assessment.
