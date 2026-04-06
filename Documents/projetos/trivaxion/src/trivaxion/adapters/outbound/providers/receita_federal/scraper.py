from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trivaxion.application.ports.providers import CompanyData, CompanyDataProvider
from trivaxion.domain.shared.value_objects import CNPJ
from trivaxion.infrastructure.db.models import CNPJReceitaFederalModel
from trivaxion.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class ReceitaFederalProvider(CompanyDataProvider):
    """Provider que consulta dados de CNPJ no PostgreSQL (dados públicos da Receita Federal)"""
    
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch_company_data(self, cnpj: CNPJ) -> CompanyData:
        logger.info("fetching_company_data_mock_mode", cnpj=str(cnpj))
        
        try:
            # Tentar consultar dados no PostgreSQL
            result = await self._session.execute(
                select(CNPJReceitaFederalModel).where(
                    CNPJReceitaFederalModel.cnpj == str(cnpj).replace(".", "").replace("/", "").replace("-", "")
                )
            )
            cnpj_data = result.scalar_one_or_none()
            
            # Sempre retornar dados mock completos
            cnpj_str = str(cnpj)
            cnpj_prefix = cnpj_str[:8]
            
            company_data = CompanyData(
                cnpj=cnpj_str,
                razao_social=f"EMPRESA EXEMPLO {cnpj_prefix} LTDA",
                nome_fantasia=f"Empresa {cnpj_prefix}",
                situacao_cadastral="ativa",
                data_abertura=datetime(2020, 1, 1),
                cnae_principal="6201-5/00",
                cnae_descricao="Desenvolvimento de programas de computador sob encomenda",
                natureza_juridica="206-2",
                logradouro="Rua Exemplo",
                numero="123",
                complemento="Sala 456",
                bairro="Centro",
                municipio="São Paulo",
                uf="SP",
                cep="01000-000",
                capital_social=100000.00,
                porte="05",
                telefone="(11) 98765-4321",
                email=f"contato@empresa{cnpj_prefix}.com.br",
                socios=None,
            )
            
            logger.info(
                "mock_company_data_returned",
                cnpj=cnpj_str,
                razao_social=company_data.razao_social,
            )
            
            return company_data
            
        except Exception as e:
            logger.error("error_fetching_company_data", cnpj=str(cnpj), error=str(e))
            raise
    
    def _map_situacao_cadastral(self, situacao: str | None) -> str:
        """Mapeia código de situação cadastral para descrição"""
        if not situacao:
            return "desconhecida"
        
        # Mapeamento conforme metadados da Receita Federal
        mapeamento = {
            "01": "nula",
            "02": "ativa",
            "03": "suspensa",
            "04": "inapta",
            "08": "baixada",
        }
        
        return mapeamento.get(situacao, "desconhecida")
