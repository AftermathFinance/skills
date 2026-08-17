# SDK Package and Accessor Inventory

The lists below describe the public high-level classes in `v2.3.0`. Methods
that return transactions generally return a Sui `Transaction`; methods that
fetch a service `txKind` object may return `{ tx, ...metadata }`.

## Pools

`sdk.Pools()` exposes:

```text
getPool, getPools, getAllPools, getOwnedLpCoins,
getPublishLpCoinTransaction, getCreatePoolTransaction,
getPoolObjectIdForLpCoinType, getPoolObjectIdsForLpCoinTypes,
isLpCoinType, getTotalVolume24hrs, getTVL, getPoolsStats,
getPoolSummaries, getOwnedDaoFeePoolOwnerCaps, getInteractionEvents
```

`getAllPools(signal?)`, `getPoolsStats(inputs, signal?)`, and
`getPoolSummaries(inputs?, signal?)` support the final abort signal. The
summary route returns `{ pool, stats }` entries and is the typed wrapper for
`POST /api/pools/summary`. A `Pool` object additionally provides deposit,
withdraw, all-coin-withdraw, trade, DAO fee update/recipient, stats,
time-series data, interaction events, and local AMM calculation helpers.

## Farms

`sdk.Farms()` exposes:

```text
getStakingPool, getStakingPools, getAllStakingPools,
getOwnedStakedPositions, getOwnedStakingPoolOwnerCaps,
getOwnedStakingPoolOneTimeAdminCaps, getTVL, getRewardsTVL,
getFarmSummaries, getCreateStakingPoolTransactionV1,
getCreateStakingPoolTransactionV2, getInteractionEvents
```

`getAllStakingPools(signal?)`, `getTVL(inputs?, signal?)`,
`getRewardsTVL(inputs?, signal?)`, and `getFarmSummaries(inputs?, signal?)`
support abort signals. `getFarmSummaries` maps to
`POST /api/farms/summary` and returns `{ farmId, tvl, rewardsTvl }`.
`FarmsStakingPool` and `FarmsStakedPosition` wrappers contain V1/V2 local
state helpers plus stake, deposit-principal, withdraw, lock, unlock, renew,
harvest, reward-emission, min-stake, and admin transaction builders.

## Staking

`sdk.Staking()` exposes:

```text
getActiveValidators, getValidatorApys, getValidatorConfigs,
getStakingPositions, getDelegatedStakes, getValidatorOperationCaps,
getStakeTransaction, getUnstakeTransaction, getStakeStakedSuiTransaction,
getUpdateValidatorFeeTransaction, getCrankAfSuiTransaction, getSuiTvl,
getAfSuiToSuiExchangeRate, getStakedSuiVaultState, getApy,
getHistoricalApy
```

It also exposes `Staking.calcAtomicUnstakeFee`. Validator and staking
transaction routes are documented in `../../api/staking.md`.

## DCA and limit orders

`sdk.Dca()` exposes:

```text
getAllDcaOrders (deprecated), getActiveDcaOrders, getPastDcaOrders,
getCreateDcaOrderTx, closeDcaOrder, closeDcaOrdersMessageToSign,
createUserAccountMessageToSign (deprecated), getUserPublicKey (deprecated),
createUserPublicKey (deprecated)
```

`sdk.LimitOrders()` exposes:

```text
getActiveLimitOrders, getPastLimitOrders, getCreateLimitOrderTx,
cancelLimitOrder, cancelLimitOrdersMessageToSign, getMinOrderSizeUsd
```

Read [backend-alignment.md](backend-alignment.md) and
`../../api/dca-and-limit-orders.md` before calling signed methods. The
current service requires a fixed reusable terms signature and plain
`orderObjectIds`; v2.3.0 types/builders still describe the old
order-specific signed JSON.

## Rewards and referrals

`sdk.Rewards()` exposes:

```text
getPoints, getHistory, getClaimable, getExpectedRewards, getClaimTransaction
```

`getExpectedRewards` calls the current kebab-case `expected-rewards` route.
`getPoints` and `getHistory` require the service's current terms auth when
called against `service-af-fe`; claim and expected-rewards have their own
request shapes.

`sdk.Referrals()` exposes:

```text
getRefCode, getLinkedRefCode, getReferees, isRefCodeTaken,
createReferralLink, setReferrer,
createReferralLinkMessageToSign, setReferrerMessageToSign
```

The last two message builders are stale for the current service. Use the
fixed terms bytes and send `refCode` as a plain field; v2.3.0's
`setReferrer` body type does not declare that required field. `createReferralLink`
may also accept a plain custom `refCode` at a raw boundary, although the
service supplies a default when omitted. `sdk.ReferralVault()` is deprecated
and only exposes `getReferrer`; use `Referrals` for the current HTTP referral
program.

## Gas and dynamic gas

`sdk.GasPools()` exposes:

```text
getPool, getCreateTx, getDepositTx, getWithdrawTx,
getSponsoredTransaction, getGrantTx, getRevokeTx, getShareTx
```

`getSponsoredTransaction` returns `{ transaction, sponsorSignature, digest }`
and its current service body also accepts optional MIST `gasBudget`. The SDK
v2.3.0 sponsor type still omits that field and its comments describe the old
`SPONSOR_GAS` JSON/date message; use the compatibility reference.

`sdk.DynamicGas()` exposes `getUseDynamicGasForTx`, for
`POST /api/dynamic-gas` non-SUI gas sponsorship.

## Router

`sdk.Router()` exposes:

```text
getVolume24hrs, getSupportedCoins, searchSupportedCoins,
getCompleteTradeRouteGivenAmountIn, getCompleteTradeRouteGivenAmountOut,
getTransactionForCompleteTradeRoute, addTransactionForCompleteTradeRoute,
getInteractionEvents
```

The current `service-af-fe` source exposes only
`POST /api/router/trade-route` and `POST /api/router/transactions/add-trade`.
Use those two methods/paths only when targeting that service; the other SDK
helpers require an API deployment that still serves the legacy router routes.

## Coin, prices, wallet, and Sui

`sdk.Coin(coinType?)` exposes:

```text
getCoinsToDecimals, getCoinMetadata, getCoinMetadatas, getPrice,
getVerifiedCoins, setCoinMetadata, setPriceInfo
```

`getCoinsToDecimals`, `getCoinMetadata`, and `getCoinMetadatas` support a final
abort signal where declared. Static helpers cover coin type parsing,
normalization, filtering, and decimal/price balance calculations.

`sdk.Prices()` exposes `getCoinPriceInfo`, `getCoinsToPriceInfo`,
`getCoinPrice`, and `getCoinsToPrice`; each current read accepts an optional
final `AbortSignal`.

`sdk.Wallet(address)` exposes `getBalance`, `getBalances`, `getAllBalances`,
and `getPastTransactions`. The low-level `AftermathApi.Wallet()` exposes
`fetchCoinBalance`, `fetchAllCoinBalances`, and `fetchPastTransactions`.

`sdk.Sui()` exposes `getSystemState`. `AftermathApi.Sui()` is the lower-level
provider and also exposes `fetchSystemState`; the latter is one of the legacy
JSON-RPC helpers. Current API utility routes include `/api/sui/epoch` and
`/api/sui/system-state`, but the high-level SDK Sui provider reads the fullnode
surface rather than those service routes.

## Auth and user data

`sdk.Auth()` exposes `init` and `adminCreateAuthAccount`. `init` signs the
auth service's serialized `GetAccessToken` payload and refreshes the bearer
token until the returned stop function is called. This is distinct from the
reusable terms signature used by service endpoints.

`sdk.UserData()` exposes:

```text
getUserPublicKey, createUserPublicKey,
createUserAccountMessageToSign,
createSignTermsAndConditionsMessageToSign
```

The service's `save-public-key` endpoint has its own `bytes`/`signature`
protocol. The `createSignTermsAndConditionsMessageToSign` helper currently
returns an action object and is not the service-af-fe reusable terms payload.

## Faucet, multisig, NFT AMM, and SuiFrens

```text
Faucet:   getSupportedCoins, getRequestCoinTransaction, getMintSuiFrenTransaction
Multisig: getMultisigForUser
NftAmm:   getMarket, getMarkets, getAllMarkets
```

An `NftAmmMarket` provides `getNfts`, buy/sell/deposit/withdraw transaction
builders, and local amount/spot-price calculations.

`sdk.SuiFrens()` exposes `getSuiFren`, `getSuiFrens`, `getOwnedSuiFrens`,
`getOwnedStakedSuiFrens`, `getAllStakedSuiFrens`, `getStakedSuiFrens`,
`getCapyLabsApp`, `getOwnedAccessories`, event readers (`getHarvestFeesEvents`,
`getMixEvents`, `getStakeEvents`, `getUnstakeEvents`),
`getMixTransaction`, `getHarvestFeesTransaction`, and `getStats`. Its
`SuiFren`/`StakedSuiFren` wrappers provide accessory, stake/unstake, mix,
harvest, and accessory transaction helpers.

## Low-level `AftermathApi` helpers

`AftermathApi` creates `DynamicFields`, `Events`, `Inspections`, `Objects`,
`Transactions`, `Wallet`, `Nfts`, `Coin`, `Sui`, `Pools`, `Faucet`,
`SuiFrens`, `Staking`, `NftAmm`, `ReferralVault`, `Perpetuals`, `Farms`,
`Dca`, `Multisig`, `LimitOrders`, and `Router` providers. It also exposes
`translateMoveErrorMessage` and `requireJsonRpcClient`.

The general helpers include object existence/ownership/typed-object reads,
BCS reads, dynamic-field pagination, event pagination/casting, transaction
parsing/building, inspection bytes, wallet reads, and NFT/Kiosk reads. Read
the corresponding `src/general/apiHelpers/*` file when working below the
high-level provider boundary; do not infer gRPC object shapes from old
JSON-RPC `content.fields` examples.
