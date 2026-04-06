from dataclasses import dataclass
from uuid import UUID

from trivaxion.domain.shared.events import DomainEvent


@dataclass
class UserCreated(DomainEvent):
    user_id: UUID
    email: str
    organization_id: UUID | None


@dataclass
class UserLoggedIn(DomainEvent):
    user_id: UUID
    ip_address: str | None = None


@dataclass
class UserPasswordChanged(DomainEvent):
    user_id: UUID


@dataclass
class UserDeactivated(DomainEvent):
    user_id: UUID
    reason: str | None = None
