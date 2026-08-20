---
name: aftermath-perpetuals
description: Integrate and troubleshoot the current Aftermath HTTP/OpenAPI and WebSocket API, including native perpetuals, CCXT, DCA and limit orders, pools, farms, staking, prices, auxiliary utilities, wallet/auth endpoints, and operational safety. Use for raw service-af-fe requests, endpoint schemas, API failures, and API-side compatibility checks; use the dedicated aftermath-ts-sdk skill for typed SDK integration.
---

# Aftermath API Integration

Production OpenAPI: `https://aftermath.finance/api/openapi/spec.json`
Last validated: `2026-07-28`
Production spec last hashed by the local change checker: `2026-07-28`
Canonical docs UI: `https://aftermath.finance/docs`

Local source snapshots used for the current references:

- API service: `service-af-fe` `d5cb82c` (2026-08-19), 260 OpenAPI operations.
- TypeScript SDK: `aftermath-ts-sdk` `v3.1.0` at `9a1b41db` (2026-08-19).

## Fast Routing

Choose one file first; do not load everything by default.

Default preference: start with native perpetuals endpoints (`/api/perpetuals/*`) because they expose the full Aftermath feature set. Use CCXT endpoints when you specifically need exchange-style compatibility. For a route not listed in a focused file, check `endpoint-inventory.md` before guessing a path.

1. CCXT endpoint work -> `ccxt.md`
2. Native perpetuals endpoint work -> `native.md`
3. TypeScript SDK method usage -> `../aftermath-ts-sdk/SKILL.md`
4. SDK/API mismatch or migration -> `../aftermath-ts-sdk/references/backend-alignment.md`
5. Signed wallet requests -> `authentication.md`
6. General wallet/auth/Sui/stable-kitchen/Dex Screener routes -> `general-endpoints.md`
7. Complete current operation list -> `endpoint-inventory.md`
8. API failures/retries -> `error-handling.md`
9. Trading safeguards -> `safety-and-risk.md`
10. DCA and spot limit orders -> `dca-and-limit-orders.md`
11. Staking -> `staking.md`
12. AMM pools -> `pools.md`
13. Coin and LP prices -> `prices.md`
14. Builder codes/gas pool/referrals/rewards/rebates/router/metastable/birdeye/dynamic gas/zkLogin/coins -> `auxiliary-endpoints.md`
15. Monitoring examples -> `monitoring-patterns.md`
16. Edge-case pitfalls -> `gotchas.md`

## Integration Modes

Preferred by default: Native perpetuals (`/api/perpetuals/*`) for complete API coverage.

| Mode | Best for | Primary file |
|---|---|---|
| CCXT compatibility (`/api/ccxt/*`) | Exchange-style payloads and build-sign-submit bots | `ccxt.md` |
| Native perpetuals (`/api/perpetuals/*`) | Full account/vault previews + tx builders | `native.md` |
| TypeScript SDK (`aftermath-ts-sdk`) | Typed app integrations, transaction builders, and gRPC-backed protocol access | `../aftermath-ts-sdk/SKILL.md` |

## High-Risk Guardrails

- Sign `signingDigest`, not `transactionBytes`.
- Keep ID types strict: CCXT write `accountId` (object ID) vs native `accountId` (numeric).
- Send native BigInt fields using their exact `"...n"` wire format where required.
- Treat preview responses as success/error unions.
- Re-sync snapshots after stream reconnect before applying deltas.
- Serialize coin/gas-object-sensitive operations to avoid version conflicts.
- For service wallet-auth routes, sign the exact reusable terms message and
  carry IDs/filters as plain JSON; do not sign route-specific action objects.
- Treat `gasBudget` as MIST and distinguish service auth signatures from CCXT
  transaction-digest signatures.

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
- Rewards estimator: `POST /api/rewards/expected-rewards` returns forward-looking per-domain expected rewards for an epoch. The TypeScript SDK fixed this path in v2.2.1.
- Market metadata: `POST /api/perpetuals/markets` entries carry nullable static display metadata; `displayName` is omitted when unavailable.
- WS user subscription payloads now also stream `twapOrders` alongside stop orders.
- Vault discovery adds predeposit totals and per-vault TVL.
- Endpoint coverage now includes current DCA and spot limit-order flows, all staking routes, all pool routes, and all price routes.

Post-v3 service updates:

- Unified wallet authentication now accepts only the reusable terms message
  `Aftermath Terms and Conditions`; DCA/limit cancellation IDs are plain
  `orderObjectIds` and gas sponsorship accepts optional `gasBudget`.
- `POST /api/perpetuals/vaults/config` returns the dynamic vault protocol
  limits; send an empty JSON object `{}`. Do not hardcode lock, deposit, market,
  or pending-order limits; see `native.md` and the SDK's `getVaultsConfig()`.
- Vault owner transactions can grant or revoke assistant capabilities through
  `/api/perpetuals/vault/transactions/owner/grant-agent-wallet` and
  `/api/perpetuals/vault/transactions/owner/revoke-agent-wallet`.
- `GET /api/perpetuals/config` serves network-specific AFLP/official-vault and
  default-collateral configuration.
- `POST /api/pools/summary` and `POST /api/farms/summary` batch and cache the
  object/stat data used by the frontend.
- CCXT metadata supports `gasFromAddressBalance`; deposit and withdraw support
  `fromAddressBalance` and `toAddressBalance` respectively.
- DCA/limit/router transaction construction and zkLogin creation now use the
  TS-helper service; zkLogin accepts a base64 ephemeral public key.
- Public paths are kebab-case where normalized, including
  `/api/rewards/expected-rewards`; do not resurrect camelCase variants.
- Gas-pool failures now map to stable codes `2030`–`2033` (with `2018` as the
  shared-service fallback); reusable-signature failures are `2034`.
- For perpetuals transactions with a named `sponsor.walletAddress`, scheduled
  execution gas is withdrawn from that gas pool and returned order gas is
  deposited back into it. With no named sponsor, returned gas goes to the
  account or vault owner.

## Progressive Disclosure

| File | Read when |
|---|---|
| `ccxt.md` | You need `/api/ccxt/*` endpoints or stream setup |
| `native.md` | You need `/api/perpetuals/*` account/market/vault APIs |
| `authentication.md` | You need reusable terms signatures, auth boundaries, or signed WebSocket subscriptions |
| `general-endpoints.md` | You need wallet, auth, Sui, user-data, stable-kitchen, DEX Screener, Binance, or config routes |
| `endpoint-inventory.md` | You need the complete operation/path audit for the current service snapshot |
| `dca-and-limit-orders.md` | You need DCA or spot limit-order reads and transaction builders |
| `staking.md` | You need staking metrics, positions, validators, or capabilities |
| `pools.md` | You need AMM pools, stats, LP ownership, volume, fees, or events |
| `prices.md` | You need coin, LP, or external-ID prices |
| `auxiliary-endpoints.md` | You need builder codes, gas pool, referrals, rewards, rebates, router, metastable, Birdeye, dynamic gas, zkLogin, coins, or utility transactions |
| `../aftermath-ts-sdk/SKILL.md` | You are coding with `aftermath-ts-sdk` classes, types, transports, or gRPC |
| `error-handling.md` | You are implementing retry, backoff, and failure parsing |
| `safety-and-risk.md` | You are shipping a bot or live strategy safeguards |
| `monitoring-patterns.md` | You need polling, pagination, WebSocket, or resync examples |
| `gotchas.md` | You need a pre-launch pitfalls checklist |

## 24h Change Check

Use the local helper script to check the production OpenAPI after the 24h window.

- Use `--force` to bypass the 24-hour window; use `--yes` to query without an
  interactive prompt in CI or another non-interactive environment. EOF on a
  required prompt is an error rather than a successful no-op.
- Script: `skills/api/scripts/check_api_changes.py`
- Behavior: if less than 24h since `Last validated`, it exits without querying.
- If 24h+ elapsed, it prompts before querying: `Query ... for API changes now? [y/N]`.
- It never auto-updates skill markdown files; it only records spec hash state in `skills/api/.api-spec-state.json`.

Run:

```bash
python3 skills/api/scripts/check_api_changes.py
```

## Local Source Coverage Check

When auditing a local `service-af-fe` checkout, compare its source/OpenAPI
route declarations with the committed operation inventory:

```bash
python3 skills/api/scripts/check_local_coverage.py \
  --service-root /path/to/service-af-fe
```

The checker ignores commented-out `utoipa::path` handlers, supports inline
paths and same-file `&str` path constants, and exits nonzero if an operation is
missing or extra. This is declaration coverage only: it does not verify Actix
registration, reverse-proxy routing, deployed runtime availability, or response
behavior. Use deployment-aware smoke tests for those checks. It does not edit
the inventory; regenerate that file only after reviewing the source diff and
response-shape changes.
