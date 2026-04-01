import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from ztvs_sdk import Finding
from aiohttp import ClientSession
from ..scanner import GitHubScanner

class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"

def log(level: str, message: str):
    """Colored logging to stderr with timestamp"""
    colors = {
        "INFO": Colors.BLUE,
        "WARN": Colors.YELLOW,
        "ALERT": Colors.RED,
        "OK": Colors.GREEN,
        "DEBUG": Colors.CYAN,
    }
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sys.stderr.write(f"{colors.get(level, Colors.RESET)}[{ts}] [{level}] {message}{Colors.RESET}\n")


class DeploymentAuditCheck:
    def id(self) -> str:
        return "github-deployment-audit"

    def name(self) -> str:
        return "GitHub Deployment Audit"

    async def run(self) -> Optional[Finding]:
        token = os.getenv("GITHUB_TOKEN")
        org = os.getenv("GITHUB_ORG")
        hours = int(os.getenv("DEPLOYMENT_LOOKBACK_HOURS", "24"))

        if not token or not org:
            return None

        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        log("INFO", f"Starting GitHub deployment audit for organization '{org}' (last {hours}h)...")
        async with ClientSession() as session:
            scanner = GitHubScanner(token, session)
            repos = await scanner.list_org_repos(org, limit=100)
            log("INFO", f"Found {len(repos)} candidate repositories to scan.")

            results = []
            for i, repo in enumerate(repos, 1):
                log("DEBUG", f"[{i}/{len(repos)}] Scanning deployments for {repo['full_name']}...")
                summary = await self.scan_repo_deployments(
                    scanner, repo["full_name"], since
                )
                if summary["total_deployments"] > 0:
                    log("OK", f"Deployments found in {repo['full_name']}: {summary['total_deployments']}")
                    results.append(summary)

            if results:
                log("INFO", f"Audit complete: {len(results)} repositories with recent activity.")
                failed_repos = [r for r in results if r["has_failed_deployments"]]
                production_repos = [
                    r for r in results if r["has_production_deployments"]
                ]

                severity = "medium"
                if failed_repos:
                    severity = "high"

                title = f"GitHub Deployments Detected in {len(results)} Repos"
                description = f"Audited GitHub organization '{org}' for deployments in the last {hours} hours."

                return Finding(
                    id="github-deployment-inventory",
                    severity=severity,
                    title=title,
                    description=description,
                    evidence={
                        "total_repos_with_deployments": len(results),
                        "production_repos": [r["repo"] for r in production_repos],
                        "failed_repos": [r["repo"] for r in failed_repos],
                        "details": results,
                    },
                    remediation="Audit failed deployments and verify production changes for security compliance.",
                )

            return None

    async def scan_repo_deployments(
        self, scanner: GitHubScanner, repo: str, since: datetime
    ) -> Dict[str, Any]:
        deployments_data = await scanner.get_deployments(repo, since)
        total_deployments = len(deployments_data)

        if not deployments_data:
            return {"repo": repo, "total_deployments": 0}

        environments = set()
        has_production = False
        has_failed = False
        deployments = []

        for dep in deployments_data:
            status = await scanner.get_deployment_status(repo, dep["id"])
            status_state = status.get("state", "unknown") if status else "unknown"

            environments.add(dep.get("environment", "unknown"))
            if dep.get("production_environment", False):
                has_production = True
            if status_state in ("failure", "error", "cancelled"):
                has_failed = True

            deployments.append(
                {
                    "id": dep["id"],
                    "environment": dep.get("environment"),
                    "status": status_state,
                    "creator": dep.get("creator", {}).get("login"),
                    "created_at": dep.get("created_at"),
                    "production": dep.get("production_environment", False),
                }
            )

        return {
            "repo": repo,
            "total_deployments": total_deployments,
            "environments": sorted(list(environments)),
            "has_production_deployments": has_production,
            "has_failed_deployments": has_failed,
            "deployments": deployments,
        }
