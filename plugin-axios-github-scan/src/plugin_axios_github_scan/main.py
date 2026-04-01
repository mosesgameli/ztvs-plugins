import asyncio
from ztvs_sdk import Metadata, run
from plugin_axios_github_scan.checks.axios import AxiosAuditCheck
from plugin_axios_github_scan.checks.deployments import DeploymentAuditCheck

async def main():
    meta = Metadata(
        name="plugin-axios-github-scan",
        version="1.0.0",
        api_version=1
    )

    checks = [
        AxiosAuditCheck(),
        DeploymentAuditCheck()
    ]

    await run(meta, checks)

if __name__ == "__main__":
    asyncio.run(main())
