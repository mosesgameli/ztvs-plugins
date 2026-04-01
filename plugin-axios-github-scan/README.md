# ZTVS Plugin: Axios & GitHub Inventory Scan

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![ZTVS Plugin](https://img.shields.io/badge/ZTVS-Plugin-orange.svg)](https://github.com/mosesgameli/ztvs)

A comprehensive Python-based plugin for the **Zero Trust Vulnerability Scanner (ZTVS)**. This plugin audits GitHub organizations for supply-chain vulnerabilities and provides deployment visibility.

## 🔍 Checks Supported

### 1. `axios-github-inventory-audit`
Performs a deep audit of repositories in a GitHub organization to detect exposure to the **axios maintainer hijack** (CVE-2026-axios-rat).
- Identifies repositories using vulnerable axios versions (`1.14.1`, `0.30.4`).
- Detects the malicious `plain-crypto-js@4.2.1` payload in lockfiles.
- Correlates findings with recent CI activity to assess actual exposure risk.

### 2. `github-deployment-audit`
Monitors and inventories GitHub deployments across the organization.
- Categorizes deployments by environment (Production, Staging, etc.).
- Flags failed or errored deployment statuses for security review.
- Provides a summary of deployment frequency and activity.

## 🛠️ Configuration

The plugin requires the following environment variables to be set:

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub Personal Access Token with `repo`, `read:org`, and `actions:read` scopes. |
| `GITHUB_ORG` | The name of the GitHub organization to scan. |
| `DEPLOYMENT_LOOKBACK_HOURS` | (Optional) How many hours to look back for deployments. Defaults to `24`. |

## 🚀 Installation

This plugin is managed by the ZTVS engine. To install it manually:

1. Copy the plugin directory to your `zt` plugins folder:
   ```bash
   cp -r plugin-axios-github-scan ~/.zt/plugins/
   ```
2. Ensure `uv` is installed on your system.

## 🧪 Development

This plugin uses `uv` for dependency management.

```bash
# Install dependencies
uv sync

# Run standalone handshake test
uv run python -m src.plugin_axios_github_scan.main < handshake.json
```

## 📄 License
MIT
