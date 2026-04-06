from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from trivaxion.adapters.inbound.http.dependencies import (
    CurrentUser,
    DBSession,
    get_audit_repository,
    get_password_hasher,
    get_user_repository,
    require_admin,
)
from trivaxion.application.dto.user_dto import CreateUserRequest, UserResponse
from trivaxion.application.ports.auth import PasswordHasher
from trivaxion.application.ports.repositories import AuditRepository, UserRepository
from trivaxion.application.use_cases.user_use_cases import (
    CreateUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


class CreateUserRequestModel(BaseModel):
    email: str
    full_name: str
    password: str
    role: str
    organization_id: str | None = None


class UserResponseModel(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    status: str
    organization_id: str | None
    created_at: str
    last_login_at: str | None


@router.post("", response_model=UserResponseModel, dependencies=[Depends(require_admin)])
async def create_user(
    request: CreateUserRequestModel,
    current_user: CurrentUser,
    session: DBSession,
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    audit_repository: Annotated[AuditRepository, Depends(get_audit_repository)],
) -> UserResponseModel:
    use_case = CreateUserUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        audit_repository=audit_repository,
    )
    
    dto_request = CreateUserRequest(
        email=request.email,
        full_name=request.full_name,
        password=request.password,
        role=request.role,
        organization_id=request.organization_id,
    )
    
    response = await use_case.execute(dto_request, current_user.id)
    
    return UserResponseModel(**response.__dict__)


@router.get("", response_model=list[UserResponseModel])
async def list_users(
    current_user: CurrentUser,
    session: DBSession,
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> list[UserResponseModel]:
    if not current_user.organization_id:
        return []
    
    use_case = ListUsersUseCase(user_repository=user_repository)
    
    users = await use_case.execute(str(current_user.organization_id))
    
    return [UserResponseModel(**user.__dict__) for user in users]


@router.get("/{user_id}", response_model=UserResponseModel)
async def get_user(
    user_id: str,
    current_user: CurrentUser,
    session: DBSession,
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserResponseModel:
    use_case = GetUserUseCase(user_repository=user_repository)
    
    response = await use_case.execute(user_id)
    
    return UserResponseModel(**response.__dict__)
