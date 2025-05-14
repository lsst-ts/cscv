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
        self, desired: str, current: dict[str, str]
    ) -> list[CSCInformation]:
        """Parse desired/current key=value strings into CSCInformation."""
        # construct dict from current version dict
        cscv_dict = {
            key.split(".")[2].lower(): [value, "no data"]
            for key, value in current.items()
        }
        # update dict with desired versions
        for line in desired.strip().splitlines():
            line_clean = line.strip()
            if not line_clean or line_clean.startswith("#"):
                continue
            if "=" in line_clean:
                key, value = line_clean.split("=", maxsplit=1)
                key = key.split("ts_")[-1]
                if key in cscv_dict:
                    cscv_dict[key][1] = value

        return [
            CSCInformation(
                name=k,
                desired_version=cscv_dict[k][1],
                current_version=cscv_dict[k][0],
            )
            for k in cscv_dict
        ]
