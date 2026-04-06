import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import datetime
from uuid import uuid4

from trivaxion.infrastructure.db.base import Base
from trivaxion.main import app
from trivaxion.domain.identity.user import User, UserRole, UserStatus
from trivaxion.domain.shared.value_objects import EntityId, Email
from trivaxion.domain.organizations.organization import Organization, OrganizationStatus, PlanType
from trivaxion.infrastructure.security.password import BcryptPasswordHasher
from trivaxion.adapters.outbound.persistence.sqlalchemy_repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyOrganizationRepository,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        "postgresql+psycopg://postgres:postgres@localhost:5432/trivaxion_test",
        echo=False,
        pool_pre_ping=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_organization(db_session: AsyncSession) -> Organization:
    """Create test organization"""
    org = Organization(
        id=EntityId.generate(),
        name="Test Organization",
        cnpj=None,
        status=OrganizationStatus.ACTIVE,
        plan=PlanType.PROFESSIONAL,
        max_users=10,
        max_analyses_per_month=100,
        analyses_count_current_month=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    repo = SQLAlchemyOrganizationRepository(db_session)
    saved_org = await repo.save(org)
    await db_session.commit()
    
    return saved_org


@pytest.fixture
async def test_user(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create test user"""
    password_hasher = BcryptPasswordHasher()
    hashed_password = password_hasher.hash("testpassword123")
    
    user = User(
        id=EntityId.generate(),
        email=Email("test@example.com"),
        full_name="Test User",
        hashed_password=hashed_password,
        role=UserRole.ANALYST,
        status=UserStatus.ACTIVE,
        organization_id=test_organization.id,
        last_login_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    repo = SQLAlchemyUserRepository(db_session)
    saved_user = await repo.save(user)
    await db_session.commit()
    
    return saved_user


@pytest.fixture
async def test_admin_user(db_session: AsyncSession, test_organization: Organization) -> User:
    """Create test admin user"""
    password_hasher = BcryptPasswordHasher()
    hashed_password = password_hasher.hash("adminpassword123")
    
    user = User(
        id=EntityId.generate(),
        email=Email("admin@example.com"),
        full_name="Admin User",
        hashed_password=hashed_password,
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        organization_id=test_organization.id,
        last_login_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    repo = SQLAlchemyUserRepository(db_session)
    saved_user = await repo.save(user)
    await db_session.commit()
    
    return saved_user


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for API testing"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def password_hasher():
    """Get password hasher instance"""
    return BcryptPasswordHasher()
