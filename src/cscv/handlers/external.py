"""Handlers for the app's external root, ``/cscv/``."""

import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from safir.dependencies.logger import logger_dependency
from safir.slack.webhook import SlackRouteErrorHandler
from structlog.stdlib import BoundLogger

from ..factory import Factory
from ..models import CSCVersionsResponseModel

__all__ = ["external_router"]

external_router = APIRouter(route_class=SlackRouteErrorHandler)
"""FastAPI router for all external handlers."""
templates = Jinja2Templates(
    directory=Path(__file__).parent.parent / "templates"
)


@external_router.get(
    "/",
    description="Redirect root to CSC versions.",
    summary="CSC versions (root)",
)
async def get_index(
    request: Request,
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Response:
    """Handle `/` by reusing the `/csc_versions` handler logic."""
    return templates.TemplateResponse(
        "csc_versions.html", {"request": request}
    )


@external_router.get("/hola", summary="Saludo buena tela :)")
async def get_saludo() -> str:
    return "holaaa!"


@external_router.get(
    "/csc_versions",
    description="Get versions of all CSCs.",
    summary="CSC versions",
)
async def csc_versions(
    request: Request,
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
    branch: Annotated[
        str, Query(default="main", description="Git branch name")
    ],
) -> Response:
    """GET `/cscv/csc_versions` endpoint."""
    factory = Factory(logger=logger)
    service = factory.create_cscv_service()
    csc_list = await service.get_csc_versions(branch)
    fetch_datetime = datetime.datetime.now(datetime.UTC).isoformat()
    csc_response = CSCVersionsResponseModel.from_domain(
        fetch_datetime=fetch_datetime, cscs=csc_list
    )
    return templates.TemplateResponse(
        "data.html",
        {
            "request": request,
            "csc_response": csc_response,
        },
    )
