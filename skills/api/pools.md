# Pools Endpoint Reference

> AMM pool objects, statistics, events, LP ownership, and CoinGecko data.

Do not confuse `/api/pools/*` with the shared sponsorship API under
`/api/gas-pool/*`.

## Current Routes

```text
POST /api/pools
GET  /api/pools/coingecko/tickers
POST /api/pools/coingecko-ticker-data
POST /api/pools/interaction-events-by-user
POST /api/pools/owned-lp-coins
POST /api/pools/pool-object-ids
POST /api/pools/stats
GET  /api/pools/total-swap-volume/{duration_ms}
POST /api/pools/tvl
POST /api/pools/{pool_id}/events/{event_type}
GET  /api/pools/{pool_id}/fees/{timeframe}
POST /api/pools/{pool_id}/interaction-events-by-user
GET  /api/pools/{pool_id}/swap-volume/{duration_ms}
GET  /api/pools/{pool_id}/volume/{timeframe}
```

## Deprecated Routes

```text
GET  /api/pools
POST /api/pools/objects
GET  /api/pools/volume-24hrs
GET  /api/pools/{pool_id}
GET  /api/pools/{pool_id}/stats
GET  /api/pools/{pool_id}/volume-24hrs
```

Prefer `POST /api/pools`, `POST /api/pools/stats`, and the duration-based volume
routes.

## Path Spelling

Only the hyphenated public paths shown above are valid.

## Pool Objects

### Fetch pools

`POST /api/pools` requires a JSON body:

```typescript
type PoolsRequest = { poolIds?: string[] | null };
```

Omitting `poolIds` or passing null returns all pools. The response is a bare
`PoolObject[]`.

The deprecated `GET /api/pools` also returns all pools. The deprecated
`POST /api/pools/objects` uses `{ objectIds?: string[] | null }`. The deprecated
`GET /api/pools/{pool_id}` returns one pool and reports a missing pool as a bad
request.

Important `PoolObject` fields:

```typescript
type PoolObject = {
  objectType: string;
  objectId: string;
  name: string;
  creator: string;
  lpCoinType: string;
  lpCoinSupply: string;
  illiquidLpCoinSupply: string;
  flatness: string;
  lpCoinDecimals: number;
  coins: Record<string, {
    weight: string;
    balance: string;
    tradeFeeIn: string;
    tradeFeeOut: string;
    depositFee: string;
    withdrawFee: string;
    normalizedBalance: string;
    decimalsScalar: string;
    decimals?: number | null;
  }>;
  daoFeePoolObject?: {
    objectId: string;
    objectType: string;
    feeBps: string;
    feeRecipient: string;
  };
};
```

Most integer-like pool fields use `"...n"` strings. Responses omit
`daoFeePoolObject` when no DAO fee object exists. Each coin entry includes the
required `balance` field.

### LP ownership and lookup

`POST /api/pools/owned-lp-coins` requires `{ walletAddress }` and returns:

```typescript
type OwnedLpCoins = Array<{ lpCoinType: string; poolId: string; balance: string }>;
```

`balance` is a `"...n"` string.

`POST /api/pools/pool-object-ids` requires `{ lpCoinTypes: string[] }` and
returns a bare `string[]` in request order. Unknown entries can map to an empty
string.

## Statistics and TVL

`POST /api/pools/stats` requires `{ poolIds: string[] }` and returns one
`PoolStats` per requested ID:

```typescript
type PoolStats = {
  volume: number;
  tvl: number;
  supplyPerLps: number[];
  lpPrice: number;
  fees: number;
  apr: number;
};
```

Unknown pool IDs produce zero/default stats. Volume and fees use a 24-hour
window. `apr` is fractional.

The deprecated `GET /api/pools/{pool_id}/stats` returns `PoolStats[]`, not one
object.

`POST /api/pools/tvl` accepts `{ poolIds?: string[] | null }` and returns a bare
USD number. Omit `poolIds` or pass null to aggregate all pools.

## Volume and Fees

Duration routes return bare USD numbers:

```text
GET /api/pools/total-swap-volume/{duration_ms}
GET /api/pools/{pool_id}/swap-volume/{duration_ms}
```

`duration_ms` must be between `1` and `32_000_000_000` inclusive.

The deprecated `volume-24hrs` routes use `86_400_000` milliseconds.

Time-series routes return `{ time, value }[]`:

```text
GET /api/pools/{pool_id}/fees/{timeframe}
GET /api/pools/{pool_id}/volume/{timeframe}
```

Supported timeframes are `1D | 1W | 1M | 3M | 6M | 1Y`.

## Events

### Pool events by type

`POST /api/pools/{pool_id}/events/{event_type}` supports:

```text
swap | deposit | withdraw
```

The body is `{ cursor?: number | null, limit?: number | null }`. Defaults are
`cursor = 0` and `limit = 10`. The response is a bare homogeneous event array;
entries do not include an `eventType` discriminator.

### User interaction events

Both routes require `{ walletAddress, cursor?, limit? }`:

```text
POST /api/pools/interaction-events-by-user
POST /api/pools/{pool_id}/interaction-events-by-user
```

Defaults are `cursor = 0` and `limit = 256`. Both responses tag each entry as
`eventType: "deposit" | "withdraw"`. Amounts use `"...n"` strings.

## CoinGecko Tickers

`GET /api/pools/coingecko/tickers` returns configured official pools.

`POST /api/pools/coingecko-ticker-data` requires `{ poolIds: string[] }`.

Both return `CoinGeckoTickerData[]` with intentionally snake_case fields:

```typescript
type CoinGeckoTickerData = {
  ticker_id: string;
  base_currency: string;
  target_currency: string;
  pool_id: string;
  last_price: number;
  base_volume: number;
  target_volume: number;
  liquidity_in_usd: number;
};
```
