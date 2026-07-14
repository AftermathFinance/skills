# Error Handling

> Failure modes and resilient handling patterns for CCXT and native Perpetuals endpoints.

---

## 1) Error Shapes to Parse

### API error variants

```typescript
type DocumentedErrorResponse = {
  error_code: number;
  message: string;
  short_message?: string | null;
};

type ApiErrorBody =
  | DocumentedErrorResponse
  | { error: string }
  | string
  | null;
```

Clients must handle object envelopes, JSON strings such as `"Error 2019: ..."`,
and plain text. When present, `X-Error-Code` contains the numeric code and
`X-Error-Message` contains message text. Preview errors use `{ error }` and set
`X-Error-Message: true`.

Parse the response body as text first, then decode JSON when possible:

```typescript
async function readBody(response: Response): Promise<ApiErrorBody | unknown> {
  const text = await response.text();
  if (!text) return null;
  try { return JSON.parse(text); } catch { return text; }
}

function getErrorMessage(response: Response, body: any): string {
  if (body && typeof body === "object") return body.error ?? body.message ?? JSON.stringify(body);
  if (typeof body === "string") return body;
  return response.headers.get("X-Error-Message") ?? `HTTP ${response.status}`;
}
```

### Preview-specific structured error envelope

Some preview routes can return HTTP `200` with an error payload:

```typescript
type PerpetualsErrorResponse = { error: string };
```

When this happens, `data.error` is the primary signal. Do not depend on the header alone.

---

## 2) CCXT Write Failures by Phase

### Build phase (`/api/ccxt/build/*`)

- Validation failures (`chId`, `accountId`, invalid size/price/leverage)
- Insufficient collateral
- Stale assumptions on account/market state

### Submit phase (`/api/ccxt/submit/*`)

- Invalid signature format
- Delayed submit leading to stale object versions
- Gas issues or coin/gas object races

---

## 3) Retry Policy

Retry only when the operation is transient.

- Retryable: build-phase network errors, 429/5xx reads, explicit stale object/version rejection after a rebuild
- Non-retryable: malformed requests, bad signatures, schema mismatch
- Ambiguous: submit timeout or lost response after bytes were sent; reconcile the original transaction before rebuilding

```typescript
function shouldRetry(error: any): boolean {
  const code = error?.status ?? error?.response?.status;
  if (code === 429 || (code >= 500 && code < 600)) return true;

  const msg = String(error?.message ?? "").toLowerCase();
  if (msg.includes("timeout") || msg.includes("connection")) return true;
  if (msg.includes("version") || msg.includes("stale")) return true;

  return false;
}
```

---

## 4) Build-Sign-Submit Pattern

```typescript
async function postJson(url: string, body: unknown) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await readBody(response);
  if (!response.ok) {
    throw Object.assign(new Error(getErrorMessage(response, data)), {
      status: response.status,
      body: data,
      errorCode: response.headers.get("X-Error-Code"),
    });
  }
  return data as any;
}

async function buildAndSubmitCcxtTx({ buildUrl, submitUrl, buildBody, signFns }: {
  buildUrl: string;
  submitUrl: string;
  buildBody: any;
  signFns: Array<(signingDigest: string) => Promise<string>>;
}) {
  let build: { transactionBytes: string; signingDigest: string } | undefined;
  for (let attempt = 0; attempt < 3 && !build; attempt++) {
    try {
      build = await postJson(buildUrl, buildBody);
    } catch (err) {
      if (attempt === 2 || !shouldRetry(err)) throw err;
      await new Promise(r => setTimeout(r, 300 * 2 ** attempt));
    }
  }

  const signatures = await Promise.all(signFns.map(fn => fn(build!.signingDigest)));

  // Submit once. A timeout after sending is ambiguous: the transaction may have
  // executed. Reconcile account/order state before deciding to resubmit or rebuild.
  return postJson(submitUrl, {
    transactionBytes: build!.transactionBytes,
    signatures,
  });
}
```

Do not automatically rebuild after an ambiguous submit failure. If the server
explicitly rejects stale object versions, rebuild from fresh state. If the
response was lost, inspect account state, positions, and order history first.

---

## 5) Preview Endpoint Guard

Preview behavior is not uniform:

- Order and cancel previews often use explicit success/error unions.
- Several vault admin previews return `PerpetualsErrorResponse` on HTTP `200` when validation fails.
- `/api/perpetuals/vault/previews/pause-vault-for-force-withdraw-request` returns a normal `TxKindResponse`.

```typescript
async function callPreview(url: string, payload: unknown) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data: any = await readBody(res);
  const isPreviewError = !!data?.error || res.headers.get("X-Error-Message") === "true";

  if (!res.ok || isPreviewError) {
    throw new Error(
      typeof data === "string"
        ? data
        : data?.error ?? data?.message ?? res.headers.get("X-Error-Message") ?? `Preview failed (${res.status})`,
    );
  }

  return data;
}
```

---

## 6) Stream Recovery Rule

For WebSocket disconnects:

1. Reconnect transport.
2. Re-fetch a fresh snapshot from polling endpoints.
3. Replace local state.
4. Resume incremental updates.

Never continue applying deltas to unknown stale state after reconnect.
