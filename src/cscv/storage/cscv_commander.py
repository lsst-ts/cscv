"""The Commander for the CSC Version dashboard."""

from __future__ import annotations

import os
from concurrent.futures import TimeoutError as FuturesTimeoutError
from importlib.resources import files

import httpx
from lsst_efd_client import EfdClient
from structlog.stdlib import BoundLogger

from .commander import Commander

__all__ = ["CSCVCommander"]


class CSCVCommander(Commander):
    """Handle calls to the cscv storage."""

    def __init__(self, *, logger: BoundLogger) -> None:
        super().__init__(logger=logger)

    async def get_current_versions_async(
        self, topic_list: list[str]
    ) -> dict[str, str]:
        return await self._fetch_latest_versions(topic_list)

    async def get_desired_versions_async(self) -> str:
        """Get the desired versions from the cycle.env file.

        Tries the branch from CYCLE_BRANCH first, falls back to 'main'.
        """
        base_url = "https://raw.githubusercontent.com/lsst-ts/ts_cycle_build/refs/heads/"
        cycle_branch = os.environ["CYCLE_BRANCH"]
        branches_to_try = [cycle_branch, "main"]

        async with httpx.AsyncClient() as client:
            for branch in branches_to_try:
                url = f"{base_url}{branch}/cycle/cycle.env"
                try:
                    response = await client.get(url, timeout=15)
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        self._logger.warning(
                            f"cycle.env not found for branch '{branch}',"
                            " trying next fallback.",
                            error=str(e),
                        )
                        continue  # Try main branch
                    raise
                else:
                    return response.text
            # If neither branch worked
            raise RuntimeError("Unable to fetch cycle.env from any branch.")

    async def get_all_csc_versions(self) -> tuple[str, dict[str, str]]:
        """Get the desired and current CSC versions."""
        try:
            desired_versions = await self.get_desired_versions_async()
        except httpx.HTTPError as e:
            self._logger.exception(
                "Failed to fetch desired versions from cycle.env",
                error=str(e),
            )
        topic_list = (
            files("cscv.data")
            .joinpath("topic_list.txt")
            .read_text()
            .splitlines()
        )
        try:
            current_versions = await self.get_current_versions_async(
                topic_list
            )
        except FuturesTimeoutError:
            self._logger.warning("Timeout while waiting for EFD data.")
            current_versions = {}

        return desired_versions, current_versions

    async def _fetch_latest_versions(self, topics: list[str]) -> dict:
        efd_instance = os.environ["ENV_EFD"]
        client = EfdClient(efd_instance)
        results = {}

        for topic in topics:
            try:
                query_results = await client.select_top_n(
                    topic_name=topic, fields=["cscVersion"], num=1
                )
                if not query_results.empty:
                    value = query_results.iloc[0, 0]  # First row, first column
                    results[topic] = str(value)
                else:
                    results[topic] = "no data"
            except Exception as e:
                results[topic] = f"Error: {e!s}"
        return results
