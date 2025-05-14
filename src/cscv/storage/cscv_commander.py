"""The Commander for the Observatory Environment system."""

from __future__ import annotations

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

    async def get_versions_async(
        self, topic_list: list[str]
    ) -> dict[str, str]:
        return await self._fetch_latest_versions(topic_list)

    async def get_all_csc_versions(self) -> tuple[str, dict[str, str]]:
        url = "https://raw.githubusercontent.com/lsst-ts/ts_cycle_build/refs/heads/tickets/DM-50726/cycle/cycle.env"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=15)
        response.raise_for_status()
        desired_versions = response.text

        topic_list = (
            files("cscv.data")
            .joinpath("topic_list.txt")
            .read_text()
            .splitlines()
        )
        try:
            current_versions = await self.get_versions_async(topic_list)
        except FuturesTimeoutError:
            self._logger.warning("Timeout while waiting for EFD data.")
            current_versions = {}

        return desired_versions, current_versions

    async def _fetch_latest_versions(self, topics: list[str]) -> dict:
        client = EfdClient("usdf_efd")
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
                    results[topic] = "No data"
            except Exception as e:
                results[topic] = f"Error: {e!s}"
        return results
