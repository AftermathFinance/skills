# Auxiliary Endpoint Families

> Quick routing for public API families outside core CCXT/native perpetual trading docs.

---

## Use This File When

- You need endpoints not covered by `ccxt.md` or `native.md`.
- You are implementing integrator flows, gas pool flows, referrals, rewards, rebates, router swaps, metastable vault stats, Birdeye data, dynamic gas sponsorship, zkLogin, or coin metadata.

Use focused references for larger families:

- DCA and spot limit orders: `dca-and-limit-orders.md`
- Staking: `staking.md`
- AMM pools: `pools.md`
- Coin and LP prices: `prices.md`

---

## Perpetual Utility Transactions

```text
POST /api/perpetuals/transactions/create-account
POST /api/perpetuals/transactions/transfer-cap
POST /api/perpetuals/account/transactions/share
```

Required fields:

- `create-account`: `walletAddress`, `collateralCoinType`
- `transfer-cap`: `recipientAddress`
- `share`: account/share-policy arguments from deferred create flow

Composition notes:

- `create-account` supports `deferShare`, optional `txKind`, and optional sponsorship.
- Deferred create-account responses can include `deferred` argument references for follow-up `/api/perpetuals/account/transactions/share` composition.
- `transfer-cap` supports composed flow fields, so do not assume `capObjectId` is always required.

Minimal request example:

```typescript
POST /api/perpetuals/transactions/create-account
{
  "walletAddress": "0x...",
  "collateralCoinType": "0xdba...::usdc::USDC",
  "deferShare": true
}
// -> { txKind, deferred?: { accountArg, adminCapArg, sharePolicyArg, collateralCoinType } }
```

---

## Gas Pool

```text
POST /api/gas-pool/pool
POST /api/gas-pool/transactions/create
POST /api/gas-pool/transactions/deposit
POST /api/gas-pool/transactions/withdraw
POST /api/gas-pool/transactions/grant
POST /api/gas-pool/transactions/revoke
POST /api/gas-pool/transactions/share
POST /api/gas-pool/transactions/sponsor
```

Read route:

- `pool`: returns `walletAddress`, `balance`, `whitelistedAddresses`, and nullable `gasPoolId`.

Composition notes:

- `create` supports optional `initialDepositAmount: "...n"`, optional `txKind`, and `deferShare` for PTB composition.
- Deferred `create` responses can include `gasPoolArg` and `sharePolicyArg`; pass them to `share` to finalize the gas pool.
- `deposit` supports direct SUI deposits and non-SUI swap-to-SUI deposits via `coinType`, optional `amount: "...n"`, optional `coinArg`, and optional `slippage`.
- `withdraw` requires `amount: "...n"`, supports `deferTransfer`, and can return `withdrawnCoinArg` for downstream PTB composition.
- `grant` / `revoke` use `targetWalletAddress`.
- `sponsor` rebates the tx sponsor from the gas pool using `walletAddress` and `amount: "...n"`.
- Most gas-pool tx builders return `TxKindResponse`; `create` and `withdraw` may additionally return PTB argument references.

Minimal request examples:

```typescript
POST /api/gas-pool/pool
{ "walletAddress": "0x..." }
```

```typescript
POST /api/gas-pool/transactions/create
{
  "walletAddress": "0x...",
  "deferShare": true,
  "initialDepositAmount": "1000000000n"
}
// -> { txKind, gasPoolArg?, sharePolicyArg? }
```

```typescript
POST /api/gas-pool/transactions/deposit
{
  "walletAddress": "0x...",
  "coinType": "0x2::sui::SUI",
  "amount": "1000000000n"
}
```

```typescript
POST /api/gas-pool/transactions/withdraw
{
  "walletAddress": "0x...",
  "amount": "500000000n",
  "deferTransfer": true
}
// -> { txKind, withdrawnCoinArg? }
```

---

## Builder Codes (Integrator)

Integrators register once globally and are identified by a numeric `integratorId` (`u32`) everywhere — not by address.

```text
POST /api/perpetuals/builder-codes/integrator-registration
POST /api/perpetuals/builder-codes/integrator-config
POST /api/perpetuals/builder-codes/transactions/create-integrator-registration
POST /api/perpetuals/builder-codes/transactions/create-integrator-config
POST /api/perpetuals/builder-codes/transactions/remove-integrator-config
```

Flow and field notes:

- `transactions/create-integrator-registration`: one-time global registration; the integrator identity is the transaction sender. Body is just optional `txKind` and optional `sponsor`.
- `integrator-registration`: resolves `{ integratorId }` to `{ integratorAddress }`.
- `integrator-config`: requires `accountId` (numeric) and `integratorId`; returns `{ exists, maxIntegratorFee }` (nullable fee).
- `transactions/create-integrator-config`: requires `accountId`, `integratorId`, `maxIntegratorFee`; optional `txKind` and `sponsor`.
- `transactions/remove-integrator-config`: requires `accountId` and `integratorId`; optional `txKind` and `sponsor`.

Minimal request example:

```typescript
POST /api/perpetuals/builder-codes/integrator-config
{
  "accountId": "123n",
  "integratorId": 1
}
// -> { exists: true, maxIntegratorFee: 0.0005 }
```

Order-placement usage:

- Order routes accept `builderCode: { integratorId, integratorFee }` — the per-order integrator fee, capped by the account's configured `maxIntegratorFee`.
- SL/TP and stop orders accept their own `builderCode`, independent of the parent order's.

---

## Perpetuals Rebates

```text
POST /api/perpetuals/rebates/rewards
POST /api/perpetuals/rebates/create-csv-rebates
```

Request notes:

- Both routes accept optional `accountIds`, required `calculationVariables`, required `totalMakerRewards`, and required `totalTakerRewards`.
- `calculationVariables` requires `qScoreCoefficient`, `uptimeCoefficient`, `mmVolumeCoefficient`, `takerVolumeCoefficient`, and `takerOiCoefficient`.
- `rewards` returns `{ rewards, totalQScoreFinal, totalEstimatedGasCost }`.
- `create-csv-rebates` accepts optional `aggregated` (default `false`) and returns `{ csv }`.

Minimal request example:

```typescript
POST /api/perpetuals/rebates/rewards
{
  "accountIds": ["123n"],
  "calculationVariables": {
    "qScoreCoefficient": 1,
    "uptimeCoefficient": 1,
    "mmVolumeCoefficient": 1,
    "takerVolumeCoefficient": 1,
    "takerOiCoefficient": 1
  },
  "totalMakerRewards": 1000,
  "totalTakerRewards": 1000
}
```

---

## Referrals

```text
POST /api/referrals/availability
POST /api/referrals/create
POST /api/referrals/link
POST /api/referrals/linked-ref-code
POST /api/referrals/query
POST /api/referrals/ref-code
```

Minimal request example:

```typescript
POST /api/referrals/link
{
  "walletAddress": "0x...",
  "bytes": "...",
  "signature": "..."
}
```

---

## Rewards

```text
POST /api/rewards/claimable
POST /api/rewards/history
POST /api/rewards/points
POST /api/rewards/expectedRewards
POST /api/rewards/transactions/claim
```

Minimal request examples:

```typescript
POST /api/rewards/claimable
{ "walletAddress": "0x..." }
```

```typescript
POST /api/rewards/points
{
  "walletAddress": "0x...",
  "bytes": "{\"action\":\"GET_POINTS\"}",
  "signature": "..."
}
```

```typescript
POST /api/rewards/transactions/claim
{
  "walletAddress": "0x..."
}
```

Request/response notes:

- `claim` requires `walletAddress`; `coinTypes`, `recipientAddress`, and `txKind` are optional.
- `history` is a signed request (`walletAddress`, `bytes`, `signature` required) supporting `cursor`, `limit`, and optional `domain` filtering. Entries carry `eventType` (`"deposit" | "withdraw" | "points"`); `coinType` may be `"points"` for point events.
- `points` is a signed request returning `{ totalPoints }` (float), representing actual accrued points.
- `expectedRewards` is a forward-looking estimator with no signed auth. Provide exactly one account selector: `address` or `accountId` (`"...n"`). Other fields are optional: `epoch`, maker/taker totals, calculation coefficients, and budget/rate overrides. Response: `{ epoch, total, domains }`; `tokensRaw` values are `"...n"` strings.

---

## Coins and Auth Utilities

```text
GET  /api/coins/verified
POST /api/coins/metadata
POST /api/zklogin/create
```

Minimal request example:

```typescript
POST /api/coins/metadata
{ "coins": ["0x2::sui::SUI"] }
```

Response note:

- Coin metadata entries can include `iconUrl`, `id`, `isGenerated`, and `metadataType` in addition to `name`, `symbol`, `description`, and `decimals`.

zkLogin note:

- `/api/zklogin/create` requires `ephemeralKeyPair`, `jwt`, `maxEpoch`, and `randomness`; it returns `walletAddress`, `addressSeed`, and a `partialZkLoginSignature`.

Referral response note:

- `/api/referrals/link` returns structured fields including `status`, `refCode`, `refereeAddress`, and `createdAt`.

---

## Router Utilities

```text
POST /api/router/trade-route
POST /api/router/transactions/add-trade
```

Router notes:

- `trade-route` requires `coinInType` and `coinOutType`. Send exactly one amount: `coinInAmount` for fixed input or `coinOutAmount` for fixed output.
- Fixed-output routing requires `slippage`. Route filters, `externalFee`, and `referrer` remain optional.
- `transactions/add-trade` composes a quoted `completeRoute` into an existing serialized transaction and returns `{ tx, coinOutId }`.
- `coinOutId` uses SDK-style Sui argument casing such as `{ "Input": 0 }`, `{ "Result": 3 }`, or `{ "NestedResult": [2, 1] }`.

---

## Metastable

```text
POST /api/metastable/vaults
POST /api/metastable/tvl
POST /api/metastable/fees/{duration_ms}
POST /api/metastable/volume/{duration_ms}
GET  /api/metastable/{vault_id}/coingecko/supply
```

Request/response notes:

- The POST reads accept an optional `vaultIds` filter (`{ "vaultIds": ["0x..."] | null }`).
- `vaults` returns vault objects with `objectId`, `objectType`, `metaCoinType`, `metaCoinDecimals`, `supply`, `metadatas`, `totalPriorities`, and `activeAssistantCap`.
- `tvl`, `fees/{duration_ms}`, and `volume/{duration_ms}` return bare numbers; `{duration_ms}` is a path param in milliseconds.
- Legacy GET routes (`GET /api/metastable/tvl`, `GET /api/metastable/24hr-volume`, `GET /api/metastable/{vault_id}/tvl`, `GET /api/metastable/{vault_id}/24hr-volume`) remain available. Prefer the POST routes.

---

## Birdeye Price Data

```text
POST /api/birdeye/historical
POST /api/birdeye/market
```

Request/response notes:

- `historical`: requires `coin` and `interval` (`"1H" | "1D" | "1W" | "1M"`); returns `{ historicalData: [{ price, timestamp, volume }] }`.
- `market`: requires `coin`; returns nullable `price`, `liquidity`, `supply`, `circulatingSupply`, `marketcap`, `circulatingMarketcap`.

---

## Dynamic Gas

```text
POST /api/dynamic-gas
```

- Sponsors a serialized transaction with gas paid in a non-SUI coin: requires `serializedTx`, `walletAddress`, `gasCoinType`; returns `{ txBytes, sponsoredSignature }`.

---

## Source of Truth

- Swagger UI: `https://aftermath.finance/docs`
- Production OpenAPI JSON: `https://aftermath.finance/api/openapi/spec.json`
