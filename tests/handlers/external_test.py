"""Tests for the cscv.handlers.external module and routes."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_index(client: AsyncClient) -> None:
    """Test ``GET /cscv/`` returns HTML."""
    response = await client.get("/cscv/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    # Check for a string that is present in the template
    assert "CSC Versions Dashboard" in response.text
