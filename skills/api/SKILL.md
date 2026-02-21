---
name: aftermath-perpetuals
description: Practical skill for integrating Aftermath Perpetuals with native endpoints as the default (full feature set), plus CCXT-compatible endpoints and the TypeScript SDK.
version: 2.3.0
capabilities:
  - api-integration
  - sdk-integration
  - order-placement
  - position-monitoring
  - risk-analysis
  - vault-management
  - error-handling
---

# Aftermath Perpetuals Skill

Verified against OpenAPI: `https://aftermath.finance/api/openapi/spec.json`
Last validated: `2026-02-21`
Canonical docs UI: `https://aftermath.finance/docs`

## Fast Routing

Choose one file first; do not load everything by default.

Default preference: start with native perpetuals endpoints (`/api/perpetuals/*`) because they expose the full Aftermath feature set. Use CCXT endpoints when you specifically need exchange-style compatibility.

1. CCXT endpoint work -> `ccxt.md`
2. Native perpetuals endpoint work -> `native.md`
3. SDK method usage -> `sdk-reference.md`
4. API failures/retries -> `error-handling.md`
5. Trading safeguards -> `safety-and-risk.md`
6. Builder codes/referrals/rewards/coins utility routes -> `auxiliary-endpoints.md`
7. Edge-case pitfalls -> `gotchas.md`

## Integration Modes

Preferred by default: Native perpetuals (`/api/perpetuals/*`) for complete API coverage.

| Mode | Best for | Primary file |
|---|---|---|
| CCXT compatibility (`/api/ccxt/*`) | Exchange-style payloads and build-sign-submit bots | `ccxt.md` |
| Native perpetuals (`/api/perpetuals/*`) | Full account/vault previews + tx builders | `native.md` |
| TypeScript SDK (`@aftermath-finance/sdk`) | Typed app integrations | `sdk-reference.md` |

## High-Risk Guardrails

- Sign `signingDigest`, not `transactionBytes`.
- Keep ID types strict: CCXT write `accountId` (object ID) vs native `accountId` (numeric).
- Treat preview responses as success/error unions.
- Re-sync snapshots after stream reconnect before applying deltas.
- Serialize coin/gas-object-sensitive operations to avoid version conflicts.

## Progressive Disclosure

| File | Read when |
|---|---|
| `ccxt.md` | You need `/api/ccxt/*` endpoints or stream setup |
| `native.md` | You need `/api/perpetuals/*` account/market/vault APIs |
| `auxiliary-endpoints.md` | You need builder-codes, referrals, rewards, coins, utility txs |
| `sdk-reference.md` | You are coding with SDK classes and methods |
| `error-handling.md` | You are implementing retry, backoff, and failure parsing |
| `safety-and-risk.md` | You are shipping a bot or live strategy safeguards |
| `gotchas.md` | You need a pre-launch pitfalls checklist |

## 24h Change Check

Use the local helper script to check for OpenAPI changes after the 24h window.

- Script: `skills/api/scripts/check_api_changes.py`
- Behavior: if less than 24h since `Last validated`, it exits without querying.
- If 24h+ elapsed, it prompts before querying: `Query ... for API changes now? [y/N]`.
- It never auto-updates skill markdown files; it only records spec hash state in `skills/api/.api-spec-state.json`.

Run:

```bash
python3 skills/api/scripts/check_api_changes.py
```
