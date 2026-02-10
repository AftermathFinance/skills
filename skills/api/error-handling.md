# Error Handling

> Failure modes and resilient handling patterns for CCXT and native Perpetuals endpoints.

---

## 1) Error Shapes to Parse

### Standard API error envelope

```typescript
type ErrorResponse = {
  error_code: number;
  message: string;
  short_message?: string | null;
};
```

### Preview-specific structured error envelope

Some preview routes can return HTTP `200` with an error payload:

```typescript
type PerpetualsErrorResponse = { error: string };
```

When this happens, response header `X-Error-Message: true` is set.

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

- Retryable: network errors, 429/5xx, stale object/version races after rebuild
- Non-retryable: malformed requests, bad signatures, schema mismatch

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

## 4) Build-Sign-Submit Retry Pattern

```typescript
async function submitCcxtTx({ buildUrl, submitUrl, buildBody, signFn }: {
  buildUrl: string;
  submitUrl: string;
  buildBody: any;
  signFn: (signingDigest: string) => Promise<string>;
}) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const build = await fetch(buildUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildBody),
      }).then(r => r.json());

      const signature = await signFn(build.signingDigest);

      const res = await fetch(submitUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transactionBytes: build.transactionBytes, signatures: [signature] }),
      });

      const body = await res.json();
      if (!res.ok) throw Object.assign(new Error("submit failed"), { status: res.status, body });
      return body;
    } catch (err) {
      if (attempt === 2 || !shouldRetry(err)) throw err;
      await new Promise(r => setTimeout(r, 300 * 2 ** attempt));
    }
  }
}
```

---

## 5) Preview Endpoint Guard

```typescript
async function callPreview(url: string, payload: unknown) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  const isPreviewError = res.headers.get("X-Error-Message") === "true" || !!data?.error;

  if (!res.ok || isPreviewError) {
    throw new Error(data?.error ?? data?.message ?? `Preview failed (${res.status})`);
  }

  return data;
}
```

---

## 6) Stream Recovery Rule

For SSE or WebSocket disconnects:

1. Reconnect transport.
2. Re-fetch a fresh snapshot from polling endpoints.
3. Replace local state.
4. Resume incremental updates.

Never continue applying deltas to unknown stale state after reconnect.
