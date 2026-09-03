# Native Perpetuals Endpoint Reference

> Native perpetuals endpoints under `/api/perpetuals/*`.

This is the preferred and canonical API surface for integrations because it exposes the complete feature set beyond CCXT compatibility.

Production OpenAPI: `https://aftermath.finance/api/openapi/spec.json`
Production spec last hashed: `2026-07-28`

For reusable wallet signatures, read `authentication.md`. For the complete
route index, read `endpoint-inventory.md`.

---

## Endpoint Families

### Accounts and positions

```text
POST /api/perpetuals/accounts/owned
POST /api/perpetuals/accounts
POST /api/perpetuals/accounts/positions
POST /api/perpetuals/account/max-order-size
POST /api/perpetuals/account/order-history
POST /api/perpetuals/account/order-history-detailed
POST /api/perpetuals/account/order-history-detailed-csv
POST /api/perpetuals/account/collateral-history
POST /api/perpetuals/account/margin-history
POST /api/perpetuals/account/stop-order-datas
POST /api/perpetuals/account/twap-order-datas
```

### Account previews and tx builders

```text
POST /api/perpetuals/account/previews/*
POST /api/perpetuals/account/transactions/*
```

Top-used explicit routes:

```text
POST /api/perpetuals/account/previews/place-market-order
POST /api/perpetuals/account/previews/place-limit-order
POST /api/perpetuals/account/previews/place-scale-order
POST /api/perpetuals/account/previews/cancel-orders
POST /api/perpetuals/account/previews/set-leverage
POST /api/perpetuals/account/previews/edit-collateral

POST /api/perpetuals/account/transactions/place-market-order
POST /api/perpetuals/account/transactions/place-limit-order
POST /api/perpetuals/account/transactions/place-scale-order
POST /api/perpetuals/account/transactions/cancel-orders
POST /api/perpetuals/account/transactions/cancel-and-place-orders
POST /api/perpetuals/account/transactions/set-leverage
POST /api/perpetuals/account/transactions/deposit-collateral
POST /api/perpetuals/account/transactions/withdraw-collateral
POST /api/perpetuals/account/transactions/allocate-collateral
POST /api/perpetuals/account/transactions/deallocate-collateral
POST /api/perpetuals/account/transactions/transfer-collateral
POST /api/perpetuals/account/transactions/place-stop-orders
POST /api/perpetuals/account/transactions/place-sl-tp-orders
POST /api/perpetuals/account/transactions/edit-stop-orders
POST /api/perpetuals/account/transactions/cancel-stop-orders
POST /api/perpetuals/account/transactions/create-twap-orders
POST /api/perpetuals/account/transactions/edit-twap-orders
POST /api/perpetuals/account/transactions/cancel-twap-orders
POST /api/perpetuals/account/transactions/share
POST /api/perpetuals/account/transactions/grant-agent-wallet
POST /api/perpetuals/account/transactions/revoke-agent-wallet
```

### Market data

```text
POST /api/perpetuals/all-markets
POST /api/perpetuals/markets
POST /api/perpetuals/markets/prices
POST /api/perpetuals/markets/24hr-stats
POST /api/perpetuals/markets/orderbooks
POST /api/perpetuals/market/candle-history
POST /api/perpetuals/market/funding-history
POST /api/perpetuals/market/order-history
GET  /api/perpetuals/config
```

### Account capability utilities

```text
POST /api/perpetuals/transactions/create-account
POST /api/perpetuals/transactions/transfer-cap
```

### Sponsored transactions and returned gas

Where a native transaction request exposes a `sponsor` object, use this shape:

```typescript
type SponsorConfig = {
  walletAddress: string;
  bytes: string;       // base64 of the fixed terms message
  signature: string;   // signature over the decoded terms bytes
  gasBudget?: number;  // SUI MIST; omit for service-derived budget
};
```

The reusable signed bytes must decode exactly to `Aftermath Terms and
Conditions`; transaction inputs, account IDs, and order data are not signed.
See `authentication.md` for the common signature and gas-pool error codes.
For perpetuals transactions with a non-empty `sponsor.walletAddress`, scheduled
execution gas is drawn from that sponsor's gas pool and returned order gas is
deposited back into it. If sponsorship is absent or the wallet address is
empty, returned gas goes to the account or vault owner. Do not model a named
sponsor's reclaimed gas as owner inventory.

### Vaults

```text
POST /api/perpetuals/vaults/config
POST /api/perpetuals/vaults
POST /api/perpetuals/vaults/lp-coin-prices
POST /api/perpetuals/vaults/owned-lp-coins
POST /api/perpetuals/vaults/owned-vault-assistant-caps
POST /api/perpetuals/vaults/owned-vault-caps
POST /api/perpetuals/vaults/owned-withdraw-requests
POST /api/perpetuals/vaults/withdraw-requests
POST /api/perpetuals/vaults/predeposits/user-total-deposits
POST /api/perpetuals/vaults/predeposits/vault-totals
GET  /api/perpetuals/vaults/{vault_id}/tvl
POST /api/perpetuals/vault/stop-order-datas
POST /api/perpetuals/vault/twap-order-datas
POST /api/perpetuals/vault/previews/*
POST /api/perpetuals/vault/transactions/*
```

Top-used explicit routes:

```text
POST /api/perpetuals/vault/previews/deposit
POST /api/perpetuals/vault/previews/create-withdraw-request
POST /api/perpetuals/vault/previews/place-market-order
POST /api/perpetuals/vault/previews/place-limit-order
POST /api/perpetuals/vault/previews/place-scale-order
POST /api/perpetuals/vault/previews/cancel-orders
POST /api/perpetuals/vault/previews/set-leverage
POST /api/perpetuals/vault/previews/edit-collateral
POST /api/perpetuals/vault/previews/owner/process-withdraw-requests
POST /api/perpetuals/vault/previews/owner/withdraw-collateral
POST /api/perpetuals/vault/previews/owner/withdraw-locked-liquidity
POST /api/perpetuals/vault/previews/owner/withdraw-performance-fees
POST /api/perpetuals/vault/previews/pause-vault-for-force-withdraw-request
POST /api/perpetuals/vault/previews/process-force-withdraw-request

POST /api/perpetuals/vault/transactions/deposit
POST /api/perpetuals/vault/transactions/create-withdraw-request
POST /api/perpetuals/vault/transactions/cancel-withdraw-request
POST /api/perpetuals/vault/transactions/create-vault
POST /api/perpetuals/vault/transactions/create-vault-cap
POST /api/perpetuals/vault/transactions/place-market-order
POST /api/perpetuals/vault/transactions/place-limit-order
POST /api/perpetuals/vault/transactions/place-scale-order
POST /api/perpetuals/vault/transactions/cancel-orders
POST /api/perpetuals/vault/transactions/cancel-and-place-orders
POST /api/perpetuals/vault/transactions/set-leverage
POST /api/perpetuals/vault/transactions/allocate-collateral
POST /api/perpetuals/vault/transactions/deallocate-collateral
POST /api/perpetuals/vault/transactions/place-stop-orders
POST /api/perpetuals/vault/transactions/place-sl-tp-orders
POST /api/perpetuals/vault/transactions/edit-stop-orders
POST /api/perpetuals/vault/transactions/cancel-stop-orders
POST /api/perpetuals/vault/transactions/create-twap-orders
POST /api/perpetuals/vault/transactions/edit-twap-orders
POST /api/perpetuals/vault/transactions/cancel-twap-orders
POST /api/perpetuals/vault/transactions/pause-vault-for-force-withdraw-request
POST /api/perpetuals/vault/transactions/process-force-withdraw-request
POST /api/perpetuals/vault/transactions/update-withdraw-request-slippage
POST /api/perpetuals/vault/transactions/owner/grant-agent-wallet
POST /api/perpetuals/vault/transactions/owner/process-withdraw-requests
POST /api/perpetuals/vault/transactions/owner/revoke-agent-wallet
POST /api/perpetuals/vault/transactions/owner/update-force-withdraw-delay
POST /api/perpetuals/vault/transactions/owner/update-lock-period
POST /api/perpetuals/vault/transactions/owner/update-performance-fee
POST /api/perpetuals/vault/transactions/owner/withdraw-collateral
POST /api/perpetuals/vault/transactions/owner/withdraw-locked-liquidity
POST /api/perpetuals/vault/transactions/owner/withdraw-performance-fees
```

### Rebates

```text
POST /api/perpetuals/rebates/rewards
POST /api/perpetuals/rebates/create-csv-rebates
POST /api/perpetuals/rebates/create-referral-csv-rebates
```

### WebSocket proxy

```text
GET /api/perpetuals/ws/updates
```

All live streams — including market candles — flow through this single general updates WebSocket. Clients subscribe/unsubscribe per stream with a JSON message:

```json
{
  "action": "subscribe",
  "subscriptionType": { "market": { "marketId": "0x..." } }
}
```

- `action`: `"subscribe"` or `"unsubscribe"`.
- `subscriptionType` is an externally tagged, camelCase enum. Variants and their args:
  - `market`: `{ marketId }` — market metadata/params/state.
  - `user`: `{ accountId: "123n", withStopOrders?: { walletAddress, bytes, signature } }` — account state, optionally with stop orders (signed auth).
  - `oracle`: `{ marketId }` — oracle prices.
  - `orderbook`: `{ marketId }` — orderbook deltas.
  - `marketOrders`: `{ marketId }` — order updates for a market.
  - `userOrders`: `{ accountId }` — order updates for an account.
  - `userCollateralChanges`: `{ accountId }` — collateral change updates.
  - `topOfOrderbook`: `{ marketId, priceBucketSize, bucketsNumber }` for bucketed top-of-book snapshots.
  - `marketCandles`: `{ marketId, interval }` for OHLCV candle updates; `interval` is one of `1m | 5m | 15m | 30m | 1h | 4h | 12h | 1d | 3d | 1w | 1mo`.

When `user.withStopOrders` is present, `bytes` must be base64 for the exact
UTF-8 terms message `Aftermath Terms and Conditions`, and `signature` must be
over those decoded bytes. The proxy verifies the pair before forwarding the
subscription. It is reusable; do not sign an account/market/action JSON
object. See `authentication.md` for the signing snippet.

Candle updates arrive as:

```json
{
  "marketCandles": {
    "marketId": "0x...",
    "interval": "1m",
    "lastCandle": { "timestamp": 1720000000000, "open": 1.0, "close": 1.1, "high": 1.2, "low": 0.9, "volume": 1000.0 }
  }
}
```

Production market updates include the current mark price. This was verified
from a live production frame at 2026-09-03 19:45 UTC. The fragment below omits
the existing `PerpetualsMarketData` fields:

```json
{
  "market": {
    "objectId": "0x...",
    "markPrice": 81000.0
  }
}
```

Production oracle updates include mark and book prices. Both fields were
verified from a live production frame at 2026-09-03 19:45 UTC:

```json
{
  "oracle": {
    "marketId": "0x...",
    "basePrice": 80990.0,
    "collateralPrice": 1.0,
    "markPrice": 81000.0,
    "bookPrice": 81010.0
  }
}
```

`market.markPrice` and `oracle.markPrice` are numeric and represent the price
used for position PnL and liquidation calculations. `oracle.bookPrice` is the
raw orderbook midpoint and is `null` when either side of the book is empty.
These additions do not change subscription messages or remove existing
response fields. REST market prices expose the same raw midpoint as `midPrice`.

Stream behavior notes:

- User payloads sort positions by market ID; pending bids/asks sort by order ID; pending orders include `clientOrderId`.
- User payloads also stream `twapOrders` (TWAP order objects or null) alongside stop orders.
- Market payloads over WS always report `isFrozen: false` — the WS market stream carries no freeze state; read the real value from REST market endpoints.

---

## Identifier Rules

| Field | Meaning |
|---|---|
| `accountId` | Numeric account ID |
| `marketId` | Market object ID |
| `vaultId` | Vault object ID |

Do not pass CCXT account capability object IDs (`0x...`) where numeric `accountId` is required.

Native BigInt fields require JSON strings with a trailing `n`, such as `"123n"`. Plain `123` and `"123"` fail for those inputs. BigInt responses also include the suffix. Other counters and timestamps remain ordinary JSON numbers, so follow each endpoint's field contract instead of applying one conversion globally.

---

## Correct Native Examples

Required-field reminders for high-risk routes:

- `/api/perpetuals/all-markets`: requires `collateralCoinType`. Markets are returned sorted by symbol.
- `/api/perpetuals/markets`: returns `{ marketDatas: [{ market, metadata }] }`. `metadata` is nullable static display data: `{ symbol, displayName?, category, image, collateralSymbol }`. Responses omit `displayName` when unavailable.
- `/api/perpetuals/market/candle-history`: requires `marketId`, `fromTimestamp`, `toTimestamp`, and `resolution`. Supported values are `1m | 5m | 15m | 30m | 1h | 4h | 12h | 1d | 3d | 1w | 1mo`. Returns `{ candles: [{ timestamp, open, high, low, close, volume }] }` with millisecond timestamps.
- `/api/perpetuals/market/funding-history`: requires `marketId`, `fromTimestamp`, and `toTimestamp`; `limit` is nullable.
- `/api/perpetuals/account/max-order-size`: requires `marketId`, `accountId: "...n"`, and `side` values `0` bid or `1` ask. Returns `{ maxOrderSize: "...n" }`.
- `/api/perpetuals/account/stop-order-datas`: requires `walletAddress`, `bytes`, `signature`, and exactly one target: `accountId: "...n"` or `vaultId`. `marketIds` is optional.
- `/api/perpetuals/account/twap-order-datas` and `/api/perpetuals/vault/twap-order-datas` require `walletAddress`, `bytes`, and `signature`; the same fixed terms message is checked before the downstream query. Their `details.size`, `processedAmount`, and `scheduledAmount` values are `"...n"` strings; optional detail expiry timestamps also use `"...n"`, while `lastExecutionTimestampMs` is a raw JSON number. Vault TWAP transactions mirror the account create/edit/cancel routes.
- `/api/perpetuals/account/order-history` and `/api/perpetuals/account/collateral-history` accept optional `authentication: { walletAddress, bytes, signature }` in the current service schema. If present, it must use the fixed terms message; the service strips the auth fields before forwarding.
- `/api/perpetuals/vaults/owned-vault-assistant-caps`: requires `walletAddress` and returns `ownedVaultAssistantCaps`.

### SL/TP and stop orders

Applies to `place-sl-tp-orders`, `place-stop-orders`, `edit-stop-orders` (account and vault variants), and embedded `slTp` on limit and market order transaction inputs:

- Price fields are `stopLossPrice` and `takeProfitPrice`.
- Optional `triggerPriceType` selects the trigger price source: `0` index price (default), `1` orderbook mid, `2` mark price.
- Each SL/TP or stop order accepts its own optional `builderCode` (`{ integratorId, integratorFee }`), independent of the parent order's builder code.
- Basic order-history `slTp` responses include only `stopLossPrice` and `takeProfitPrice`; they do not include `triggerPriceType` or `builderCode`.

### Client order IDs

- Transaction `place-limit-order` accepts optional `clientOrderId` (`"...n"`); transaction `place-scale-order` accepts `clientOrderIds`.
- Transaction `cancel-and-place-orders` accepts per-order `clientOrderId`, plus `clientOrderIdsToCancel` and `shouldAbortOnMissingId`.
- Transaction `cancel-orders` accepts per-market `clientOrderIds`; preview `cancel-orders` does not. Both accept `shouldAbortOnMissingId`.
- Position `pendingOrders` entries include `clientOrderId` (`"...n"` string or `null`).

### Builder codes on orders

Order-placement `builderCode` objects are `{ integratorId: u32, integratorFee: number }`. See `auxiliary-endpoints.md` for integrator registration and config routes.

### Response-shape notes

- Market params: `basePriceFeedId` and `collateralPriceFeedId` are numeric (`u32`). `priorityTakerFee` (nullable) governs priority-gas transactions — `null` means priority-gas transactions are rejected.
- Vault parameters: `collateralPriceFeedStorageId` is `u32`; `collateralPriceFeedStorageSourceId` is `u16`.
- Positions carry no per-position `makerFee`/`takerFee` fields.
- Collateral-change history: liquidation entries report net fees without a separate force-cancel component.

### Account order history (cursor pagination)

```http
POST /api/perpetuals/account/order-history
Content-Type: application/json

{
  "accountId": "123n",
  "limit": 50,
  "beforeTimestampCursor": null
}
// -> { orders: [...], nextBeforeTimestampCursor: number | null }
```

### Account detailed trade history

```http
POST /api/perpetuals/account/order-history-detailed
Content-Type: application/json

{
  "accountId": "123n",
  "limit": 100,
  "afterTimestampCursor": null,
  "beforeTimestampCursor": null
}
// -> { trades: [...], nextBeforeTimestampCursor: number | null }
```

### Account detailed trade history CSV

```http
POST /api/perpetuals/account/order-history-detailed-csv
Content-Type: application/json

{
  "accountId": "123n",
  "limit": 100
}
// -> { csv: "..." }
```

### Stop order datas (signed auth)

```http
POST /api/perpetuals/account/stop-order-datas
Content-Type: application/json

{
  "walletAddress": "0x...",
  "bytes": "<base64 of Aftermath Terms and Conditions>",
  "signature": "<signature over decoded terms bytes>",
  "marketIds": ["0x..."],
  "accountId": "123n"
}
```

### Dynamic vault protocol configuration

Use this route for the vault protocol’s live limits. It is distinct from
`GET /api/perpetuals/config`, which returns network-specific AFLP/official-vault
and default-collateral configuration.

`POST /api/perpetuals/vaults/config`
Content-Type: application/json

{}

The request is unauthenticated and must contain the empty JSON object. The
response is a bare object; integer-like values are serialized as bigint-style
strings and decimal limits are JSON numbers:

```typescript
type PerpetualsVaultsConfig = {
  id: string;
  version: string; // e.g. "123n"
  collateralPriceFeedStorageToleranceMs: string;
  maxLockPeriodMs: string;
  maxForceWithdrawDelayMs: string;
  maxPerformanceFeePercentage: number;
  minOwnerLockUsd: number;
  maxOwnerLockUsd: number;
  minDepositUsd: number;
  maxMarketsInVault: string;
  maxPendingOrdersPerPosition: string;
  forceWithdrawPauseMs: string;
  maxAssistantsPerVault: string;
};
```

Treat these values as dynamic deployment configuration. Do not restore SDK
constants or hardcode values such as lock periods, minimum deposits, market
counts, or pending-order limits. In `aftermath-ts-sdk` v3.1.0, use
`sdk.Perpetuals().getVaultsConfig(abortSignal?)`.

### Vault assistant capabilities

These owner-only routes build, but do not broadcast, a vault transaction:

```text
POST /api/perpetuals/vault/transactions/owner/grant-agent-wallet
POST /api/perpetuals/vault/transactions/owner/revoke-agent-wallet
```

`grant-agent-wallet` requires `vaultId` and `recipientAddress`; `revoke-agent-wallet`
requires `vaultId` and `accountCapId`. Both accept optional base64 `txKind` and
optional `sponsor` fields. The response is `{ txKind }` when unsponsored and
adds `sponsorSignature` when a named sponsor is used.

Submit the returned transaction from the vault owner's `ADMIN` capability. The
recipient receives an assistant capability for supported vault trading actions,
not withdrawal or assistant-management authority. Revocation remains an owner
operation even when the vault is paused or frozen.

### Network configuration

```http
GET /api/perpetuals/config
```

Returns `{ aflpVaultId, officialVaultIds, defaultCollateralCoinType }` for
the current network. An upstream config outage returns a 500-style API error;
do not silently substitute an empty vault list or collateral type.

### Vault predeposit totals and TVL

```http
POST /api/perpetuals/vaults/predeposits/user-total-deposits
Content-Type: application/json

{ "userAddress": "0x..." }
// -> { totalDeposits: "1000n" }
```

No recorded deposits return `"0n"`.

```http
POST /api/perpetuals/vaults/predeposits/vault-totals
Content-Type: application/json

{}
// -> { totalDepositors: 12, totalDeposits: "1000n" }
```

Send the empty JSON object; the endpoint requires a JSON body. No records return
`0` and `"0n"`.

```http
GET /api/perpetuals/vaults/0x.../tvl
// -> 12345.67
```

The TVL response is a bare USD number. A missing vault returns HTTP 400 using
the standard API error format.

### Preview error semantics

Some preview routes can return HTTP `200` with:

```json
{ "error": "..." }
```

and header:

```text
X-Error-Message: true
```

Treat preview responses as success/error unions.

More specifically:

- Order and cancel previews commonly return a `oneOf` success-or-`{ error }` schema.
- Several vault admin previews return either a success object or `{ error }` on `200`.
- `/api/perpetuals/vault/previews/pause-vault-for-force-withdraw-request` returns a normal `TxKindResponse`.

---

## Source of Truth

- Swagger UI: `https://aftermath.finance/docs`
- Production OpenAPI JSON: `https://aftermath.finance/api/openapi/spec.json`
