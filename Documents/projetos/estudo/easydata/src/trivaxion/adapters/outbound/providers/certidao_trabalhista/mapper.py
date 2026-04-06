from trivaxion.adapters.outbound.providers.certidao_trabalhista.models import (
    CertidaoTrabalhistaRawData,
)
from trivaxion.application.ports.providers import LaborCertificateData


class CertidaoTrabalhistaMapper:
    @staticmethod
    def to_labor_certificate_data(raw_data: CertidaoTrabalhistaRawData) -> LaborCertificateData:
        return LaborCertificateData(
            cnpj=raw_data.cnpj,
            status=raw_data.status or "desconhecida",
            emissao=raw_data.data_emissao,
            validade=raw_data.data_validade,
            numero_certidao=raw_data.numero_certidao,
            mensagem=raw_data.mensagem_oficial,
        )
