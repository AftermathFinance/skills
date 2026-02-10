# Safety & Risk Management

> Read this when building anything that involves real funds, margin, or automated trading on Aftermath Perpetuals.

---

## Isolated Margin Model

Aftermath uses **isolated margin** — each position has its own margin allocation. A liquidation in one market does not directly drain collateral from other positions.

### Collateral Flow

```
Wallet USDC
  -> Deposit -> Account (unallocated collateral)
    -> Allocate -> Position A (isolated margin)
    -> Allocate -> Position B (isolated margin)
```

Unallocated collateral sits in the account but is NOT protecting any position. You must explicitly allocate margin to each position.

---

## Margin & Liquidation Mechanics

### Key Metrics

| Metric | Description | Where to Find |
|--------|-------------|---------------|
| **Initial Margin Ratio** | Minimum margin to open a position | `market.initialMarginRatio()` or `market.marketParams.marginRatioInitial` |
| **Maintenance Margin Ratio** | Below this = liquidation | `market.maintenanceMarginRatio()` or `market.marketParams.marginRatioMaintenance` |
| **Max Leverage** | `1 / initialMarginRatio` | `market.maxLeverage()` or `Market.limits.leverage.max` |

### Liquidation Cascade

Aftermath uses a four-layer liquidation system:

```
1. Partial Liquidation   -- Reduce position to restore margin health
2. Insurance Fund        -- Absorbs losses if position is bankrupt
3. Socialized Losses     -- Spread across profitable traders (rare)
4. Auto-Deleverage (ADL) -- Close profitable positions against bankrupt ones (extreme)
```

### Calculating Margin Health

```typescript
// For a single isolated position:
// margin ratio = position collateral / notional value
// notional = abs(size) * mark price

async function checkPositionHealth(
  account: PerpetualsAccount,
  market: PerpetualsMarket,
  marketId: string
) {
  const position = account.positionForMarketId({ marketId });
  if (!position) return { status: "NO_POSITION" };

  const notional = Math.abs(Number(position.baseAssetAmount)) * market.indexPrice;
  const collateral = Number(position.collateral);
  const marginRatio = collateral / notional;
  const maintenanceRatio = market.maintenanceMarginRatio();

  return {
    marginRatio,
    maintenanceRatio,
    bufferPct: ((marginRatio - maintenanceRatio) * 100).toFixed(2) + "%",
    status: marginRatio < maintenanceRatio ? "LIQUIDATION"
          : marginRatio < maintenanceRatio * 1.5 ? "DANGER"
          : marginRatio < maintenanceRatio * 2 ? "WARNING"
          : "SAFE",
  };
}
```

### Margin Health Zones

| Zone | Margin Ratio vs Maintenance | Action |
|------|----------------------------|--------|
| **Safe** | > 2x maintenance | Normal monitoring |
| **Warning** | 1.5x - 2x maintenance | Increase monitoring frequency |
| **Danger** | 1x - 1.5x maintenance | Add margin or reduce position NOW |
| **Liquidation** | < 1x maintenance | Liquidation imminent or in progress |

---

## Position Sizing

### Conservative: 2% Rule

Never risk more than 2% of total account value on a single trade:

```typescript
function calculateMaxSize(
  accountCollateral: number,   // Total USDC in account
  entryPrice: number,
  stopLossPrice: number,
  riskPercent: number = 2
): number {
  const riskAmount = accountCollateral * (riskPercent / 100);
  const priceDistance = Math.abs(entryPrice - stopLossPrice);
  return riskAmount / priceDistance;
}

// Example: $10,000 account, buying SOL at $150, stop at $140
// Risk amount = $200, price distance = $10
// Max size = 20 SOL
```

### Leverage Guidelines

| Experience | Max Leverage | Rationale |
|------------|-------------|-----------|
| Learning / testing | 1-2x | Room for mistakes |
| Normal trading | 3-5x | Balanced risk/reward |
| Experienced | 5-10x | Requires active monitoring |
| Expert / MM | 10-20x | Requires automated risk systems |

---

## API-Assisted Risk Checks

Use native Perpetuals endpoints to enforce limits before submitting transactions.

### Max Order Size Guard

```typescript
async function fetchMaxOrderSize(accountId: number, marketId: string, side: 0 | 1) {
  const res = await fetch("https://aftermath.finance/api/perpetuals/account/max-order-size", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ accountId, marketId, side }), // side enum: 0=bid, 1=ask
  });
  return res.json();
}
```

Call this before placing large orders or increasing leverage.

### Historical Risk Telemetry

Track account behavior over time using:

- `POST /api/perpetuals/account/margin-history`
- `POST /api/perpetuals/account/collateral-history`

Use these for drawdown alerts, margin utilization trends, and post-incident analysis.

---

## Circuit Breakers

Automated safety limits for trading bots. Implement these before going live.

### Tier 1: Soft Limits (Log Warnings)

```typescript
interface SoftLimits {
  maxDrawdownPct: number;      // e.g., 0.05 = 5%
  maxPositionNotional: number; // e.g., 50000 USDC
  maxLeverage: number;         // e.g., 5
  minMarginBuffer: number;     // e.g., 2.0 = 2x maintenance margin
}

function checkSoftLimits(limits: SoftLimits, state: BotState): string[] {
  const warnings: string[] = [];

  if (state.drawdownPct > limits.maxDrawdownPct) {
    warnings.push(`Drawdown ${(state.drawdownPct * 100).toFixed(1)}% exceeds soft limit`);
  }
  if (state.positionNotional > limits.maxPositionNotional) {
    warnings.push(`Position $${state.positionNotional} exceeds max notional`);
  }
  if (state.effectiveLeverage > limits.maxLeverage) {
    warnings.push(`Leverage ${state.effectiveLeverage.toFixed(1)}x exceeds limit`);
  }

  return warnings;
}
```

### Tier 2: Hard Limits (Stop Trading)

```typescript
interface HardLimits {
  maxDrawdownPct: number;      // e.g., 0.15 = 15%
  maxDailyLoss: number;        // e.g., 5000 USDC
  maxDailyTrades: number;      // e.g., 200
}

function enforceHardLimits(limits: HardLimits, state: BotState): string | null {
  if (state.drawdownPct > limits.maxDrawdownPct) {
    return "HALT: Maximum drawdown exceeded";
  }
  if (state.dailyLoss > limits.maxDailyLoss) {
    return "HALT: Daily loss limit reached";
  }
  if (state.dailyTradeCount > limits.maxDailyTrades) {
    return "HALT: Daily trade limit reached";
  }
  return null; // No halt needed
}
```

---

## Kill Switch Pattern

Aftermath has **no built-in dead man's switch** (see `gotchas.md`). Bots must implement their own.

### Heartbeat-Based Kill Switch

```typescript
class KillSwitch {
  private lastHeartbeat: number = Date.now();
  private armed: boolean = true;

  constructor(
    private maxSilenceMs: number = 30_000,  // 30 seconds without heartbeat = kill
    private cancelAllFn: () => Promise<void>,
  ) {}

  heartbeat() {
    this.lastHeartbeat = Date.now();
  }

  async check(): Promise<boolean> {
    if (!this.armed) return false;

    const silenceMs = Date.now() - this.lastHeartbeat;
    if (silenceMs > this.maxSilenceMs) {
      console.error(`Kill switch triggered: ${silenceMs}ms since last heartbeat`);
      await this.trigger("Heartbeat timeout");
      return true;
    }
    return false;
  }

  async trigger(reason: string) {
    if (!this.armed) return;
    this.armed = false;

    console.error(`KILL SWITCH: ${reason}`);

    try {
      await this.cancelAllFn();
      console.log("All orders cancelled successfully");
    } catch (err) {
      console.error("Kill switch cancel failed:", err);
      // At this point, manual intervention is required
    }
  }

  disarm() { this.armed = false; }
  rearm()  { this.armed = true; this.lastHeartbeat = Date.now(); }
}
```

### Usage with CCXT API

```typescript
const killSwitch = new KillSwitch(30_000, async () => {
  // Cancel all orders across all markets
  const markets = await fetch(`${BASE_URL}/api/ccxt/markets`).then(r => r.json());

  for (const market of markets) {
    const pendingOrders = await fetch(`${BASE_URL}/api/ccxt/myPendingOrders`, {
      method: "POST",
      body: JSON.stringify({ accountNumber, chId: market.id }),
    }).then(r => r.json());

    if (pendingOrders.length > 0) {
      const orderIds = pendingOrders.map((o: any) => o.id);
      // Build -> sign -> submit cancel
      const { transactionBytes, signingDigest } = await fetch(
        `${BASE_URL}/api/ccxt/build/cancelOrders`,
        {
          method: "POST",
          body: JSON.stringify({
            chId: market.id,
            orderIds,
            accountId: accountCapId,
            deallocateFreeCollateral: false,
            metadata: { sender: walletAddress },
          }),
        }
      ).then(r => r.json());

      const signature = signDigest(signingDigest, keypair);
      await fetch(`${BASE_URL}/api/ccxt/submit/cancelOrders`, {
        method: "POST",
        body: JSON.stringify({ transactionBytes, signatures: [signature] }),
      });
    }
  }
});

// In your main loop:
setInterval(() => killSwitch.check(), 5_000);

// In your trading logic:
function onTick() {
  killSwitch.heartbeat();
  // ... trading logic ...
}

// On SIGINT/SIGTERM:
process.on("SIGINT", () => killSwitch.trigger("Manual interrupt"));
process.on("SIGTERM", () => killSwitch.trigger("Process terminated"));
```

---

## Emergency Procedures

| Scenario | Immediate Action | Follow-Up |
|----------|-----------------|-----------|
| **Approaching liquidation** | Allocate more margin or close position | Review leverage settings |
| **Bot unresponsive** | Kill switch triggers auto-cancel | Check logs, restart with lower limits |
| **Wrong market/size** | Cancel order immediately | Add order validation |
| **Deposit race condition** | Wait for first deposit to confirm, then retry | Serialize deposit operations |
| **API returning errors** | Pause trading, check status | Implement backoff (see error-handling.md) |
| **Unexpected fills** | Check `myPendingOrders` for stale orders | Cancel all, audit order history |

---

## Pre-Launch Checklist

Before deploying any bot to mainnet:

- [ ] Tested all logic on testnet (`https://testnet.aftermath.finance`)
- [ ] Circuit breakers implemented and tested (both soft and hard limits)
- [ ] Kill switch implemented with heartbeat timeout
- [ ] Position sizing enforced (never exceeds risk limits)
- [ ] Error handling covers all failure modes (see error-handling.md)
- [ ] Logging captures all order submissions, fills, and errors
- [ ] SIGINT/SIGTERM handlers cancel all orders on shutdown
- [ ] Deposit operations are serialized (no parallel deposits)
- [ ] Account state is refreshed after every order/fill/cancel
