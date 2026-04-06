from dataclasses import dataclass


@dataclass
class LoginRequest:
    email: str
    password: str


@dataclass
class LoginResponse:
    access_token: str
    refresh_token: str
    token_type: str
    user_id: str
    email: str
    full_name: str
    role: str


@dataclass
class RefreshTokenRequest:
    refresh_token: str


@dataclass
class ChangePasswordRequest:
    old_password: str
    new_password: str


@dataclass
class ForgotPasswordRequest:
    email: str


@dataclass
class ResetPasswordRequest:
    token: str
    new_password: str
