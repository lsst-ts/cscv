"""The Commander for the Observatory Environment system."""

from __future__ import annotations

import requests
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
        file_contents = response.text
        return file_contents, file_contents
