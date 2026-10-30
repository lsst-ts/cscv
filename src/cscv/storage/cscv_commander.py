"""The Commander for the CSC Version dashboard."""

from __future__ import annotations

import ast
import os
from concurrent.futures import TimeoutError as FuturesTimeoutError
from importlib.resources import files

import pandas as pd
from lsst_efd_client import EfdClient
from structlog.stdlib import BoundLogger

from .commander import Commander
from .repo_mirror import RepoMirror

__all__ = ["CSCVCommander"]


class CSCVCommander(Commander):
    """Handle calls to the cscv storage."""

    def __init__(self, *, repo: RepoMirror, logger: BoundLogger) -> None:
        super().__init__(logger=logger)
        self.repo = repo

    async def get_current_versions_async(self) -> list[dict[str, str]]:
        return await self._fetch_latest_versions()

    async def get_desired_versions_async(self, branch: str) -> str | None:
        """Get the desired versions from the cycle.env file."""
        response = None
        try:
            response = await self.repo.show_from_ref(branch)
        except Exception as e:
            self._logger.warning(f"Error while reading {branch}: {e}")
        return response

    async def get_all_csc_versions(
        self, branch: str
    ) -> tuple[str, list[dict[str, str]]]:
        """Get the desired and current CSC versions."""
        current_versions = []
        desired_versions = ""
        try:
            desired_versions = (
                await self.get_desired_versions_async(branch) or ""
            )
        except Exception as e:
            self._logger.exception(
                "Failed to fetch desired versions from cycle.env",
                error=str(e),
            )
        try:
            current_versions = await self.get_current_versions_async()
        except FuturesTimeoutError:
            self._logger.warning("Timeout while waiting for EFD data.")
        return desired_versions, current_versions

    async def _fetch_latest_versions(self) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []

        try:
            efd_instance = os.environ["ENV_EFD"]
            topic_file = f"{efd_instance}_topic_list.csv"
            topic_package = pd.read_csv(
                files("cscv.data").joinpath(topic_file)
            )
            client = EfdClient(f"{efd_instance}_efd")
        except Exception as e:
            self._logger.exception(
                "Error getting enviroment variables or reading topic file.",
                error=str(e),
            )
            return results
        else:
            for _, row in topic_package.iterrows():
                topic = row["topic"]
                package = row["package"]
                namespace = row["namespace"]
                index_list = ast.literal_eval(row["index"])
                for index in index_list:
                    index_int = int(index)
                    item = {
                        "topic": topic,
                        "package": package,
                        "namespace": namespace,
                        "index": index,
                        "current": "no data",
                        "desired": "no data",
                    }
                    try:
                        query_results = await client.select_top_n(
                            topic_name=topic,
                            fields=["cscVersion"],
                            num=1,
                            index=index_int,
                        )
                    except ValueError as e:
                        if "not in EFD schema" not in str(e):
                            raise
                        self._logger.warning(
                            "Topic not found in EFD schema.",
                            topic=topic,
                            index=index,
                        )
                    except Exception as e:
                        self._logger.exception(
                            f"Error fetching data for topic {topic}"
                            "at index {index}",
                            error=str(e),
                        )
                    else:
                        if not query_results.empty:
                            item["current"] = query_results.iloc[0, 0]
                    results.append(item)

            return results
