from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReceitaFederalRawData:
    cnpj: str
    razao_social: str | None = None
    nome_fantasia: str | None = None
    situacao_cadastral: str | None = None
    data_situacao_cadastral: datetime | None = None
    data_abertura: datetime | None = None
    cnae_fiscal: str | None = None
    cnae_fiscal_descricao: str | None = None
    natureza_juridica: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    municipio: str | None = None
    uf: str | None = None
    cep: str | None = None
    capital_social: str | None = None
    porte: str | None = None
    socios: list[dict[str, str]] | None = None
    raw_html: str | None = None
