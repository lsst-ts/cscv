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
        self, desired: str, current: str
    ) -> list[CSCInformation]:
        """Parse desired/current key=value strings into CSCInformation."""

        def parse_version_block(text: str) -> dict[str, str]:
            result = {}
            for line in text.strip().splitlines():
                line_clean = line.strip()
                if not line_clean or line_clean.startswith("#"):
                    continue
                if "=" in line_clean:
                    key, value = line_clean.split("=", maxsplit=1)
                    result[key.strip()] = value.strip()
            return result

        desired_map = parse_version_block(desired)
        current_map = parse_version_block(current)

        csc_list = []
        for name, desired_version in desired_map.items():
            current_version = current_map.get(name, "")
            csc_list.append(
                CSCInformation(
                    name=name,
                    desired_version=desired_version,
                    current_version=current_version,
                )
            )

        return csc_list
