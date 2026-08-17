# Current API Operation Inventory

Generated from the `utoipa::path` declarations in `service-af-fe` `a0ab6c1`.

The source contains **257 OpenAPI operations**. `/api/metastable/tvl`, `/api/pools`, and `/api/wallet/{address}/balances` each have separate GET and POST operations, so there are **254 distinct URL paths**. Keep this file as the audit index; use the focused references for schemas and behavior.

The extractor intentionally ignores source lines beginning with `//` so commented-out historical handlers are not treated as live API operations.

## addresses

- `GET /api/addresses`

## auth

- `POST /api/auth/access-token`
- `POST /api/auth/create-account`

## binance

- `POST /api/binance/check-addresses`

## birdeye

- `POST /api/birdeye/historical`
- `POST /api/birdeye/market`

## ccxt

- `POST /api/ccxt/accounts`
- `POST /api/ccxt/balance`
- `POST /api/ccxt/build/allocate`
- `POST /api/ccxt/build/cancelOrders`
- `POST /api/ccxt/build/createAccount`
- `POST /api/ccxt/build/createOrders`
- `POST /api/ccxt/build/deallocate`
- `POST /api/ccxt/build/deposit`
- `POST /api/ccxt/build/setLeverage`
- `POST /api/ccxt/build/withdraw`
- `GET /api/ccxt/currencies`
- `GET /api/ccxt/markets`
- `POST /api/ccxt/myPendingOrders`
- `POST /api/ccxt/OHLCV`
- `POST /api/ccxt/orderbook`
- `POST /api/ccxt/positions`
- `GET /api/ccxt/stream/orderbook`
- `GET /api/ccxt/stream/orders`
- `GET /api/ccxt/stream/positions`
- `GET /api/ccxt/stream/trades`
- `POST /api/ccxt/submit/allocate`
- `POST /api/ccxt/submit/cancelOrders`
- `POST /api/ccxt/submit/createAccount`
- `POST /api/ccxt/submit/createOrders`
- `POST /api/ccxt/submit/deallocate`
- `POST /api/ccxt/submit/deposit`
- `POST /api/ccxt/submit/setLeverage`
- `POST /api/ccxt/submit/withdraw`
- `POST /api/ccxt/ticker`
- `POST /api/ccxt/trades`

## coins

- `GET /api/coins/{coin_type}`
- `POST /api/coins/metadata`
- `GET /api/coins/verified`

## dca

- `POST /api/dca/active`
- `POST /api/dca/cancel`
- `POST /api/dca/past`
- `POST /api/dca/transactions/create-order`
- `POST /api/dca/user/add`
- `POST /api/dca/user/get`

## dex-screener

- `GET /api/dex-screener/asset`
- `GET /api/dex-screener/events`
- `GET /api/dex-screener/health`
- `GET /api/dex-screener/latest-block`
- `GET /api/dex-screener/pair`

## dynamic-gas

- `POST /api/dynamic-gas`

## farms

- `POST /api/farms/summary`

## gas-pool

- `POST /api/gas-pool/pool`
- `POST /api/gas-pool/transactions/create`
- `POST /api/gas-pool/transactions/deposit`
- `POST /api/gas-pool/transactions/grant`
- `POST /api/gas-pool/transactions/revoke`
- `POST /api/gas-pool/transactions/share`
- `POST /api/gas-pool/transactions/sponsor`
- `POST /api/gas-pool/transactions/withdraw`

## limit-orders

- `POST /api/limit-orders/active`
- `POST /api/limit-orders/cancel`
- `POST /api/limit-orders/min-order-size-usd`
- `POST /api/limit-orders/past`
- `POST /api/limit-orders/transactions/create-order`

## metastable

- `GET /api/metastable/{vault_id}/24hr-volume`
- `GET /api/metastable/{vault_id}/coingecko/supply`
- `GET /api/metastable/{vault_id}/tvl`
- `GET /api/metastable/24hr-volume`
- `POST /api/metastable/fees/{duration_ms}`
- `GET /api/metastable/tvl`
- `POST /api/metastable/tvl`
- `POST /api/metastable/vaults`
- `POST /api/metastable/volume/{duration_ms}`

## perpetuals

- `POST /api/perpetuals/account/collateral-history`
- `POST /api/perpetuals/account/margin-history`
- `POST /api/perpetuals/account/max-order-size`
- `POST /api/perpetuals/account/order-history`
- `POST /api/perpetuals/account/order-history-detailed`
- `POST /api/perpetuals/account/order-history-detailed-csv`
- `POST /api/perpetuals/account/previews/cancel-orders`
- `POST /api/perpetuals/account/previews/edit-collateral`
- `POST /api/perpetuals/account/previews/place-limit-order`
- `POST /api/perpetuals/account/previews/place-market-order`
- `POST /api/perpetuals/account/previews/place-scale-order`
- `POST /api/perpetuals/account/previews/set-leverage`
- `POST /api/perpetuals/account/stop-order-datas`
- `POST /api/perpetuals/account/transactions/allocate-collateral`
- `POST /api/perpetuals/account/transactions/cancel-and-place-orders`
- `POST /api/perpetuals/account/transactions/cancel-orders`
- `POST /api/perpetuals/account/transactions/cancel-stop-orders`
- `POST /api/perpetuals/account/transactions/cancel-twap-orders`
- `POST /api/perpetuals/account/transactions/create-twap-orders`
- `POST /api/perpetuals/account/transactions/deallocate-collateral`
- `POST /api/perpetuals/account/transactions/deposit-collateral`
- `POST /api/perpetuals/account/transactions/edit-stop-orders`
- `POST /api/perpetuals/account/transactions/edit-twap-orders`
- `POST /api/perpetuals/account/transactions/grant-agent-wallet`
- `POST /api/perpetuals/account/transactions/place-limit-order`
- `POST /api/perpetuals/account/transactions/place-market-order`
- `POST /api/perpetuals/account/transactions/place-scale-order`
- `POST /api/perpetuals/account/transactions/place-sl-tp-orders`
- `POST /api/perpetuals/account/transactions/place-stop-orders`
- `POST /api/perpetuals/account/transactions/revoke-agent-wallet`
- `POST /api/perpetuals/account/transactions/set-leverage`
- `POST /api/perpetuals/account/transactions/share`
- `POST /api/perpetuals/account/transactions/transfer-collateral`
- `POST /api/perpetuals/account/transactions/withdraw-collateral`
- `POST /api/perpetuals/account/twap-order-datas`
- `POST /api/perpetuals/accounts`
- `POST /api/perpetuals/accounts/owned`
- `POST /api/perpetuals/accounts/positions`
- `POST /api/perpetuals/all-markets`
- `POST /api/perpetuals/builder-codes/integrator-config`
- `POST /api/perpetuals/builder-codes/integrator-registration`
- `POST /api/perpetuals/builder-codes/transactions/create-integrator-config`
- `POST /api/perpetuals/builder-codes/transactions/create-integrator-registration`
- `POST /api/perpetuals/builder-codes/transactions/remove-integrator-config`
- `GET /api/perpetuals/config`
- `POST /api/perpetuals/market/candle-history`
- `POST /api/perpetuals/market/funding-history`
- `POST /api/perpetuals/market/order-history`
- `POST /api/perpetuals/markets`
- `POST /api/perpetuals/markets/24hr-stats`
- `POST /api/perpetuals/markets/orderbooks`
- `POST /api/perpetuals/markets/prices`
- `POST /api/perpetuals/rebates/create-csv-rebates`
- `POST /api/perpetuals/rebates/create-referral-csv-rebates`
- `POST /api/perpetuals/rebates/rewards`
- `POST /api/perpetuals/transactions/create-account`
- `POST /api/perpetuals/transactions/transfer-cap`
- `POST /api/perpetuals/vault/previews/cancel-orders`
- `POST /api/perpetuals/vault/previews/create-withdraw-request`
- `POST /api/perpetuals/vault/previews/deposit`
- `POST /api/perpetuals/vault/previews/edit-collateral`
- `POST /api/perpetuals/vault/previews/owner/process-withdraw-requests`
- `POST /api/perpetuals/vault/previews/owner/withdraw-collateral`
- `POST /api/perpetuals/vault/previews/owner/withdraw-locked-liquidity`
- `POST /api/perpetuals/vault/previews/owner/withdraw-performance-fees`
- `POST /api/perpetuals/vault/previews/pause-vault-for-force-withdraw-request`
- `POST /api/perpetuals/vault/previews/place-limit-order`
- `POST /api/perpetuals/vault/previews/place-market-order`
- `POST /api/perpetuals/vault/previews/place-scale-order`
- `POST /api/perpetuals/vault/previews/process-force-withdraw-request`
- `POST /api/perpetuals/vault/previews/set-leverage`
- `POST /api/perpetuals/vault/stop-order-datas`
- `POST /api/perpetuals/vault/transactions/allocate-collateral`
- `POST /api/perpetuals/vault/transactions/cancel-and-place-orders`
- `POST /api/perpetuals/vault/transactions/cancel-orders`
- `POST /api/perpetuals/vault/transactions/cancel-stop-orders`
- `POST /api/perpetuals/vault/transactions/cancel-twap-orders`
- `POST /api/perpetuals/vault/transactions/cancel-withdraw-request`
- `POST /api/perpetuals/vault/transactions/create-twap-orders`
- `POST /api/perpetuals/vault/transactions/create-vault`
- `POST /api/perpetuals/vault/transactions/create-vault-cap`
- `POST /api/perpetuals/vault/transactions/create-withdraw-request`
- `POST /api/perpetuals/vault/transactions/deallocate-collateral`
- `POST /api/perpetuals/vault/transactions/deposit`
- `POST /api/perpetuals/vault/transactions/edit-stop-orders`
- `POST /api/perpetuals/vault/transactions/edit-twap-orders`
- `POST /api/perpetuals/vault/transactions/owner/process-withdraw-requests`
- `POST /api/perpetuals/vault/transactions/owner/update-force-withdraw-delay`
- `POST /api/perpetuals/vault/transactions/owner/update-lock-period`
- `POST /api/perpetuals/vault/transactions/owner/update-performance-fee`
- `POST /api/perpetuals/vault/transactions/owner/withdraw-collateral`
- `POST /api/perpetuals/vault/transactions/owner/withdraw-locked-liquidity`
- `POST /api/perpetuals/vault/transactions/owner/withdraw-performance-fees`
- `POST /api/perpetuals/vault/transactions/pause-vault-for-force-withdraw-request`
- `POST /api/perpetuals/vault/transactions/place-limit-order`
- `POST /api/perpetuals/vault/transactions/place-market-order`
- `POST /api/perpetuals/vault/transactions/place-scale-order`
- `POST /api/perpetuals/vault/transactions/place-sl-tp-orders`
- `POST /api/perpetuals/vault/transactions/place-stop-orders`
- `POST /api/perpetuals/vault/transactions/process-force-withdraw-request`
- `POST /api/perpetuals/vault/transactions/set-leverage`
- `POST /api/perpetuals/vault/transactions/update-withdraw-request-slippage`
- `POST /api/perpetuals/vault/twap-order-datas`
- `POST /api/perpetuals/vaults`
- `GET /api/perpetuals/vaults/{vault_id}/tvl`
- `POST /api/perpetuals/vaults/lp-coin-prices`
- `POST /api/perpetuals/vaults/owned-lp-coins`
- `POST /api/perpetuals/vaults/owned-vault-assistant-caps`
- `POST /api/perpetuals/vaults/owned-vault-caps`
- `POST /api/perpetuals/vaults/owned-withdraw-requests`
- `POST /api/perpetuals/vaults/predeposits/user-total-deposits`
- `POST /api/perpetuals/vaults/predeposits/vault-totals`
- `POST /api/perpetuals/vaults/withdraw-requests`
- `GET /api/perpetuals/ws/updates`

## pools

- `GET /api/pools`
- `POST /api/pools`
- `GET /api/pools/{pool_id}`
- `POST /api/pools/{pool_id}/events/{event_type}`
- `GET /api/pools/{pool_id}/fees/{timeframe}`
- `POST /api/pools/{pool_id}/interaction-events-by-user`
- `GET /api/pools/{pool_id}/stats`
- `GET /api/pools/{pool_id}/swap-volume/{duration_ms}`
- `GET /api/pools/{pool_id}/volume-24hrs`
- `GET /api/pools/{pool_id}/volume/{timeframe}`
- `POST /api/pools/coingecko-ticker-data`
- `GET /api/pools/coingecko/tickers`
- `POST /api/pools/interaction-events-by-user`
- `POST /api/pools/objects`
- `POST /api/pools/owned-lp-coins`
- `POST /api/pools/pool-object-ids`
- `POST /api/pools/stats`
- `POST /api/pools/summary`
- `GET /api/pools/total-swap-volume/{duration_ms}`
- `POST /api/pools/tvl`
- `GET /api/pools/volume-24hrs`

## price-info

- `POST /api/price-info`
- `GET /api/price-info/{coin_types}`

## prices

- `POST /api/prices`
- `GET /api/prices/cetus/{coin_type}/{coin_decimals}`

## referrals

- `POST /api/referrals/availability`
- `POST /api/referrals/create`
- `POST /api/referrals/link`
- `POST /api/referrals/linked-ref-code`
- `POST /api/referrals/query`
- `POST /api/referrals/ref-code`

## rewards

- `POST /api/rewards/claimable`
- `POST /api/rewards/expected-rewards`
- `POST /api/rewards/history`
- `POST /api/rewards/points`
- `POST /api/rewards/transactions/claim`

## router

- `POST /api/router/trade-route`
- `POST /api/router/transactions/add-trade`

## stable-kitchen

- `GET /api/stable-kitchen/{vault_id}/coingecko/supply`
- `POST /api/stable-kitchen/fees/{duration_ms}`
- `POST /api/stable-kitchen/tvl`
- `POST /api/stable-kitchen/vaults`
- `POST /api/stable-kitchen/volume/{duration_ms}`

## staking

- `GET /api/staking/active-validators`
- `GET /api/staking/afsui-exchange-rate`
- `GET /api/staking/apy`
- `POST /api/staking/delegated-stakes`
- `POST /api/staking/historical-apy`
- `GET /api/staking/staked-sui-vault-state`
- `POST /api/staking/staking-positions`
- `GET /api/staking/staking-rewards`
- `GET /api/staking/sui-tvl`
- `GET /api/staking/unique-stakers`
- `GET /api/staking/validator-apys`
- `GET /api/staking/validator-configs`
- `POST /api/staking/validator-operation-caps`

## sui

- `GET /api/sui/epoch`
- `GET /api/sui/system-state`

## user-data

- `POST /api/user-data/public-key`
- `POST /api/user-data/save-public-key`

## wallet

- `GET /api/wallet/{address}/balances`
- `POST /api/wallet/{address}/balances`
- `GET /api/wallet/{address}/balances/{coin}`
- `POST /api/wallet/{address}/balances/coins`
- `POST /api/wallet/{address}/transactions`
- `POST /api/wallet/all-coin-balances`
- `POST /api/wallet/coin-balances`
- `POST /api/wallet/past-transactions`

## zklogin

- `POST /api/zklogin/create`

## Focused references

- Perpetuals: [native.md](native.md)
- CCXT: [ccxt.md](ccxt.md)
- DCA and limit orders: [dca-and-limit-orders.md](dca-and-limit-orders.md)
- Pools: [pools.md](pools.md)
- Prices: [prices.md](prices.md)
- Staking: [staking.md](staking.md)
- Auxiliary families: [auxiliary-endpoints.md](auxiliary-endpoints.md)
- General utility families: [general-endpoints.md](general-endpoints.md)
- Signed request rules: [authentication.md](authentication.md)
