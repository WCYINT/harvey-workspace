---
name: clashofcoins
description: Use when an agent should interact with the ClashOfCoins x402 commerce service and choose the correct sub-skill for either buying items or integrating the service into another agent platform.
---

# ClashOfCoins

Use this skill as the entrypoint for the ClashOfCoins commerce service on Base mainnet.

## Service URL

- Production: `https://x402.clashofcoins.com`

## Network

- Chain: `Base`
- Network ID: `eip155:8453`
- Payment asset: `USDC`
- Sale contract: `0x3C83eF6119EB05Ca44144F05b331dbEE60656d5b`

## What This Package Contains

- `clashofcoins-buyer/SKILL.md`
  Use this when the agent needs to discover active offers and complete a canonical x402 purchase.
- `clashofcoins-integrator/SKILL.md`
  Use this when the agent needs to integrate the service into another platform, agent runtime, scanner, or orchestration layer.

## Selection Rules

- If the task is to buy, quote, settle, or poll purchase status, use `clashofcoins-buyer`.
- If the task is to consume discovery metadata, wire channels, register the service, or build a wrapper over the commerce API, use `clashofcoins-integrator`.
- If both are needed, use `clashofcoins-integrator` first for discovery and route selection, then use `clashofcoins-buyer` for the actual paid x402 execution path.

## Service Contract

The service exposes discovery at the domain root and commerce routes under `/agentic`.

Important entrypoints:

- `GET /.well-known/x402`
- `GET /openapi.json`
- `GET /.well-known/agent.json`
- `GET /llms.txt`
- `GET /agentic/x402/offers`
- `GET /agentic/x402/quote`
- `POST /agentic/x402/buy`
- `GET /agentic/x402/purchases/{paymentTx}`

## Critical Rule

There is one canonical payment and fulfillment flow.

Non-x402 namespaces such as A2A, XMTP, or MPP are wrappers over the same purchase core and must not introduce a second settlement or mint pipeline.

## Important Execution Notes

- Sale IDs and prices are dynamic. Agents must read `GET /agentic/x402/offers` instead of hardcoding a catalog.
- Payment uses `USDC` with `Permit2`, so a wallet's first purchase may require an approval step before x402 settlement succeeds.
- Payment signatures are produced by the buyer wallet or the buyer's x402 client, not by this skill package.
- This service never asks an external buyer to provide a wallet private key, seed phrase, or relayer API secret.
