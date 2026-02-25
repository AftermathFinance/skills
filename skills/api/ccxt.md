# CCXT Endpoint Reference

> CCXT-compatible endpoints under `/api/ccxt/*`.

Use CCXT when you need exchange-style request/response compatibility. For full Aftermath feature coverage, prefer native perpetuals endpoints in `native.md`.

Verified against OpenAPI: `https://aftermath.finance/api/openapi/spec.json`
Last validated: `2026-02-25`

---

## Endpoint Groups

### Public market data

```text
GET  /api/ccxt/markets
GET  /api/ccxt/currencies
POST /api/ccxt/orderbook
POST /api/ccxt/ticker
POST /api/ccxt/OHLCV
POST /api/ccxt/trades
```

### Account reads

```text
POST /api/ccxt/accounts
POST /api/ccxt/balance
POST /api/ccxt/positions
POST /api/ccxt/myPendingOrders
```

### Signed writes (build -> sign -> submit)

```text
POST /api/ccxt/build/createOrders   -> POST /api/ccxt/submit/createOrders
POST /api/ccxt/build/cancelOrders   -> POST /api/ccxt/submit/cancelOrders
POST /api/ccxt/build/createAccount  -> POST /api/ccxt/submit/createAccount
POST /api/ccxt/build/deposit        -> POST /api/ccxt/submit/deposit
POST /api/ccxt/build/withdraw       -> POST /api/ccxt/submit/withdraw
POST /api/ccxt/build/allocate       -> POST /api/ccxt/submit/allocate
POST /api/ccxt/build/deallocate     -> POST /api/ccxt/submit/deallocate
POST /api/ccxt/build/setLeverage    -> POST /api/ccxt/submit/setLeverage
```

### Streams

```text
GET /api/ccxt/stream/orderbook?chId={marketId}
GET /api/ccxt/stream/orders?chId={marketId}
GET /api/ccxt/stream/positions?accountNumber={number}
GET /api/ccxt/stream/trades?chId={marketId}
```

OpenAPI currently models these GET stream routes with request-body schemas (`chId`/`accountNumber`). Browser `EventSource` cannot send request bodies, so validate query-parameter behavior in your deployment before relying on it.

Canonical client pattern: use query parameters for browser/EventSource clients.

Because OpenAPI models request bodies on these GET stream routes, treat stream transport as deployment-specific. Validate once in staging, then lock one mode for production.

If query-based SSE is not accepted in your environment, use native WebSocket updates via `/api/perpetuals/ws/updates` and adapt payload handling.

Do not rely on GET request bodies for browser clients.

```typescript
const BASE_URL = "https://aftermath.finance";

// Browser SSE (canonical)
const es = new EventSource(`${BASE_URL}/api/ccxt/stream/orderbook?chId=${marketId}`);

// Native WS fallback
const ws = new WebSocket("wss://aftermath.finance/api/perpetuals/ws/updates");
```

---

## CCXT IDs

| Field | Meaning |
|---|---|
| `chId` | Market object ID |
| `accountId` | Account capability object ID (for writes) |
| `accountNumber` | Numeric account identifier (for reads/streams) |

---

## Request Types (Current Schema)

```typescript
interface OrderRequest {
  chId: string;
  type: "market" | "limit";
  side: "buy" | "sell";
  amount?: number;
  price?: number;
  reduceOnly?: boolean;
  expirationTimestampMs?: number;
}

interface TransactionMetadata {
  sender: string;
  gasBudget?: number;
  gasPrice?: number;
  sponsor?: string;
  gasCoins?: Array<{ objectId: string; version: string | number; digest: string }>;
}

interface TransactionBuildResponse {
  transactionBytes: string;
  signingDigest: string;
}

interface SubmitTransactionRequest {
  transactionBytes: string;
  signatures: string[];
}
```

Notes:
- Sign `signingDigest`, not `transactionBytes`.
- `signatures` can contain multiple signatures (for example sender + separate gas owner/sponsor signer).
- `OrderRequest` does not currently include `clientOrderId`, `timeInForce`, or `postOnly`.

---

## Common Examples

### Place orders

```http
POST /api/ccxt/build/createOrders
Content-Type: application/json

{
  "orders": [{ "chId": "0x...", "type": "limit", "side": "buy", "amount": 0.01, "price": 95000 }],
  "accountId": "0x...",
  "deallocateFreeCollateral": false,
  "metadata": { "sender": "0x..." }
}
```

### Fetch paginated trades

```http
POST /api/ccxt/trades
Content-Type: application/json

{ "chId": "0x...", "limit": 200, "cursor": null, "until": null }
// -> { trades: Trade[], nextCursor: number | null }
```

---

## Source of Truth

- Swagger UI: `https://aftermath.finance/docs`
- OpenAPI JSON: `https://aftermath.finance/api/openapi/spec.json`
