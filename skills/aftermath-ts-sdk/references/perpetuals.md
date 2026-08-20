# Perpetuals SDK Reference

Use `const perps = sdk.Perpetuals()` after `Aftermath.create`. The SDK uses the
`perpetuals` API prefix and the current service's kebab-case route names for
the core market/account/vault surface. Raw request/response details live in
`../../api/native.md`.

## `Perpetuals` provider

### Discovery and data

```text
getAllMarkets, getMarket, getMarkets,
getVaultsConfig,
getAllVaults, getVault, getVaults,
getAccount, getAccounts, getAccountObjects,
getOwnedAccountCaps, getOwnedVaultCaps, getOwnedVaultAssistantCaps,
getOwnedVaultWithdrawRequests, getOwnedVaultLpCoins, getAdminAccountCaps,
getMarketCandleHistory, getMarketFundingHistory, getMarkets24hrStats,
getPrices, getLpCoinPrices
```

Notable response changes in the v3 service contract:

- `getMarkets` entries carry nullable static metadata. `displayName` can be
  absent; do not treat it as a required string.
- Market and vault identifiers are object IDs. Perpetual account identifiers
  are numeric BigInts and serialize on the wire as `"123n"`.
- Candle history uses `resolution` labels (`1m`, `5m`, `15m`, `30m`, `1h`,
  `4h`, `12h`, `1d`, `3d`, `1w`, `1mo`) and millisecond timestamps.
- TWAP data uses `details.size`, `processedAmount`, and `scheduledAmount` as
  BigInt-style values; `lastExecutionTimestampMs` is an ordinary JSON number.

### Dynamic vault protocol configuration

`getVaultsConfig(abortSignal?)` maps to:

`POST /api/perpetuals/vaults/config`

`{}`

The endpoint requires the empty JSON object and returns the live
`PerpetualsVaultsConfig`. Integer-like response fields decode to TypeScript
`bigint` values, including `maxLockPeriodMs`, `maxMarketsInVault`, and
`maxPendingOrdersPerPosition`; decimal limits remain numbers. The configuration
is deployment-driven, so fetch it instead of hardcoding vault lock, deposit,
market-count, or pending-order limits.

The removed `PerpetualsVault.constants` table is not a source of current
limits. Use `perps.getVaultsConfig(signal)` before applying client-side
validation.

### Transaction builders

```text
getTransferCapTx, getCreateAccountTx, getGrantAgentWalletTx,
getShareAccountTx, getCreateVaultCapTx, getCreateVaultTx
```

Agent-wallet transactions are account-admin operations. The agent can trade
and manage supported orders but cannot withdraw collateral or grant/revoke
other agent wallets. Use the transaction return value as a normal Sui
`Transaction` and sign/execute it with the appropriate wallet.

### Rebates and builder codes

```text
getCurrentRebateRewards, getCsvRebates, getReferralCsvRebates,
getCreateBuilderCodeIntegratorConfigTx,
getRemoveBuilderCodeIntegratorConfigTx,
getBuilderCodeIntegratorConfig
```

The current service also has one-time global registration:
`POST /api/perpetuals/builder-codes/transactions/create-integrator-registration`
and `POST /api/perpetuals/builder-codes/integrator-registration`. The v3.0.0
SDK does not expose a matching high-level create-registration method; use the
raw API or `AftermathApi` path when needed.

Order-level builder data is `{ integratorId, integratorFee }`. The v3 service
does not use the removed address-based integrator vault model.

The source still contains the following methods/types, but the corresponding
service routes are removed and must not be used against `service-af-fe`:

```text
getCreateBuilderCodeIntegratorVaultTx
getClaimBuilderCodeIntegratorVaultFeesTx
getBuilderCodeIntegratorVaults
```

### WebSockets

```text
openUpdatesWebsocketStream
openMarketCandlesWebsocketStream
```

Both implementations connect to `/api/perpetuals/ws/updates`. The dedicated
`ws/market-candles/{market_id}/{interval_ms}` route no longer exists. The
controller supports these subscription variants:

```text
market, user, oracle, orderbook, marketOrders, userOrders,
userCollateralChanges, topOfOrderbook, marketCandles
```

`subscribeMarketCandles({ marketId, interval })` uses the same general socket.
For `subscribeUser`, the optional `withStopOrders` object contains
`walletAddress`, `bytes`, and `signature`; against the current service, the
base64-decoded bytes must be the reusable terms message. The proxy verifies
that signature before forwarding only the wallet address to the downstream
perpetuals service.

## `PerpetualsAccount`

An account wrapper is returned by `getAccount`. Its public methods are:

### Collateral and orders

```text
getDepositCollateralTx, getWithdrawCollateralTx,
getAllocateCollateralTx, getDeallocateCollateralTx,
getTransferCollateralTx,
getPlaceMarketOrderTx, getPlaceLimitOrderTx, getPlaceScaleOrderTx,
getCancelAndPlaceOrdersTx, getCancelOrdersTx, getCancelStopOrdersTx,
getPlaceStopOrdersTx, getPlaceSlTpOrdersTx, getEditStopOrdersTx,
getCreateTwapOrdersTx, getEditTwapOrdersTx, getCancelTwapOrdersTx,
getSetLeverageTx,
getGrantAgentWalletTx, getRevokeAgentWalletTx
```

Account wrappers created for vault accounts use the corresponding `/vault/`
routes for supported operations. Order inputs can carry `clientOrderId` or
`clientOrderIds`; cancel-and-place supports `clientOrderIdsToCancel` and
`shouldAbortOnMissingId`.

### Previews and data

```text
getPlaceMarketOrderPreview, getPlaceLimitOrderPreview,
getPlaceScaleOrderPreview, getCancelOrdersPreview,
getSetLeveragePreview, getEditCollateralPreview,
getStopOrderDatas, getTwapOrderDatas,
getCollateralHistory, getOrderHistory, getMarginHistory
```

Preview results can be `{ error }` data even with HTTP 200. Treat them as
success/error unions. `getCollateralHistory` and `getOrderHistory` accept
optional `authentication` inputs in the current service request schema when
the route requires user authorization; the terms signature is optional where
the service declares it optional, but if supplied it must use the fixed terms
message.

`getStopOrderDatas` and `getTwapOrderDatas` construct the wallet address and
account/vault selector from the wrapper, then send `bytes` and `signature`.
The existing `getStopOrdersMessageToSign` method is stale: it returns an
action/account/market JSON object. Do not sign that object for the current
service; sign the fixed terms message and pass the target IDs plainly.

### Local account helpers

```text
positionForMarketId, nonSlTpStopOrderDatas, slTpStopOrderDatas,
nonSlTpStopOrderDatasForPosition, slTpStopOrderDatasForPosition,
slTpStopOrderDatasForLimitOrder, orderDatas, collateral, isVault,
ownerAddress, accountObjectId, accountId, accountCapId
```

`accountId()` is a numeric BigInt-like value; `accountObjectId()` and
`accountCapId()` are object IDs. Keep those types distinct.

## `PerpetualsMarket`

```text
get24hrStats, getOrderbook, getMaxOrderSize,
getPlaceMarketOrderPreview, getPlaceLimitOrderPreview,
getPlaceScaleOrderPreview, getOrderHistory, getPrices,
lotSize, tickSize, maxLeverage, initialMarginRatio,
maintenanceMarginRatio
```

The market object also contains local helpers for estimated funding, time
until the next funding event, rounding valid sizes/prices, and constructing an
empty position. `getMaxOrderSize` uses the account namespace and returns a
BigInt-sized `maxOrderSize`.

## `PerpetualsVault`

### Transactions

```text
getProcessForceWithdrawRequestTx,
getPauseVaultForForceWithdrawRequestTx,
getUpdateWithdrawRequestSlippageTx,
getOwnerUpdateForceWithdrawDelayTx, getOwnerUpdateLockPeriodTx,
getOwnerUpdatePerformanceFeeTx, getOwnerProcessWithdrawRequestsTx,
getOwnerWithdrawPerformanceFeesTx, getOwnerWithdrawCollateralTx,
getOwnerWithdrawLockedLiquidityTx,
getCreateWithdrawRequestTx, getCancelWithdrawRequestTx, getDepositTx
```

### Queries and previews

```text
getAllWithdrawRequests,
getPreviewOwnerProcessWithdrawRequests,
getPreviewOwnerWithdrawPerformanceFees,
getPreviewOwnerWithdrawCollateral,
getPreviewOwnerWithdrawLockedLiquidity,
getPreviewCreateWithdrawRequest, getPreviewDeposit,
getPreviewProcessForceWithdrawRequest,
getPreviewPauseVaultForForceWithdrawRequest,
getLpCoinPrice, partialVaultCap, getAccountObject, getAccount, isPaused
```

Vault accounts share the account order/stop/TWAP methods and route families.
Vault discovery also has current service reads for owned assistant caps,
predeposit totals, and `GET /api/perpetuals/vaults/{vault_id}/tvl`; the SDK
does not expose a dedicated `getPerpetualsConfig` accessor for the separate
network config route.

## Current wire and migration rules

- Use `integratorId`/`integratorFee`, not `integratorAddress`/`takerFee`.
- Use `stopLossPrice`/`takeProfitPrice`; optional `triggerPriceType` is `0`
  index, `1` orderbook mid, or `2` mark price.
- Market params use numeric price-feed IDs. Removed response fields include
  per-position maker/taker fees and several pre-v3 vault/market fee fields.
- Candle updates are a `marketCandles` subscription. Do not revive the removed
  dedicated candle socket based on stale SDK comments.
- Reconnect by fetching a fresh REST snapshot before applying WebSocket
  deltas. See `../../api/monitoring-patterns.md` for operational patterns.
