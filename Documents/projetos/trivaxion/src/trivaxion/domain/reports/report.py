from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from trivaxion.domain.shared.entity import Entity
from trivaxion.domain.shared.value_objects import EntityId


class ReportFormat(str, Enum):
    HTML = "html"
    PDF = "pdf"
    JSON = "json"


class ReportStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Report(Entity):
    analysis_id: EntityId = field(default=None)
    organization_id: EntityId = field(default=None)
    format: ReportFormat = field(default=ReportFormat.JSON)
    status: ReportStatus = field(default=ReportStatus.PENDING)
    content: str | None = field(default=None)
    file_path: str | None = field(default=None)
    generated_at: datetime | None = field(default=None)
    error_message: str | None = field(default=None)

    def start_generation(self) -> None:
        self.status = ReportStatus.GENERATING

    def complete(self, content: str, file_path: str | None = None) -> None:
        self.status = ReportStatus.COMPLETED
        self.content = content
        self.file_path = file_path
        self.generated_at = datetime.now()

    def fail(self, error: str) -> None:
        self.status = ReportStatus.FAILED
        self.error_message = error
