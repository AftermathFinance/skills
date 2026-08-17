# API Authentication and Signed Requests

The current `service-af-fe` source centralizes several wallet-authenticated
routes on one reusable signature check. Do not infer the signed payload from
old SDK message-builder names or from stale comments in individual handlers.

## Reusable terms signature

The only message accepted by `verify_terms_signature` is:

```text
Aftermath Terms and Conditions
```

The wallet signs the UTF-8 bytes of that exact string. Send those bytes as
base64 in `bytes`, and send the wallet's signature over the decoded bytes in
`signature`:

```typescript
const termsMessage = "Aftermath Terms and Conditions";
const messageBytes = new TextEncoder().encode(termsMessage);
const bytes = Buffer.from(messageBytes).toString("base64");
const { signature } = await wallet.signPersonalMessage({ message: messageBytes });

const auth = { walletAddress, bytes, signature };
```

In a browser, use the platform's base64 encoder instead of Node's `Buffer`.
The signature is reusable for the wallet connection. The request-specific
object IDs, filters, referral code, or history cursor travel as ordinary JSON
fields and are not signed.

## Routes using the terms check

| Family | Routes or fields |
|---|---|
| DCA | `POST /api/dca/cancel` |
| Spot limit orders | `POST /api/limit-orders/active`, `POST /api/limit-orders/cancel` |
| Gas pool | `POST /api/gas-pool/transactions/sponsor` |
| Referrals | `ref-code`, `linked-ref-code`, `create`, and `link` under `/api/referrals/` |
| Rewards | `POST /api/rewards/history`, `POST /api/rewards/points` |
| Perpetual data | `stop-order-datas` and `twap-order-datas` for account/vault; optional `authentication` on order/collateral history where declared |
| Perpetual WebSocket | `withStopOrders` on the `user` subscription to `GET /api/perpetuals/ws/updates` |
| Sponsored perpetual transactions | Embedded `sponsor` auth configs on routes that accept them |

For DCA and limit-order cancellation, include the IDs plainly:

```json
{
  "walletAddress": "0x...",
  "bytes": "<base64 terms bytes>",
  "signature": "<signature>",
  "orderObjectIds": ["0x...", "0x..."]
}
```

The service verifies the wallet address, base64, UTF-8 decoding, exact terms
text, and signature. A rejected signature is a 400-level human-readable API
error with code `2034` (`SignatureVerificationFailed`); do not retry it as a
transient transport failure.

## Flows that use a different message protocol

Do not apply the terms message to these routes:

- `POST /api/auth/access-token` and `POST /api/auth/create-account`: sign the
  caller's `serializedJson` payload and send its signature. The access-token
  response's `expirationTimestamp` is Unix milliseconds.
- `POST /api/user-data/save-public-key`: the `bytes` value is the public-key
  registration message expected by the user-data service; `public-key` reads
  are unsigned.
- CCXT build/submit: sign the returned `signingDigest`, not a wallet-auth
  message and not `transactionBytes`.

## Gas-pool sponsorship response

`POST /api/gas-pool/transactions/sponsor` requires `walletAddress`, terms
`bytes`, and `signature`; it accepts optional `txKind` and optional
`gasBudget` in MIST. It returns:

```typescript
type SponsoredTransaction = {
  transaction: string;
  sponsorSignature: string;
  digest: string;
};
```

The client signs `transaction` as the sender and submits it with the sponsor
signature. `gasBudget` is exact when supplied; otherwise the service derives a
budget. The SDK v2.3.0 comments still describe an action/date `SPONSOR_GAS`
message, which the current service no longer accepts.

## Authenticated WebSocket subscription

```json
{
  "action": "subscribe",
  "subscriptionType": {
    "user": {
      "accountId": "123n",
      "withStopOrders": {
        "walletAddress": "0x...",
        "bytes": "<base64 terms bytes>",
        "signature": "<signature>"
      }
    }
  }
}
```

The proxy verifies `withStopOrders` before forwarding the wallet address to
the downstream stream. A failed verification is a subscription/connection
error; reconnect with a valid auth object only after correcting the payload.
