from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from trivaxion.adapters.outbound.config.json_source_config_provider import JsonSourceConfigProvider
from trivaxion.adapters.outbound.persistence.sqlalchemy_repositories import (
    SQLAlchemyAnalysisRepository,
    SQLAlchemyAuditRepository,
    SQLAlchemyCompanyRepository,
    SQLAlchemyOrganizationRepository,
    SQLAlchemyReportRepository,
    SQLAlchemyUserRepository,
)
from trivaxion.adapters.outbound.providers.certidao_trabalhista.scraper import (
    CertidaoTrabalhistaProvider,
)
from trivaxion.adapters.outbound.providers.receita_federal.scraper import ReceitaFederalProvider
from trivaxion.adapters.outbound.search.elasticsearch_adapter import ElasticsearchAdapter
from trivaxion.application.ports.auth import PasswordHasher, TokenService
from trivaxion.application.ports.providers import CompanyDataProvider, LaborCertificateProvider
from trivaxion.application.ports.repositories import (
    AnalysisRepository,
    AuditRepository,
    CompanyRepository,
    OrganizationRepository,
    ReportRepository,
    UserRepository,
)
from trivaxion.application.ports.search import SearchPort
from trivaxion.application.ports.source_config import SourceConfigProvider
from trivaxion.infrastructure.config.settings import Settings, get_settings
from trivaxion.infrastructure.security.jwt import JWTTokenService
from trivaxion.infrastructure.security.password import BcryptPasswordHasher


class Container:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._password_hasher: PasswordHasher | None = None
        self._token_service: TokenService | None = None
        self._search_port: SearchPort | None = None
        self._company_data_provider: CompanyDataProvider | None = None
        self._labor_certificate_provider: LaborCertificateProvider | None = None
        self._source_config_provider: SourceConfigProvider | None = None

    @property
    def settings(self) -> Settings:
        return self._settings

    def get_password_hasher(self) -> PasswordHasher:
        if self._password_hasher is None:
            self._password_hasher = BcryptPasswordHasher()
        return self._password_hasher

    def get_token_service(self) -> TokenService:
        if self._token_service is None:
            self._token_service = JWTTokenService(self._settings)
        return self._token_service

    def get_search_port(self) -> SearchPort:
        if self._search_port is None:
            self._search_port = ElasticsearchAdapter(self._settings)
        return self._search_port

    def get_company_data_provider(self) -> CompanyDataProvider:
        if self._company_data_provider is None:
            self._company_data_provider = ReceitaFederalProvider(self._settings)
        return self._company_data_provider

    def get_labor_certificate_provider(self) -> LaborCertificateProvider:
        if self._labor_certificate_provider is None:
            self._labor_certificate_provider = CertidaoTrabalhistaProvider(self._settings)
        return self._labor_certificate_provider

    def get_source_config_provider(self) -> SourceConfigProvider:
        if self._source_config_provider is None:
            self._source_config_provider = JsonSourceConfigProvider(self._settings)
        return self._source_config_provider

    def get_user_repository(self, session: AsyncSession) -> UserRepository:
        return SQLAlchemyUserRepository(session)

    def get_organization_repository(self, session: AsyncSession) -> OrganizationRepository:
        return SQLAlchemyOrganizationRepository(session)

    def get_company_repository(self, session: AsyncSession) -> CompanyRepository:
        return SQLAlchemyCompanyRepository(session)

    def get_analysis_repository(self, session: AsyncSession) -> AnalysisRepository:
        return SQLAlchemyAnalysisRepository(session)

    def get_report_repository(self, session: AsyncSession) -> ReportRepository:
        return SQLAlchemyReportRepository(session)

    def get_audit_repository(self, session: AsyncSession) -> AuditRepository:
        return SQLAlchemyAuditRepository(session)


@lru_cache
def get_container() -> Container:
    settings = get_settings()
    return Container(settings)
