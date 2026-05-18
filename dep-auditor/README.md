# dep-auditor MCP Server

Package Security & License Auditor — an MCP server that checks package licenses, known vulnerabilities, and metadata across **npm**, **PyPI**, and **Cargo**.

Built for AI agents (Claude, Cursor, Windsurf, etc.) to autonomously audit dependencies.

## Tools

| Tool | Description | Price |
|------|-------------|-------|
| `check_package` | Get package license, version, description, maintainers | $0.01 |
| `audit_vulns` | Check for known CVEs via OSV.dev database | $0.02 |

## Usage with Claude Desktop

```json
{
  "mcpServers": {
    "dep-auditor": {
      "command": "python",
      "args": ["path/to/main.py"]
    }
  }
}
```

## Deployment

### Apify (recommended — generates revenue)

1. Push to GitHub
2. Import in [Apify Console](https://console.apify.com)
3. Apify hosts, scales, and distributes to 130K+ developers
4. Pricing auto-configured per `apify.json`: $0.01–$0.02 per call

### Manual

```bash
pip install -r requirements.txt
python main.py
```

## Monetization

Listed on Apify Store with pay-per-event pricing. 1000 checks/day = $10–$20/day passive.
