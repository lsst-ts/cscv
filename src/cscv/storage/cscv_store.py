"""CSC versions store."""

from __future__ import annotations

from structlog.stdlib import BoundLogger

from ..domain.models import CSCInformation
from .cscv_commander import CSCVCommander
from .store import Store

__all__ = ["CSCVStore"]


class CSCVStore(Store):
    """CSCV storage handler."""

    def __init__(self, *, logger: BoundLogger) -> None:
        super().__init__(logger=logger)
        self._commander = CSCVCommander(logger=logger)

    async def get_csc_versions(self) -> list[CSCInformation]:
        dv, cv = await self._commander.get_all_csc_versions()
        return self._parser.parse_double_pass(desired=dv, current=cv)
