#!/usr/bin/env python3
"""
Seed script to create initial data for Trivaxion
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from sqlalchemy.ext.asyncio import AsyncSession
from trivaxion.domain.identity.user import User, UserRole, UserStatus
from trivaxion.domain.organizations.organization import Organization, OrganizationStatus, PlanType
from trivaxion.domain.shared.value_objects import Email, EntityId
from trivaxion.infrastructure.db.base import engine
from trivaxion.infrastructure.db.models import Base
from trivaxion.adapters.outbound.persistence.sqlalchemy_repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyOrganizationRepository,
)
from trivaxion.application.ports.auth import PasswordHasher
from trivaxion.infrastructure.security.password import BcryptPasswordHasher


async def create_initial_data():
    """Create initial organization and admin user"""
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with AsyncSession(engine) as session:
        # Initialize repositories
        org_repo = SQLAlchemyOrganizationRepository(session)
        user_repo = SQLAlchemyUserRepository(session)
        password_hasher = BcryptPasswordHasher()
        
        # Create default organization
        org = Organization(
            name="Trivaxion Demo",
            status=OrganizationStatus.ACTIVE,
            plan=PlanType.FREE,
            max_users=10,
            max_analyses_per_month=100,
            analyses_count_current_month=0,
        )
        
        # Check if organization already exists
        existing_orgs = await org_repo.find_all()
        if existing_orgs:
            print("Organization already exists, skipping seed...")
            return
        
        org = await org_repo.save(org)
        print(f"Created organization: {org.name} (ID: {org.id})")
        
        # Create admin user
        admin_password = "admin123"
        hashed_password = password_hasher.hash(admin_password)
        
        admin_user = User(
            email=Email("admin@trivaxion.com"),
            full_name="Admin User",
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            organization_id=org.id,
        )
        
        admin_user = await user_repo.save(admin_user)
        print(f"Created admin user: {admin_user.email} (ID: {admin_user.id})")
        print(f"Login credentials: email={admin_user.email}, password={admin_password}")


if __name__ == "__main__":
    asyncio.run(create_initial_data())
