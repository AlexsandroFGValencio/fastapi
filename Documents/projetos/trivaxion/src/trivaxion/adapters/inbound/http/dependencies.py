from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from trivaxion.application.ports.auth import PasswordHasher, TokenService
from trivaxion.application.ports.repositories import (
    AnalysisRepository,
    AuditRepository,
    CompanyRepository,
    OrganizationRepository,
    ReportRepository,
    UserRepository,
)
from trivaxion.domain.identity.user import User
from trivaxion.domain.shared.value_objects import EntityId
from trivaxion.infrastructure.security.jwt import JWTTokenService
from trivaxion.infrastructure.db.base import get_db_session
from trivaxion.infrastructure.security.password import BcryptPasswordHasher
from trivaxion.infrastructure.config.settings import get_settings
from trivaxion.adapters.outbound.persistence.sqlalchemy_repositories import (
    SQLAlchemyAnalysisRepository,
    SQLAlchemyAuditRepository,
    SQLAlchemyCompanyRepository,
    SQLAlchemyOrganizationRepository,
    SQLAlchemyReportRepository,
    SQLAlchemyUserRepository,
)

security = HTTPBearer()


# Service factories
def get_password_hasher() -> PasswordHasher:
    """Get password hasher instance"""
    return BcryptPasswordHasher()


def get_token_service() -> TokenService:
    """Get token service instance"""
    settings = get_settings()
    return JWTTokenService(settings)


# Repository factories
async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """Get user repository instance"""
    return SQLAlchemyUserRepository(session)


async def get_organization_repository(session: AsyncSession = Depends(get_db_session)) -> OrganizationRepository:
    """Get organization repository instance"""
    return SQLAlchemyOrganizationRepository(session)


async def get_analysis_repository(session: AsyncSession = Depends(get_db_session)) -> AnalysisRepository:
    """Get analysis repository instance"""
    return SQLAlchemyAnalysisRepository(session)


async def get_company_repository(session: AsyncSession = Depends(get_db_session)) -> CompanyRepository:
    """Get company repository instance"""
    return SQLAlchemyCompanyRepository(session)


async def get_report_repository(session: AsyncSession = Depends(get_db_session)) -> ReportRepository:
    """Get report repository instance"""
    return SQLAlchemyReportRepository(session)


async def get_audit_repository(session: AsyncSession = Depends(get_db_session)) -> AuditRepository:
    """Get audit repository instance"""
    return SQLAlchemyAuditRepository(session)


# Provider factories
async def get_company_data_provider(
    session: DBSession
) -> CompanyDataProvider:
    from trivaxion.adapters.outbound.providers.receita_federal.scraper import ReceitaFederalProvider
    return ReceitaFederalProvider(session)


def get_labor_certificate_provider():
    """Get labor certificate provider instance"""
    from trivaxion.adapters.outbound.providers.certidao_trabalhista.scraper import CertidaoTrabalhistaProvider
    settings = get_settings()
    return CertidaoTrabalhistaProvider(settings)


async def get_search_port(session: DBSession):
    """Get search port instance - PostgreSQL Full-Text Search"""
    from trivaxion.adapters.outbound.search.postgresql_search import PostgreSQLSearchAdapter
    return PostgreSQLSearchAdapter(session)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_service: TokenService = Depends(get_token_service),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    try:
        token = credentials.credentials
        payload = token_service.verify_token(token)
        user_id_str = payload.get("sub")
        
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
        user_id = EntityId.from_string(str(user_id_str))
        user = await user_repository.find_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        if not user.is_active():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active",
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
        )


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active():
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.can_manage_users():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user


DBSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
