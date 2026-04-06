from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from trivaxion.domain.shared.value_objects import CNPJ


@dataclass
class CompanyData:
    cnpj: str
    razao_social: str
    nome_fantasia: str | None
    situacao_cadastral: str
    data_abertura: datetime | None
    cnae_principal: str | None
    cnae_descricao: str | None
    natureza_juridica: str | None
    logradouro: str | None
    numero: str | None
    complemento: str | None
    bairro: str | None
    municipio: str | None
    uf: str | None
    cep: str | None
    capital_social: float | None
    porte: str | None
    telefone: str | None = None
    email: str | None = None
    socios: list[dict[str, object]] | None = None


@dataclass
class LaborCertificateData:
    cnpj: str
    status: str
    emissao: datetime | None
    validade: datetime | None
    numero_certidao: str | None
    mensagem: str | None


class CompanyDataProvider(ABC):
    @abstractmethod
    async def fetch_company_data(self, cnpj: CNPJ) -> CompanyData:
        pass


class LaborCertificateProvider(ABC):
    @abstractmethod
    async def fetch_certificate(self, cnpj: CNPJ) -> LaborCertificateData:
        pass
