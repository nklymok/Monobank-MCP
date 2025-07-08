# Monobank MCP Server

Monobank MCP Server exposes your Monobank personal account as Model Context Protocol (MCP) tools.

## Features

- Lightweight Python 3 server.
- Two ready-to-use MCP tools:
  - `get_client_info` – returns client, accounts and jars metadata.
  - `get_statement` – returns account statement for a given period (≤ 31 days).

## Quick Start

1. **Install dependencies**
   ```bash
   uv pip install -r pyproject.toml # or use your preferred tool
   ```
2. **Create `.env`** (in the project root) containing your Monobank token:
   ```dotenv
   MONOBANK_API_TOKEN=<your_personal_token>
   ```
3. **Register the server in your MCP configuration**
   ```json
   {
     "mcpServers": {
       "monobank-mcp": {
         "command": "python3.11 /path/to/monobank-mcp/main.py"
       }
     }
   }
   ```
4. **Run your MCP client** – the two tools will be available immediately.

## Tool Reference

| Tool              | Description                                                                                                                       | Rate limits      |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| `get_client_info` | Fetches client profile, list of accounts and jars.                                                                                | 1 request / 60 s |
| `get_statement`   | Retrieves transaction list for a specific account and time range.<br/>Parameters: `account_id`, `from_timestamp`, `to_timestamp`. | 1 request / 60 s |

## Environment Variables

| Name                 | Required | Description                       |
| -------------------- | -------- | --------------------------------- |
| `MONOBANK_API_TOKEN` | ✅       | Your personal Monobank API token. |

## License

MIT
