from dataclasses import dataclass

from trivaxion.application.dto.user_dto import CreateUserRequest, UpdateUserRequest, UserResponse
from trivaxion.application.ports.auth import PasswordHasher
from trivaxion.application.ports.repositories import AuditRepository, UserRepository
from trivaxion.domain.audit.audit_event import AuditEvent, EventType
from trivaxion.domain.identity.user import User, UserRole, UserStatus
from trivaxion.domain.shared.exceptions import ConflictError, NotFoundError, ValidationError
from trivaxion.domain.shared.value_objects import Email, EntityId


@dataclass
class CreateUserUseCase:
    user_repository: UserRepository
    password_hasher: PasswordHasher
    audit_repository: AuditRepository

    async def execute(self, request: CreateUserRequest, created_by: EntityId) -> UserResponse:
        email = Email(request.email)
        existing = await self.user_repository.find_by_email(email)
        if existing:
            raise ConflictError(f"User with email {request.email} already exists")

        try:
            role = UserRole(request.role)
        except ValueError:
            raise ValidationError(f"Invalid role: {request.role}")

        hashed_password = self.password_hasher.hash(request.password)
        organization_id = (
            EntityId.from_string(request.organization_id) if request.organization_id else None
        )

        user = User(
            email=email,
            full_name=request.full_name,
            hashed_password=hashed_password,
            role=role,
            organization_id=organization_id,
        )

        saved_user = await self.user_repository.save(user)

        audit_event = AuditEvent(
            event_type=EventType.USER_CREATED,
            user_id=created_by,
            organization_id=organization_id,
            resource_type="user",
            resource_id=saved_user.id,
        )
        await self.audit_repository.save(audit_event)

        return self._to_response(saved_user)

    def _to_response(self, user: User) -> UserResponse:
        return UserResponse(
            id=str(user.id),
            email=str(user.email),
            full_name=user.full_name,
            role=user.role.value,
            status=user.status.value,
            organization_id=str(user.organization_id) if user.organization_id else None,
            created_at=user.created_at.isoformat(),
            last_login_at=user.last_login_at,
        )


@dataclass
class GetUserUseCase:
    user_repository: UserRepository

    async def execute(self, user_id: str) -> UserResponse:
        entity_id = EntityId.from_string(user_id)
        user = await self.user_repository.find_by_id(entity_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")

        return UserResponse(
            id=str(user.id),
            email=str(user.email),
            full_name=user.full_name,
            role=user.role.value,
            status=user.status.value,
            organization_id=str(user.organization_id) if user.organization_id else None,
            created_at=user.created_at.isoformat(),
            last_login_at=user.last_login_at,
        )


@dataclass
class ListUsersUseCase:
    user_repository: UserRepository

    async def execute(self, organization_id: str) -> list[UserResponse]:
        entity_id = EntityId.from_string(organization_id)
        users = await self.user_repository.find_by_organization(entity_id)

        return [
            UserResponse(
                id=str(user.id),
                email=str(user.email),
                full_name=user.full_name,
                role=user.role.value,
                status=user.status.value,
                organization_id=str(user.organization_id) if user.organization_id else None,
                created_at=user.created_at.isoformat(),
                last_login_at=user.last_login_at,
            )
            for user in users
        ]
