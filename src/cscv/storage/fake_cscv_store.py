"""Fake CSCV Store."""

from __future__ import annotations

from structlog.stdlib import BoundLogger

from ..domain.models import CSCInformation
from .fake_commander import FakeCommander
from .store import Store

__all__ = ["FakeCSCVStore"]


class FakeCSCVStore(Store):
    """Handle creating information from fake data."""

    def __init__(self, logger: BoundLogger) -> None:
        super().__init__(logger=logger)
        self._commander = FakeCommander(logger=logger)

    def get_csc_versions(self) -> list[CSCInformation]:
        fake_rv, fake_cv = self._commander.get_all_csc_versions()
        return self._parser.parse_double_pass(
            original=fake_rv, current=fake_cv
        )
