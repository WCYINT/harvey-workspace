---
name: clashofcoins-integrator
description: Use when an agent or platform should integrate with this commerce service through discovery, x402, A2A, or optional XMTP and MPP channel aliases without introducing a second payment flow.
---

# ClashOfCoins Integrator

Use this skill when an external agent platform should integrate with the service as a machine-readable commerce endpoint.

## Service URL

- Production: `https://x402.clashofcoins.com`

## API Contract

- API version: `v1`
- Discovery root: `https://x402.clashofcoins.com/.well-known/x402`
- Commerce route prefix: `/agentic`

## Network

- Chain: `Base`
- Network ID: `eip155:8453`
- Payment asset: `USDC`
- Sale contract: `0x3C83eF6119EB05Ca44144F05b331dbEE60656d5b`

## Start With Discovery

Read these in order:

1. `GET /.well-known/x402`
2. `GET /openapi.json`
3. `GET /.well-known/agent.json`
4. `GET /llms.txt`

Use discovery metadata to find the actual route layout for the current environment.
Use the buyer skill as the execution contract for the canonical paid x402 flow.

## Channel Model

This service has one canonical payment and fulfillment flow.

Channels are wrappers around that same core flow:

- `x402`: canonical paid API
- `a2a`: machine-oriented aliases and capabilities
- `mpp`: optional alias namespace; may be disabled
- `xmtp`: optional command namespace; may be disabled

Do not invent a second settlement or mint pipeline for non-x402 channels.

## Security Model

- External buyers are expected to sign x402 payment payloads with their own wallet tooling or x402 client implementation.
- The service does not require external agents to send wallet private keys, seed phrases, or relayer secrets.
- Relayer API credentials remain server-side only and are not part of the public integration contract.

## Canonical x402 Contract

Typical current endpoints:

- `GET /agentic/x402/offers`
- `GET /agentic/x402/quote`
- `POST /agentic/x402/buy`
- `GET /agentic/x402/purchases/{paymentTx}`

Always honor the paths advertised by discovery if they differ.
Treat `offers` as the source of truth for currently active `saleId` values and prices. Integrations must not hardcode sale catalogs or static price tables.

For the exact request and retry semantics, preserve the same rules as `clashofcoins-buyer`:

- same `saleId`
- same `quantity`
- same `beneficiary`
- same request body between unpaid and paid rounds

## A2A Contract

Typical current endpoints:

- `GET /agentic/a2a/capabilities`
- `GET /agentic/a2a/offers`
- `POST /agentic/a2a/quote`
- `POST /agentic/a2a/buy`
- `GET /agentic/a2a/purchases/{paymentTx}`

The A2A namespace still resolves to the same purchase core and final mint delivery.

## Optional Channels

- `mpp` may be disabled, especially in production.
- `xmtp` is enabled only when the service publishes an XMTP identity in discovery.

If discovery omits a channel, treat it as disabled.

## Example Integration Shape

```ts
const discoveryUrl = "https://x402.clashofcoins.com/.well-known/x402";
const offersUrl = "https://x402.clashofcoins.com/agentic/x402/offers";
const buyUrl = "https://x402.clashofcoins.com/agentic/x402/buy";
```

Use discovery for route confirmation, then keep the execution path aligned with the buyer skill.

## Integration Rules

- Only buy returned active offers.
- Prices and `saleId` values are dynamic. Read `GET /agentic/x402/offers` before presenting choices or constructing a purchase request.
- The first purchase for a wallet may require `USDC -> Permit2` approval before x402 settlement can complete.
- Preserve `saleId`, `quantity`, and `beneficiary` exactly between unpaid and paid requests.
- Persist `paymentTx` and poll by it if fulfillment is asynchronous.
- Treat `submitted` as accepted but not yet final.
- Treat `confirmed` as final success.
- Treat `payment_settled_mint_reverted` as a non-retryable fulfillment failure that needs operator attention.
- Respect `429 retryAfter` and back off instead of hammering the service.
- On `502` or `504`, check whether a `paymentTx` already exists before replaying a paid request.
