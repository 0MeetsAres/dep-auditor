# dep-auditor

[![MCPize](https://mcpize.com/badge/@directlytoomar/dep-auditor)](https://mcpize.com/mcp/dep-auditor)

Package Security & License Auditor MCP Server.

Check package licenses, known vulnerabilities, and metadata across **npm**, **PyPI**, and **Cargo** ecosystems — all from your AI agent.

## Connect via MCPize

Use this MCP server instantly with no local installation:

```bash
npx -y mcpize connect @directlytoomar/dep-auditor --client claude
```

Or connect at: **https://mcpize.com/mcp/dep-auditor**

## Tools

- `check_package` — License, version, description, maintainers
- `audit_vulns` — Known CVEs via OSV.dev database

## Quick Start

```json
{
  "mcpServers": {
    "dep-auditor": {
      "command": "python",
      "args": ["path/to/dep-auditor/main.py"]
    }
  }
}
```

See [dep-auditor/README.md](dep-auditor/README.md) for full documentation.