"""CSC versions store."""

from __future__ import annotations

from structlog.stdlib import BoundLogger

from ..domain.models import CSCInformation
from .cscv_commander import CSCVCommander
from .repo_mirror import RepoMirror
from .store import Store

__all__ = ["CSCVStore"]


class CSCVStore(Store):
    """CSCV storage handler."""

    def __init__(self, *, repo: RepoMirror, logger: BoundLogger) -> None:
        super().__init__(logger=logger)
        self._commander = CSCVCommander(repo=repo, logger=logger)

    async def get_repo_branches(self) -> list[str]:
        return await self._commander.repo.list_branches()

    async def get_csc_versions(
        self, branch: str
    ) -> tuple[list[str], list[CSCInformation]]:
        dv, cv = await self._commander.get_all_csc_versions(branch)
        return self._parser.parse_double_pass(desired=dv, current=cv)
