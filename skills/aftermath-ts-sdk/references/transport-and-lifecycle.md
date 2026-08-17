# SDK Lifecycle and Transport

## Package runtime

The published package is ESM (`type: module`) and expects
`@mysten/sui >=2.0.0 <3.0.0` as a peer dependency. Import the package through
its root export; do not rely on the repository's internal source paths.

## Initialization

The public factory is asynchronous and accepts an optional final abort signal:

```typescript
const controller = new AbortController();
const sdk = await Aftermath.create(
  {
    network: "MAINNET", // MAINNET | TESTNET | DEVNET | LOCAL
    // baseUrl, fullnodeUrl, apiEndpoint, addresses, or api are optional
  },
  controller.signal,
);
```

`AftermathOptions` supports `network`, `baseUrl`, `fullnodeUrl`,
`apiEndpoint` (defaults to `api`), preloaded `addresses`, or a pre-built
`AftermathApi`. `baseUrl` overrides the API host; `fullnodeUrl` is passed to
both `SuiGrpcClient.baseUrl` and `SuiJsonRpcClient.url`. Supplying `addresses`
or `api` avoids address discovery.

Canonical hosts in v2.3.0:

| Network | API | Sui fullnode |
|---|---|---|
| MAINNET | `https://aftermath.finance` | `https://fullnode.mainnet.sui.io:443` |
| TESTNET | `https://testnet.aftermath.finance` | `https://fullnode.testnet.sui.io:443` |
| DEVNET | `https://devnet.aftermath.finance` | `https://fullnode.devnet.sui.io:443` |
| LOCAL | `http://localhost:3000` | `http://127.0.0.1:9000` |

The effective HTTP URL is `{baseUrl}/{apiEndpoint}/{provider-prefix}/{path}`.
For a custom service mounted without `/api`, set `apiEndpoint: ""`; do not
hard-code `/api` into a provider path.

## Request and response serialization

`Caller.fetchApi` sends GET when the body is `undefined`, and POST for every
defined body (including `{}`). It sets `Content-Type: application/json` and
adds `Authorization: Bearer <accessToken>` when `Auth.init` has installed a
token.

The SDK's JSON replacer converts a JavaScript `bigint` to a string with an `n`
suffix, for example `123n` → `"123n"`. Normal responses use
`Helpers.parseJsonWithBigint` to revive safe `"123n"` values to `bigint`.
Pass `disableBigIntJsonParsing` only when a provider explicitly requires raw
JSON. Do not assume every number is a BigInt: timestamps, prices, booleans,
and counts remain ordinary JSON values.

Transaction helpers behave as follows:

- `fetchApiTransaction` parses a bare serialized transaction as a Sui
  `Transaction`, using `Transaction.fromKind` for `txKind: true` and
  `Transaction.from` otherwise.
- `fetchApiTxObject` parses `response.txKind` with `Transaction.from` when the
  response also has `sponsorSignature`; otherwise it uses `Transaction.fromKind`.
- A request `walletAddress` is applied as the transaction sender after parsing.

## Abort and transport errors

The v2.3.0 `AftermathTransportError` is exported from the package root:

```typescript
import {
  isAftermathTransportError,
} from "aftermath-ts-sdk";

try {
  await sdk.Pools().getAllPools(controller.signal);
} catch (error) {
  if (isAftermathTransportError(error)) {
    console.log(error.kind, error.status, error.retryAfterMs, error.code);
  }
}
```

`kind` is one of:

| Kind | Meaning | Useful fields |
|---|---|---|
| `http` | Server returned a non-2xx response | `status`, `retryAfterMs` |
| `network` | Fetch/DNS/socket failure | `cause`, `code` |
| `abort` | Caller-owned signal was aborted | `abortSource: "caller"` |
| `timeout` | Timeout or timeout-like fetch failure | `abortSource: "timeout"`, `code` |
| `decode` | A successful response was not valid JSON | `cause` |

HTTP errors preserve the old `Error` name and message format:
`HTTP <status> <statusText>: <body>`. `Retry-After` is parsed into
`retryAfterMs` for integer seconds or valid HTTP dates.

Retry reads and bootstrap calls on transient `network`, `timeout`, `429`, and
5xx failures when safe. Do not blindly retry transaction submission or a
request whose bytes may already have been accepted; reconcile chain/account
state first. Treat caller aborts as intentional cancellation.

## gRPC-first `AftermathApi`

Construct the low-level provider with a `SuiGrpcClient`, resolved config
addresses, and optionally a `SuiJsonRpcClient`:

```typescript
const api = new AftermathApi(grpcClient, addresses, jsonRpcClient);
const sdk = await Aftermath.create({ api });
```

The current source describes the optional JSON-RPC surface as three legacy
helpers: `Events().fetchCastEventsWithCursor`,
`Transactions().fetchTransactionsWithCursor`, and deprecated
`Sui().fetchSystemState`. `AftermathApi.requireJsonRpcClient()` throws a
descriptive error when those helpers are called without a JSON-RPC client.
Every other current `AftermathApi` call is intended to use gRPC. Prefer the
Aftermath service's high-level providers for events, transaction history, and
system state where possible. Sui JSON-RPC is scheduled for removal from
fullnodes in mid-October 2026.
