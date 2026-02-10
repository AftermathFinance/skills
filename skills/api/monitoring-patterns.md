# Monitoring Patterns

> Practical monitoring patterns using CCXT and native Perpetuals endpoints.

---

## 1) Fast Market Scanner (Native Bulk Endpoints)

Use native bulk endpoints to reduce request fanout:

```typescript
const BASE_URL = "https://aftermath.finance.lp";

async function scanMarkets() {
  const markets = await fetch(`${BASE_URL}/api/perpetuals/all-markets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      collateralCoinType: "0xdba34672e30cb065b1f93e3ab55318768fd6fef66c15942c9f7cb846e2f900e7::usdc::USDC",
    }),
  }).then(r => r.json());

  const prices = await fetch(`${BASE_URL}/api/perpetuals/markets/prices`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ marketIds: markets.markets.map((m: any) => m.marketId) }),
  }).then(r => r.json());

  const stats24h = await fetch(`${BASE_URL}/api/perpetuals/markets/24hr-stats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ marketIds: markets.markets.map((m: any) => m.marketId) }),
  }).then(r => r.json());

  return { markets, prices, stats24h };
}
```

---

## 2) CCXT-Compatible Scanner (Simple and Portable)

```typescript
async function scanWithCcxt() {
  const markets = await fetch(`${BASE_URL}/api/ccxt/markets`).then(r => r.json());

  const rows = await Promise.all(
    markets
      .filter((m: any) => m.active)
      .map(async (m: any) => {
        const ticker = await fetch(`${BASE_URL}/api/ccxt/ticker`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chId: m.id }),
        }).then(r => r.json());

        return {
          symbol: m.symbol,
          bid: ticker.bid,
          ask: ticker.ask,
          markPrice: ticker.markPrice,
          indexPrice: ticker.indexPrice,
        };
      }),
  );

  console.table(rows);
}
```

---

## 3) Position Health Monitor

```typescript
async function monitorPositions(accountNumber: number) {
  const positions = await fetch(`${BASE_URL}/api/ccxt/positions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ accountNumber }),
  }).then(r => r.json());

  for (const p of positions) {
    const ratio = p.marginRatio ?? (p.notional ? p.collateral / p.notional : null);
    if (ratio === null) continue;

    const state = ratio < 0.05 ? "LIQUIDATION" : ratio < 0.08 ? "DANGER" : "OK";
    console.log(`${p.symbol}: ratio=${(ratio * 100).toFixed(2)}% state=${state}`);
  }
}
```

---

## 4) Trades Backfill With Cursor Pagination

```typescript
async function fetchAllTrades(chId: string, pageSize = 200) {
  const out: any[] = [];
  let cursor: number | null = null;

  while (true) {
    const page = await fetch(`${BASE_URL}/api/ccxt/trades`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chId, limit: pageSize, cursor }),
    }).then(r => r.json());

    out.push(...page.trades);
    if (page.nextCursor == null) break;
    cursor = page.nextCursor;
  }

  return out;
}
```

---

## 5) Stream Updates

### CCXT SSE stream

```typescript
const es = new EventSource(`${BASE_URL}/api/ccxt/stream/orderbook?chId=0x...`);
es.onmessage = (event) => {
  const delta = JSON.parse(event.data);
  // apply orderbook deltas
};
```

### Native WebSocket proxy

```typescript
const ws = new WebSocket("wss://aftermath.finance.lp/api/perpetuals/ws/updates");
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // handle multi-type perpetuals updates
};
```

Also available: market candles stream

```text
GET /api/perpetuals/ws/market-candles/{market_id}/{interval_ms}
```

---

## 6) Reconnect and Resync Rule

On stream reconnect:

1. Re-fetch snapshots (`/api/ccxt/orderbook`, positions, or native markets/orderbooks).
2. Replace local state atomically.
3. Resume delta processing.

Do not continue from stale in-memory state after disconnects.
