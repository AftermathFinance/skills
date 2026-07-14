# Price Endpoint Reference

> Coin, LP token, and external-ID price lookups.

## Current Routes

```text
POST /api/prices
POST /api/price-info
```

## Deprecated Routes

```text
GET /api/price-info/{coin_types}
GET /api/prices/cetus/{coin_type}/{coin_decimals}
```

## Price Map

`POST /api/prices` requires:

```json
{ "coinTypes": ["0x2::sui::SUI"] }
```

It returns a bare price map:

```typescript
type PriceMap = Record<string, number>;
```

Inputs can be Sui coin types, LP coin types, or supported external CoinGecko
IDs. The API canonicalizes Sui and LP type keys to full addresses; external IDs
remain unchanged. Canonicalize type strings before looking up response values.

## Price Information

`POST /api/price-info` requires:

```json
{ "coins": ["0x2::sui::SUI"] }
```

It returns:

```typescript
type PriceInfoMap = Record<string, {
  price: number;
  priceChange24HoursPercentage: number;
}>;
```

Sui and LP keys use the same canonicalization rule as `/api/prices`.

The API returns `0` for the 24-hour percentage on Sui and LP
prices that do not have external change data.

## Deprecated GET Forms

`GET /api/price-info/{coin_types}` returns the same shape as
`POST /api/price-info`. The path segment must be a URL-encoded JSON string
array. Prefer the POST route.

`GET /api/prices/cetus/{coin_type}/{coin_decimals}` returns:

```typescript
type LegacyCetusPriceResponse = { data: number[] };
```

The response contains one value. `coin_decimals` must be between `0` and `255`.
Prefer `POST /api/prices`.

## Related Price APIs

- Native perpetual market prices: `native.md`.
- Birdeye historical and market data: `auxiliary-endpoints.md`.
