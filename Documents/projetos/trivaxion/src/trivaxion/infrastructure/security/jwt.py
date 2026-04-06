from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from trivaxion.application.ports.auth import TokenService
from trivaxion.domain.shared.value_objects import EntityId
from trivaxion.infrastructure.config.settings import Settings


class JWTTokenService(TokenService):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_access_token(self, user_id: EntityId, organization_id: EntityId | None) -> str:
        expires = datetime.utcnow() + timedelta(
            minutes=self._settings.jwt_access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "org_id": str(organization_id) if organization_id else None,
            "exp": expires,
            "type": "access",
        }
        return jwt.encode(payload, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm)

    def create_refresh_token(self, user_id: EntityId) -> str:
        expires = datetime.utcnow() + timedelta(days=self._settings.jwt_refresh_token_expire_days)
        payload = {
            "sub": str(user_id),
            "exp": expires,
            "type": "refresh",
        }
        return jwt.encode(payload, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm)

    def verify_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret_key,
                algorithms=[self._settings.jwt_algorithm],
            )
            return payload
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}")

    def decode_token(self, token: str) -> dict[str, Any]:
        return self.verify_token(token)
