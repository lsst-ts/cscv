"""Models for the obsenv API domain."""

from __future__ import annotations

from dataclasses import dataclass

from packaging import version

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

    def are_versions_equal(self) -> bool:
        # Normalize and compare
        try:
            return version.parse(self.current_version) == version.parse(
                self.desired_version
            )
        except version.InvalidVersion:
            return False
