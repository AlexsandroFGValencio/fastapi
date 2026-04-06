from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from trivaxion.domain.shared.entity import Entity
from trivaxion.domain.shared.value_objects import Email, EntityId


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class User(Entity):
    email: Email = field(default=None)
    full_name: str = field(default="")
    hashed_password: str = field(default="")
    role: UserRole = field(default=UserRole.VIEWER)
    status: UserStatus = field(default=UserStatus.ACTIVE)
    organization_id: EntityId | None = field(default=None)
    last_login_at: datetime | None = field(default=None)

    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    def can_manage_users(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]

    def can_create_analysis(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.ANALYST]

    def activate(self) -> None:
        self.status = UserStatus.ACTIVE

    def deactivate(self) -> None:
        self.status = UserStatus.INACTIVE

    def suspend(self) -> None:
        self.status = UserStatus.SUSPENDED
