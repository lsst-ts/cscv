"""CSC Versions Service."""

from __future__ import annotations

from structlog.stdlib import BoundLogger

from ..domain.models import CSCInformation
from ..storage.store import Store

__all__ = ["CSCVService"]


class CSCVService:
    """A service for managing cscv.

    Parameters
    ----------
    logger
        The structlog logger.
    """

    def __init__(self, logger: BoundLogger, cscv_store: Store) -> None:
        self._logger = logger
        self._cscv_store = cscv_store

    async def get_repo_branches(self) -> list[str]:
        self._logger.info("Retrive branches from ts_cycle_build repo.")
        return await self._cscv_store.get_repo_branches()

    async def get_csc_versions(self, branch: str) -> list[CSCInformation]:
        self._logger.info("Retrive CSC versions from store.")
        return await self._cscv_store.get_csc_versions(branch)
