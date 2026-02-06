---
name: aftermath-perpetuals
description: Expert knowledge for building on Aftermath Perpetuals (Sui). Covers the CCXT REST API, TypeScript SDK, vaults, and all trading operations.
---

# Aftermath Perpetuals - Complete Developer Reference

Use this skill when working on anything related to Aftermath Finance perpetual futures on Sui.

---

## 1. Protocol Overview

Aftermath Perpetuals is a **fully onchain perpetual futures exchange on Sui**. Every order, cancellation, trade, and liquidation executes transparently onchain with single-slot finality.

- **Architecture**: Onchain central limit order book (CLOB) in Move smart contracts
- **Margin**: Isolated margin (leverage varies per market)
- **Collateral**: USDC on Sui (`0xdba34672e30cb065b1f93e3ab55318768fd6fef66c15942c9f7cb846e2f900e7::usdc::USDC`)
- **Oracle**: Aggregator combining Pyth, Stork, Switchboard, and Seda feeds
- **Mark Price**: Median of book price, funding price, and TWAP
- **Liquidation**: Four-layer cascade (partial liquidation → insurance fund → socialized losses → auto-deleverage)
- **afLP Vault**: Community-owned liquidity for market making (LP deposit → share in fees + PnL)

---

## 2. Two Integration Approaches

### Approach A: CCXT REST API (Recommended for bots)

The CCXT REST API is simpler and recommended for bots. Base URLs:

| Environment | URL |
|---|---|
| Production | `https://aftermath.finance` |
| Mainnet Preview | `https://mainnet-perpetuals-preview.aftermath.finance` |
| Testnet | `https://testnet.aftermath.finance` |

**Transaction Workflow** (Build → Sign → Submit):

```typescript
// 1. Build: POST /api/ccxt/build/createOrders → { transactionBytes, signingDigest }
// 2. Sign: Client signs signingDigest with Ed25519 keypair
// 3. Submit: POST /api/ccxt/submit/createOrders → order results
```

**All Endpoints (30 total):**

| Method | Endpoint | Description |
|---|---|---|
| **Market Data** | | |
| GET | `/api/ccxt/markets` | List all markets |
| GET | `/api/ccxt/currencies` | List all currencies |
| POST | `/api/ccxt/orderbook` | Get orderbook snapshot |
| POST | `/api/ccxt/ticker` | Get ticker for a market |
| POST | `/api/ccxt/OHLCV` | Get candlestick data |
| POST | `/api/ccxt/trades` | Get public trade history |
| **Account** | | |
| POST | `/api/ccxt/accounts` | Get accounts for wallet |
| POST | `/api/ccxt/balance` | Get account balance |
| POST | `/api/ccxt/positions` | Get account positions |
| POST | `/api/ccxt/myPendingOrders` | Get pending orders for a market |
| **Orders** | | |
| POST | `/api/ccxt/build/createOrders` | Build order tx |
| POST | `/api/ccxt/submit/createOrders` | Submit signed order tx |
| POST | `/api/ccxt/build/cancelOrders` | Build cancel tx |
| POST | `/api/ccxt/submit/cancelOrders` | Submit signed cancel tx |
| **Account Setup** | | |
| POST | `/api/ccxt/build/createAccount` | Build create account tx |
| POST | `/api/ccxt/submit/createAccount` | Submit signed create account tx |
| **Collateral** | | |
| POST | `/api/ccxt/build/deposit` | Deposit collateral into account |
| POST | `/api/ccxt/submit/deposit` | Submit signed deposit tx |
| POST | `/api/ccxt/build/withdraw` | Withdraw collateral from account |
| POST | `/api/ccxt/submit/withdraw` | Submit signed withdraw tx |
| **Margin** | | |
| POST | `/api/ccxt/build/allocate` | Allocate margin to a position |
| POST | `/api/ccxt/submit/allocate` | Submit signed allocate tx |
| POST | `/api/ccxt/build/deallocate` | Deallocate margin from a position |
| POST | `/api/ccxt/submit/deallocate` | Submit signed deallocate tx |
| **Leverage** | | |
| POST | `/api/ccxt/build/setLeverage` | Set leverage for a position |
| POST | `/api/ccxt/submit/setLeverage` | Submit signed set leverage tx |

**SSE Streaming Endpoints:**

| Endpoint | Description |
|---|---|
| GET `/api/ccxt/stream/orderbook?chId={marketId}` | Orderbook deltas |
| GET `/api/ccxt/stream/orders?chId={marketId}` | Order updates |
| GET `/api/ccxt/stream/positions?accountNumber={num}` | Position updates |
| GET `/api/ccxt/stream/trades?chId={marketId}` | Trade stream |

**Key Identifiers:**

| ID | Description | Source |
|---|---|---|
| `chId` | Clearing house / Market ID | `Market.id` from `/api/ccxt/markets` |
| `accountCapId` | Account capability object ID | `Account.id` where `type == "capability"` |
| `accountNumber` | Numerical account identifier | `Account.accountNumber` |

**CCXT API Types:**

```typescript
interface TransactionMetadata {
  sender: string;           // Wallet address (0x-prefixed 32-byte hex)
  gasBudget?: number;       // Max SUI MIST (estimated via dry-run if omitted)
  gasPrice?: number;        // SUI MIST per gas unit (defaults to reference gas price)
  sponsor?: string;         // Address owning gas coins (defaults to sender)
}

interface OrderRequest {
  chId: string;                    // Market ID (clearing house object ID)
  type: "market" | "limit";
  side: "buy" | "sell";
  amount?: number;                 // Base currency amount
  price?: number;                  // Required for limit orders
  reduceOnly?: boolean;
  expirationTimestampMs?: number;
}

interface TransactionBuildResponse {
  transactionBytes: string;  // Base64 BCS-encoded transaction
  signingDigest: string;     // Base64 32-byte digest to sign
}

interface SubmitTransactionRequest {
  transactionBytes: string;
  signatures: string[];      // Base64 Sui signatures
}
```

**Sui Signing (Ed25519):**

All CCXT write operations follow a build → sign → submit flow. Here's how to sign:

```typescript
import { Ed25519Keypair } from "@mysten/sui/keypairs/ed25519";

// 1. Create keypair from private key
const keypair = Ed25519Keypair.fromSecretKey(privateKeyBytes); // 32-byte seed

// 2. Build the transaction
const { transactionBytes, signingDigest } = await fetch("/api/ccxt/build/createOrders", {
  method: "POST",
  body: JSON.stringify({ orders, accountId, deallocateFreeCollateral: false, metadata: { sender: address } }),
}).then(r => r.json());

// 3. Sign the digest (NOT the transactionBytes)
const digestBytes = Buffer.from(signingDigest, "base64");
const { signature } = await keypair.signPersonalMessage(digestBytes);

// 4. Construct full Sui signature: [0x00 scheme flag] + [64-byte Ed25519 sig] + [32-byte pubkey]
const sigBytes = Buffer.from(signature, "base64");
const pubkeyBytes = keypair.getPublicKey().toRawBytes();
const fullSignature = Buffer.concat([Buffer.from([0x00]), sigBytes, pubkeyBytes]);

// 5. Submit
const result = await fetch("/api/ccxt/submit/createOrders", {
  method: "POST",
  body: JSON.stringify({
    transactionBytes,
    signatures: [fullSignature.toString("base64")],
  }),
}).then(r => r.json());
```

**Account Creation Flow:**

Before trading, you need a trading account:

```typescript
// 1. Build create account tx (settleId comes from Market.settleId via /api/ccxt/markets)
const { transactionBytes, signingDigest } = await fetch("/api/ccxt/build/createAccount", {
  method: "POST",
  body: JSON.stringify({
    settleId: "0xdba34672e30cb065b1f93e3ab55318768fd6fef66c15942c9f7cb846e2f900e7::usdc::USDC",
    metadata: { sender: walletAddress },
  }),
}).then(r => r.json());

// 2. Sign & submit (same pattern as above)
// Response: Account[] with { id, type: "capability"|"account", accountNumber, collateral }
```

**Markets Response Schema:**

```typescript
GET /api/ccxt/markets
// → Array<Market>
// Key fields for trading:
{
  id: string;              // ← This is your chId (clearing house / market ID)
  symbol: string;          // e.g. "BTC/USD:USDC"
  base: string;            // e.g. "BTC"
  quote: string;           // e.g. "USD"
  settle: string;          // e.g. "USDC"
  settleId: string;        // ← Full coin type, needed for createAccount
  active: boolean;
  type: "swap";            // Perpetual swap
  contract: true;
  linear: true;
  contractSize: number;
  precision: { amount: number, price: number };
  limits: {
    amount: { min, max },
    price: { min, max },
    leverage: { min, max }
  };
  maker: number;           // Maker fee rate (e.g. 0.0002 = 0.02%)
  taker: number;           // Taker fee rate (e.g. 0.0005 = 0.05%)
}
```

**Full Request/Response Examples:**

```typescript
// Place a limit order
POST /api/ccxt/build/createOrders
{
  "orders": [{
    "chId": "0x...",          // Market.id from /api/ccxt/markets
    "type": "limit",
    "side": "buy",
    "amount": 0.01,           // Base currency amount
    "price": 95000,           // Limit price
    "reduceOnly": false
  }],
  "accountId": "0x...",       // AccountCap ID (type == "capability")
  "deallocateFreeCollateral": false,
  "metadata": { "sender": "0x..." }
}
// → { "transactionBytes": "base64...", "signingDigest": "base64..." }

// Cancel orders
POST /api/ccxt/build/cancelOrders
{
  "chId": "0x...",            // Market ID
  "orderIds": ["123", "456"],
  "accountId": "0x...",
  "deallocateFreeCollateral": false,
  "metadata": { "sender": "0x..." }
}

// Get orderbook
POST /api/ccxt/orderbook
{ "chId": "0x..." }
// → { "bids": [[95000, 1.5], [94999, 0.8]], "asks": [[95001, 2.0], [95002, 1.2]], "nonce": 42, "timestamp": 1738800000000 }

// Get positions
POST /api/ccxt/positions
{ "accountNumber": 123 }
// → [{ "symbol": "BTC/USD:USDC", "side": "long", "contracts": 0.5, "entryPrice": 94500,
//      "leverage": 5, "unrealizedPnl": 250, "liquidationPrice": 80000, "collateral": 9450,
//      "marginMode": "isolated", "notional": 47250, "initialMargin": 9450 }]

// Get accounts for a wallet
POST /api/ccxt/accounts
{ "address": "0x..." }
// → [{ "id": "0x...", "type": "capability", "accountNumber": 123, "code": "USDC", "collateral": 10000 },
//    { "id": "0x...", "type": "account", "accountNumber": 123, "code": "USDC", "collateral": 10000 }]

// Get balance
POST /api/ccxt/balance
{ "account": "0x..." }  // capability or account object ID
// → { "balances": { "USDC": { "free": 5000, "used": 5000, "total": 10000 } }, "timestamp": 1738800000000 }

// Get pending orders
POST /api/ccxt/myPendingOrders
{ "accountNumber": 123, "chId": "0x..." }
// → [{ "id": "789", "status": "open", "symbol": "BTC/USD:USDC", "side": "buy", "type": "limit",
//      "price": 94000, "amount": 0.1, "filled": 0, "remaining": 0.1, "timeInForce": "GTC" }]

// Get ticker
POST /api/ccxt/ticker
{ "chId": "0x..." }
// → { "symbol": "BTC/USD:USDC", "bid": 95000, "ask": 95001, "last": 95000, "high": 96000,
//      "low": 94000, "baseVolume": 1250, "markPrice": 95000.5, "indexPrice": 95001 }

// Get OHLCV candles
POST /api/ccxt/OHLCV
{ "chId": "0x...", "timeframe": "1h", "limit": 100 }
// → [[1738800000000, 94500, 95200, 94100, 95000, 1250], ...]  // [timestamp, open, high, low, close, volume]

// Get public trades
POST /api/ccxt/trades
{ "chId": "0x...", "limit": 50 }
// → { "trades": [{ "price": 95000, "amount": 0.5, "side": "buy", "timestamp": 1738800000000, "takerOrMaker": "taker" }], "nextCursor": 456 }

// Deposit collateral (build → sign → submit)
POST /api/ccxt/build/deposit
{ "accountId": "0x...", "amount": 1000, "metadata": { "sender": "0x..." } }
// → { "transactionBytes": "base64...", "signingDigest": "base64..." }
// ⚠️ Prone to race conditions — concurrent deposits may use same coin object

// Withdraw collateral
POST /api/ccxt/build/withdraw
{ "accountId": "0x...", "amount": 500, "metadata": { "sender": "0x..." } }

// Allocate margin to a position (moves funds from account → position)
POST /api/ccxt/build/allocate
{ "accountId": "0x...", "chId": "0x...", "amount": 1000, "metadata": { "sender": "0x..." } }

// Deallocate margin from a position (moves funds from position → account)
POST /api/ccxt/build/deallocate
{ "accountId": "0x...", "chId": "0x...", "amount": 500, "metadata": { "sender": "0x..." } }

// Set leverage
POST /api/ccxt/build/setLeverage
{ "accountId": "0x...", "chId": "0x...", "leverage": 10, "metadata": { "sender": "0x..." } }

// Get user order history (REST, not SSE — via perpetuals API, not CCXT)
POST /api/perpetuals/account/order-history
{ "accountId": "0x...", "limit": 50 }
// → Paginated order history across all markets (fills, cancels, etc.)
// Sorted reverse chronological, cursor-based pagination

// Get order fill data by order IDs
POST /api/perpetuals/account/order-datas
{ "accountId": "0x...", "orderIds": ["123", "456"] }
// → Returns initial sizes per order; filledSize = initialSize - currentSize

// Get market-level trade history
POST /api/perpetuals/market/order-history
{ "marketId": "0x...", "limit": 50 }
// → Recent trades for a specific market, paginated
```

**SSE Streaming Format:**

Connect via `GET` with query parameters. Events are Server-Sent Events (SSE):

```typescript
// Orderbook deltas
const es = new EventSource("/api/ccxt/stream/orderbook?chId=0x...");
es.onmessage = (event) => {
  const delta = JSON.parse(event.data);
  // { bids: [[price, amount_delta], ...], asks: [[price, amount_delta], ...], nonce: 43, timestamp: 1738800001000 }
  // amount_delta: new absolute size at that price level (0 = level removed)
};

// Order updates
const es = new EventSource("/api/ccxt/stream/orders?chId=0x...");
es.onmessage = (event) => {
  const order = JSON.parse(event.data);
  // Full Order object: { id, status, symbol, side, price, amount, filled, remaining, ... }
};

// Position updates
const es = new EventSource("/api/ccxt/stream/positions?accountNumber=123");
es.onmessage = (event) => {
  const position = JSON.parse(event.data);
  // Full Position object: { symbol, side, contracts, entryPrice, leverage, unrealizedPnl, ... }
};

// Trade stream
const es = new EventSource("/api/ccxt/stream/trades?chId=0x...");
es.onmessage = (event) => {
  const trade = JSON.parse(event.data);
  // { amount, price, side, timestamp, takerOrMaker, ... }
};
```

### Approach B: TypeScript SDK (@aftermath-finance/sdk)

For frontend apps and more complex integrations:

```typescript
import { Aftermath } from "@aftermath-finance/sdk";

const afSdk = new Aftermath("MAINNET");
await afSdk.init();
const perps = afSdk.Perpetuals();
```

**SDK Class Hierarchy:**

- `Perpetuals` - Main entry point. Market/vault/account discovery, tx builders, WebSocket, pricing.
- `PerpetualsMarket` - Wrapper around a single market. Orderbook, stats, previews, max order size, rounding.
- `PerpetualsAccount` - Wrapper around a trading account. Collateral mgmt, order placement, previews, history.
- `PerpetualsVault` - Wrapper around an afLP vault. Deposits, withdrawals, admin ops, LP pricing.

---

## 3. SDK: Perpetuals Class (Key Methods)

### Market Discovery
```typescript
const { markets } = await perps.getAllMarkets({ collateralCoinType: "0xdba...::usdc::USDC" });
const { market } = await perps.getMarket({ marketId: "0x..." });
const { markets } = await perps.getMarkets({ marketIds: ["0x...", "0x..."] });
```

### Account Management
```typescript
// Get account caps (ownership objects)
const { accounts: caps } = await perps.getOwnedAccountCaps({ walletAddress: "0x..." });

// Fetch full account with positions
const { account } = await perps.getAccount({ accountCap: caps[0] });

// Access account data
account.collateral();          // Available collateral
account.account.totalEquity;   // Total equity
account.account.positions;     // Array of positions
account.accountId();           // Numeric account ID
account.positionForMarketId({ marketId: "0x..." }); // Find specific position
```

### Order Placement (via Account)
```typescript
// Market order
const { tx } = await account.getPlaceMarketOrderTx({
  marketId: "0x...",
  side: PerpetualsOrderSide.Bid,  // Bid = buy/long, Ask = sell/short
  size: 1n * Casting.Fixed.fixedOneN9,  // Size in base units (9 decimals)
  collateralChange: 5000,  // Add 5000 USDC
  reduceOnly: false,
  leverage: 5,
  slTp: { stopLossIndexPrice: 40000, takeProfitIndexPrice: 50000 }  // Optional
});

// Limit order
const { tx } = await account.getPlaceLimitOrderTx({
  marketId: "0x...",
  side: PerpetualsOrderSide.Bid,
  size: 1n * Casting.Fixed.fixedOneN9,
  price: 42000,
  collateralChange: 5000,
  reduceOnly: false,
  orderType: PerpetualsOrderType.PostOnly,
  expiration: Date.now() + 86400000,
});

// Cancel orders
const { tx } = await account.getCancelOrdersTx({
  marketIdsToData: {
    "0xMARKET_ID": { orderIds: [12345n], collateralChange: -1000, leverage: 5 }
  }
});

// Set leverage
const { tx } = await account.getSetLeverageTx({ marketId: "0x...", leverage: 10, collateralChange: -1000 });
```

### Collateral Management (via Account)
```typescript
await account.getDepositCollateralTx({ depositAmount: 10n * 1_000_000n });
await account.getWithdrawCollateralTx({ withdrawAmount: 5n * 1_000_000n, recipientAddress: "0x..." });
await account.getAllocateCollateralTx({ marketId: "0x...", allocateAmount: 10n * 1_000_000n });
await account.getDeallocateCollateralTx({ marketId: "0x...", deallocateAmount: 5n * 1_000_000n });
await account.getTransferCollateralTx({ transferAmount: 10n * 1_000_000n, toAccountId: 456n });
```

### Order/Position Previews
```typescript
const preview = await account.getPlaceMarketOrderPreview({ ... });
// Returns: { executionPrice, slippage, filledSize, postedSize, updatedPosition } or { error }

const preview = await account.getPlaceLimitOrderPreview({ ... });
const preview = await account.getCancelOrdersPreview({ ... });
const preview = await account.getSetLeveragePreview({ marketId, leverage });
const preview = await account.getEditCollateralPreview({ marketId, collateralChange });
```

### Stop Orders (require signed auth)
```typescript
const message = account.getStopOrdersMessageToSign({ marketIds: ["0x..."] });
const { signature } = await wallet.signMessage({ message: new TextEncoder().encode(JSON.stringify(message)) });
const { stopOrderDatas } = await account.getStopOrderDatas({ bytes: JSON.stringify(message), signature });
```

### History
```typescript
const { orderHistory, nextBeforeTimestampCursor } = await account.getOrderHistory({ limit: 50 });
const { collateralHistory } = await account.getCollateralHistory({ limit: 50 });
const { marginHistoryDatas } = await account.getMarginHistory({ fromTimestamp, toTimestamp, intervalMs });
```

---

## 4. SDK: PerpetualsMarket Class

```typescript
// Properties
market.marketId;          // ObjectId
market.indexPrice;        // Current oracle price
market.collateralPrice;   // Collateral price (e.g., USDC = ~1.0)
market.collateralCoinType;
market.marketParams;      // { lotSize, tickSize, marginRatioInitial, marginRatioMaintenance, makerFee, takerFee, ... }
market.marketState;       // { openInterestLong, openInterestShort, cumFundingRateLong, cumFundingRateShort, ... }

// Methods
market.lotSize();            // Min order size increment
market.tickSize();           // Min price increment
market.maxLeverage();        // e.g., 20
market.initialMarginRatio();
market.maintenanceMarginRatio();
market.estimatedFundingRate();
market.timeUntilNextFundingMs();
market.roundToValidSize({ size, floor?: boolean });
market.roundToValidPrice({ price });

// Data fetching
const { orderbook } = await market.getOrderbook();  // { bids: [{price, size}], asks: [{price, size}] }
const { midPrice } = await market.getOrderbookMidPrice();
const stats = await market.get24hrStats();  // { volume24h, priceChange24h, high24h, low24h, trades24h, ... }
const { maxOrderSize } = await market.getMaxOrderSize({ accountId, side, leverage?, price? });
const { estimatedPrice } = await market.getEstimatedExecutionPrice({ side, size });
const { basePrice, collateralPrice } = await market.getPrices();

// Previews (market-level, no account needed)
const preview = await market.getPlaceMarketOrderPreview({ side, size, leverage?, collateralChange?, slippageTolerance? });
const preview = await market.getPlaceLimitOrderPreview({ side, size, price, leverage?, collateralChange? });
```

---

## 5. SDK: PerpetualsVault Class

Vaults are managed accounts accepting LP deposits. Constants:

```typescript
PerpetualsVault.constants = {
  maxLockPeriodMs: 5184000000,        // 2 months
  maxForceWithdrawDelayMs: 86400000,  // 1 day
  maxPerformanceFeePercentage: 0.2,   // 20%
  minDepositUsd: 1,
  maxMarketsInVault: 12,
  maxPendingOrdersPerPosition: 70,
};
```

Key methods:
```typescript
// Vault discovery
const { vaults } = await perps.getAllVaults();
const { vault } = await perps.getVault({ marketId: vaultObjectId });  // Note: param named marketId but is vault ID

// User operations
await vault.getDepositTx({ walletAddress, depositAmount, minLpAmountOut });
await vault.getCreateWithdrawRequestTx({ walletAddress, lpWithdrawAmount, minCollateralAmountOut });
await vault.getCancelWithdrawRequestTx({ walletAddress });

// Owner admin
await vault.getOwnerProcessWithdrawRequestsTx({ userAddresses: [...] });
await vault.getOwnerWithdrawPerformanceFeesTx({ withdrawAmount, recipientAddress });
await vault.getOwnerUpdateLockPeriodTx({ lockPeriodMs });
await vault.getOwnerUpdatePerformanceFeeTx({ performanceFeePercentage });

// Queries
const lpPrice = await vault.getLpCoinPrice();
const { account } = await vault.getAccount();
const { withdrawRequests } = await vault.getWithdrawRequests({});
vault.isPaused();

// Force withdraw flow
await vault.getPauseVaultForForceWithdrawRequestTx({});
await vault.getProcessForceWithdrawRequestTx({ walletAddress, sizesToClose, recipientAddress });
```

---

## 6. Fee Structure

See the official docs for current fee tiers: https://docs.aftermath.finance/perpetuals/aftermath-perpetuals

---

## 7. Important Gotchas

1. **Size units**: SDK uses `bigint` with 9 decimal places (`Casting.Fixed.fixedOneN9`). CCXT API uses `number` (float). Always convert correctly.
2. **Collateral units**: USDC has 6 decimals. `10n * 1_000_000n` = 10 USDC.
3. **LP token units**: 9 decimals typically.
4. **`getVault` parameter name**: The param is named `marketId` but it actually takes a **vault object ID**.
5. **Account state is a snapshot**: Refresh after placing/canceling orders, after fills, liquidations, or funding.
6. **Transaction model**: All writes require build → sign → submit (two-phase). Sign the `signingDigest` not the `transactionBytes`.
7. **Sui signature format**: `[0x00 flag byte] + [64-byte Ed25519 signature] + [32-byte public key]`, Base64 encoded.
8. **Rate limit**: Aftermath API allows ~1000 requests per 10 seconds.
9. **Order types**: Market, Limit (GTC, IOC, FOK, PostOnly).
10. **Deposit race condition**: Concurrent deposits for the same sender may try to use the same coin object. Avoid parallel deposit txs.
11. **Collateral flow**: Deposit → Account (unallocated) → Allocate → Position (margin). Reverse: Deallocate → Withdraw.
12. **No order modify/amend**: To update a resting order, you must cancel and re-place. Only stop orders (SL/TP) can be edited in-place via `edit-stop-orders`.
13. **Client Order ID**: Supported — set `clientOrderId` when placing orders. Returned on all `Order` objects. Useful for tracking orders without relying on exchange-assigned IDs.
14. **Funding rate**: Live estimated rate available via market data (`estimatedFundingRate`, `nextFundingTimestampMs`). Per-position unrealized funding via `unrealizedFundingsUsd`. No dedicated historical funding rate time-series endpoint.
15. **Order status lookup**: No single "get order by ID" endpoint. Use `myPendingOrders` for open orders, `order-history` for historical, or `order-datas` for fill info by order ID.
16. **No dead man's switch**: No scheduled cancel / kill switch. MM bots should implement their own heartbeat-based cancel logic.
17. **No user fee tier query**: Market-level maker/taker rates are on the `Market` object. No endpoint to query your personal fee tier. Check the docs for the tier schedule.
18. **No user rate limit query**: Rate limit is ~1000 requests per 10 seconds. No endpoint to check current usage.

---

## 8. Reference Links

- Aftermath Docs: https://docs.aftermath.finance/perpetuals/aftermath-perpetuals
- CCXT OpenAPI Spec: https://mainnet-perpetuals-preview.aftermath.finance/api/openapi/spec.json
- SDK npm: `@aftermath-finance/sdk` (or `aftermath-ts-sdk`)
- Sui TypeScript SDK: https://sdk.mystenlabs.com/typescript
- Example market maker bot (built with this skill): https://github.com/mission69b/aftermath-market-maker
