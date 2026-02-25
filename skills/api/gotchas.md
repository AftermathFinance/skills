# Gotchas & Edge Cases

> Common pitfalls when integrating with the public API at `https://aftermath.finance/docs`.

---

## 1) Account ID vs Account Object ID

- CCXT write endpoints use `accountId` as an account capability object ID (`0x...`).
- CCXT read/stream endpoints use `accountNumber` (number).
- Native Perpetuals account endpoints use numeric `accountId`.

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
- optional `amount`, `price`, `reduceOnly`, `expirationTimestampMs`

Do not assume fields like `clientOrderId`, `timeInForce`, or `postOnly` are accepted by `/api/ccxt/build/createOrders` unless the OpenAPI schema adds them.

---

## 4) Native History Endpoints Are Cursor-Based

- `/api/perpetuals/account/order-history` paginates with `beforeTimestampCursor`.
- Response includes `nextBeforeTimestampCursor`.

Keep the cursor from each response if you need full history backfill.

---

## 5) Stop-Order Data Requires Signed Auth

`/api/perpetuals/account/stop-order-datas` requires auth payload fields (`walletAddress`, `bytes`, `signature`) plus exactly one target (`accountId` or `vaultId`).

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

## 10) Use the OpenAPI Spec as Source of Truth

When docs and examples disagree, verify against:

- `https://aftermath.finance/api/openapi/spec.json`

Schema drift is normal; hardcode less and validate request shapes in code.

---

## 11) No Built-In Dead Man's Switch

There is no protocol-level scheduled cancel safety net for your bot.

Implement a heartbeat-driven kill switch that cancels all open orders when the strategy loop stalls or process health checks fail.

---

## 12) CCXT Submit May Require Multiple Signatures

`/api/ccxt/submit/*` accepts `signatures[]`, not a single signature.

When sender and gas owner are different, collect both signatures over the same `signingDigest` before submit.
