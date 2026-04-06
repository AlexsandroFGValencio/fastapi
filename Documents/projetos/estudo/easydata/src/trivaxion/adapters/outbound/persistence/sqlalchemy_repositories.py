from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trivaxion.application.ports.repositories import (
    AnalysisRepository,
    AuditRepository,
    CompanyRepository,
    OrganizationRepository,
    ReportRepository,
    UserRepository,
)
from trivaxion.domain.analysis.analysis import Analysis, AnalysisStatus, DataSource, RiskLevel, RiskSignal, SourceResult
from trivaxion.domain.audit.audit_event import AuditEvent
from trivaxion.domain.companies.company import Company, CompanyStatus, Partner
from trivaxion.domain.identity.user import User
from trivaxion.domain.organizations.organization import Organization
from trivaxion.domain.reports.report import Report
from trivaxion.domain.shared.value_objects import Address, CNPJ, Email, EntityId, Money
from trivaxion.infrastructure.db.models import (
    AnalysisModel,
    AuditEventModel,
    CompanyModel,
    OrganizationModel,
    ReportModel,
    UserModel,
)


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> User:
        model = await self._session.get(UserModel, user.id.value)
        if model:
            model.email = str(user.email)
            model.full_name = user.full_name
            model.hashed_password = user.hashed_password
            model.role = user.role
            model.status = user.status
            model.organization_id = user.organization_id.value if user.organization_id else None
            model.last_login_at = user.last_login_at
        else:
            model = UserModel(
                id=user.id.value,
                email=str(user.email),
                full_name=user.full_name,
                hashed_password=user.hashed_password,
                role=user.role,
                status=user.status,
                organization_id=user.organization_id.value if user.organization_id else None,
                last_login_at=user.last_login_at,
            )
            self._session.add(model)
        
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, user_id: EntityId) -> User | None:
        model = await self._session.get(UserModel, user_id.value)
        return self._to_domain(model) if model else None

    async def find_by_email(self, email: Email) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == str(email))
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_organization(self, organization_id: EntityId) -> list[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.organization_id == organization_id.value)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def delete(self, user_id: EntityId) -> None:
        model = await self._session.get(UserModel, user_id.value)
        if model:
            await self._session.delete(model)
            await self._session.commit()

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=EntityId(model.id),
            email=Email(model.email),
            full_name=model.full_name,
            hashed_password=model.hashed_password,
            role=model.role,
            status=model.status,
            organization_id=EntityId(model.organization_id) if model.organization_id else None,
            last_login_at=model.last_login_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyOrganizationRepository(OrganizationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, organization: Organization) -> Organization:
        model = await self._session.get(OrganizationModel, organization.id.value)
        if model:
            model.name = organization.name
            model.cnpj = str(organization.cnpj) if organization.cnpj else None
            model.status = organization.status
            model.plan = organization.plan
            model.max_users = organization.max_users
            model.max_analyses_per_month = organization.max_analyses_per_month
            model.analyses_count_current_month = organization.analyses_count_current_month
        else:
            model = OrganizationModel(
                id=organization.id.value,
                name=organization.name,
                cnpj=str(organization.cnpj) if organization.cnpj else None,
                status=organization.status,
                plan=organization.plan,
                max_users=organization.max_users,
                max_analyses_per_month=organization.max_analyses_per_month,
                analyses_count_current_month=organization.analyses_count_current_month,
            )
            self._session.add(model)
        
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, organization_id: EntityId) -> Organization | None:
        model = await self._session.get(OrganizationModel, organization_id.value)
        return self._to_domain(model) if model else None

    async def find_all(self) -> list[Organization]:
        result = await self._session.execute(select(OrganizationModel))
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model: OrganizationModel) -> Organization:
        return Organization(
            id=EntityId(model.id),
            name=model.name,
            cnpj=CNPJ(model.cnpj) if model.cnpj else None,
            status=model.status,
            plan=model.plan,
            max_users=model.max_users,
            max_analyses_per_month=model.max_analyses_per_month,
            analyses_count_current_month=model.analyses_count_current_month,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyCompanyRepository(CompanyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, company: Company) -> Company:
        result = await self._session.execute(
            select(CompanyModel).where(CompanyModel.cnpj == str(company.cnpj))
        )
        model = result.scalar_one_or_none()
        
        # Endereço será salvo em colunas separadas
        
        partners_data = None
        if company.partners:
            partners_data = [
                {
                    "name": p.name,
                    "cpf_cnpj": p.cpf_cnpj,
                    "qualification": p.qualification,
                    "entry_date": p.entry_date.isoformat() if p.entry_date else None,
                }
                for p in company.partners
            ]
        
        if model:
            model.razao_social = company.razao_social
            model.nome_fantasia = company.nome_fantasia
            model.status = company.status
            model.opening_date = company.opening_date
            model.cnae_principal = company.cnae_principal
            model.cnae_description = company.cnae_description
            model.legal_nature = company.legal_nature
            if company.address:
                model.address_street = company.address.street
                model.address_number = company.address.number
                model.address_complement = company.address.complement
                model.address_neighborhood = company.address.neighborhood
                model.address_city = company.address.city
                model.address_state = company.address.state
                model.address_zipcode = company.address.zip_code
            model.capital_social = company.capital_social.amount if company.capital_social else None
            model.company_size = company.company_size.value if company.company_size else None
            model.partners_data = partners_data
            model.last_updated = company.last_updated
        else:
            model = CompanyModel(
                id=company.id.value,
                cnpj=str(company.cnpj),
                razao_social=company.razao_social,
                nome_fantasia=company.nome_fantasia,
                status=company.status,
                opening_date=company.opening_date,
                cnae_principal=company.cnae_principal,
                cnae_description=company.cnae_description,
                legal_nature=company.legal_nature,
                address_street=company.address.street if company.address else None,
                address_number=company.address.number if company.address else None,
                address_complement=company.address.complement if company.address else None,
                address_neighborhood=company.address.neighborhood if company.address else None,
                address_city=company.address.city if company.address else None,
                address_state=company.address.state if company.address else None,
                address_zipcode=company.address.zip_code if company.address else None,
                capital_social=company.capital_social.amount if company.capital_social else None,
                company_size=company.company_size.value if company.company_size else None,
                partners_data=partners_data,
                last_updated=company.last_updated,
            )
            self._session.add(model)
        
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, company_id: EntityId) -> Company | None:
        model = await self._session.get(CompanyModel, company_id.value)
        return self._to_domain(model) if model else None

    async def find_by_cnpj(self, cnpj: CNPJ) -> Company | None:
        result = await self._session.execute(
            select(CompanyModel).where(CompanyModel.cnpj == str(cnpj))
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_organization(self, organization_id: EntityId) -> list[Company]:
        return []

    def _to_domain(self, model: CompanyModel) -> Company:
        from datetime import datetime
        
        address = None
        if model.address_street:
            address = Address(
                street=model.address_street,
                number=model.address_number,
                complement=model.address_complement,
                neighborhood=model.address_neighborhood,
                city=model.address_city,
                state=model.address_state,
                zip_code=model.address_zipcode,
                country="Brasil",
            )
        
        partners = []
        if model.partners_data:
            for p_data in model.partners_data:
                partners.append(
                    Partner(
                        name=p_data["name"],
                        cpf_cnpj=p_data["cpf_cnpj"],
                        qualification=p_data["qualification"],
                        entry_date=datetime.fromisoformat(p_data["entry_date"]) if p_data.get("entry_date") else None,
                    )
                )
        
        return Company(
            id=EntityId(model.id),
            cnpj=CNPJ(model.cnpj),
            razao_social=model.razao_social,
            nome_fantasia=model.nome_fantasia,
            status=model.status,
            opening_date=model.opening_date,
            cnae_principal=model.cnae_principal,
            cnae_description=model.cnae_description,
            legal_nature=model.legal_nature,
            address=address,
            capital_social=Money(model.capital_social) if model.capital_social else None,
            partners=partners,
            last_updated=model.last_updated,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyAnalysisRepository(AnalysisRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, analysis: Analysis) -> Analysis:
        model = await self._session.get(AnalysisModel, analysis.id.value)
        
        risk_signals_data = [
            {
                "source": signal.source,
                "signal_type": signal.signal_type,
                "severity": signal.severity,
                "description": signal.description,
                "weight": signal.weight,
                "detected_at": signal.detected_at.isoformat(),
            }
            for signal in analysis.risk_signals
        ]
        
        source_results_data = [
            {
                "source": result.source.value,
                "success": result.success,
                "data": result.data,
                "error_message": result.error_message,
                "collected_at": result.collected_at.isoformat(),
            }
            for result in analysis.source_results
        ]
        
        if model:
            model.status = analysis.status
            model.risk_level = analysis.risk_level
            model.risk_score = analysis.risk_score
            model.risk_signals_data = risk_signals_data
            model.source_results_data = source_results_data
            model.started_at = analysis.started_at
            model.completed_at = analysis.completed_at
            model.error_message = analysis.error_message
        else:
            model = AnalysisModel(
                id=analysis.id.value,
                cnpj=str(analysis.cnpj),
                organization_id=analysis.organization_id.value,
                requested_by=analysis.requested_by.value,
                status=analysis.status,
                risk_level=analysis.risk_level,
                risk_score=analysis.risk_score,
                risk_signals_data=risk_signals_data,
                source_results_data=source_results_data,
                started_at=analysis.started_at,
                completed_at=analysis.completed_at,
                error_message=analysis.error_message,
            )
            self._session.add(model)
        
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, analysis_id: EntityId) -> Analysis | None:
        model = await self._session.get(AnalysisModel, analysis_id.value)
        return self._to_domain(model) if model else None

    async def find_by_organization(self, organization_id: EntityId, limit: int = 50) -> list[Analysis]:
        result = await self._session.execute(
            select(AnalysisModel)
            .where(AnalysisModel.organization_id == organization_id.value)
            .order_by(AnalysisModel.created_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def find_recent(self, organization_id: EntityId, limit: int = 10) -> list[Analysis]:
        result = await self._session.execute(
            select(AnalysisModel)
            .where(AnalysisModel.organization_id == organization_id.value)
            .where(AnalysisModel.status == AnalysisStatus.COMPLETED)
            .order_by(AnalysisModel.completed_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model: AnalysisModel) -> Analysis:
        from datetime import datetime
        
        risk_signals = []
        if model.risk_signals_data:
            for signal_data in model.risk_signals_data:
                risk_signals.append(
                    RiskSignal(
                        source=signal_data["source"],
                        signal_type=signal_data["signal_type"],
                        severity=signal_data["severity"],
                        description=signal_data["description"],
                        weight=signal_data["weight"],
                        detected_at=datetime.fromisoformat(signal_data["detected_at"]),
                    )
                )
        
        source_results = []
        if model.source_results_data:
            for result_data in model.source_results_data:
                source_results.append(
                    SourceResult(
                        source=DataSource(result_data["source"]),
                        success=result_data["success"],
                        data=result_data.get("data"),
                        error_message=result_data.get("error_message"),
                        collected_at=datetime.fromisoformat(result_data["collected_at"]),
                    )
                )
        
        return Analysis(
            id=EntityId(model.id),
            cnpj=CNPJ(model.cnpj),
            organization_id=EntityId(model.organization_id),
            requested_by=EntityId(model.requested_by),
            status=model.status,
            risk_level=model.risk_level,
            risk_score=model.risk_score,
            risk_signals=risk_signals,
            source_results=source_results,
            started_at=model.started_at,
            completed_at=model.completed_at,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyReportRepository(ReportRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, report: Report) -> Report:
        model = await self._session.get(ReportModel, report.id.value)
        if model:
            model.status = report.status
            model.content = report.content
            model.file_path = report.file_path
            model.generated_at = report.generated_at
            model.error_message = report.error_message
        else:
            model = ReportModel(
                id=report.id.value,
                analysis_id=report.analysis_id.value,
                organization_id=report.organization_id.value,
                format=report.format,
                status=report.status,
                content=report.content,
                file_path=report.file_path,
                generated_at=report.generated_at,
                error_message=report.error_message,
            )
            self._session.add(model)
        
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, report_id: EntityId) -> Report | None:
        model = await self._session.get(ReportModel, report_id.value)
        return self._to_domain(model) if model else None

    async def find_by_analysis(self, analysis_id: EntityId) -> list[Report]:
        result = await self._session.execute(
            select(ReportModel).where(ReportModel.analysis_id == analysis_id.value)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model: ReportModel) -> Report:
        return Report(
            id=EntityId(model.id),
            analysis_id=EntityId(model.analysis_id),
            organization_id=EntityId(model.organization_id),
            format=model.format,
            status=model.status,
            content=model.content,
            file_path=model.file_path,
            generated_at=model.generated_at,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLAlchemyAuditRepository(AuditRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, event: AuditEvent) -> AuditEvent:
        model = AuditEventModel(
            id=event.id.value,
            event_type=event.event_type,
            user_id=event.user_id.value if event.user_id else None,
            organization_id=event.organization_id.value if event.organization_id else None,
            resource_type=event.resource_type,
            resource_id=event.resource_id.value if event.resource_id else None,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            event_metadata=event.metadata,
            timestamp=event.timestamp,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def find_by_organization(self, organization_id: EntityId, limit: int = 100) -> list[AuditEvent]:
        result = await self._session.execute(
            select(AuditEventModel)
            .where(AuditEventModel.organization_id == organization_id.value)
            .order_by(AuditEventModel.timestamp.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def find_by_user(self, user_id: EntityId, limit: int = 100) -> list[AuditEvent]:
        result = await self._session.execute(
            select(AuditEventModel)
            .where(AuditEventModel.user_id == user_id.value)
            .order_by(AuditEventModel.timestamp.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    def _to_domain(self, model: AuditEventModel) -> AuditEvent:
        return AuditEvent(
            id=EntityId(model.id),
            event_type=model.event_type,
            user_id=EntityId(model.user_id) if model.user_id else None,
            organization_id=EntityId(model.organization_id) if model.organization_id else None,
            resource_type=model.resource_type,
            resource_id=EntityId(model.resource_id) if model.resource_id else None,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            metadata=model.event_metadata or {},
            timestamp=model.timestamp,
            created_at=model.created_at,
        )
