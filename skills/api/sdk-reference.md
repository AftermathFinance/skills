# TypeScript SDK Bridge

The maintained SDK reference is the dedicated
[Aftermath TypeScript SDK skill](../aftermath-ts-sdk/SKILL.md). Use it for
`aftermath-ts-sdk` v3.0.0 initialization, provider methods, transaction
builders, transport errors, gRPC, and all SDK/API compatibility notes.

## Current bootstrap

```typescript
import { Aftermath } from "aftermath-ts-sdk";

const afSdk = await Aftermath.create({ network: "MAINNET" });
const perps = afSdk.Perpetuals();
const pools = afSdk.Pools();
```

The package is `aftermath-ts-sdk`; do not use the removed
`@aftermath-finance/sdk` name or direct construction plus `init()`.

## Current SDK/API boundaries

Before using signed DCA, limit-order, referral, gas-pool, stop-order, or TWAP
helpers, read [backend-alignment.md](../aftermath-ts-sdk/references/backend-alignment.md).
The current `service-af-fe` snapshot accepts a reusable signature over the
exact message `Aftermath Terms and Conditions`; deprecated v3.0.0 SDK message
builders still emit old action-specific JSON. DCA and limit-order cancellation
IDs now travel as plain `orderObjectIds`.

The v3.0.0 SDK additions that are safe to rely on include:

- async `Aftermath.create(options, abortSignal?)` and final-position abort
  signals on selected reads;
- typed `Pools().getPoolSummaries` and `Farms().getFarmSummaries`;
- dynamic `Perpetuals().getVaultsConfig(abortSignal?)` for current vault protocol
  limits; do not use the removed hardcoded `PerpetualsVault.constants`;
- typed plain `orderObjectIds`/`refCode` request fields and the canonical
  `UserData.createTermsAndConditionsMessage()` helper; old action-message
  helpers remain deprecated;
- `Rewards().getExpectedRewards` using `expected-rewards`;
- `AftermathTransportError` classification for HTTP, network, abort, timeout,
  and decode failures;
- gRPC-first `AftermathApi` with an optional JSON-RPC client for its remaining
  legacy helpers.

For raw endpoint shapes, use the API references in this directory, especially
`native.md`, `dca-and-limit-orders.md`, `authentication.md`, and
`endpoint-inventory.md`.
