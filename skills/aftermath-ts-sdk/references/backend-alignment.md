# SDK and `service-af-fe` Alignment

Compare these two local snapshots before assuming a typed SDK method is a
working service call:

- SDK: `aftermath-ts-sdk` `ae289995` / `v2.3.0`.
- API service: `service-af-fe` `a0ab6c1`.
- Service surface: 257 OpenAPI operations; `/api/pools` intentionally has both
  GET (deprecated) and POST (current).

## Current service changes that affect SDK callers

### Reusable terms authentication

The service verifies that the base64-decoded `bytes` are exactly:

```text
Aftermath Terms and Conditions
```

The wallet signs the decoded UTF-8 bytes; send the base64 representation in
`bytes` and the wallet signature in `signature`. Sign once per wallet
connection and reuse the pair. Route-specific values are plain request fields,
not part of the signed message.

This affects service routes for DCA cancellation, limit-order active/cancel
requests, gas-pool sponsorship, referral ref-code/link/create actions, rewards
history/points, optional perpetuals order/collateral history authentication,
perpetuals account/vault TWAP and stop-order reads, and authenticated user
WebSocket stop-order subscriptions. `UserData.save-public-key` and the auth
access-token endpoints retain their own message protocols; do not apply the
terms message to them.

The v2.3.0 SDK still exposes old message builders such as
`Dca.closeDcaOrdersMessageToSign`,
`LimitOrders.cancelLimitOrdersMessageToSign`,
`Referrals.createReferralLinkMessageToSign`,
`Referrals.setReferrerMessageToSign`, `UserData.createSignTermsAndConditionsMessageToSign`,
and gas-pool comments mentioning `SPONSOR_GAS` JSON/date payloads. Do not pass
those generated action objects to the current service. Build the fixed terms
bytes yourself until the SDK types/builders are updated.

For DCA and limit-order cancellation, send the IDs as plain fields:

```json
{
  "walletAddress": "0x...",
  "bytes": "<base64 of Aftermath Terms and Conditions>",
  "signature": "<signature over decoded bytes>",
  "orderObjectIds": ["0x...", "0x..."]
}
```

### Current API additions and SDK status

| Service route/family | SDK status |
|---|---|
| `GET /api/addresses` | `Aftermath.getAddresses()` uses it during bootstrap. |
| `GET /api/perpetuals/config` | No high-level SDK accessor in v2.3.0; call the API directly when network defaults/official vault IDs are needed. |
| `POST /api/pools/summary` | `Pools.getPoolSummaries(inputs?, signal?)`; response entries are `{ pool, stats }`. |
| `POST /api/farms/summary` | `Farms.getFarmSummaries(inputs?, signal?)`; response entries are `{ farmId, tvl, rewardsTvl }`. |
| `POST /api/rewards/expected-rewards` | `Rewards.getExpectedRewards` was fixed in 2.2.1 to use the kebab-case path. |
| `POST /api/perpetuals/rebates/create-referral-csv-rebates` | `Perpetuals.getReferralCsvRebates` is present. |
| `/api/ccxt/build/*` address-balance options | Raw API supports `metadata.gasFromAddressBalance`, deposit `fromAddressBalance`, and withdraw `toAddressBalance`; verify SDK types before relying on them. |
| Gas-pool/perps `gasBudget` | Current service accepts optional MIST `gasBudget`; v2.3.0 `ApiGasPoolSponsorBody` and `PerpetualsSponsorConfig` types do not yet expose it. Extend the raw request type when using an exact budget. |
| `POST /api/zklogin/create` | Current service is a plain TS-helper proxy: use `jwt`, `maxEpoch`, base64 `ephemeralPublicKey`, and `randomness`. Do not send an ephemeral private keypair. |

## Known stale SDK calls

These methods exist in the SDK source but do not correspond to current
`service-af-fe` operations or current request shapes:

- `Dca.getAllDcaOrders` calls `dca/orders`; current service exposes `active`,
  `past`, `cancel`, `transactions/create-order`, plus deprecated `user/add`
  and `user/get`.
- `Dca.closeDcaOrder` and `LimitOrders.cancelLimitOrder` type bodies omit the
  current plain `orderObjectIds` array.
- `Referrals.setReferrer`'s v2.3.0 body type omits the current required plain
  `refCode`; `createReferralLink` also omits the optional plain custom code
  (the service defaults one when omitted). Add those fields at the raw request
  boundary rather than signing them into an action message.
- `GasPools.getSponsoredTransaction` and every perpetuals sponsor config use
  the stale action/date message comments and omit the service's optional
  `gasBudget`. Send the reusable terms bytes and extend the body when an exact
  MIST budget is needed.
- `Perpetuals.getCreateBuilderCodeIntegratorVaultTx`,
  `getClaimBuilderCodeIntegratorVaultFeesTx`, and
  `getBuilderCodeIntegratorVaults` call removed integrator-vault routes. The
  current service uses one-time global integrator registration and
  integrator-config routes.
- Several `Router` helpers (`getVolume24hrs`, `getSupportedCoins`,
  `searchSupportedCoins`, `getInteractionEvents`) call legacy router paths.
  The current service source exposes only `trade-route` and
  `transactions/add-trade`; verify a different backend before using the other
  helpers.
- `Perpetuals.openMarketCandlesWebsocketStream` has stale JSDoc describing the
  removed dedicated candles path, but its implementation correctly subscribes
  to `ws/updates` with `marketCandles`. Use the implementation/current API
  contract, not that comment.

## Correctly aligned SDK additions

- `Pools.getPoolSummaries` and `Farms.getFarmSummaries` are typed batch reads;
  both accept a final `AbortSignal` and map to the new summary routes.
- `Rewards.getExpectedRewards` uses `expected-rewards`, not camelCase.
- Perpetuals SDK order, scale-order, TWAP, vault, and general-WebSocket paths
  use the current kebab-case route names. Still apply the terms-auth caveat to
  stop-order/TWAP reads and optional authenticated histories.
- `Aftermath.create` and the v2.3.0 transport changes are additive and belong
  to the SDK; they do not change raw API wire formats.

## Reconciliation workflow

1. Inspect the SDK method's `fetchApi` path and input type.
2. Check the matching route in the service source/OpenAPI operation.
3. Compare camelCase names, `"...n"` BigInt fields, signed-auth requirements,
   and whether the response is bare, wrapped, or a `txKind` object.
4. If the method calls an absent/removed route, use the current raw endpoint or
   mark the SDK method unsupported; do not send the old payload to the service.
