# SDK and API Alignment

Check the following before assuming a typed SDK method is a working API call.
This page applies to `aftermath-ts-sdk` v3.1.0 and the Aftermath API as of
2026-08-19, whose surface is 260 OpenAPI operations; `/api/pools`
intentionally has both GET (deprecated) and POST (current).

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
requests, gas-pool sponsorship, referral ref-code/linked-ref-code/link/create actions, rewards
history/points, optional perpetuals order/collateral history authentication,
perpetuals account/vault TWAP and stop-order reads, and authenticated user
WebSocket stop-order subscriptions. `UserData.save-public-key` and the auth
access-token endpoints retain their own message protocols; do not apply the
terms message to them.

The v3.1.0 SDK still exposes deprecated action-message builders such as
`Dca.closeDcaOrdersMessageToSign`, `LimitOrders.cancelLimitOrdersMessageToSign`,
`Referrals.createReferralLinkMessageToSign`, `Referrals.setReferrerMessageToSign`,
and `UserData.createSignTermsAndConditionsMessageToSign`; gas-pool comments also
mention the obsolete `SPONSOR_GAS` JSON/date payload. Do not pass those action
objects to the current service. Use `UserData.createTermsAndConditionsMessage()`
or sign the exact reusable terms bytes directly.

For DCA and limit-order cancellation, send the IDs as plain fields:

```json
{
  "walletAddress": "0x...",
  "bytes": "<base64 of Aftermath Terms and Conditions>",
  "signature": "<signature over decoded bytes>",
  "orderObjectIds": ["0x...", "0x..."]
}
```

For perpetuals transaction builders with a non-empty `sponsor.walletAddress`,
returned order gas is deposited back into that sponsor's gas pool. With no
named sponsor (absent or empty wallet), returned gas goes to the account or
vault owner. Scheduled stop/TWAP execution gas is drawn from the sponsor pool
as a deferred coin input, so do not assume sender/owner coin objects fund or
receive it.

### Current API additions and SDK status

| Service route/family | SDK status |
|---|---|
| `GET /api/addresses` | `Aftermath.getAddresses()` uses it during bootstrap. |
| `GET /api/perpetuals/config` | No high-level SDK accessor in v3.1.0; call the API directly when network defaults/official vault IDs are needed. |
| `POST /api/perpetuals/vaults/config` | `Perpetuals.getVaultsConfig(abortSignal?)`; sends `{}` and returns dynamic `PerpetualsVaultsConfig` with bigint integer fields. |
| `POST /api/perpetuals/vault/transactions/owner/grant-agent-wallet` | `Perpetuals.getGrantVaultAgentWalletTx({ vaultId, recipientAddress, sponsor?, tx? })` or `PerpetualsVault.getGrantAgentWalletTx({ recipientAddress, sponsor?, tx? })`; submit from the vault owner's `ADMIN` capability. |
| `POST /api/perpetuals/vault/transactions/owner/revoke-agent-wallet` | `Perpetuals.getRevokeVaultAgentWalletTx({ vaultId, accountCapId, sponsor?, tx? })` or `PerpetualsVault.getRevokeAgentWalletTx({ accountCapId, sponsor?, tx? })`; revoke the assistant capability from the vault owner. |
| `POST /api/pools/summary` | `Pools.getPoolSummaries(inputs?, signal?)`; response entries are `{ pool, stats }`. |
| `POST /api/farms/summary` | `Farms.getFarmSummaries(inputs?, signal?)`; response entries are `{ farmId, tvl, rewardsTvl }`. |
| `POST /api/rewards/expected-rewards` | `Rewards.getExpectedRewards` was fixed in 2.2.1 to use the kebab-case path. |
| `POST /api/perpetuals/rebates/create-referral-csv-rebates` | `Perpetuals.getReferralCsvRebates` is present. |
| `/api/ccxt/build/*` address-balance options | Raw API supports `metadata.gasFromAddressBalance`, deposit `fromAddressBalance`, and withdraw `toAddressBalance`; verify SDK types before relying on them. |
| Gas-pool/perps `gasBudget` | Current service accepts optional MIST `gasBudget`; v3.1.0 `ApiGasPoolSponsorBody` and `PerpetualsSponsorConfig` types still do not expose it. Extend the raw request type when using an exact budget. |
| `POST /api/zklogin/create` | Use `jwt`, `maxEpoch`, base64 `ephemeralPublicKey`, and `randomness`. Do not send an ephemeral private keypair. |

## Known stale SDK calls

These methods exist in the SDK source but do not correspond to current
current API operations or request shapes:

- `Dca.getAllDcaOrders` calls `dca/orders`; current service exposes `active`,
  `past`, `cancel`, `transactions/create-order`, plus deprecated `user/add`
  and `user/get`.
- `GasPools.getSponsoredTransaction` still carries stale action/date
  `SPONSOR_GAS` comments and its type omits optional `gasBudget`;
  `PerpetualsSponsorConfig` uses the terms message but still omits that field.
  Send the reusable terms bytes and extend the body when an exact MIST budget is needed.
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
- `Aftermath.create` and the v3.1.0 transport changes are additive and belong
  to the SDK; they do not change raw API wire formats.
- `Perpetuals.getVaultsConfig(abortSignal?)` posts an empty JSON object to
  `/api/perpetuals/vaults/config` and returns deployment-driven limits; integer
  fields decode to `bigint`. The removed `PerpetualsVault.constants` is not a
  valid source of current limits.

## Reconciliation workflow

1. Inspect the SDK method's `fetchApi` path and input type.
2. Check the matching OpenAPI operation.
3. Compare camelCase names, `"...n"` BigInt fields, signed-auth requirements,
   and whether the response is bare, wrapped, or a `txKind` object.
4. If the method calls an absent/removed route, use the current raw endpoint or
   mark the SDK method unsupported; do not send the old payload to the service.
