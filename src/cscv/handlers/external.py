"""Handlers for the app's external root, ``/cscv/``."""

import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from safir.slack.webhook import SlackRouteErrorHandler

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
) -> Response:
    """Handle `/` by reusing the `/csc_versions` handler logic."""
    return templates.TemplateResponse(
        "csc_versions.html", {"request": request}
    )


@external_router.get("/branches")
async def repo_branches(
    request: Request,
) -> dict[str, list[str]]:
    service = request.app.state.cscv_service
    branches = await service.get_repo_branches()
    return {"branches": branches}


@external_router.get(
    "/csc_versions",
    description="Get versions of all CSCs.",
    summary="CSC versions",
)
async def csc_versions(
    request: Request,
    branch: Annotated[str, Query(description="Git branch name")] = "main",
) -> Response:
    """GET `/cscv/csc_versions` endpoint."""
    service = request.app.state.cscv_service
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
