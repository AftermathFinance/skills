# Auxiliary Endpoint Families

> Quick routing for public API families outside core CCXT/native perpetual trading docs.

---

## Use This File When

- You need endpoints not covered by `ccxt.md` or `native.md`.
- You are implementing integrator flows, gas pool flows, referrals, rewards, or coin metadata.

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

- `create` supports optional `initialDepositAmount`, optional `txKind`, and `deferShare` for PTB composition.
- Deferred `create` responses can include `gasPoolArg` and `sharePolicyArg`; pass them to `share` to finalize the gas pool.
- `deposit` supports direct SUI deposits and non-SUI swap-to-SUI deposits via `coinType`, `amount`, optional `coinArg`, and optional `slippage`.
- `withdraw` supports `deferTransfer` and can return `withdrawnCoinArg` for downstream PTB composition.
- `grant` / `revoke` use `targetWalletAddress`.
- `sponsor` rebates the tx sponsor from the gas pool using `walletAddress` and `amount`.
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
  "initialDepositAmount": 1000000000
}
// -> { txKind, gasPoolArg?, sharePolicyArg? }
```

```typescript
POST /api/gas-pool/transactions/deposit
{
  "walletAddress": "0x...",
  "coinType": "0x2::sui::SUI",
  "amount": 1000000000
}
```

```typescript
POST /api/gas-pool/transactions/withdraw
{
  "walletAddress": "0x...",
  "amount": 500000000,
  "deferTransfer": true
}
// -> { txKind, withdrawnCoinArg? }
```

---

## Builder Codes (Integrator)

```text
POST /api/perpetuals/builder-codes/integrator-config
POST /api/perpetuals/builder-codes/integrator-vaults
POST /api/perpetuals/builder-codes/transactions/create-integrator-config
POST /api/perpetuals/builder-codes/transactions/remove-integrator-config
POST /api/perpetuals/builder-codes/transactions/create-integrator-vault
POST /api/perpetuals/builder-codes/transactions/claim-integrator-vault-fees
```

Minimal request example:

```typescript
POST /api/perpetuals/builder-codes/integrator-vaults
{
  "integratorAddress": "0x...",
  "marketIds": ["0x..."]
}
```

Response data reminder:

- `integratorVaults[]` entries include `marketId`, `collateralCoinType`, `fees`, and `feesUsd`.

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
- `history` supports `cursor`, `limit`, and optional `domain` filtering.
- `points` is a signed request returning `{ points }`.

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

Referral response note:

- `/api/referrals/link` returns structured fields including `status`, `refCode`, `refereeAddress`, and `createdAt`.

---

## Source of Truth

- Swagger UI: `https://aftermath.finance/docs`
- OpenAPI JSON: `https://aftermath.finance/api/openapi/spec.json`
