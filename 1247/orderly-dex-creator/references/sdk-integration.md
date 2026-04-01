# SDK Integration Reference (Orderly DEX Creator)

Practical reference for custom SDK/API builds on Orderly.

> Always validate endpoint behavior and package versions against the latest official docs before production rollout.

## 1) React Components SDK (fastest UI integration)

### Install

```bash
npm install @orderly.network/ui @orderly.network/react-app @orderly.network/wallet-connector
```

### App provider wiring

```tsx
import "@orderly.network/ui/dist/styles.css";
import { OrderlyAppProvider } from "@orderly.network/react-app";
import { WalletConnectorProvider } from "@orderly.network/wallet-connector";

export function AppProviders({ children }) {
  return (
    <WalletConnectorProvider>
      <OrderlyAppProvider
        brokerId="your-broker-id"
        brokerName="Your DEX"
        networkId="mainnet" // or "testnet"
        appIcons="/logo.svg"
      >
        {children}
      </OrderlyAppProvider>
    </WalletConnectorProvider>
  );
}
```

### Feature/page packages

```bash
npm install @orderly.network/trading @orderly.network/portfolio @orderly.network/referral @orderly.network/markets @orderly.network/trading-rewards @orderly.network/affiliate @orderly.network/ui-scaffold
```

---

## 2) Hooks SDK (custom UI)

```bash
npm install @orderly.network/hooks
```

Use hooks when you need full UI ownership while retaining Orderly data primitives.

---

## 3) Python connector (backend/bots)

```bash
pip install orderly-evm-connector-python
```

Repo: https://github.com/OrderlyNetwork/orderly-evm-connector-python

---

## 4) Private API auth model

### Required headers

| Header | Meaning |
|---|---|
| `orderly-account-id` | Account identifier |
| `orderly-key` | ed25519 public key |
| `orderly-timestamp` | current timestamp (ms) |
| `orderly-signature` | Base64URL signature |

### Signature payload

```text
message = timestamp + method + requestPath + bodyString
```

Sign with ed25519 secret key; send Base64URL output in `orderly-signature`.

---

## 5) Endpoint map (common)

| Path | Method(s) | Use |
|---|---|---|
| `/v1/register_account` | POST | account registration |
| `/v1/orderly_key` | POST | add/manage key |
| `/v1/order` | POST/PUT/DELETE | create/modify/cancel order |
| `/v1/orders` | GET/DELETE | list/cancel orders |
| `/v1/positions` | GET | positions |
| `/v1/client/holding` | GET | balances/holdings |
| `/v1/withdraw_request` | POST | withdrawals |
| `/v1/settle_pnl` | POST | settle PnL |
| `/v1/broker/fee_rate/default` | GET/POST | default builder fee |
| `/v1/broker/fee_rate/set` | POST | user-specific fee |
| `/v1/referral/create` | POST | referral creation |

---

## 6) WebSocket notes

Use official Orderly docs as source-of-truth for current WS hostnames and topic schemas.

### Validation checklist
- Confirm public vs private WS endpoints for your environment (mainnet/testnet)
- Confirm whether account-scoped path parameters are required per endpoint
- Validate auth handshake for private streams
- Validate topics you rely on (`trade`, `orderbook`, `kline`, execution/position/balance)

If docs and historical examples conflict, trust latest official docs/dashboard values.

---

## 7) Chain support + addresses

- Chains: query `GET /v1/public/chain_info`
- Contract addresses: see official Orderly omnichain addresses page

---

## 8) Production hardening checklist

- [ ] Pin package versions / lockfile committed
- [ ] Per-environment API/WS host config (dev/stage/prod)
- [ ] Retries + idempotency strategy for order endpoints
- [ ] Clock sync guard for signed requests
- [ ] Structured logs for order lifecycle + auth failures
- [ ] Alerting for WS disconnect bursts and order reject spikes
- [ ] Runbook for key rotation and degraded-mode trading
