from sqlalchemy.orm import Session
from domain.models import Version
from domain.schemas import VersionCreate, VersionUpdate
from typing import List

class VersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, version: VersionCreate) -> Version:
        """Create a new version in the database."""
        db_version = Version(name=version.name)
        self.db.add(db_version)
        self.db.commit()
        self.db.refresh(db_version)
        return db_version

    def get_all(self) -> List[Version]:
        """Retrieve all versions from the database."""
        return self.db.query(Version).all()

    def get(self, version_id: int) -> Version | None:
        """Retrieve a version by its ID."""
        return self.db.query(Version).filter(Version.id == version_id).first()

    def update(self, version_id: int, version: VersionUpdate) -> Version | None:
        """Update an existing version."""
        db_version = self.get(version_id)
        if db_version:
            if version.name:
                db_version.name = version.name
            self.db.commit()
            self.db.refresh(db_version)
            return db_version
        return None

    def delete(self, version_id: int) -> bool:
        """Delete a version by its ID."""
        db_version = self.get(version_id)
        if db_version:
            self.db.delete(db_version)
            self.db.commit()
            return True
        return False