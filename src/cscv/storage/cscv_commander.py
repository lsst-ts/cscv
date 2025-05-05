"""The Commander for the Observatory Environment system."""

from __future__ import annotations

import asyncio
from concurrent.futures import TimeoutError as FuturesTimeoutError
from importlib.resources import files

import requests
from lsst_efd_client import EfdClient
from structlog.stdlib import BoundLogger

from .commander import Commander

__all__ = ["CSCVCommander"]


class CSCVCommander(Commander):
    """Handle calls to the cscv storage."""

    def __init__(self, *, logger: BoundLogger) -> None:
        super().__init__(logger=logger)

    def get_all_csc_versions(self) -> tuple[str, str]:
        url = "https://raw.githubusercontent.com/lsst-ts/ts_cycle_build/refs/heads/tickets/DM-50303/cycle/cycle.env"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        desired_versions = response.text

        topic_list = (
            files("cscv.data")
            .joinpath("topic_list.txt")
            .read_text()
            .splitlines()
        )
        current_versions = {}

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Schedule the coroutine to run in the background loop
            future = asyncio.run_coroutine_threadsafe(
                self._fetch_latest_versions(topic_list), loop
            )
            try:
                current_versions = future.result(timeout=10)
            except FuturesTimeoutError:
                self._logger.warning("Timeout while waiting for EFD data.")

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
