from dataclasses import dataclass

from trivaxion.application.dto.auth_dto import LoginRequest, LoginResponse
from trivaxion.application.ports.auth import PasswordHasher, TokenService
from trivaxion.application.ports.repositories import AuditRepository, UserRepository
from trivaxion.domain.audit.audit_event import AuditEvent, EventType
from trivaxion.domain.identity.user import User
from trivaxion.domain.shared.exceptions import UnauthorizedError
from trivaxion.domain.shared.value_objects import Email


@dataclass
class LoginUseCase:
    user_repository: UserRepository
    password_hasher: PasswordHasher
    token_service: TokenService
    audit_repository: AuditRepository

    async def execute(self, request: LoginRequest, ip_address: str | None = None) -> LoginResponse:
        email = Email(request.email)
        user = await self.user_repository.find_by_email(email)

        if not user or not self.password_hasher.verify(request.password, user.hashed_password):
            raise UnauthorizedError("Invalid credentials")

        if not user.is_active():
            raise UnauthorizedError("User account is not active")

        access_token = self.token_service.create_access_token(user.id, user.organization_id)
        refresh_token = self.token_service.create_refresh_token(user.id)

        audit_event = AuditEvent(
            event_type=EventType.USER_LOGIN,
            user_id=user.id,
            organization_id=user.organization_id,
            ip_address=ip_address,
        )
        await self.audit_repository.save(audit_event)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=str(user.id),
            email=str(user.email),
            full_name=user.full_name,
            role=user.role.value,
        )


@dataclass
class RefreshTokenUseCase:
    user_repository: UserRepository
    token_service: TokenService

    async def execute(self, refresh_token: str) -> dict[str, str]:
        try:
            payload = self.token_service.verify_token(refresh_token)
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise UnauthorizedError("Invalid token")

            from trivaxion.domain.shared.value_objects import EntityId

            user_id = EntityId.from_string(str(user_id_str))
            user = await self.user_repository.find_by_id(user_id)

            if not user or not user.is_active():
                raise UnauthorizedError("User not found or inactive")

            access_token = self.token_service.create_access_token(user.id, user.organization_id)

            return {
                "access_token": access_token,
                "token_type": "bearer",
            }
        except Exception as e:
            raise UnauthorizedError(f"Invalid refresh token: {e}")
