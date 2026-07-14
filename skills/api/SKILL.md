---
name: aftermath-perpetuals
description: Practical skill for integrating Aftermath Perpetuals with native endpoints as the default (full feature set), plus CCXT-compatible endpoints and the TypeScript SDK.
version: 3.0.0
capabilities:
  - api-integration
  - sdk-integration
  - order-placement
  - position-monitoring
  - risk-analysis
  - vault-management
  - dca
  - limit-orders
  - staking
  - pools
  - prices
  - error-handling
---

# Aftermath Perpetuals Skill

Production OpenAPI: `https://aftermath.finance/api/openapi/spec.json`
Last validated: `2026-07-28`
Canonical docs UI: `https://aftermath.finance/docs`

## Fast Routing

Choose one file first; do not load everything by default.

Default preference: start with native perpetuals endpoints (`/api/perpetuals/*`) because they expose the full Aftermath feature set. Use CCXT endpoints when you specifically need exchange-style compatibility.

1. CCXT endpoint work -> `ccxt.md`
2. Native perpetuals endpoint work -> `native.md`
3. SDK method usage -> `sdk-reference.md`
4. API failures/retries -> `error-handling.md`
5. Trading safeguards -> `safety-and-risk.md`
6. DCA and spot limit orders -> `dca-and-limit-orders.md`
7. Staking -> `staking.md`
8. AMM pools -> `pools.md`
9. Coin and LP prices -> `prices.md`
10. Builder codes/gas pool/referrals/rewards/rebates/router/metastable/birdeye/dynamic gas/zkLogin/coins -> `auxiliary-endpoints.md`
11. Monitoring examples -> `monitoring-patterns.md`
12. Edge-case pitfalls -> `gotchas.md`

## Integration Modes

Preferred by default: Native perpetuals (`/api/perpetuals/*`) for complete API coverage.

| Mode | Best for | Primary file |
|---|---|---|
| CCXT compatibility (`/api/ccxt/*`) | Exchange-style payloads and build-sign-submit bots | `ccxt.md` |
| Native perpetuals (`/api/perpetuals/*`) | Full account/vault previews + tx builders | `native.md` |
| TypeScript SDK (`@aftermath-finance/sdk`) | Typed app integrations | `sdk-reference.md` |

## High-Risk Guardrails

- Sign `signingDigest`, not `transactionBytes`.
- Keep ID types strict: CCXT write `accountId` (object ID) vs native `accountId` (numeric).
- Send native BigInt fields using their exact `"...n"` wire format where required.
- Treat preview responses as success/error unions.
- Re-sync snapshots after stream reconnect before applying deltas.
- Serialize coin/gas-object-sensitive operations to avoid version conflicts.

## Recent API Updates

Breaking (v3.0.0):

- Builder codes migrated from per-market integrator vaults to a global integrator registration: `integratorAddress` (address string) is replaced by `integratorId` (`u32`) everywhere, order-level `builderCode.takerFee` is now `builderCode.integratorFee`, config `maxTakerFee` is now `maxIntegratorFee`, and the integrator-vault fetch/create/claim routes are removed.
- Candle streaming moved to the general updates WebSocket (`/api/perpetuals/ws/updates`) via a `marketCandles` subscription; the dedicated `/api/perpetuals/ws/market-candles/{market_id}/{interval_ms}` route is removed.
- Candle intervals are CCXT-style timeframe strings everywhere: native `candle-history` uses `resolution` (was `intervalMs`) and CCXT OHLCV uses `timeframe`. See `native.md` for the full enum.
- SL/TP price fields are `stopLossPrice` and `takeProfitPrice`. Transaction inputs add optional `triggerPriceType` (`0` index, `1` book mid, `2` mark) and per-SL/TP/stop-order `builderCode`; basic history responses contain only the prices.
- Rewards `points` response is `{ totalPoints }` (float, was `{ points }` integer) and `/api/rewards/history` now requires signed auth (`bytes` + `signature`); history entries carry `eventType`.
- Removed response fields: position `makerFee`/`takerFee`; vault `totalCollateral`/`totalCollateralUsd`; market params `gasPriceTwapPeriodMs`, `forceCancelFee`, `gasPriceTakerFee`, `zScoreThreshold` (replaced by `priorityTakerFee`); liquidation `forceCancelFeesUsd`. Price-feed IDs are numeric (`u32`) instead of address strings.

Additive (v3.0.0):

- TWAP orders: `/api/perpetuals/account/twap-order-datas` plus `create-twap-orders` / `edit-twap-orders` / `cancel-twap-orders` transaction routes.
- Client order IDs: `clientOrderId`(s) on limit/scale/cancel-and-place order placement, plus client-ID cancellation on supported transaction routes.
- Deterministic ordering, funding history, vault assistant capabilities, rebate tooling, scale orders, cancel-and-place, account sharing, and expanded account history.
- Vault TWAP orders: `/api/perpetuals/vault/twap-order-datas` plus `create-twap-orders` / `edit-twap-orders` / `cancel-twap-orders` vault transaction routes (mirrors the account TWAP surface).
- Rewards estimator: `POST /api/rewards/expectedRewards` returns forward-looking per-domain expected rewards for an epoch.
- Market metadata: `POST /api/perpetuals/markets` entries carry nullable static display metadata; `displayName` is omitted when unavailable.
- WS user subscription payloads now also stream `twapOrders` alongside stop orders.
- Vault discovery adds predeposit totals and per-vault TVL.
- Endpoint coverage now includes current DCA and spot limit-order flows, all staking routes, all pool routes, and all price routes.

## Progressive Disclosure

| File | Read when |
|---|---|
| `ccxt.md` | You need `/api/ccxt/*` endpoints or stream setup |
| `native.md` | You need `/api/perpetuals/*` account/market/vault APIs |
| `dca-and-limit-orders.md` | You need DCA or spot limit-order reads and transaction builders |
| `staking.md` | You need staking metrics, positions, validators, or capabilities |
| `pools.md` | You need AMM pools, stats, LP ownership, volume, fees, or events |
| `prices.md` | You need coin, LP, or external-ID prices |
| `auxiliary-endpoints.md` | You need builder codes, gas pool, referrals, rewards, rebates, router, metastable, Birdeye, dynamic gas, zkLogin, coins, or utility transactions |
| `sdk-reference.md` | You are coding with SDK classes and methods |
| `error-handling.md` | You are implementing retry, backoff, and failure parsing |
| `safety-and-risk.md` | You are shipping a bot or live strategy safeguards |
| `monitoring-patterns.md` | You need polling, pagination, WebSocket, or resync examples |
| `gotchas.md` | You need a pre-launch pitfalls checklist |

## 24h Change Check

Use the local helper script to check the production OpenAPI after the 24h window.

- Script: `skills/api/scripts/check_api_changes.py`
- Behavior: if less than 24h since `Last validated`, it exits without querying.
- If 24h+ elapsed, it prompts before querying: `Query ... for API changes now? [y/N]`.
- It never auto-updates skill markdown files; it only records spec hash state in `skills/api/.api-spec-state.json`.

Run:

```bash
python3 skills/api/scripts/check_api_changes.py
```
