import re
import os
import sys
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
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

VULNERABLE_AXIOS_VERSIONS = {"1.14.1", "0.30.4"}
MALICIOUS_DEP_NAME = "plain-crypto-js"
MALICIOUS_DEP_VERSION = "4.2.1"


class AxiosAuditCheck:
    def id(self) -> str:
        return "axios-github-inventory-audit"

    def name(self) -> str:
        return "Axios GitHub Inventory Audit"

    async def run(self) -> Optional[Finding]:
        token = os.getenv("GITHUB_TOKEN")
        org = os.getenv("GITHUB_ORG")

        if not token or not org:
            return None

        log("INFO", f"Starting axios vulnerability audit for organization '{org}'...")
        async with ClientSession() as session:
            scanner = GitHubScanner(token, session)
            repos = await scanner.list_org_repos(org, limit=100)
            log("INFO", f"Found {len(repos)} candidate repositories to scan.")

            results = []
            for i, repo in enumerate(repos, 1):
                log("DEBUG", f"[{i}/{len(repos)}] Scanning {repo['full_name']}...")
                risk = await self.scan_repo(scanner, repo["full_name"])
                if risk["risk_level"] in ["HIGH", "CRITICAL"]:
                    log("ALERT", f"VULN FOUND: {repo['full_name']} -> {risk['risk_level']}")
                    results.append(risk)

            if results:
                log("WARN", f"Audit complete: {len(results)} vulnerable repositories identified.")
                return Finding(
                    id="axios-vuln-inventory",
                    severity="critical"
                    if any(r["risk_level"] == "CRITICAL" for r in results)
                    else "high",
                    title=f"Axios Vulnerability Exposure Detected in {len(results)} Repos",
                    description=f"Audited GitHub organization '{org}' and found repositories at risk of axios supply-chain attack.",
                    evidence={"vulnerable_repos": results},
                    remediation="Refer to the 'recommendation' field in each vulnerable repo entry for remediation steps.",
                )

            return None

    async def scan_repo(self, scanner: GitHubScanner, repo: str) -> Dict[str, Any]:
        risk = {
            "repo": repo,
            "has_axios": False,
            "axios_spec": None,
            "axios_locked_version": None,
            "could_resolve_to_vuln": False,
            "actually_has_vuln_version": False,
            "has_malicious_dep": False,
            "recent_workflow_runs": 0,
            "risk_level": "NONE",
            "recommendation": "",
        }

        # Details & workflows
        runs, _ = await scanner.get_recent_workflow_runs(repo)
        risk["recent_workflow_runs"] = runs

        # package.json
        pkg_json = await scanner.fetch_file(repo, "package.json")
        if not pkg_json:
            return self.calculate_risk(risk)

        deps = {
            **pkg_json.get("dependencies", {}),
            **pkg_json.get("devDependencies", {}),
        }
        axios_spec = deps.get("axios")
        if not axios_spec:
            return self.calculate_risk(risk)

        risk["has_axios"] = True
        risk["axios_spec"] = axios_spec

        c1, c2 = self.parse_semver_range(axios_spec)
        risk["could_resolve_to_vuln"] = c1 or c2

        # lockfile
        lockfile = await scanner.fetch_file(repo, "package-lock.json")
        if lockfile:
            locked_version = self.extract_axios_from_lockfile(lockfile)
            risk["axios_locked_version"] = locked_version
            if locked_version in VULNERABLE_AXIOS_VERSIONS:
                risk["actually_has_vuln_version"] = True

            if self.extract_malicious_dep(lockfile):
                risk["has_malicious_dep"] = True

        return self.calculate_risk(risk)

    def parse_semver_range(self, spec: str) -> Tuple[bool, bool]:
        if not spec:
            return False, False
        spec_clean = spec.strip()
        version_match = re.match(r"^[\^~>=<]*\s*v?(\d+\.\d+\.\d+)", spec_clean)
        if not version_match:
            return (
                (True, True)
                if "*" in spec_clean or spec_clean in ["latest", ""]
                else (False, False)
            )

        base_version = version_match.group(1)
        parts = [int(p) for p in base_version.split(".")]
        major, minor, patch = parts[0], parts[1], parts[2]

        if re.match(r"^=?v?\d+\.\d+\.\d+$", spec_clean):
            is_vuln = base_version in VULNERABLE_AXIOS_VERSIONS
            return is_vuln, is_vuln

        if spec_clean.startswith("^") or not any(
            spec_clean.startswith(p) for p in ["~", ">", "<", "="]
        ):
            if major == 1:
                return (major, minor, patch) <= (1, 14, 1), False
            elif major == 0:
                return False, minor == 30 and patch <= 4

        if spec_clean.startswith("~"):
            is_vuln = base_version in VULNERABLE_AXIOS_VERSIONS
            return is_vuln, is_vuln

        return False, False

    def extract_axios_from_lockfile(self, lock_data: Dict[str, Any]) -> Optional[str]:
        packages = lock_data.get("packages", {})
        for key, pkg in packages.items():
            if key == "node_modules/axios" or pkg.get("name") == "axios":
                return pkg.get("version", "").lstrip("v")
        return None

    def extract_malicious_dep(self, lock_data: Dict[str, Any]) -> bool:
        packages = lock_data.get("packages", {})
        for pkg in packages.values():
            if pkg.get("name") == MALICIOUS_DEP_NAME:
                if pkg.get("version", "").lstrip("v") == MALICIOUS_DEP_VERSION:
                    return True
        return False

    def calculate_risk(self, risk: Dict[str, Any]) -> Dict[str, Any]:
        if not risk["has_axios"]:
            risk["risk_level"] = "NONE"
            return risk

        if risk["actually_has_vuln_version"] or risk["has_malicious_dep"]:
            risk["risk_level"] = "CRITICAL"
            risk["recommendation"] = (
                "🚨 CRITICAL: Vulnerable axios pinned or malicious dependency found. 1) DO NOT run npm install. 2) Pin axios to 1.14.0 or 0.30.3. 3) Reinstall with --ignore-scripts. 4) Rotate credentials."
            )
            return risk

        if risk["could_resolve_to_vuln"] and risk["recent_workflow_runs"] > 0:
            risk["risk_level"] = "HIGH"
            risk["recommendation"] = (
                f"⚠️ HIGH: axios spec '{risk['axios_spec']}' could result in compromise given recent CI activity."
            )
            return risk

        if risk["could_resolve_to_vuln"]:
            risk["risk_level"] = "MEDIUM"
            risk["recommendation"] = (
                f"⚠️ MEDIUM: spec '{risk['axios_spec']}' allows vulnerable versions. Pin to safe version."
            )
            return risk

        risk["risk_level"] = "LOW"
        return risk
