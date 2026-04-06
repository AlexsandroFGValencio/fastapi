from dataclasses import dataclass
from datetime import datetime


@dataclass
class CertidaoTrabalhistaRawData:
    cnpj: str
    status: str | None = None
    data_emissao: datetime | None = None
    data_validade: datetime | None = None
    numero_certidao: str | None = None
    mensagem_oficial: str | None = None
    codigo_validacao: str | None = None
    raw_html: str | None = None
