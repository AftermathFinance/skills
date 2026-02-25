# Auxiliary Endpoint Families

> Quick routing for public API families outside core CCXT/native perpetual trading docs.

---

## Use This File When

- You need endpoints not covered by `ccxt.md` or `native.md`.
- You are implementing integrator flows, builder codes, referrals, rewards, or coin metadata.

---

## Perpetual Utility Transactions

```text
POST /api/perpetuals/transactions/create-account
POST /api/perpetuals/transactions/transfer-cap
```

Required fields:

- `create-account`: `walletAddress`, `collateralCoinType`
- `transfer-cap`: `recipientAddress`, `capObjectId`

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
POST /api/rewards/transactions/claim
```

Minimal request examples:

```typescript
POST /api/rewards/claimable
{ "walletAddress": "0x..." }
```

```typescript
POST /api/rewards/transactions/claim
{
  "walletAddress": "0x...",
  "recipientAddress": "0x..."
}
```

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

---

## Source of Truth

- Swagger UI: `https://aftermath.finance/docs`
- OpenAPI JSON: `https://aftermath.finance/api/openapi/spec.json`
