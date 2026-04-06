from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class EntityId:
    value: UUID

    @classmethod
    def generate(cls) -> "EntityId":
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "EntityId":
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class CNPJ:
    value: str

    def __post_init__(self) -> None:
        normalized = self._normalize(self.value)
        if not self._is_valid(normalized):
            raise ValueError(f"Invalid CNPJ: {self.value}")
        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _normalize(cnpj: str) -> str:
        return "".join(filter(str.isdigit, cnpj))

    @staticmethod
    def _is_valid(cnpj: str) -> bool:
        if len(cnpj) != 14:
            return False
        if cnpj == cnpj[0] * 14:
            return False

        def calculate_digit(cnpj_partial: str, weights: list[int]) -> int:
            total = sum(int(digit) * weight for digit, weight in zip(cnpj_partial, weights))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        weights_second = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        first_digit = calculate_digit(cnpj[:12], weights_first)
        second_digit = calculate_digit(cnpj[:13], weights_second)

        return cnpj[-2:] == f"{first_digit}{second_digit}"

    def formatted(self) -> str:
        return f"{self.value[:2]}.{self.value[2:5]}.{self.value[5:8]}/{self.value[8:12]}-{self.value[12:]}"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        return "@" in email and "." in email.split("@")[1]

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"


@dataclass(frozen=True)
class DateRange:
    start: datetime
    end: datetime | None = None

    def __post_init__(self) -> None:
        if self.end and self.start > self.end:
            raise ValueError("Start date must be before end date")

    def is_active(self) -> bool:
        return self.end is None or self.end > datetime.now()


@dataclass(frozen=True)
class Address:
    street: str
    number: str
    complement: str | None
    neighborhood: str
    city: str
    state: str
    zip_code: str
    country: str = "Brasil"

    def full_address(self) -> str:
        parts = [
            f"{self.street}, {self.number}",
            self.complement or "",
            self.neighborhood,
            f"{self.city} - {self.state}",
            f"CEP: {self.zip_code}",
        ]
        return ", ".join(filter(None, parts))
