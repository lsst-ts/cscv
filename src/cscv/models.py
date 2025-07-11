"""Models for cscv."""

from collections import defaultdict
from typing import Self

from pydantic import BaseModel, Field
from safir.metadata import Metadata as SafirMetadata

from .domain.models import CSCInformation

__all__ = [
    "CSCVersions",
    "CSCVersionsResponseModel",
    "Index",
]


class Index(BaseModel):
    """Metadata returned by the external root URL of the application.

    Notes
    -----
    As written, this is not very useful. Add additional metadata that will be
    helpful for a user exploring the application, or replace this model with
    some other model that makes more sense to return from the application API
    root.
    """

    metadata: SafirMetadata = Field(..., title="Package metadata")


class CSCVersions(BaseModel):
    """CSC version information."""

    name: str = Field(..., title="CSC name", description="Name of the CSC.")
    namespace: str = Field(
        ...,
        title="Namespace",
        description="The namespace of the T&S application the CSC belongs to.",
    )
    index: int = Field(
        ...,
        title="Index",
        description="The index of the CSC within the namespace.",
    )
    current_version: str = Field(
        ...,
        title="Current version",
        description="The version the CSC is currently running.",
    )
    desired_version: str = Field(
        ...,
        title="Desired version",
        description="The version the CSC is supposed to run.",
    )
    is_same: bool = Field(
        False,
        title="Version difference.",
        description=(
            "Flag to highlight is there is a difference between desired and "
            "current version."
        ),
    )

    @classmethod
    def from_domain(cls, *, csc_info: CSCInformation) -> Self:
        """Construct the CSCVersion model from the CSC information."""
        return cls(
            name=csc_info.name,
            namespace=csc_info.namespace,
            index=csc_info.index,
            desired_version=csc_info.desired_version,
            current_version=csc_info.current_version,
            is_same=csc_info.are_versions_equal(),
        )


class CSCVersionsResponseModel(BaseModel):
    """CSC version information."""

    fetch_datetime: str = Field(
        ...,
        title="Datetime of fetch",
        description=(
            "The datetime ISO formatted string when the CSC versions were "
            "fetched."
        ),
    )

    cscs: dict[str, list[CSCVersions]] = Field(
        default_factory=dict,
        title="CSC list grouped by namespace",
        description="Dict of CSCVersions grouped by namespace.",
    )

    @classmethod
    def from_domain(
        cls, *, fetch_datetime: str, cscs: list[CSCInformation]
    ) -> Self:
        """Construct the list of CSCVersions from the CSCInformation."""
        grouped_cscs = defaultdict(list)
        for csc in cscs:
            cscv = CSCVersions.from_domain(csc_info=csc)
            grouped_cscs[csc.namespace].append(cscv)

        return cls(fetch_datetime=fetch_datetime, cscs=grouped_cscs)
