from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from trivaxion.domain.shared.entity import Entity
from trivaxion.domain.shared.value_objects import EntityId


class EventType(str, Enum):
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ANALYSIS_CREATED = "analysis_created"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_FAILED = "analysis_failed"
    REPORT_GENERATED = "report_generated"
    COMPANY_SEARCHED = "company_searched"
    SCRAPER_EXECUTED = "scraper_executed"
    SCRAPER_FAILED = "scraper_failed"


@dataclass
class AuditEvent(Entity):
    event_type: EventType = field(default=EventType.USER_LOGIN)
    user_id: EntityId | None = field(default=None)
    organization_id: EntityId | None = field(default=None)
    resource_type: str | None = field(default=None)
    resource_id: EntityId | None = field(default=None)
    ip_address: str | None = field(default=None)
    user_agent: str | None = field(default=None)
    metadata: dict[str, object] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def add_metadata(self, key: str, value: object) -> None:
        self.metadata[key] = value
