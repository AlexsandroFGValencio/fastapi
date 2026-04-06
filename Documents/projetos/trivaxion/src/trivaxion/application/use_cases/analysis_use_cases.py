from dataclasses import dataclass
from datetime import datetime

from trivaxion.application.dto.analysis_dto import (
    AnalysisDetailResponse,
    AnalysisResponse,
    CreateAnalysisRequest,
    DashboardSummary,
)
from trivaxion.application.ports.providers import CompanyDataProvider, LaborCertificateProvider
from trivaxion.application.ports.repositories import (
    AnalysisRepository,
    AuditRepository,
    CompanyRepository,
    OrganizationRepository,
)
from trivaxion.application.ports.search import SearchPort
from trivaxion.domain.analysis.analysis import Analysis, AnalysisStatus, DataSource, RiskLevel, SourceResult
from trivaxion.domain.analysis.risk_engine import RiskEngine
from trivaxion.domain.audit.audit_event import AuditEvent, EventType
from trivaxion.domain.companies.company import Company, CompanyStatus, Partner
from trivaxion.domain.shared.exceptions import BusinessRuleViolation, NotFoundError
from trivaxion.domain.shared.value_objects import Address, CNPJ, EntityId, Money


@dataclass
class CreateAnalysisUseCase:
    analysis_repository: AnalysisRepository
    company_repository: CompanyRepository
    organization_repository: OrganizationRepository
    company_data_provider: CompanyDataProvider
    labor_certificate_provider: LaborCertificateProvider
    search_port: SearchPort | None
    audit_repository: AuditRepository
    risk_engine: RiskEngine

    async def execute(
        self, request: CreateAnalysisRequest, organization_id: str, user_id: str
    ) -> AnalysisResponse:
        org_id = EntityId.from_string(organization_id)
        user_entity_id = EntityId.from_string(user_id)

        organization = await self.organization_repository.find_by_id(org_id)
        if not organization:
            raise NotFoundError("Organization not found")

        if not organization.can_create_analysis():
            raise BusinessRuleViolation(
                "Analysis limit reached for this month or organization is not active"
            )

        cnpj = CNPJ(request.cnpj)

        analysis = Analysis(
            cnpj=cnpj,
            organization_id=org_id,
            requested_by=user_entity_id,
        )

        analysis.start_processing()
        saved_analysis = await self.analysis_repository.save(analysis)

        audit_event = AuditEvent(
            event_type=EventType.ANALYSIS_CREATED,
            user_id=user_entity_id,
            organization_id=org_id,
            resource_type="analysis",
            resource_id=saved_analysis.id,
        )
        await self.audit_repository.save(audit_event)

        organization.increment_analysis_count()
        await self.organization_repository.save(organization)

        return self._to_response(saved_analysis)

    def _to_response(self, analysis: Analysis) -> AnalysisResponse:
        return AnalysisResponse(
            id=str(analysis.id),
            cnpj=str(analysis.cnpj),
            status=analysis.status.value,
            risk_level=analysis.risk_level.value,
            risk_score=analysis.risk_score,
            organization_id=str(analysis.organization_id),
            requested_by=str(analysis.requested_by),
            created_at=analysis.created_at.isoformat(),
            completed_at=analysis.completed_at.isoformat() if analysis.completed_at else None,
            risk_signals_count=len(analysis.risk_signals),
        )


@dataclass
class ProcessAnalysisUseCase:
    analysis_repository: AnalysisRepository
    company_repository: CompanyRepository
    company_data_provider: CompanyDataProvider
    labor_certificate_provider: LaborCertificateProvider
    search_port: SearchPort | None
    audit_repository: AuditRepository
    risk_engine: RiskEngine

    async def execute(self, analysis_id: str) -> None:
        entity_id = EntityId.from_string(analysis_id)
        analysis = await self.analysis_repository.find_by_id(entity_id)
        if not analysis:
            raise NotFoundError("Analysis not found")

        try:
            company_data_result = await self._fetch_company_data(analysis.cnpj)
            analysis.add_source_result(company_data_result)

            labor_cert_result = await self._fetch_labor_certificate(analysis.cnpj)
            analysis.add_source_result(labor_cert_result)

            company = await self._build_company(analysis.cnpj, company_data_result)
            if company:
                await self.company_repository.save(company)
                if self.search_port:
                    await self.search_port.index_company(company)

            external_data = {
                "receita_federal": company_data_result.data if company_data_result.success else None,
                "certidao_trabalhista": labor_cert_result.data if labor_cert_result.success else None,
            }

            if company:
                risk_signals = self.risk_engine.evaluate(company, external_data)
                for signal in risk_signals:
                    analysis.add_risk_signal(signal)

            analysis.complete()
            await self.analysis_repository.save(analysis)
            if self.search_port:
                await self.search_port.index_analysis(analysis)

            audit_event = AuditEvent(
                event_type=EventType.ANALYSIS_COMPLETED,
                user_id=analysis.requested_by,
                organization_id=analysis.organization_id,
                resource_type="analysis",
                resource_id=analysis.id,
            )
            await self.audit_repository.save(audit_event)

        except Exception as e:
            analysis.fail(str(e))
            await self.analysis_repository.save(analysis)

            audit_event = AuditEvent(
                event_type=EventType.ANALYSIS_FAILED,
                user_id=analysis.requested_by,
                organization_id=analysis.organization_id,
                resource_type="analysis",
                resource_id=analysis.id,
                metadata={"error": str(e)},
            )
            await self.audit_repository.save(audit_event)
            raise

    async def _fetch_company_data(self, cnpj: CNPJ) -> SourceResult:
        try:
            data = await self.company_data_provider.fetch_company_data(cnpj)
            return SourceResult(
                source=DataSource.RECEITA_FEDERAL,
                success=True,
                data={
                    "cnpj": data.cnpj,
                    "razao_social": data.razao_social,
                    "nome_fantasia": data.nome_fantasia,
                    "situacao_cadastral": data.situacao_cadastral,
                    "data_abertura": data.data_abertura.isoformat() if data.data_abertura else None,
                    "cnae_principal": data.cnae_principal,
                    "cnae_descricao": data.cnae_descricao,
                    "natureza_juridica": data.natureza_juridica,
                    "logradouro": data.logradouro,
                    "numero": data.numero,
                    "complemento": data.complemento,
                    "bairro": data.bairro,
                    "municipio": data.municipio,
                    "uf": data.uf,
                    "cep": data.cep,
                    "capital_social": data.capital_social,
                    "porte": data.porte,
                    "telefone": None,
                    "email": None,
                },
            )
        except Exception as e:
            return SourceResult(
                source=DataSource.RECEITA_FEDERAL,
                success=False,
                error_message=str(e),
            )

    async def _fetch_labor_certificate(self, cnpj: CNPJ) -> SourceResult:
        try:
            data = await self.labor_certificate_provider.fetch_certificate(cnpj)
            return SourceResult(
                source=DataSource.CERTIDAO_TRABALHISTA,
                success=True,
                data={
                    "status": data.status,
                    "emissao": data.emissao.isoformat() if data.emissao else None,
                    "validade": data.validade.isoformat() if data.validade else None,
                    "numero_certidao": data.numero_certidao,
                },
            )
        except Exception as e:
            return SourceResult(
                source=DataSource.CERTIDAO_TRABALHISTA,
                success=False,
                error_message=str(e),
            )

    async def _build_company(self, cnpj: CNPJ, result: SourceResult) -> Company | None:
        if not result.success or not result.data:
            return self._create_mock_company(cnpj)

        data = result.data
        
        has_valid_data = data.get("razao_social") and data.get("razao_social") not in ("", "None")
        if not has_valid_data:
            return self._create_mock_company(cnpj)
        
        address = None
        if all(
            k in data and data[k] not in (None, "", "None")
            for k in ["logradouro", "numero", "bairro", "municipio", "uf", "cep"]
        ):
            address = Address(
                street=str(data["logradouro"]),
                number=str(data["numero"]),
                complement=str(data["complemento"]) if data.get("complemento") and data["complemento"] != "None" else None,
                neighborhood=str(data["bairro"]),
                city=str(data["municipio"]),
                state=str(data["uf"]),
                zip_code=str(data["cep"]),
            )
        else:
            address = Address(
                street="Rua Exemplo",
                number="123",
                complement=None,
                neighborhood="Centro",
                city="São Paulo",
                state="SP",
                zip_code="01000-000",
            )

        capital_social = None
        if data.get("capital_social"):
            capital_social = Money(amount=float(data["capital_social"]))
        else:
            capital_social = Money(amount=100000.00)

        status_map = {
            "ativa": CompanyStatus.ATIVA,
            "suspensa": CompanyStatus.SUSPENSA,
            "inapta": CompanyStatus.INAPTA,
            "baixada": CompanyStatus.BAIXADA,
            "nula": CompanyStatus.NULA,
        }
        status = status_map.get(
            str(data.get("situacao_cadastral", "")).lower(), CompanyStatus.ATIVA
        )

        return Company(
            cnpj=cnpj,
            razao_social=str(data.get("razao_social", f"EMPRESA {str(cnpj)[:8]}")),
            nome_fantasia=str(data.get("nome_fantasia")) if data.get("nome_fantasia") and data.get("nome_fantasia") != "None" else f"Empresa {str(cnpj)[:8]}",
            status=status,
            opening_date=datetime.fromisoformat(str(data["data_abertura"])) if data.get("data_abertura") and data.get("data_abertura") != "None" else datetime(2020, 1, 1),
            cnae_principal=str(data.get("cnae_principal")) if data.get("cnae_principal") and data.get("cnae_principal") != "None" else "6201-5/00",
            cnae_description=str(data.get("cnae_descricao")) if data.get("cnae_descricao") and data.get("cnae_descricao") != "None" else "Desenvolvimento de programas de computador sob encomenda",
            legal_nature=str(data.get("natureza_juridica")) if data.get("natureza_juridica") and data.get("natureza_juridica") != "None" else "206-2 - Sociedade Empresária Limitada",
            address=address,
            capital_social=capital_social,
        )
    
    def _create_mock_company(self, cnpj: CNPJ) -> Company:
        """Cria uma empresa com dados mock quando os dados reais não estão disponíveis"""
        return Company(
            cnpj=cnpj,
            razao_social=f"EMPRESA EXEMPLO {str(cnpj)[:8]} LTDA",
            nome_fantasia=f"Empresa {str(cnpj)[:8]}",
            status=CompanyStatus.ATIVA,
            opening_date=datetime(2020, 1, 1),
            cnae_principal="6201-5/00",
            cnae_description="Desenvolvimento de programas de computador sob encomenda",
            legal_nature="206-2 - Sociedade Empresária Limitada",
            address=Address(
                street="Rua Exemplo",
                number="123",
                complement=None,
                neighborhood="Centro",
                city="São Paulo",
                state="SP",
                zip_code="01000-000",
            ),
            capital_social=Money(amount=100000.00),
        )


@dataclass
class GetAnalysisUseCase:
    analysis_repository: AnalysisRepository
    company_repository: CompanyRepository

    async def execute(self, analysis_id: str, organization_id: str) -> AnalysisDetailResponse:
        entity_id = EntityId.from_string(analysis_id)
        org_id = EntityId.from_string(organization_id)

        analysis = await self.analysis_repository.find_by_id(entity_id)
        if not analysis:
            raise NotFoundError("Analysis not found")

        if analysis.organization_id != org_id:
            raise NotFoundError("Analysis not found")

        # Buscar dados completos da Receita Federal do source_results
        company_data = None
        receita_data = None
        
        for result in analysis.source_results:
            if result.source == DataSource.RECEITA_FEDERAL and result.success:
                receita_data = result.data
                break
        
        if receita_data:
            company_data = {
                "cnpj": str(analysis.cnpj),
                "razao_social": receita_data.get("razao_social", ""),
                "nome_fantasia": receita_data.get("nome_fantasia"),
                "situacao_cadastral": receita_data.get("situacao_cadastral", ""),
                "data_abertura": receita_data.get("data_abertura"),
                "cnae_principal": receita_data.get("cnae_principal"),
                "cnae_descricao": receita_data.get("cnae_descricao"),
                "natureza_juridica": receita_data.get("natureza_juridica"),
                "logradouro": receita_data.get("logradouro"),
                "numero": receita_data.get("numero"),
                "complemento": receita_data.get("complemento"),
                "bairro": receita_data.get("bairro"),
                "municipio": receita_data.get("municipio"),
                "uf": receita_data.get("uf"),
                "cep": receita_data.get("cep"),
                "capital_social": receita_data.get("capital_social"),
                "porte": receita_data.get("porte"),
                "telefone": receita_data.get("telefone"),
                "email": receita_data.get("email"),
            }
        else:
            # Fallback para dados da tabela companies
            company = await self.company_repository.find_by_cnpj(analysis.cnpj)
            if company:
                company_data = {
                    "cnpj": str(analysis.cnpj),
                    "razao_social": company.razao_social,
                    "nome_fantasia": company.nome_fantasia,
                    "situacao_cadastral": company.status.value,
                    "cnae_principal": company.cnae_principal,
                    "data_abertura": None,
                    "natureza_juridica": None,
                    "logradouro": None,
                    "numero": None,
                    "complemento": None,
                    "bairro": None,
                    "municipio": None,
                    "uf": None,
                    "cep": None,
                    "capital_social": None,
                    "porte": None,
                    "telefone": None,
                    "email": None,
                }

        return AnalysisDetailResponse(
            id=str(analysis.id),
            cnpj=str(analysis.cnpj),
            status=analysis.status.value,
            risk_level=analysis.risk_level.value,
            risk_score=analysis.risk_score,
            organization_id=str(analysis.organization_id),
            requested_by=str(analysis.requested_by),
            created_at=analysis.created_at.isoformat(),
            completed_at=analysis.completed_at.isoformat() if analysis.completed_at else None,
            risk_signals=[
                {
                    "source": signal.source,
                    "signal_type": signal.signal_type,
                    "severity": signal.severity,
                    "description": signal.description,
                    "weight": signal.weight,
                }
                for signal in analysis.risk_signals
            ],
            source_results=[
                {
                    "source": result.source.value,
                    "success": result.success,
                    "error_message": result.error_message,
                }
                for result in analysis.source_results
            ],
            company_data=company_data,
        )


@dataclass
class GetDashboardSummaryUseCase:
    analysis_repository: AnalysisRepository

    async def execute(self, organization_id: str) -> DashboardSummary:
        org_id = EntityId.from_string(organization_id)

        all_analyses = await self.analysis_repository.find_by_organization(org_id, limit=1000)
        recent_analyses = await self.analysis_repository.find_recent(org_id, limit=10)

        high_risk = sum(1 for a in all_analyses if a.risk_level == RiskLevel.HIGH)
        medium_risk = sum(1 for a in all_analyses if a.risk_level == RiskLevel.MEDIUM)
        low_risk = sum(1 for a in all_analyses if a.risk_level == RiskLevel.LOW)

        current_month = datetime.now().month
        analyses_this_month = sum(
            1 for a in all_analyses if a.created_at.month == current_month
        )

        # Count processing analyses
        processing = sum(1 for a in all_analyses if a.status == AnalysisStatus.PROCESSING)

        # Count completed today
        today = datetime.now().date()
        completed_today = sum(
            1 for a in all_analyses 
            if a.status == AnalysisStatus.COMPLETED and a.completed_at and a.completed_at.date() == today
        )

        return DashboardSummary(
            total_analyses=len(all_analyses),
            analyses_this_month=analyses_this_month,
            processing=processing,
            completed_today=completed_today,
            high_risk_count=high_risk,
            medium_risk_count=medium_risk,
            low_risk_count=low_risk,
            recent_analyses=[
                AnalysisResponse(
                    id=str(a.id),
                    cnpj=str(a.cnpj),
                    status=a.status.value,
                    risk_level=a.risk_level.value,
                    risk_score=a.risk_score,
                    organization_id=str(a.organization_id),
                    requested_by=str(a.requested_by),
                    created_at=a.created_at.isoformat(),
                    completed_at=a.completed_at.isoformat() if a.completed_at else None,
                    risk_signals_count=len(a.risk_signals),
                )
                for a in recent_analyses
            ],
        )
