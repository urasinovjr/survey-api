from sqlalchemy.orm import Session
from models.version import Version
from schemas.version import VersionCreate, VersionUpdate
import logging

logger = logging.getLogger(__name__)

class VersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, version: VersionCreate) -> Version:
        logger.info(f"Creating version with name: {version.name}")
        db_version = Version(name=version.name)
        self.db.add(db_version)
        self.db.commit()
        self.db.refresh(db_version)
        return db_version

    def get(self, version_id: int) -> Version | None:
        return self.db.query(Version).filter(Version.id == version_id).first()

    def get_all(self) -> list[Version]:
        return self.db.query(Version).all()

    def update(self, version_id: int, version: VersionUpdate) -> Version | None:
        db_version = self.get(version_id)
        if not db_version:
            logger.warning(f"Version {version_id} not found for update")
            return None
        for key, value in version.dict(exclude_unset=True).items():
            setattr(db_version, key, value)
        self.db.commit()
        self.db.refresh(db_version)
        logger.info(f"Updated version {version_id}")
        return db_version

    def delete(self, version_id: int) -> bool:
        db_version = self.get(version_id)
        if not db_version:
            logger.warning(f"Version {version_id} not found for deletion")
            return False
        self.db.delete(db_version)
        self.db.commit()
        logger.info(f"Deleted version {version_id}")
        return True