# HERMES Customer Configuration Format

When provisioning a new HERMES customer (via `provision.sh`), a dedicated directory (e.g. `/opt/hermes/customers/business_id/`) is created containing their specific `config.json` and a templated SQLite DB.

## Default `config.json` Structure

```json
{
  "providers": {
    "openrouter": {
      "api_key": "sk-or-v1-customer_key_here",
      "model": "claude-3-haiku"
    }
  },
  "agents": {
    "workspace": "/opt/hermes/customers/business_id/",
    "maxToolIterations": 20
  },
  "channels": {
    "telegram": {
      "token": "bot_token_here",
      "allowFrom": [
        123456789,
        987654321
      ]
    }
  }
}
```

## Key Configuration Fields

### 1. `providers`

- **openrouter**: The primary LLM provider.
  - **api_key**: Using OpenRouter for access to multiple top-tier models.
  - **model**: We default to Anthropic's `claude-3-haiku` (via OpenRouter) or `gpt-4o-mini` for speed/cost effectiveness on invoice generation and bookkeeping instructions. Fast reasoning is paramount.

### 2. `agents`

- **workspace**: Absolute path to the directory containing this customer's customized `SOUL.md` (the prompt with their business details mapped) and `hermes.db` SQLite database.
- **maxToolIterations**: Set to 20 to allow multi-step tasks (e.g. create client -> draft invoice -> email invoice -> generate response in one prompt loop).

### 3. `channels`

- **telegram**: The primary interface for HERMES SMB owners.
  - **token**: The business's unique bot token (created via BotFather).
  - **allowFrom**: Extremely important. This whitelist of Telegram user IDs ensures ONLY authorized business owners/managers can interact with their bot and database. Messages from other users are ignored natively.

### Note on MCP

- HERMES natively integrates all bookkeeping, receipt parsing, quotation rendering, and Udhaar tracking tools via local Python function bridging (Phase 11). **Therefore, no MCP (Model Context Protocol) block is required** in this config as external bridging isn't needed—everything operates synchronously on the deployment server against the local SQLite file.
