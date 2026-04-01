import asyncio
import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, List, Dict
from aiohttp import ClientSession

GITHUB_API = "https://api.github.com"
RATE_LIMIT_DELAY = 0.1


class GitHubScanner:
    def __init__(self, token: str, session: ClientSession, debug: bool = False):
        self.token = token
        self.session = session
        self.debug = debug
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.rate_limit_remaining = 5000

    async def _get(self, url: str, params: dict = None) -> Any:
        """Make authenticated GET request with rate limiting"""
        await asyncio.sleep(RATE_LIMIT_DELAY)

        async with self.session.get(url, headers=self.headers, params=params) as resp:
            self.rate_limit_remaining = int(
                resp.headers.get("X-RateLimit-Remaining", 0)
            )

            if resp.status == 403 and "rate limit" in (await resp.text()).lower():
                await asyncio.sleep(60)
                return await self._get(url, params)

            resp.raise_for_status()
            return await resp.json()

    async def _head(self, url: str, params: dict = None) -> int:
        """Lightweight HEAD request to check file existence"""
        await asyncio.sleep(RATE_LIMIT_DELAY)
        async with self.session.head(url, headers=self.headers, params=params) as resp:
            return resp.status

    async def list_org_repos(self, org: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List all repositories in an organization"""
        repos = []
        page = 1

        while len(repos) < limit:
            url = f"{GITHUB_API}/orgs/{org}/repos"
            params = {
                "type": "all",
                "sort": "updated",
                "direction": "desc",
                "per_page": min(100, limit - len(repos)),
                "page": page,
            }

            data = await self._get(url, params)
            if not data:
                break

            for repo in data:
                if repo.get("fork") or repo.get("archived"):
                    continue
                repos.append(repo)

            if len(data) < params["per_page"]:
                break
            page += 1

        return repos

    async def fetch_file(
        self, repo: str, path: str, ref: str = "HEAD"
    ) -> Optional[Any]:
        """Fetch file content from repo"""
        url = f"{GITHUB_API}/repos/{repo}/contents/{path}"
        params = {"ref": ref}

        try:
            data = await self._get(url, params)
            if "content" in data and data.get("encoding") == "base64":
                content = base64.b64decode(data["content"]).decode("utf-8")
                return json.loads(content) if path.endswith(".json") else content
        except:
            pass
        return None

    async def get_recent_workflow_runs(
        self, repo: str, hours: int = 24
    ) -> tuple[int, Optional[str]]:
        """Get count of workflow runs in last N hours"""
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        url = f"{GITHUB_API}/repos/{repo}/actions/runs"

        EXECUTED_STATUSES = {"completed", "in_progress"}
        executed_runs = []

        try:
            data = await self._get(url, {"created": f">{since}", "per_page": 100})
            runs = data.get("workflow_runs", [])
            for run in runs:
                if run.get("status") in EXECUTED_STATUSES:
                    executed_runs.append(run)

            count = len(executed_runs)
            latest = executed_runs[0]["updated_at"] if executed_runs else None
            return count, latest
        except:
            return 0, None

    async def get_deployments(self, repo: str, since: datetime) -> List[Dict[str, Any]]:
        """Get deployments for a repo since a cutoff time"""
        deployments = []
        url = f"{GITHUB_API}/repos/{repo}/deployments"

        try:
            data = await self._get(url, {"per_page": 100})
            for dep in data:
                created_at = datetime.fromisoformat(
                    dep["created_at"].replace("Z", "+00:00")
                )
                if created_at >= since:
                    deployments.append(dep)
            return deployments
        except:
            return []

    async def get_deployment_status(
        self, repo: str, deployment_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get latest status for a deployment"""
        url = f"{GITHUB_API}/repos/{repo}/deployments/{deployment_id}/statuses"
        try:
            data = await self._get(url, {"per_page": 1})
            return data[0] if data else None
        except:
            return None
