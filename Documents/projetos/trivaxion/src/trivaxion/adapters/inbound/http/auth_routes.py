from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from trivaxion.adapters.inbound.http.dependencies import (
    CurrentUser,
    DBSession,
    get_audit_repository,
    get_password_hasher,
    get_token_service,
    get_user_repository,
)
from trivaxion.application.dto.auth_dto import LoginRequest, LoginResponse, RefreshTokenRequest
from trivaxion.application.ports.auth import PasswordHasher, TokenService
from trivaxion.application.ports.repositories import AuditRepository, UserRepository
from trivaxion.application.use_cases.auth_use_cases import LoginUseCase, RefreshTokenUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequestModel(BaseModel):
    email: str
    password: str


class RefreshTokenRequestModel(BaseModel):
    refresh_token: str


class LoginResponseModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: str
    email: str
    full_name: str
    role: str


@router.post("/login", response_model=LoginResponseModel)
async def login(
    request: LoginRequestModel,
    session: DBSession,
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
    user_repository: UserRepository = Depends(get_user_repository),
    audit_repository: AuditRepository = Depends(get_audit_repository),
) -> LoginResponseModel:
    use_case = LoginUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_service=token_service,
        audit_repository=audit_repository,
    )
    
    dto_request = LoginRequest(email=request.email, password=request.password)
    response = await use_case.execute(dto_request)
    
    return LoginResponseModel(
        access_token=response.access_token,
        refresh_token=response.refresh_token,
        token_type=response.token_type,
        user_id=response.user_id,
        email=response.email,
        full_name=response.full_name,
        role=response.role,
    )


@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequestModel,
    session: DBSession,
    token_service: TokenService = Depends(get_token_service),
    user_repository: UserRepository = Depends(get_user_repository),
) -> dict[str, str]:
    use_case = RefreshTokenUseCase(
        user_repository=user_repository,
        token_service=token_service,
    )
    
    return await use_case.execute(request.refresh_token)


@router.post("/logout")
async def logout(current_user: CurrentUser) -> dict[str, str]:
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(current_user: CurrentUser) -> dict[str, object]:
    return {
        "id": str(current_user.id),
        "email": str(current_user.email),
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "status": current_user.status.value,
        "organization_id": str(current_user.organization_id) if current_user.organization_id else None,
    }
