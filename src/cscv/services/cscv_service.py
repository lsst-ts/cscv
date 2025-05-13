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

    async def get_csc_versions(self) -> list[CSCInformation]:
        self._logger.info("Retrive CSC versions from store.")
        return await self._cscv_store.get_csc_versions()
