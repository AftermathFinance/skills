# CCXT Endpoint Reference

> CCXT-compatible endpoints under `/api/ccxt/*`.

Use CCXT when you need exchange-style request/response compatibility. For full Aftermath feature coverage, prefer native perpetuals endpoints in `native.md`.

Production OpenAPI: `https://aftermath.finance/api/openapi/spec.json`
Last validated: `2026-07-28`

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

`OHLCV` requires `chId` and accepts optional `timeframe`, `since`, and `limit`. `timeframe` defaults to `"1h"`; supported labels are `1m | 5m | 15m | 30m | 1h | 4h | 12h | 1d | 3d | 1w | 1mo`. The API clamps `limit` to `512`.

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

```typescript
const orderbookWs = new WebSocket(
  `wss://aftermath.finance/api/ccxt/stream/orderbook?chId=${marketId}`,
);

// Alternative native multiplexed WebSocket API
const nativeWs = new WebSocket("wss://aftermath.finance/api/perpetuals/ws/updates");
```

---

## CCXT IDs

| Field | Meaning |
|---|---|
| `chId` | Market object ID |
| `accountId` | Account capability object ID (for writes) |
| `accountNumber` | Numeric account identifier (for reads/streams) |
| `account` | Balance lookup identifier accepted by `/api/ccxt/balance` |

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
  clientOrderId?: string;
}

interface CancelOrdersRequest {
  accountId: string;
  chId: string;
  orderIds: string[];
  deallocateFreeCollateral: boolean;
  metadata: TransactionMetadata;
  shouldAbortOnMissingId?: boolean; // default false: missing IDs tolerated
  clientOrderIds?: string[];        // client-managed IDs to cancel, in addition to orderIds
}

interface TransactionMetadata {
  sender: string;
  gasBudget?: number;
  gasPrice?: number;
  sponsor?: string;
  gasCoins?: Array<{ objectId: string; version: number; digest: string }>;
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
- `signingDigest` is base64-encoded. Decode it before signing unless your signer accepts base64 directly.
- Each `signatures` entry is a base64-encoded complete Sui `UserSignature` byte sequence.
- `signatures` can contain multiple signatures (for example sender + separate gas owner/sponsor signer).
- `POST /api/ccxt/balance` expects `account`, not `accountId` or `accountNumber`.
- `OrderRequest` supports optional `clientOrderId`. Do not send unsupported `timeInForce` or `postOnly` fields.
- CCXT order responses can still include omitted or nullable fields such as `clientOrderId`, `postOnly`, `timeInForce`, `stopPrice`, and `takeProfitPrice`.

Submit responses:

| Route suffix | Response |
|---|---|
| `createAccount` | `Account[]` |
| `deposit`, `withdraw` | `Account` |
| `allocate`, `deallocate`, `setLeverage` | `Position` |
| `createOrders`, `cancelOrders` | `Order[]` |

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

{ "chId": "0x...", "limit": 50, "cursor": null, "until": null }
// -> { trades: Trade[], nextCursor: number | null }
```

The API clamps trade pages to `50`. Omitting `until` uses the current time.

---

## Source of Truth

- Swagger UI: `https://aftermath.finance/docs`
- Production OpenAPI JSON: `https://aftermath.finance/api/openapi/spec.json`
