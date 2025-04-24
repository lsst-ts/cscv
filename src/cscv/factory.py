"""Component factory for the application."""

from structlog.stdlib import BoundLogger

from .config import config
from .services.cscv_service import CSCVService
from .storage.cscv_store import CSCVStore
from .storage.fake_cscv_store import FakeCSCVStore
from .storage.store import Store


class Factory:
    """A factory for the application components."""

    def __init__(self, *, logger: BoundLogger) -> None:
        self.logger = logger

    def create_cscv_service(self) -> CSCVService:
        """Create a cscv service."""
        return CSCVService(
            logger=self.logger, obsenv_store=self.create_cscv_store()
        )

    def create_cscv_store(self) -> Store:
        """Create a cscv store."""
        if config.use_fake_obsenv_manager:
            return FakeCSCVStore(logger=self.logger)
        else:
            return CSCVStore(logger=self.logger)
