# General Aftermath API Endpoints

These current service families are outside the core CCXT/native-perpetuals
references. Paths below are from `service-af-fe` commit `d5cb82c`; preserve
the exact kebab-case spelling.

## Network config and auth

```text
GET  /api/addresses
POST /api/auth/access-token
POST /api/auth/create-account
GET  /api/perpetuals/config
GET  /api/sui/epoch
GET  /api/sui/system-state
```

`GET /api/addresses` returns the complete free-form network addresses config;
the SDK uses it during `Aftermath.create` unless addresses are supplied.

`POST /api/auth/access-token` and `POST /api/auth/create-account` use:

```typescript
type SignedJson = {
  walletAddress: string;
  serializedJson: string;
  signature: string;
};
```

The access-token response is `{ accessToken, header,
expirationTimestamp }`, where the expiration is Unix milliseconds. The
create-account response is a bare boolean. These are not the reusable terms
signature routes; see [authentication.md](authentication.md).

`GET /api/perpetuals/config` returns:

```typescript
type PerpetualsConfig = {
  aflpVaultId: string;
  officialVaultIds: string[];
  defaultCollateralCoinType: string;
};
```

It returns a 500-style API error if the static enricher has not served a
usable config. `GET /api/sui/epoch` returns a bare string; `GET
/api/sui/system-state` returns the camelCase Sui system-state summary with
integer-like fields represented as strings.

## Coins

```text
GET  /api/coins/verified
POST /api/coins/metadata
GET  /api/coins/{coin_type}       (deprecated shape)
```

`POST /api/coins/metadata` accepts `{ coins: string[] }` and returns a bare
array of `{ decimals, description, iconUrl, id, name, symbol, isGenerated?,
metadataType? }`. The service enforces its configured maximum number of coins.
`GET /api/coins/verified` returns a bare `string[]` of configured verified
coin types. The deprecated path parameter is a URL-encoded JSON array, for
example `[%22type-a%22,%22type-b%22]`, and returns the same metadata shape.

## Wallet balances and transactions

```text
POST /api/wallet/all-coin-balances
POST /api/wallet/coin-balances
POST /api/wallet/past-transactions

GET  /api/wallet/{address}/balances                 (deprecated)
POST /api/wallet/{address}/balances                 (deprecated)
POST /api/wallet/{address}/balances/coins           (deprecated)
GET  /api/wallet/{address}/balances/{coin}           (deprecated)
POST /api/wallet/{address}/transactions              (deprecated)
```

Current request/response forms:

```typescript
// POST /api/wallet/all-coin-balances
{ walletAddress: string }
// -> Record<coinType, string>   // values end in "n"

// POST /api/wallet/coin-balances
{ walletAddress: string; coins: string[] }
// -> string[]                   // same order, values end in "n"

// POST /api/wallet/past-transactions
{ walletAddress: string; cursor?: string; limit?: number }
// -> { transactions: object[]; nextCursor?: string; hasNextPage: boolean }
```

The legacy path forms remain in the service for compatibility. Prefer the
current body-based routes and keep the `"...n"` suffix on balances.

## User public-key data

```text
POST /api/user-data/public-key
POST /api/user-data/save-public-key
```

The read body is `{ walletAddress }` and returns the stored public-key bytes
or an undefined/null-like result. The save body is `{ walletAddress, bytes,
signature }` and returns a bare boolean indicating whether a public key was
stored. This service uses the user-data signature protocol, not the unified
terms message.

## zkLogin

```text
POST /api/zklogin/create
```

The current TS-helper proxy accepts:

```typescript
type ZkLoginCreateRequest = {
  jwt: string;
  maxEpoch: number;
  ephemeralPublicKey: string; // base64 Ed25519 public key
  randomness: string;
};
```

It returns `{ walletAddress, partialZkLoginSignature, addressSeed }`. The
private key never leaves the client. Downstream 400, 401, 502, and 504 proof
errors are part of the route contract; a transport failure in the proxy can
be 502.

## Pool and farm summaries

```text
POST /api/pools/summary
POST /api/farms/summary
```

Both accept an optional filter (`poolIds` or `farmIds`) and return a bare array.
Pool entries are `{ pool, stats }`, where `pool` is the full pool object and
`stats` is the current pool statistics object. Farm entries are:

```typescript
type FarmSummary = {
  farmId: string;
  tvl: number;
  rewardsTvl: number;
};
```

The service caches these computed summaries for roughly 30 seconds. The SDK
v3.1.0 maps these routes to `getPoolSummaries` and `getFarmSummaries`, both
with final-position abort signals.

## Stable Kitchen

These are distinct from the legacy `/api/metastable/*` routes:

```text
POST /api/stable-kitchen/vaults
POST /api/stable-kitchen/tvl
POST /api/stable-kitchen/fees/{duration_ms}
POST /api/stable-kitchen/volume/{duration_ms}
GET  /api/stable-kitchen/{vault_id}/coingecko/supply
```

Vault requests accept optional `vaultIds`, plus `sortBy` (`creation-time` or
`market-cap`), `order` (`ascending` or `descending`), `filter`, `cursor`, and
`limit`. Vault responses contain camelCase fields including
`objectType`, `objectId`, `baseCoinType`, `quoteCoinType`, `quoteSupply`,
`baseFunds`, `fees`, `feeBps`, `creationTimestampMs`, `creatorAddress`, and
`rewards`; metadata fields are included by the route. Balance-like values use
`"...n"` strings.

TVL, fees, and volume return bare USD numbers. Duration is milliseconds,
must be positive, and is capped at `32_000_000_000`. The CoinGecko supply
route returns `{ result: string }`.

## DEX Screener compatibility

```text
GET /api/dex-screener/asset?id={coinType}
GET /api/dex-screener/pair?id={pairId}
GET /api/dex-screener/events?fromBlock={n}&toBlock={n}&skip={n}&limit={n}
GET /api/dex-screener/latest-block
GET /api/dex-screener/health
```

`asset` returns `{ asset: { id, name, symbol, decimals, totalSupply?,
circulatingSupply? } }`. `pair` returns a wrapped pair object; `id` may be a
pool ID or the generated multi-asset `pool-coin0-coin1` pair ID.
`events` returns `{ events: [...] }` for inclusive checkpoint bounds and
defaults `skip` to 0 and `limit` to 50. `latest-block` returns
`{ block: { blockNumber, blockTimestamp } }`, with the timestamp in seconds.
`health` reports `isInit`, nullable `whiteListedPools`, and nullable
`blackListedPools`.

## Binance address check

```text
POST /api/binance/check-addresses
```

The body is `{ walletAddress: string[] }` and the response is
`{ list: Array<{ address: string; checked: boolean }> }`. In the current
service implementation the checker returns `checked: false` for each supplied
address; treat it as a placeholder/compatibility route, not as proof of a
successful Binance address validation.

## Source routing

For the complete operation list, use [endpoint-inventory.md](endpoint-inventory.md).
For Birdeye, dynamic gas, router, referrals, rewards, rebates, gas pools, and
metastable routes, use [auxiliary-endpoints.md](auxiliary-endpoints.md).
