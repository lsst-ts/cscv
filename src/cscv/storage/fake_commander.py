"""Fake commander."""

from __future__ import annotations

from importlib.resources import files

from structlog.stdlib import BoundLogger

from .commander import Commander

__all__ = ["FakeCommander"]


class FakeCommander(Commander):
    """Handle calls to the fake storage."""

    def __init__(self, *, logger: BoundLogger) -> None:
        super().__init__(logger=logger)

    def get_all_csc_versions(self) -> tuple[str, str]:
        dv = files("cscv.data").joinpath("cycle_rev.env").read_text()
        cv = files("cscv.data").joinpath("cycle.env").read_text()
        return dv, cv
