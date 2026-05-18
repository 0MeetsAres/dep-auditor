# dep-auditor MCP Server

Package Security & License Auditor — an MCP server that checks package licenses, known vulnerabilities, and metadata across **npm**, **PyPI**, and **Cargo**.

Built for AI agents (Claude, Cursor, Windsurf, etc.) to autonomously audit dependencies during development.

## Tools

| Tool | Description |
|------|-------------|
| `check_package` | Get license, latest version, description, maintainers, deprecation status |
| `audit_vulns` | Check for known CVEs via the OSV.dev open vulnerability database |

### check_package

Fetches package metadata from the ecosystem's public registry.

**Input:**
- `ecosystem` (string): `npm`, `pypi`, or `cargo`
- `package` (string): Package name (e.g. `express`, `requests`, `serde`)

**Output example:**
```json
{
  "name": "express",
  "ecosystem": "npm",
  "latest_version": "5.2.1",
  "license": "MIT",
  "description": "Fast, unopinionated, minimalist web framework",
  "homepage": "https://expressjs.com",
  "repository": "https://github.com/expressjs/express",
  "keywords": ["web", "framework", "http"],
  "maintainers": ["dougwilson", "wesleytodd"],
  "deprecated": false
}
```

### audit_vulns

Queries the OSV.dev open source vulnerability database for known security advisories.

**Input:**
- `ecosystem` (string): `npm`, `pypi`, or `cargo`
- `package` (string): Package name

**Output example:**
```json
{
  "package": "lodash",
  "ecosystem": "npm",
  "vulnerability_count": 10,
  "vulnerabilities": [
    {
      "id": "GHSA-29mw-wpgm-hmr9",
      "summary": "Prototype Pollution in lodash",
      "aliases": ["CVE-2020-28503"],
      "published": "2021-01-29T19:54:51Z"
    }
  ]
}
```

## Use Cases

- **License compliance** — Verify all dependencies use permissive licenses before shipping
- **Security auditing** — Check for known CVEs in your supply chain
- **Dependency evaluation** — Assess a package's maintenance status and deprecation state
- **CI/CD integration** — Automate auditing as part of your build pipeline

## Configuration

No API keys required. All data is fetched from public registries:
- [npm registry](https://registry.npmjs.org)
- [PyPI JSON API](https://pypi.org/pypi)
- [crates.io API](https://crates.io/api/v1/crates)
- [OSV.dev](https://api.osv.dev/v1)

## Supported Ecosystems

| Ecosystem | Registry | Package Manager |
|-----------|----------|-----------------|
| **npm** | registry.npmjs.org | npm, yarn, pnpm |
| **PyPI** | pypi.org | pip, poetry, uv |
| **Cargo** | crates.io | cargo |

## Usage with MCP Clients

### Claude Desktop
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

### Cursor / Windsurf
Add the same configuration to your IDE's MCP settings file.

## Local Development

```bash
pip install -r requirements.txt
python main.py
```

The server will start on stdio and be available for MCP client connections.
