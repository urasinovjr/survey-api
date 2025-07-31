from sqlalchemy.orm import Session
from domain.schemas import VersionCreate, VersionUpdate, Version
from repositories.version import VersionRepository
from typing import List

class VersionService:
    def __init__(self, db: Session):
        self.repo = VersionRepository(db)

    def create(self, version: VersionCreate) -> Version:
        """Create a new survey version."""
        return self.repo.create(version)

    def get_all(self) -> List[Version]:
        """Retrieve all survey versions."""
        return self.repo.get_all()

    def get(self, version_id: int) -> Version | None:
        """Retrieve a specific version by ID."""
        return self.repo.get(version_id)

    def update(self, version_id: int, version: VersionUpdate) -> Version | None:
        """Update an existing version."""
        return self.repo.update(version_id, version)

    def delete(self, version_id: int) -> bool:
        """Delete a version by ID."""
        return self.repo.delete(version_id)