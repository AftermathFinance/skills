# Monitoring Patterns

> Practical monitoring patterns using CCXT and native Perpetuals endpoints.

---

## 1) Fast Market Scanner (Native Bulk Endpoints)

Use native bulk endpoints to reduce request fanout:

```typescript
const BASE_URL = "https://aftermath.finance";

async function fetchJson<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  const text = await response.text();
  let body: unknown = text;
  try { body = text ? JSON.parse(text) : null; } catch {}
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${typeof body === "string" ? body : JSON.stringify(body)}`);
  return body as T;
}

async function scanMarkets() {
  const markets = await fetchJson<{ markets: Array<{ objectId: string }> }>(`${BASE_URL}/api/perpetuals/all-markets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      collateralCoinType: "0xdba34672e30cb065b1f93e3ab55318768fd6fef66c15942c9f7cb846e2f900e7::usdc::USDC",
    }),
  });

  const marketIds = markets.markets.map((market) => market.objectId);
  const prices = await fetchJson(`${BASE_URL}/api/perpetuals/markets/prices`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ marketIds }),
  });

  const stats24h = await fetchJson(`${BASE_URL}/api/perpetuals/markets/24hr-stats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ marketIds }),
  });

  return { markets, prices, stats24h };
}
```

---

## 2) CCXT-Compatible Scanner (Simple and Portable)

```typescript
async function scanWithCcxt() {
  const markets = await fetchJson<any[]>(`${BASE_URL}/api/ccxt/markets`);

  const rows = await Promise.all(
    markets
      .filter((m: any) => m.active)
      .map(async (m: any) => {
        const ticker = await fetchJson<any>(`${BASE_URL}/api/ccxt/ticker`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chId: m.id }),
        });

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
async function monitorPositions(
  accountNumber: number,
  maintenanceRatioBySymbol: Record<string, number>,
) {
  const positions = await fetchJson<any[]>(`${BASE_URL}/api/ccxt/positions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ accountNumber }),
  });

  for (const p of positions) {
    const ratio = Number.isFinite(p.marginRatio)
      ? p.marginRatio
      : Number.isFinite(p.notional) && p.notional !== 0 && Number.isFinite(p.collateral)
        ? p.collateral / p.notional
        : null;
    const maintenance = maintenanceRatioBySymbol[p.symbol];
    if (ratio === null || !Number.isFinite(maintenance)) continue;

    const state = ratio <= maintenance ? "LIQUIDATION" : ratio <= maintenance * 1.5 ? "DANGER" : "OK";
    console.log(`${p.symbol}: ratio=${(ratio * 100).toFixed(2)}% state=${state}`);
  }
}
```

---

## 4) Trades Backfill With Cursor Pagination

```typescript
async function fetchAllTrades(chId: string, pageSize = 50) {
  const out: any[] = [];
  let cursor: number | null = null;

  while (true) {
    const page = await fetchJson<{ trades: any[]; nextCursor?: number | null }>(`${BASE_URL}/api/ccxt/trades`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chId, limit: pageSize, cursor }),
    });

    out.push(...page.trades);
    if (page.nextCursor == null) break;
    cursor = page.nextCursor;
  }

  return out;
}
```

---

## 5) Stream Updates

### CCXT WebSocket stream

```typescript
const orderbookWs = new WebSocket("wss://aftermath.finance/api/ccxt/stream/orderbook?chId=0x...");
orderbookWs.onmessage = (event) => {
  const delta = JSON.parse(event.data);
  // apply orderbook deltas
};
```

### Native WebSocket proxy

```typescript
const ws = new WebSocket("wss://aftermath.finance/api/perpetuals/ws/updates");
ws.onopen = () => {
  // subscribe per stream; see native.md for all subscriptionType variants
  ws.send(JSON.stringify({
    action: "subscribe",
    subscriptionType: { marketCandles: { marketId: "0x...", interval: "1m" } },
  }));
};
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // handle multi-type perpetuals updates (market, user, orderbook, marketCandles, ...)
};
```

Market candles stream over this same socket via the `marketCandles` subscription. See `native.md` for the full interval enum.

---

## 6) Reconnect and Resync Rule

On WebSocket reconnect:

1. Re-fetch snapshots (`/api/ccxt/orderbook`, positions, or native markets/orderbooks).
2. Replace local state atomically.
3. Resume delta processing.

Do not continue from stale in-memory state after disconnects.
