# Staking Endpoint Reference

> Staking protocol metrics, wallet positions, validator data, and validator capabilities.

## Routes

```text
GET  /api/staking/active-validators
GET  /api/staking/afsui-exchange-rate
GET  /api/staking/apy
POST /api/staking/delegated-stakes
POST /api/staking/historical-apy
GET  /api/staking/staked-sui-vault-state
POST /api/staking/staking-positions
GET  /api/staking/staking-rewards
GET  /api/staking/sui-tvl
GET  /api/staking/unique-stakers
GET  /api/staking/validator-apys
GET  /api/staking/validator-configs
POST /api/staking/validator-operation-caps
```

## Protocol Metrics

### afSUI exchange rate

`GET /api/staking/afsui-exchange-rate` returns a bare JSON number.

### APY

`GET /api/staking/apy` returns a bare fractional APY, or `0` when no APY value
is available.

`POST /api/staking/historical-apy` requires:

```typescript
type HistoricalApyRequest = { timeframe: "1W" | "1M" | "3M" | "6M" | "1Y" | "ALL" };
```

It returns `{ timestamp, apy }[]`. The response filters historical points outside
the range `0.01 < apy < 0.05`.

### TVL and staker count

- `GET /api/staking/sui-tvl` returns a bare `"...n"` string.
- `GET /api/staking/unique-stakers` returns a bare JSON integer.

### Staked SUI vault state

`GET /api/staking/staked-sui-vault-state` returns:

```typescript
type StakedSuiVaultState = {
  objectId: string;
  objectType: string;
  atomicUnstakeSuiReservesTargetValue: string;
  atomicUnstakeSuiReserves: string;
  minAtomicUnstakeFee: string;
  maxAtomicUnstakeFee: string;
  totalSuiAmount: string;
  totalRewardsAmount: string;
  activeEpoch: string;
};
```

All seven numeric state fields are `"...n"` strings.

### Staking rewards summary

`GET /api/staking/staking-rewards` returns:

```typescript
type StakingRewards = {
  name: string;
  totalBalanceUsd: number;
  supportedAssets: Array<{
    contractAddress: string;
    symbol: string;
    slug: string;
    baseSlug: string;
    supply: number;
    apr: number;
    fee: number;
    users: number;
    unstakingTime: number;
    exchangeRatio: number;
  }>;
};
```

`apr` and `fee` are percentages in this response. `unstakingTime` is seconds.

## Wallet Positions

### Delegated stakes

`POST /api/staking/delegated-stakes` requires:

```json
{ "walletAddress": "0x..." }
```

It returns a bare array sorted by `stakeRequestEpoch` descending:

```typescript
type DelegatedStake = {
  stakedSuiId: string;
  stakeRequestEpoch: string;
  stakeActiveEpoch: string;
  principal: string;
  status: "Active" | "Pending" | "Unstaked";
  estimatedReward: string | null;
  stakingPool: string;
  validatorAddress: string;
};
```

Epoch, principal, and reward values are `"...n"` strings.

### Staking positions

`POST /api/staking/staking-positions` accepts:

```typescript
type StakingPositionsRequest = {
  walletAddress: string;
  positionType?: "stake" | "unstake" | "all" | null;
  cursor?: number | null;
  limit?: number | null;
};
```

Defaults are `positionType = "all"`, `cursor = 0`, and `limit = 256`.

With `positionType: "all"`, each result includes a `positionType` discriminator.
The API returns raw stake or unstake objects without that discriminator when you
request only one type. Amount and epoch fields use `"...n"` strings.

## Validators

### Active validators

`GET /api/staking/active-validators` returns a bare `SuiValidatorSummary[]`.
Fields use camelCase. Public-key byte fields are base64 strings. Next-epoch key,
address, and activation fields can be null.

### Validator APYs

`GET /api/staking/validator-apys` returns:

```typescript
type ValidatorApys = {
  apys: Array<{ address: string; apy: number }>;
  epoch: string;
};
```

### Validator configs

`GET /api/staking/validator-configs` returns a bare array:

```typescript
type ValidatorConfigs = Array<{
  objectType: string;
  objectId: string;
  suiAddress: string;
  operationCapId: string;
  fee: number;
}>;
```

### Validator operation capabilities

`POST /api/staking/validator-operation-caps` requires `{ walletAddress }` and
returns:

```typescript
type ValidatorOperationCaps = Array<{
  objectType: string;
  objectId: string;
  authorizerValidatorAddress: string;
}>;
```

## Wire Format

Use the documented `"...n"` strings for HTTP requests and responses.
