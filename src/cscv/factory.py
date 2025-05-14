"""Component factory for the application."""

from structlog.stdlib import BoundLogger

from .services.cscv_service import CSCVService
from .storage.cscv_store import CSCVStore
from .storage.store import Store


class Factory:
    """A factory for the application components."""

    def __init__(self, *, logger: BoundLogger) -> None:
        self.logger = logger

    def create_cscv_service(self) -> CSCVService:
        """Create a cscv service."""
        return CSCVService(
            logger=self.logger, cscv_store=self.create_cscv_store()
        )

    def create_cscv_store(self) -> Store:
        """Create a cscv store."""
        """Create an obsenv store."""
        return CSCVStore(logger=self.logger)
