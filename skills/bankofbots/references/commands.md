# BOB CLI — Current Command Reference

## Identity

```bash
bob auth me
bob config show
bob config set api-url <url>
bob config set platform <generic|openclaw|claude>
bob init --code BOB-XXXX-XXXX
bob doctor
```

## Agent

```bash
bob agent create --name <name>
bob agent get <agent-id>
bob agent list
bob agent approve <agent-id>
bob score me
bob agent credit-events <agent-id> [--limit 50] [--offset 0]
bob agent credit-import <agent-id> --proof-type <type> --proof-ref <ref> \
  --rail onchain --currency <BTC|ETH|SOL> --amount <atomic-units> \
  --direction <outbound|inbound> [--sender-address <addr>] [--recipient-address <addr>] \
  [--counterparty-ref <ref>]

# Example: outbound EVM proof (sender-address required, verified against on-chain sender)
bob agent credit-import <agent-id> --proof-type eth_onchain_tx --proof-ref <0x...txhash> \
  --rail onchain --currency ETH --amount <wei> --direction outbound \
  --sender-address <your-bound-wallet>

# Example: inbound proof (you received the payment)
bob agent credit-import <agent-id> --proof-type eth_onchain_tx --proof-ref <0x...txhash> \
  --rail onchain --currency ETH --amount <wei> --direction inbound \
  --recipient-address <your-bound-wallet>

bob agent credit-imports <agent-id> [--limit 50] [--offset 0]
bob agent x402-import <agent-id> --tx <tx-hash> --network <caip2> \
  --payer <address> --payee <address> --amount <atomic-units> \
  [--resource-url <url>] [--direction <outbound|inbound>]
```

## BOB Score

```bash
bob score me
bob score composition
bob score leaderboard
bob score signals --signal <signal-type> --visible <true|false>
```

## Wallet binding

```bash
bob binding challenge --rail <evm|btc|solana> --address <addr>
bob binding verify --rail <evm|btc|solana> --challenge-id <id> --address <addr> --signature <sig>

# EVM-specific options
bob binding verify --rail evm --challenge-id <id> --address <0x...> --signature <sig> [--chain-id 0x1] [--wallet-type coinbase]
```

## Webhooks and inbox

```bash
bob webhook create <agent-id> --url <url> [--events proof.verified,credit.updated]
bob webhook list <agent-id>
bob webhook get <agent-id> <webhook-id>
bob webhook update <agent-id> <webhook-id> --active true
bob webhook delete <agent-id> <webhook-id>

bob inbox list <agent-id> [--limit 30] [--offset 0]
bob inbox ack <agent-id> <event-id>
bob inbox events <agent-id> [--limit 30]
```

## Loans

```bash
bob loan eligibility                      # Check if you qualify
bob loan request --amount <usdc-units> --duration <days> --purpose "description"
bob loan requests                         # List your loan requests
bob loan accept-terms [loan-id]           # Sign terms (USDC auto-transfers to your wallet)
bob loan status <loan-id>                 # Check status, total owed, safe_address for repayment
bob loan repay <loan-id> --tx <hash> --amount <usdc-units>
bob loan list [--agent-id <id>]
bob loan request-cancel <request-id>
```

## API keys

```bash
bob api-key list
bob api-key create --name <label>
bob api-key revoke <key-id>
```
