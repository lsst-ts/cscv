"""Handlers for the app's external root, ``/cscv/``."""

import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from safir.dependencies.logger import logger_dependency
from safir.metadata import get_metadata
from safir.slack.webhook import SlackRouteErrorHandler
from structlog.stdlib import BoundLogger

from ..config import config
from ..factory import Factory
from ..models import CSCVersionsResponseModel, Index

__all__ = ["external_router"]

external_router = APIRouter(route_class=SlackRouteErrorHandler)
"""FastAPI router for all external handlers."""


@external_router.get(
    "/",
    description=(
        "Document the top-level API here. By default it only returns metadata"
        " about the application."
    ),
    response_model_exclude_none=True,
    summary="Application metadata",
)
async def get_index(
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Index:
    # Customize this handler to return whatever the top-level resource of your
    # application should return. For example, consider listing key API URLs.
    # When doing so, also change or customize the response model in
    # cscv.models.Index.
    #
    # By convention, the root of the external API includes a field called
    # metadata that provides the same Safir-generated metadata as the internal
    # root endpoint.

    # There is no need to log simple requests since uvicorn will do this
    # automatically, but this is included as an example of how to use the
    # logger for more complex logging.
    logger.info("Request for application metadata")

    metadata = get_metadata(
        package_name="cscv",
        application_name=config.name,
    )
    return Index(metadata=metadata)


@external_router.get("/hola", summary="Saludo buena tela :)")
async def get_saludo() -> str:
    return "holaaa!"


@external_router.get(
    "/csc_versions",
    description="Get all the versions of cscs.",
    summary="CSC versions",
)
async def csc_versions(
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> CSCVersionsResponseModel:
    """GET `/cscv/csc_versions` endpoint."""
    factory = Factory(logger=logger)
    service = factory.create_cscv_service()
    pkg_list = service.get_csc_versions()
    fetch_datetime = datetime.datetime.now(datetime.UTC).isoformat()
    return CSCVersionsResponseModel.from_domain(
        fetch_datetime=fetch_datetime, pkg_list=pkg_list
    )
