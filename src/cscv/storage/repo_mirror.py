"""Repository mirror utility for reading files from a git repo clone."""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Any

from git import GitCommandError, Repo
from structlog.stdlib import BoundLogger

__all__ = ["RepoMirror"]


class RepoMirror:
    """
    Provides the RepoMirror class, which clones or fetches a bare
    Git mirror and allows reading specific files (like cycle.env) from branches
    without performing a checkout.
    """

    def __init__(
        self,
        repo_url: str = "https://github.com/lsst-ts/ts_cycle_build.git",
        mirror_dir: str | None = None,
        file_path: str = "cycle/cycle.env",
        fetch_min_interval_sec: int = 0,
        logger: BoundLogger = None,
    ) -> None:
        if mirror_dir is None:
            mirror_dir = os.getenv(
                "REPO_DIR", "~/.cache/ts_cycle_build/ts_cycle_build.git"
            )
        expanded = os.path.expandvars(mirror_dir)
        self.mirror_dir = Path(expanded).expanduser().resolve()
        self.repo_url = repo_url
        self.mirror_dir = mirror_dir
        self.file_path = file_path
        self._repo: Repo | None = None
        self._last_fetch_ts: float = 0.0
        self.fetch_min_interval_sec = fetch_min_interval_sec
        self._logger = logger

    async def list_branches(self) -> list[str]:
        """Return the names of all remote branches."""
        repo = await self._ensure_mirror()
        await self._fetch_all()
        repo_heads = repo.heads
        return [h.name for h in repo_heads]

    async def show_from_ref(self, ref: str) -> str | None:
        await self._ensure_mirror()

        def _show() -> str | None:
            try:
                return self._repo.git.show(f"{ref}:{self.file_path}")
            except GitCommandError:
                return None

        return await self._to_thread(_show)

    async def _to_thread(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))

    async def _ensure_mirror(self) -> Repo:
        if self._repo is not None:
            return self._repo

        Path(self.mirror_dir).parent.mkdir(parents=True, exist_ok=True)
        if not Path(self.mirror_dir).is_dir():
            self._logger.info(
                f"Cloning mirror: {self.repo_url} -> {self.mirror_dir}"
            )
            self._repo = await self._to_thread(
                Repo.clone_from, self.repo_url, self.mirror_dir, mirror=True
            )
        else:
            self._repo = Repo(self.mirror_dir)
        return self._repo

    async def _fetch_all(self) -> None:
        """Update refs; throttled by fetch_min_interval_sec if set."""
        await self._ensure_mirror()
        now = time.time()
        if (
            self.fetch_min_interval_sec
            and (now - self._last_fetch_ts) < self.fetch_min_interval_sec
        ):
            return
        self._logger.debug("Fetching mirror refs (prune + tags)")
        await self._to_thread(
            self._repo.remotes.origin.fetch, prune=True, tags=True
        )
        self._last_fetch_ts = now
