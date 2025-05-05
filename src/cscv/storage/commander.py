"""Abstract commander class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from structlog.stdlib import BoundLogger

__all__ = ["Commander"]


class Commander(ABC):
    """Abstract class for handling manager commands."""

    def __init__(self, *, logger: BoundLogger) -> None:
        self._logger = logger

    @abstractmethod
    def get_all_csc_versions(self) -> tuple[str, str]: ...
