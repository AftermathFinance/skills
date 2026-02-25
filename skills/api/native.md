# Native Perpetuals Endpoint Reference

> Native perpetuals endpoints under `/api/perpetuals/*`.

This is the preferred and canonical API surface for integrations because it exposes the complete feature set beyond CCXT compatibility.

Verified against OpenAPI: `https://aftermath.finance/api/openapi/spec.json`
Last validated: `2026-02-25`

---

## Endpoint Families

### Accounts and positions

```text
POST /api/perpetuals/accounts/owned
POST /api/perpetuals/accounts
POST /api/perpetuals/accounts/positions
POST /api/perpetuals/account/max-order-size
POST /api/perpetuals/account/order-history
POST /api/perpetuals/account/collateral-history
POST /api/perpetuals/account/margin-history
POST /api/perpetuals/account/stop-order-datas
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
POST /api/perpetuals/market/order-history
```

### Vaults

```text
POST /api/perpetuals/vaults
POST /api/perpetuals/vaults/lp-coin-prices
POST /api/perpetuals/vaults/owned-lp-coins
POST /api/perpetuals/vaults/owned-vault-caps
POST /api/perpetuals/vaults/owned-withdraw-requests
POST /api/perpetuals/vaults/withdraw-requests
POST /api/perpetuals/vault/stop-order-datas
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
POST /api/perpetuals/vault/previews/owner/withdraw-performance-fees
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
POST /api/perpetuals/vault/transactions/pause-vault-for-force-withdraw-request
POST /api/perpetuals/vault/transactions/process-force-withdraw-request
POST /api/perpetuals/vault/transactions/update-withdraw-request-slippage
POST /api/perpetuals/vault/transactions/owner/process-withdraw-requests
POST /api/perpetuals/vault/transactions/owner/update-force-withdraw-delay
POST /api/perpetuals/vault/transactions/owner/update-lock-period
POST /api/perpetuals/vault/transactions/owner/update-performance-fee
POST /api/perpetuals/vault/transactions/owner/withdraw-collateral
POST /api/perpetuals/vault/transactions/owner/withdraw-performance-fees
```

### WebSocket proxy

```text
GET /api/perpetuals/ws/updates
GET /api/perpetuals/ws/market-candles/{market_id}/{interval_ms}
```

---

## Identifier Rules

| Field | Meaning |
|---|---|
| `accountId` | Numeric account ID |
| `marketId` | Market object ID |
| `vaultId` | Vault object ID |

Do not pass CCXT account capability object IDs (`0x...`) where numeric `accountId` is required.

---

## Correct Native Examples

Required-field reminders for high-risk routes:

- `/api/perpetuals/all-markets`: requires `collateralCoinType`.
- `/api/perpetuals/account/max-order-size`: requires `marketId`, numeric `accountId`, and `side` (`0` bid, `1` ask).
- `/api/perpetuals/account/stop-order-datas`: requires auth payload (`walletAddress`, `bytes`, `signature`) plus exactly one target (`accountId` or `vaultId`).

### Account order history (cursor pagination)

```http
POST /api/perpetuals/account/order-history
Content-Type: application/json

{
  "accountId": 123,
  "limit": 50,
  "beforeTimestampCursor": null
}
// -> { orders: [...], nextBeforeTimestampCursor: number | null }
```

### Stop order datas (signed auth)

```http
POST /api/perpetuals/account/stop-order-datas
Content-Type: application/json

{
  "walletAddress": "0x...",
  "bytes": "...",
  "signature": "...",
  "marketIds": ["0x..."],
  "accountId": 123
}
```

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

---

## Source of Truth

- Swagger UI: `https://aftermath.finance/docs`
- OpenAPI JSON: `https://aftermath.finance/api/openapi/spec.json`
