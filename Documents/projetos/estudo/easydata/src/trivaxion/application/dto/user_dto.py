from dataclasses import dataclass


@dataclass
class CreateUserRequest:
    email: str
    full_name: str
    password: str
    role: str
    organization_id: str | None = None


@dataclass
class UpdateUserRequest:
    full_name: str | None = None
    role: str | None = None
    status: str | None = None


@dataclass
class UserResponse:
    id: str
    email: str
    full_name: str
    role: str
    status: str
    organization_id: str | None
    created_at: str
    last_login_at: str | None
