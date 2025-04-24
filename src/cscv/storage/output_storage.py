"""Handle parsing output from cscv CLI tool."""

from __future__ import annotations

import os

from structlog.stdlib import BoundLogger

from ..domain.models import CSCInformation

__all__ = ["OutputParser"]


class OutputParser:
    """Handle parsing output from cscv CLI tool."""

    def __init__(self, *, logger: BoundLogger) -> None:
        self._logger = logger

    def parse_double_pass(
        self, original: str, current: str
    ) -> list[CSCInformation]:
        csc_list = []
        for line in original.strip().split(os.linesep)[2:]:
            name_set, required_version = line.strip().split()[-2:]
            name = name_set.rstrip(":")
            csc_list.append(
                CSCInformation(
                    name=name,
                    required_version=required_version,
                    current_version="",
                )
            )

        for line in current.strip().split(os.linesep)[2:]:
            name_set, current_version = line.strip().split()[-2:]
            name = name_set.rstrip(":")
            item = next((i for i in csc_list if i.name == name), None)
            if item is not None:
                item.current_version = current_version

        return csc_list
