---
name: aftermath-ts-sdk
description: Integrate and troubleshoot the current Aftermath TypeScript SDK for Sui, including Aftermath.create initialization, protocol accessors, transaction builders, perpetuals, pools, farms, transport errors, gRPC setup, and SDK/API compatibility. Use when working with the aftermath-ts-sdk package, its TypeScript source/types, or code that must reconcile the SDK with service-af-fe endpoints.
---

# Aftermath TypeScript SDK

Use the repository snapshot documented here: `aftermath-ts-sdk` `v3.1.0` at
commit `9a1b41db` (2026-08-19). The companion API snapshot is
`service-af-fe` commit `d5cb82c` (2026-08-19). Read the focused reference files
only for the package or compatibility surface being changed.

## Start with the supported entry point

Install and import the package by its actual name:

```bash
npm i aftermath-ts-sdk@3.1.0
```

```typescript
import { Aftermath } from "aftermath-ts-sdk";

const sdk = await Aftermath.create({ network: "MAINNET" });
const pools = sdk.Pools();
const perps = sdk.Perpetuals();
```

Do not use the old `new Aftermath(...); await init()` pattern or the old
`@aftermath-finance/sdk` package name. Direct construction is private; the
async factory bootstraps addresses and a `SuiGrpcClient`.

## Choose the surface

| Need | Use |
|---|---|
| Initialization, network overrides, BigInt, abort signals, gRPC, JSON-RPC, or transport errors | [transport-and-lifecycle.md](references/transport-and-lifecycle.md) |
| Pool/farm/staking/router/coin/wallet/general package methods | [packages.md](references/packages.md) |
| Perpetual markets, accounts, vaults, order builders, TWAP, or WebSockets | [perpetuals.md](references/perpetuals.md) |
| Determine whether an SDK method matches the current API service | [backend-alignment.md](references/backend-alignment.md) |
| Raw endpoint payloads and operational safety | [../api/SKILL.md](../api/SKILL.md) and its focused references |

The root package re-exports the configured provider, selected package classes,
types, casting helpers, and transport error utilities. Prefer
`sdk.<Accessor>()` for configured clients; the accessors are functions, not
singleton properties. The current configured accessors are `Pools`, `Staking`,
`SuiFrens`, `Faucet`, `Router`, `NftAmm`, `ReferralVault` (deprecated),
`Referrals`, `GasPools`, `Perpetuals`, `Rewards`, `Farms`, `Dca`, `Multisig`,
`LimitOrders`, `UserData`, `Sui`, `Prices`, `Wallet(address)`,
`Coin(coinType?)`, `DynamicGas`, and `Auth`. At v3.1.0, not every accessor
class is re-exported from the package barrel (`Dca`, `LimitOrders`,
`Multisig`, `Referrals`, `Rewards`, `UserData`, and `DynamicGas` are the
important exceptions); use the configured accessors instead of assuming a
direct named import exists.

## Rules that prevent common breakage

- Serialize SDK `bigint` request values as the SDK expects; its JSON replacer
  emits strings such as `"123n"`, and normal response parsing revives those
  strings to `bigint`. Do not globally patch `BigInt.prototype`.
- Transaction methods return `@mysten/sui` `Transaction` objects. The SDK
  chooses `Transaction.fromKind` for ordinary `txKind` responses and
  `Transaction.from` when a response includes `sponsorSignature`; set the
  sender when the request has `walletAddress`.
- Pass an `AbortSignal` as the final positional argument where supported.
  `Aftermath.create(options, signal)` supports bootstrap cancellation, and
  selected pool/farm/price/coin metadata/decimal reads and summary methods
  accept final positional abort signals.
- `Perpetuals().getVaultsConfig(signal?)` reads the live vault protocol limits
  from `POST /api/perpetuals/vaults/config`. Integer fields are returned as
  `bigint` values; do not use removed hardcoded `PerpetualsVault.constants`.
- `Perpetuals().getGrantVaultAgentWalletTx(...)` and
  `getRevokeVaultAgentWalletTx(...)` build vault-owner transactions for
  assistant capabilities. A `PerpetualsVault` wrapper exposes the corresponding
  `getGrantAgentWalletTx(...)` and `getRevokeAgentWalletTx(...)` methods.
- Catch `AftermathTransportError` and branch on `kind` (`http`, `network`,
  `abort`, `timeout`, or `decode`) instead of matching only error text. HTTP
  messages retain the legacy `HTTP <status> <statusText>: <body>` format.
- Check [backend-alignment.md](references/backend-alignment.md) before using
  signed DCA, limit-order, referral, gas-sponsor, or deprecated integrator
  vault helpers. The service has moved to reusable terms authentication while
  deprecated v3.1.0 action-message builders remain in some package surfaces.
- Use `AftermathApi` only when direct protocol API helpers are needed. It is
  gRPC-first; the optional JSON-RPC client is required by the three legacy
  helpers named by `requireJsonRpcClient`. Prefer high-level Aftermath API
  providers for events, transaction history, and system state.
