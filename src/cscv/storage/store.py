"""Abstract storage."""

from __future__ import annotations

from abc import ABC, abstractmethod

from structlog.stdlib import BoundLogger

from ..domain.models import CSCInformation
from .output_parser import OutputParser

__all__ = ["Store"]


class Store(ABC):
    """Abstract class for the storage."""

    def __init__(self, *, logger: BoundLogger) -> None:
        self._logger = logger
        self._parser = OutputParser(logger=logger)

    @abstractmethod
    def get_csc_versions(self) -> list[CSCInformation]: ...
