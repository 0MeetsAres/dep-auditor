# dep-auditor

Package Security & License Auditor MCP Server.

Check package licenses, known vulnerabilities, and metadata across **npm**, **PyPI**, and **Cargo** ecosystems — all from your AI agent.

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
