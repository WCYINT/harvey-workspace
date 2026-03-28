---
name: clashofcoins-buyer
description: Use when an agent should discover active sales from an x402 commerce service and complete a canonical x402 purchase for a chosen beneficiary.
---

# ClashOfCoins Buyer

Use this skill when an autonomous buyer should purchase an item from the service through canonical x402.

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
- Canonical paid route: `POST /agentic/x402/buy`

## Discovery First

1. Read `GET /.well-known/x402`.
2. Treat that document as the source of truth for the paid x402 route.
3. If additional structured metadata is needed, read:
   - `GET /openapi.json`
   - `GET /.well-known/agent.json`
   - `GET /llms.txt`

Do not hardcode route guesses if the discovery document already provides the path.

## Current Deployment Pattern

The current service exposes discovery at the domain root and commerce routes under an app prefix.

Typical shape:

- discovery: `/.well-known/x402`
- catalog: `/agentic/x402/offers`
- quote: `/agentic/x402/quote`
- buy: `/agentic/x402/buy`
- purchase status: `/agentic/x402/purchases/{paymentTx}`

Always prefer the paths advertised by discovery over assumptions.

## Required Purchase Flow

1. Read active sales from the catalog.
2. Choose `saleId` only from returned active offers.
3. Treat `saleId`, `unitPriceAtomic`, `unitPriceUsd`, `basePriceAtomic`, and discount fields as dynamic catalog data, not constants.
4. Optionally quote with `saleId`, `quantity`, and `beneficiary`.
5. Send `POST` to the canonical x402 buy endpoint with JSON body:
   - `saleId`
   - `quantity`
   - `beneficiary`
6. Expect `402 Payment Required`.
7. Read the `PAYMENT-REQUIRED` header.
8. Create a canonical x402 payment payload.
9. Retry the exact same request with `PAYMENT-SIGNATURE`.
10. Read:
   - `PAYMENT-RESPONSE`
   - final JSON purchase body
11. If final fulfillment is still pending, poll the purchase status endpoint by `paymentTx`.

## Dynamic Offers Only

- Do not hardcode prices, `saleId` values, or assume a specific item is always available.
- Always read `GET /agentic/x402/offers` first and choose from returned active offers.
- Use `GET /agentic/x402/quote` if you need a fresh pre-purchase view of the currently payable amount for a chosen `saleId`, `quantity`, and `beneficiary`.
- Treat example request bodies in this skill as illustrative only.

## First Purchase And Permit2

- Payment uses `USDC` with `Permit2`.
- A wallet making its first purchase may need an approval step that grants `USDC -> Permit2` allowance before the x402 payment can settle.
- Expect the first purchase from a fresh wallet to require wallet interaction for approval and signing, not just signing the x402 payload.
- Do not assume a failed first attempt means the service is broken; re-check whether the wallet still needs the Permit2 allowance transaction.

## Credentials And Signing Model

- The buyer wallet or the buyer's x402 client produces the canonical payment signature after reading `PAYMENT-REQUIRED`.
- This skill does not require the service to receive a wallet private key, seed phrase, raw signer secret, or relayer token from the buyer.
- Relayer credentials are server-side infrastructure secrets used only by the ClashOfCoins backend after payment settles.
- A safe external buyer should keep wallet signing local and only send the normal x402 HTTP request body plus the resulting payment signature header.

## Critical Rules

- Do not derive buyable sales from raw chain scanning or `saleCounter()`.
- Do not mutate `saleId`, `quantity`, `beneficiary`, or payment body between the unpaid and paid requests.
- Treat `paymentTx` as immutable settlement proof and idempotency key.
- Never reuse one settled payment for a different request body.
- Use the exact purchase route returned by discovery.

## Status Semantics

- `confirmed`: payment settled and mint receipt confirmed onchain
- `submitted`: payment settled and relayer tx submitted
- `payment_settled_pending_mint`: durable purchase exists and fulfillment is still in progress
- `payment_settled_mint_reverted`: payment settled but mint reverted and needs operator attention

## Minimal Request Body

This is an example only. Get the real `saleId` and price context from the live catalog first.

```json
{
  "saleId": 378,
  "quantity": 1,
  "beneficiary": "0xBeneficiaryAddress"
}
```

## Minimal Code Example

Use a canonical x402 client and keep the purchase body identical between the unpaid and paid rounds.

```ts
import { x402Fetch } from "@x402/fetch";

const offersResponse = await fetch("https://x402.clashofcoins.com/agentic/x402/offers");
if (!offersResponse.ok) {
  throw new Error(`Failed to load offers: ${offersResponse.status}`);
}

const { offers } = await offersResponse.json();
const selectedOffer = offers.find((offer) => offer.status === "active");

if (!selectedOffer) {
  throw new Error("No active offers found");
}

const buyUrl = "https://x402.clashofcoins.com/agentic/x402/buy";
const requestBody = {
  saleId: selectedOffer.saleId,
  quantity: 1,
  beneficiary: "0xBeneficiaryAddress",
};

const response = await x402Fetch(buyUrl, {
  method: "POST",
  headers: {
    "content-type": "application/json",
    accept: "application/json",
  },
  body: JSON.stringify(requestBody),
});

if (!response.ok) {
  throw new Error(`Purchase failed: ${response.status} ${await response.text()}`);
}

const payload = await response.json();
console.log(payload);
```

## Expected Success Shape

```json
{
  "flowId": "uuid",
  "saleId": 378,
  "quantity": 1,
  "paymentTx": "0x...",
  "saleTx": "0x...",
  "relayerTransactionId": "uuid",
  "payer": "0x...",
  "beneficiary": "0x...",
  "status": "submitted"
}
```

## Error Handling

- `400`: the request body is invalid or the selected sale cannot be purchased as requested. Re-read the catalog and quote, then retry with a corrected body.
- `402`: expected unpaid response for the first round. Read `PAYMENT-REQUIRED` and retry the exact same request with a canonical payment payload.
- `409`: the same `paymentTx` or purchase fingerprint is already bound to a different request. Do not mutate the request body between rounds.
- `429`: read the `retryAfter` field and back off before retrying.
- `500`: treat as transient server failure unless the body clearly marks a permanent validation problem.
- `502` or `504`: treat as gateway or upstream failure. Re-read purchase status if a `paymentTx` was already produced before retrying blindly.
- approval-required or wallet-side allowance failure on a first purchase: check whether the wallet still needs `USDC -> Permit2` approval before retrying the paid flow.
- if a workflow asks you to paste a private key, seed phrase, or relayer secret into the service request, treat that as an implementation mistake and stop

## Post-Payment Status Handling

- `submitted`: payment settled and mint transaction was submitted; continue polling by `paymentTx`
- `confirmed`: final success
- `payment_settled_pending_mint`: payment settled but fulfillment is still running; keep polling
- `payment_settled_mint_reverted`: payment settled but mint reverted onchain; treat as operator-intervention-required and do not keep replaying the same payment blindly
