from sqlalchemy.orm import Session
from schemas.version import VersionCreate, VersionUpdate
from repositories.version import VersionRepository
import logging

logger = logging.getLogger(__name__)

class VersionService:
    def __init__(self, db: Session):
        self.repo = VersionRepository(db)

    def create(self, version: VersionCreate):
        logger.info(f"Service: Creating version {version.name}")
        return self.repo.create(version)

    def get(self, version_id: int):
        return self.repo.get(version_id)

    def get_all(self):
        return self.repo.get_all()

    def update(self, version_id: int, version: VersionUpdate):
        return self.repo.update(version_id, version)

    def delete(self, version_id: int):
        return self.repo.delete(version_id)