# TypeScript SDK Reference

> Complete reference for `@aftermath-finance/sdk`. Use this for frontend apps, complex integrations, and vault management.

---

## Initialization

```typescript
import { Aftermath } from "@aftermath-finance/sdk";

const afSdk = new Aftermath("MAINNET");  // or "TESTNET"
await afSdk.init();
const perps = afSdk.Perpetuals();
```

### SDK Class Hierarchy

- `Perpetuals` - Main entry point. Market/vault/account discovery, tx builders, WebSocket, pricing.
- `PerpetualsMarket` - Wrapper around a single market. Orderbook, stats, previews, max order size, rounding.
- `PerpetualsAccount` - Wrapper around a trading account. Collateral mgmt, order placement, previews, history.
- `PerpetualsVault` - Wrapper around an afLP vault. Deposits, withdrawals, admin ops, LP pricing.

---

## Perpetuals Class (Entry Point)

### API Mapping (Mental Model)

- SDK market reads generally map to native market endpoints under `/api/perpetuals/markets*` and `/api/perpetuals/market*`.
- SDK account transactions/previews generally map to `/api/perpetuals/account/transactions/*` and `/api/perpetuals/account/previews/*`.
- SDK vault operations generally map to `/api/perpetuals/vault/transactions/*` and `/api/perpetuals/vault/previews/*`.
- Use SDK when you want typed abstractions; use `native.md` for exact HTTP schemas.

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

---

## PerpetualsAccount Class

### Order Placement

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

### Collateral Management

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

Preview responses can carry errors as data; always guard for error-shaped results before using numeric fields.

### Stop Orders (require signed auth)

```typescript
const message = account.getStopOrdersMessageToSign({ marketIds: ["0x..."] });
const { signature } = await wallet.signMessage({ message: new TextEncoder().encode(JSON.stringify(message)) });
const { stopOrderDatas } = await account.getStopOrderDatas({ bytes: JSON.stringify(message), signature });
```

This flow corresponds to native stop-order data and transaction routes. Reach for `native.md` when debugging payload shape mismatches.

### History

```typescript
const { orderHistory, nextBeforeTimestampCursor } = await account.getOrderHistory({ limit: 50 });
const { collateralHistory } = await account.getCollateralHistory({ limit: 50 });
const { marginHistoryDatas } = await account.getMarginHistory({ fromTimestamp, toTimestamp, intervalMs });
```

---

## PerpetualsMarket Class

### Properties

```typescript
market.marketId;          // ObjectId
market.indexPrice;        // Current oracle price
market.collateralPrice;   // Collateral price (e.g., USDC = ~1.0)
market.collateralCoinType;
market.marketParams;      // { lotSize, tickSize, marginRatioInitial, marginRatioMaintenance, makerFee, takerFee, ... }
market.marketState;       // { openInterestLong, openInterestShort, cumFundingRateLong, cumFundingRateShort, ... }
```

### Methods

```typescript
market.lotSize();            // Min order size increment
market.tickSize();           // Min price increment
market.maxLeverage();        // e.g., 20
market.initialMarginRatio();
market.maintenanceMarginRatio();
market.estimatedFundingRate();
market.timeUntilNextFundingMs();
market.roundToValidSize({ size, floor?: boolean });
market.roundToValidPrice({ price });
```

### Data Fetching

```typescript
const { orderbook } = await market.getOrderbook();  // { bids: [{price, size}], asks: [{price, size}] }
const { midPrice } = await market.getOrderbookMidPrice();
const stats = await market.get24hrStats();  // { volume24h, priceChange24h, high24h, low24h, trades24h, ... }
const { maxOrderSize } = await market.getMaxOrderSize({ accountId, side, leverage?, price? });
const { estimatedPrice } = await market.getEstimatedExecutionPrice({ side, size });
const { basePrice, collateralPrice } = await market.getPrices();
```

### Previews (Market-Level, No Account Needed)

```typescript
const preview = await market.getPlaceMarketOrderPreview({ side, size, leverage?, collateralChange?, slippageTolerance? });
const preview = await market.getPlaceLimitOrderPreview({ side, size, price, leverage?, collateralChange? });
```

---

## PerpetualsVault Class

Vaults are managed accounts accepting LP deposits.

### Constants

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

### Vault Discovery

```typescript
const { vaults } = await perps.getAllVaults();
const { vault } = await perps.getVault({ marketId: vaultObjectId });  // Note: param named marketId but is vault ID
```

### User Operations

```typescript
await vault.getDepositTx({ walletAddress, depositAmount, minLpAmountOut });
await vault.getCreateWithdrawRequestTx({ walletAddress, lpWithdrawAmount, minCollateralAmountOut });
await vault.getCancelWithdrawRequestTx({ walletAddress });
```

### Owner Admin

```typescript
await vault.getOwnerProcessWithdrawRequestsTx({ userAddresses: [...] });
await vault.getOwnerWithdrawPerformanceFeesTx({ withdrawAmount, recipientAddress });
await vault.getOwnerUpdateLockPeriodTx({ lockPeriodMs });
await vault.getOwnerUpdatePerformanceFeeTx({ performanceFeePercentage });
```

### Queries

```typescript
const lpPrice = await vault.getLpCoinPrice();
const { account } = await vault.getAccount();
const { withdrawRequests } = await vault.getWithdrawRequests({});
vault.isPaused();
```

### Force Withdraw Flow

```typescript
await vault.getPauseVaultForForceWithdrawRequestTx({});
await vault.getProcessForceWithdrawRequestTx({ walletAddress, sizesToClose, recipientAddress });
```

---

## Fee Structure

See the official docs for current fee tiers: https://docs.aftermath.finance/perpetuals/aftermath-perpetuals
