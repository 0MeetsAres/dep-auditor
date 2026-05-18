"""
dep-auditor: Package Security & License Auditor MCP Server

Exposes MCP tools for checking package licenses, known vulnerabilities,
and metadata across npm, PyPI, and Cargo ecosystems.

Tools:
  - check_package    : Get license, version, metadata for a package
  - audit_vulns      : Check for known vulnerabilities via OSV.dev API
  - compare_versions : Compare version specs across ecosystems
"""

import json
import httpx
from typing import Any
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

server = Server("dep-auditor")

# --- Utility ---

NPM_API = "https://registry.npmjs.org"
PYPI_API = "https://pypi.org/pypi"
CARGO_API = "https://crates.io/api/v1/crates"
OSV_API = "https://api.osv.dev/v1"

ECOSYSTEM_MAP = {
    "npm": NPM_API,
    "pypi": PYPI_API,
    "cargo": CARGO_API,
}


async def fetch_json(url: str, headers: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()


async def fetch_npm(pkg: str) -> dict:
    data = await fetch_json(f"{NPM_API}/{pkg}")
    latest = data.get("dist-tags", {}).get("latest", "unknown")
    versions = data.get("versions", {})
    pkg_data = versions.get(latest, {})
    return {
        "name": pkg,
        "ecosystem": "npm",
        "latest_version": latest,
        "license": pkg_data.get("license", "unknown"),
        "description": (data.get("description") or ""),
        "homepage": pkg_data.get("homepage") or "",
        "repository": pkg_data.get("repository", {}).get("url", "") if isinstance(pkg_data.get("repository"), dict) else "",
        "keywords": data.get("keywords", []),
        "maintainers": [
            m.get("name") for m in (pkg_data.get("maintainers") or [])
        ],
        "deprecated": pkg_data.get("deprecated") or False,
    }


async def fetch_pypi(pkg: str) -> dict:
    data = await fetch_json(f"{PYPI_API}/{pkg}/json")
    info = data.get("info", {})
    return {
        "name": pkg,
        "ecosystem": "pypi",
        "latest_version": info.get("version", "unknown"),
        "license": info.get("license") or info.get("classifiers", []),
        "description": (info.get("summary") or ""),
        "homepage": info.get("home_page") or "",
        "repository": info.get("project_urls", {}).get("Source", ""),
        "keywords": info.get("keywords", "").split(",") if info.get("keywords") else [],
        "author": info.get("author") or "",
        "requires_python": info.get("requires_python") or "",
        "deprecated": False,
    }


async def fetch_cargo(pkg: str) -> dict:
    data = await fetch_json(f"{CARGO_API}/{pkg}", headers={"User-Agent": "dep-auditor-mcp/1.0"})
    crate = data.get("crate", {})
    return {
        "name": pkg,
        "ecosystem": "cargo",
        "latest_version": crate.get("max_version", "unknown"),
        "license": crate.get("license") or "unknown",
        "description": (crate.get("description") or ""),
        "homepage": crate.get("homepage") or "",
        "repository": crate.get("repository") or "",
        "keywords": crate.get("keywords", []),
        "downloads": crate.get("downloads", 0),
        "deprecated": crate.get("links", {}).get("deprecated") is not None,
    }


FETCHERS = {
    "npm": fetch_npm,
    "pypi": fetch_pypi,
    "cargo": fetch_cargo,
}


async def query_osv(ecosystem: str, pkg: str) -> list[dict]:
    """Query the OSV.dev API for known vulnerabilities."""
    osv_eco = {"npm": "npm", "pypi": "PyPI", "cargo": "crates.io"}.get(ecosystem, ecosystem)
    payload = {"package": {"name": pkg, "ecosystem": osv_eco}}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{OSV_API}/query", json=payload)
        if resp.status_code != 200:
            return []
        data = resp.json()
        return data.get("vulns", [])


def _normalize_license(license_data: Any) -> str:
    if isinstance(license_data, list):
        # PyPi classifiers: look for one containing "License"
        for c in license_data:
            if isinstance(c, str) and "License" in c:
                return c.split(" :: ")[-1]
        return "unknown"
    return str(license_data) if license_data else "unknown"


# --- MCP Tool Definitions ---

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="check_package",
            description="Get package metadata: license, latest version, description, maintainer info. Supports npm, pypi, cargo.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ecosystem": {
                        "type": "string",
                        "enum": ["npm", "pypi", "cargo"],
                        "description": "Package ecosystem",
                    },
                    "package": {
                        "type": "string",
                        "description": "Package name (e.g. express, requests, serde)",
                    },
                },
                "required": ["ecosystem", "package"],
            },
        ),
        Tool(
            name="audit_vulns",
            description="Check a package for known security vulnerabilities using OSV.dev database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ecosystem": {
                        "type": "string",
                        "enum": ["npm", "pypi", "cargo"],
                        "description": "Package ecosystem",
                    },
                    "package": {
                        "type": "string",
                        "description": "Package name",
                    },
                },
                "required": ["ecosystem", "package"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    ecosystem = arguments.get("ecosystem", "").lower()
    package = arguments.get("package", "").strip()

    if ecosystem not in FETCHERS:
        return [TextContent(type="text", text=f"Unsupported ecosystem: {ecosystem}. Use: npm, pypi, cargo")]

    if not package:
        return [TextContent(type="text", text="Package name is required.")]

    if name == "check_package":
        try:
            data = await FETCHERS[ecosystem](package)
            data["license"] = _normalize_license(data["license"])
            result = json.dumps(data, indent=2)
            return [TextContent(type="text", text=result)]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return [TextContent(type="text", text=f"Package '{package}' not found in {ecosystem}.")]
            return [TextContent(type="text", text=f"Error querying {ecosystem}: {e}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Unexpected error: {e}")]

    elif name == "audit_vulns":
        try:
            vulns = await query_osv(ecosystem, package)
            if not vulns:
                return [TextContent(type="text", text=f"No known vulnerabilities found for {package} on {ecosystem}.")]
            summary = []
            for v in vulns:
                summary.append({
                    "id": v.get("id", "N/A"),
                    "summary": v.get("summary", "") or (v.get("details", "") or "")[:200],
                    "aliases": v.get("aliases", []),
                    "severity": v.get("severity", []),
                    "published": v.get("published", ""),
                })
            result = json.dumps({"package": package, "ecosystem": ecosystem, "vulnerability_count": len(summary), "vulnerabilities": summary}, indent=2)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error querying vulnerabilities: {e}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# --- Entrypoint ---

async def main():
    async with server.run() as running:
        await running.wait_closed()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
