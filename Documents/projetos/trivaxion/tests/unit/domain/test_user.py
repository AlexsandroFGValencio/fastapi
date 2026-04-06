import pytest
from datetime import datetime

from trivaxion.domain.identity.user import User, UserRole, UserStatus
from trivaxion.domain.shared.value_objects import EntityId, Email


@pytest.mark.unit
class TestUser:
    """Test User domain entity"""
    
    def test_create_user(self):
        """Test creating a user"""
        user = User(
            id=EntityId.generate(),
            email=Email("test@example.com"),
            full_name="Test User",
            hashed_password="hashed_password",
            role=UserRole.ANALYST,
            status=UserStatus.ACTIVE,
            organization_id=EntityId.generate(),
            last_login_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert user.email.value == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == UserRole.ANALYST
        assert user.status == UserStatus.ACTIVE
    
    def test_user_is_active(self):
        """Test user is_active method"""
        active_user = User(
            id=EntityId.generate(),
            email=Email("active@example.com"),
            full_name="Active User",
            hashed_password="hashed",
            role=UserRole.ANALYST,
            status=UserStatus.ACTIVE,
            organization_id=EntityId.generate(),
            last_login_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        inactive_user = User(
            id=EntityId.generate(),
            email=Email("inactive@example.com"),
            full_name="Inactive User",
            hashed_password="hashed",
            role=UserRole.ANALYST,
            status=UserStatus.INACTIVE,
            organization_id=EntityId.generate(),
            last_login_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert active_user.is_active() is True
        assert inactive_user.is_active() is False
    
    def test_user_can_manage_users(self):
        """Test user can_manage_users method"""
        admin = User(
            id=EntityId.generate(),
            email=Email("admin@example.com"),
            full_name="Admin",
            hashed_password="hashed",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            organization_id=EntityId.generate(),
            last_login_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        manager = User(
            id=EntityId.generate(),
            email=Email("manager@example.com"),
            full_name="Manager",
            hashed_password="hashed",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
            organization_id=EntityId.generate(),
            last_login_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        analyst = User(
            id=EntityId.generate(),
            email=Email("analyst@example.com"),
            full_name="Analyst",
            hashed_password="hashed",
            role=UserRole.ANALYST,
            status=UserStatus.ACTIVE,
            organization_id=EntityId.generate(),
            last_login_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert admin.can_manage_users() is True
        assert manager.can_manage_users() is True
        assert analyst.can_manage_users() is False
    
    def test_user_can_create_analysis(self):
        """Test user can_create_analysis method"""
        admin = User(
            id=EntityId.generate(),
            email=Email("admin@example.com"),
            full_name="Admin",
            hashed_password="hashed",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            organization_id=EntityId.generate(),
            last_login_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        analyst = User(
            id=EntityId.generate(),
            email=Email("analyst@example.com"),
            full_name="Analyst",
            hashed_password="hashed",
            role=UserRole.ANALYST,
            status=UserStatus.ACTIVE,
            organization_id=EntityId.generate(),
            last_login_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        viewer = User(
            id=EntityId.generate(),
            email=Email("viewer@example.com"),
            full_name="Viewer",
            hashed_password="hashed",
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE,
            organization_id=EntityId.generate(),
            last_login_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert admin.can_create_analysis() is True
        assert analyst.can_create_analysis() is True
        assert viewer.can_create_analysis() is False
