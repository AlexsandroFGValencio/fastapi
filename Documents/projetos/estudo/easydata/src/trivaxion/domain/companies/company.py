from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from trivaxion.domain.shared.entity import Entity
from trivaxion.domain.shared.value_objects import Address, CNPJ, Money


class CompanyStatus(str, Enum):
    ATIVA = "ativa"
    SUSPENSA = "suspensa"
    INAPTA = "inapta"
    BAIXADA = "baixada"
    NULA = "nula"


class CompanySize(str, Enum):
    MEI = "mei"
    ME = "me"
    EPP = "epp"
    DEMAIS = "demais"


@dataclass
class Partner:
    name: str
    cpf_cnpj: str
    qualification: str
    entry_date: datetime | None = None


@dataclass
class Company(Entity):
    cnpj: CNPJ = field(default=None)
    razao_social: str = field(default="")
    nome_fantasia: str | None = field(default=None)
    status: CompanyStatus = field(default=CompanyStatus.ATIVA)
    opening_date: datetime | None = field(default=None)
    cnae_principal: str | None = field(default=None)
    cnae_description: str | None = field(default=None)
    legal_nature: str | None = field(default=None)
    address: Address | None = field(default=None)
    capital_social: Money | None = field(default=None)
    company_size: CompanySize | None = field(default=None)
    partners: list[Partner] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def is_active(self) -> bool:
        return self.status == CompanyStatus.ATIVA

    def age_in_days(self) -> int | None:
        if not self.opening_date:
            return None
        return (datetime.now() - self.opening_date).days

    def is_recent(self, threshold_days: int = 365) -> bool:
        age = self.age_in_days()
        return age is not None and age < threshold_days

    def add_partner(self, partner: Partner) -> None:
        self.partners.append(partner)
