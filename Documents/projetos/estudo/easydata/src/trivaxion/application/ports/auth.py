from abc import ABC, abstractmethod
from dataclasses import dataclass

from trivaxion.domain.identity.user import User
from trivaxion.domain.shared.value_objects import EntityId


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        pass

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        pass


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: EntityId, organization_id: EntityId | None) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, user_id: EntityId) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str) -> dict[str, object]:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> dict[str, object]:
        pass
