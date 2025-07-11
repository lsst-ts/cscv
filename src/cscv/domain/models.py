"""Models for the obsenv API domain."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["CSCInformation"]


@dataclass(kw_only=True)
class CSCInformation:
    """CSC version information."""

    name: str
    """Name of the CSC."""

    namespace: str
    """Name of the T&S namespace the CSC belongs to."""

    index: str
    """Index of the CSC."""

    current_version: str
    """The version the CSC is currently running."""

    desired_version: str
    """The the CSC is supposed to be running."""

    def is_different(self) -> bool:
        return self.current_version != self.desired_version
