from datetime import datetime, timedelta

from trivaxion.adapters.outbound.providers.certidao_trabalhista.client import (
    CertidaoTrabalhistaClient,
)
from trivaxion.adapters.outbound.providers.certidao_trabalhista.mapper import (
    CertidaoTrabalhistaMapper,
)
from trivaxion.adapters.outbound.providers.certidao_trabalhista.parser import (
    CertidaoTrabalhistaParser,
)
from trivaxion.application.ports.providers import LaborCertificateData, LaborCertificateProvider
from trivaxion.domain.shared.value_objects import CNPJ
from trivaxion.infrastructure.config.settings import Settings
from trivaxion.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CertidaoTrabalhistaProvider(LaborCertificateProvider):
    def __init__(self, settings: Settings) -> None:
        self._client = CertidaoTrabalhistaClient(settings)
        self._parser = CertidaoTrabalhistaParser()
        self._mapper = CertidaoTrabalhistaMapper()

    async def fetch_certificate(self, cnpj: CNPJ) -> LaborCertificateData:
        logger.info("returning_mock_certidao_trabalhista", cnpj=str(cnpj))
        
        try:
            # Sempre retornar dados mock de certidão positiva (sem débitos)
            now = datetime.now()
            certificate_data = LaborCertificateData(
                status="POSITIVA",
                emissao=now,
                validade=now + timedelta(days=180),
                numero_certidao=f"CERT-{str(cnpj)[:8]}-{now.strftime('%Y%m%d')}",
            )
            
            logger.info(
                "mock_certidao_trabalhista_returned",
                cnpj=str(cnpj),
                status=certificate_data.status,
            )
            
            return certificate_data
            
        except Exception as e:
            logger.error("certidao_trabalhista_mock_failed", cnpj=str(cnpj), error=str(e))
            raise
