# DCA and Spot Limit Orders

> DCA and spot limit-order reads, signed actions, and transaction builders.

These APIs return frontend-ready serialized transactions. They do not use the
CCXT build-sign-submit response shape.

## DCA Routes

```text
POST /api/dca/active
POST /api/dca/past
POST /api/dca/cancel
POST /api/dca/transactions/create-order
```

### Read orders

`active` and `past` require the same body:

```json
{ "walletAddress": "0x..." }
```

Both return a bare `DcaOrderObject[]`, sorted by creation time descending.

Important response fields:

- `objectId`: DCA order object ID.
- `overview.allocatedCoin`, `overview.buyCoin`, and `overview.totalSpent`: amounts are `"...n"` strings.
- `overview.intervalMs`, `overview.totalTrades`, `overview.tradesRemaining`, and `overview.maxSlippageBps`: JSON numbers.
- `overview.strategy`: nullable `{ minPrice, maxPrice }`, with `"...n"` price strings.
- `overview.created`, `overview.nextTrade`, and optional `overview.lastExecutedTrade`: transaction timing data.
- `trades`: completed executions; coin amounts are decimal strings without an added `n`.
- `failed`: `{ timestamp, reason }[]`.

`OrderTxData` includes the canonical `timestamp` and `txnDigest` fields plus the
legacy duplicates `time` and misspelled `tnx_digest`.

### Create a DCA order transaction

```typescript
type CreateDcaOrderRequest = {
  allocateCoinAmount: string;
  walletAddress: string;
  allocateCoinType: string;
  buyCoinType: string;
  frequencyMs: number;
  tradesAmount: number;
  delayTimeMs: number;
  maxAllowableSlippageBps: number;
  coinPerTradeAmount: string;
  isSponsoredTx: boolean;
  strategy?: { minPrice: string; maxPrice: string } | null;
  customRecipient?: string | null;
  integratorFee?: { feeRecipient: string; feeBps: number } | null;
};
```

Request rules:

- `allocateCoinAmount`, `coinPerTradeAmount`, and strategy prices may include a trailing `n`.
- `tradesAmount` must not exceed `255`. Oversized requests use error code `2007`.
- Omitting `strategy` uses the full price range.
- An absent or empty `customRecipient` defaults to `walletAddress`.
- An absent `integratorFee` uses a zero fee and zero address.
- Dry-run failures use error code `2008`.

The response is a bare JSON string containing the serialized transaction.

### Cancel a DCA order

`POST /api/dca/cancel` requires signed authentication:

```json
{
  "walletAddress": "0x...",
  "bytes": "...",
  "signature": "..."
}
```

The signed bytes identify the order to cancel.

## Spot Limit-Order Routes

```text
POST /api/limit-orders/active
POST /api/limit-orders/past
POST /api/limit-orders/cancel
POST /api/limit-orders/min-order-size-usd
POST /api/limit-orders/transactions/create-order
```

### Reads and cancellation

- `active` requires `walletAddress`, `bytes`, and `signature`.
- `past` requires only `walletAddress`.
- `active` and `past` return a bare `LimitOrderObject[]`, sorted by creation time descending.
- Response objects use camelCase fields such as `objectId`, `allocatedCoin`, `buyCoin`, `currentAmountSold`, `currentAmountBought`, `expiryTimestamp`, `integratorFee`, and `outputToInputStopLossExchangeRate`.
- `allocatedCoin.amount`, `buyCoin.amount`, `currentAmountSold`, and `currentAmountBought` are `"...n"` strings.
- `created` and optional `finished` are `{ timestamp, txnDigest }`.
- `cancel` requires the same signed fields as `active` and returns a bare boolean.
- `min-order-size-usd` accepts a bodyless POST and returns a bare USD number.

### Create a limit-order transaction

```typescript
type CreateLimitOrderRequest = {
  walletAddress: string;
  allocateCoinType: string;
  allocateCoinAmount: string;
  buyCoinType: string;
  expiryDurationMs: number;
  outputToInputExchangeRate: number;
  isSponsoredTx: boolean;
  customRecipient?: string | null;
  integratorFee?: { feeRecipient: string; feeBps: number } | null;
  outputToInputStopLossExchangeRate?: number | null;
};
```

Request rules:

- `allocateCoinAmount` may include a trailing `n`.
- An absent or empty `customRecipient` defaults to `walletAddress`.
- An absent integrator fee uses a zero fee and zero address.
- An absent stop-loss exchange rate disables the stop loss.
- Dry-run failures use error code `2009`.

The response is a bare JSON string containing the serialized transaction.

## Errors

Do not assume all failures use the OpenAPI `ErrorResponse` object. The API can
return a JSON string with error headers, plain text, or a structured body. See
`error-handling.md`.
