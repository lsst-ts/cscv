"""Handle parsing output from cscv CLI tool."""

from __future__ import annotations

from structlog.stdlib import BoundLogger

from ..domain.models import CSCInformation

__all__ = ["OutputParser"]


class OutputParser:
    """Handle parsing output from cscv CLI tool."""

    def __init__(self, *, logger: BoundLogger) -> None:
        self._logger = logger

    def parse_double_pass(
        self, desired: str, current: list[dict[str, str]]
    ) -> list[CSCInformation]:
        """Parse desired/current key=value strings into CSCInformation."""
        results = []
        desired_versions = {}

        for line in desired.strip().splitlines():
            line_clean = line.strip()
            if not line_clean or line_clean.startswith("#"):
                continue
            if "=" in line_clean:
                key, value = line_clean.split("=", maxsplit=1)
                key = key.strip()
                value = value.strip()
                desired_versions[key] = value

        for item in current:
            package = item["package"]
            if package in desired_versions:
                item["desired"] = desired_versions[package]

            csc = CSCInformation(
                name=item["topic"].split(".")[2],
                namespace=item["namespace"],
                index=item["index"],
                desired_version=item["desired"],
                current_version=item["current"],
            )
            results.append(csc)

        return results
