# Gotchas & Edge Cases

> Common pitfalls when integrating with the public API at `https://aftermath.finance/docs`.

---

## 1) Account ID vs Account Object ID

- CCXT write endpoints use `accountId` as an account capability object ID (`0x...`).
- CCXT read/stream endpoints use `accountNumber` (number).
- Native Perpetuals account endpoints use a numeric account ID, commonly transported as a mandatory `"123n"` string.

Mixing these is one of the most common integration failures.

---

## 2) Build -> Sign -> Submit Is Mandatory

For CCXT writes:

```text
POST /api/ccxt/build/* -> sign signingDigest -> POST /api/ccxt/submit/*
```

Sign the `signingDigest`, not `transactionBytes`.

---

## 3) CCXT `OrderRequest` Is Minimal

Current schema supports:

- `type`: `market | limit`
- `side`: `buy | sell`
- optional `amount`, `price`, `reduceOnly`, `expirationTimestampMs`, `clientOrderId`

Fields such as `timeInForce` and `postOnly` are unsupported by `/api/ccxt/build/createOrders` and may be ignored if sent.

---

## 4) Native History Endpoints Are Cursor-Based

- `/api/perpetuals/account/order-history` paginates with `beforeTimestampCursor`.
- Response includes `nextBeforeTimestampCursor`.

Keep the cursor from each response if you need full history backfill.

---

## 5) Stop-Order Data Requires Signed Auth

`/api/perpetuals/account/stop-order-datas` and `/api/perpetuals/vault/stop-order-datas` require `walletAddress`, `bytes`, `signature`, and one target: `accountId: "...n"` or `vaultId`. Optional `marketIds` narrows the response.

---

## 6) Preview Endpoints Can Return 200 With Error Payload

Some `/api/perpetuals/account/previews/*` and vault preview routes can return:

- HTTP `200`
- body `{ error: string }`
- header `X-Error-Message: true`

Treat preview responses as tagged unions, not always-success payloads.

---

## 7) Ticker Does Not Guarantee Funding-Rate Fields

CCXT ticker includes fields such as `markPrice` and `indexPrice`. Do not rely on explicit funding-rate fields being present in ticker responses.

---

## 8) Coin and Gas Object Concurrency Is Real

Concurrent signed transactions can race on shared Sui objects (USDC coin objects, gas coins) and fail with version/equivocation-style errors.

Serialize critical funding operations and manage gas coins intentionally for parallel submission.

---

## 9) Account State Is Quickly Stale

After any fill/cancel/withdraw/deposit/leverage update, refresh account and position state before computing new risk or order decisions.

---

## 10) Follow Endpoint Wire Formats

Use the public OpenAPI for discovery:

- `https://aftermath.finance/api/openapi/spec.json`

Use the endpoint-specific request and response formats in this skill when
serializing BigInt values, preview unions, and pool paths.

---

## 11) Native BigInt Fields Use Exact Strings

Native BigInt fields require `"...n"` request strings and return `"...n"` response strings. Plain numbers and strings without the suffix fail for those inputs. Other timestamps and counters remain JSON numbers, so follow endpoint-specific types.

---

## 12) Deferred Create Flows Change Response Shape

`/api/perpetuals/transactions/create-account` can return deferred PTB argument references when `deferShare = true`.

Do not hardcode the response as `{ txKind }` only if you compose transactions client-side.

---

## 13) No Built-In Dead Man's Switch

The public API does not provide a scheduled cancel or dead-man-switch endpoint.

Implement a heartbeat-driven kill switch that cancels all open orders when the strategy loop stalls or process health checks fail.

---

## 14) CCXT Submit May Require Multiple Signatures

`/api/ccxt/submit/*` accepts `signatures[]`, not a single signature.

When sender and gas owner are different, collect both signatures over the same `signingDigest` before submit.

---

## 15) Migrating From the Pre-v3 API

If your integration predates skill v3.0.0, these renames and removals will break requests that still use the old shapes:

- Candle intervals: `intervalMs` / `interval_ms` (milliseconds) are gone. Native `candle-history` takes `resolution` and CCXT OHLCV takes `timeframe`. See `native.md` for the full enum.
- Candles WebSocket: `GET /api/perpetuals/ws/market-candles/{market_id}/{interval_ms}` no longer exists. Subscribe with `marketCandles` on `/api/perpetuals/ws/updates`.
- Builder codes: `integratorAddress` is replaced by numeric `integratorId`; order-level `builderCode.takerFee` is now `builderCode.integratorFee`; config `maxTakerFee` is now `maxIntegratorFee`. The integrator-vault routes (`integrator-vaults`, `create-integrator-vault`, `claim-integrator-vault-fees`) are removed in favor of one-time integrator registration.
- SL/TP: `stopLossIndexPrice` / `takeProfitIndexPrice` are now `stopLossPrice` / `takeProfitPrice`. Transaction inputs can also include `triggerPriceType`; basic order-history `slTp` does not.
- Rewards: `/api/rewards/points` returns `{ totalPoints }` (float, was `{ points }`); `/api/rewards/history` now requires `bytes` + `signature`.
- Removed response fields: position `makerFee`/`takerFee`; vault `totalCollateral`/`totalCollateralUsd`; market params `gasPriceTwapPeriodMs`, `forceCancelFee`, `gasPriceTakerFee`, `zScoreThreshold`; liquidation `forceCancelFeesUsd`. Price-feed IDs are numeric.
- Ordering: markets sort by symbol; positions sort by market ID; pending bids and asks each sort by order ID; stop-order market groups sort by market ID. Inner stop-order ordering is unspecified.

---

## 16) TypeScript SDK May Lag Native Renames

`sdk-reference.md` describes selected SDK flows, but installed SDK versions can expose different names from raw native HTTP. Verify your package's generated types instead of assuming both surfaces match.

---

## 17) CCXT Streams Use WebSockets

Connect to CCXT stream routes with WebSockets and pass `chId` or
`accountNumber` as query parameters. Do not use `EventSource` or GET request
bodies for these streams.
