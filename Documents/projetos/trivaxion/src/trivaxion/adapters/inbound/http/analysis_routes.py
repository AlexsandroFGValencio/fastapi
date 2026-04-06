from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from trivaxion.adapters.inbound.http.dependencies import (
    CurrentUser,
    DBSession,
    get_analysis_repository,
    get_audit_repository,
    get_company_data_provider,
    get_company_repository,
    get_labor_certificate_provider,
    get_organization_repository,
    get_search_port,
)
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
from trivaxion.application.use_cases.analysis_use_cases import (
    CreateAnalysisUseCase,
    GetAnalysisUseCase,
    GetDashboardSummaryUseCase,
    ProcessAnalysisUseCase,
)
from trivaxion.domain.analysis.risk_engine import RiskEngine

router = APIRouter(prefix="/analyses", tags=["analyses"])


class CreateAnalysisRequestModel(BaseModel):
    cnpj: str
    sources: list[str] = []


class AnalysisResponseModel(BaseModel):
    id: str
    cnpj: str
    status: str
    risk_level: str
    risk_score: float
    organization_id: str
    requested_by: str
    created_at: str
    completed_at: str | None
    risk_signals_count: int
    company_name: str | None = None


class PaginatedAnalysisResponse(BaseModel):
    items: list[AnalysisResponseModel]
    total: int
    page: int
    per_page: int
    pages: int


@router.post("", response_model=AnalysisResponseModel)
async def create_analysis(
    request: CreateAnalysisRequestModel,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    session: DBSession,
    analysis_repository: Annotated[AnalysisRepository, Depends(get_analysis_repository)],
    company_repository: Annotated[CompanyRepository, Depends(get_company_repository)],
    organization_repository: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    audit_repository: Annotated[AuditRepository, Depends(get_audit_repository)],
    company_data_provider: Annotated[CompanyDataProvider, Depends(get_company_data_provider)],
    labor_certificate_provider: Annotated[LaborCertificateProvider, Depends(get_labor_certificate_provider)],
    search_port: Annotated[SearchPort, Depends(get_search_port)],
) -> AnalysisResponseModel:
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    use_case = CreateAnalysisUseCase(
        analysis_repository=analysis_repository,
        company_repository=company_repository,
        organization_repository=organization_repository,
        company_data_provider=company_data_provider,
        labor_certificate_provider=labor_certificate_provider,
        search_port=search_port,
        audit_repository=audit_repository,
        risk_engine=RiskEngine.default(),
    )
    
    dto_request = CreateAnalysisRequest(cnpj=request.cnpj, sources=request.sources)
    response = await use_case.execute(
        dto_request,
        str(current_user.organization_id),
        str(current_user.id),
    )
    
    process_use_case = ProcessAnalysisUseCase(
        analysis_repository=analysis_repository,
        company_repository=company_repository,
        company_data_provider=company_data_provider,
        labor_certificate_provider=labor_certificate_provider,
        search_port=search_port,
        audit_repository=audit_repository,
        risk_engine=RiskEngine.default(),
    )
    background_tasks.add_task(process_use_case.execute, response.id)
    
    return AnalysisResponseModel(**response.__dict__)


@router.get("", response_model=PaginatedAnalysisResponse)
async def list_analyses(
    current_user: CurrentUser,
    session: DBSession,
    analysis_repository: Annotated[AnalysisRepository, Depends(get_analysis_repository)],
    company_repository: Annotated[CompanyRepository, Depends(get_company_repository)],
    page: int = 1,
    per_page: int = 10,
    limit: int | None = None,
) -> PaginatedAnalysisResponse:
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    # Se limit for fornecido (para compatibilidade), use-o
    if limit:
        analyses = await analysis_repository.find_by_organization(
            current_user.organization_id,
            limit=limit,
        )
        items = [
            AnalysisResponseModel(
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
                company_name=None,
            )
            for a in analyses
        ]
        return PaginatedAnalysisResponse(
            items=items,
            total=len(items),
            page=1,
            per_page=limit,
            pages=1,
        )
    
    # Paginação normal
    all_analyses = await analysis_repository.find_by_organization(
        current_user.organization_id,
        limit=1000,  # Limite alto para pegar todos
    )
    
    total = len(all_analyses)
    pages = (total + per_page - 1) // per_page if total > 0 else 1
    page = max(1, min(page, pages))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_analyses = all_analyses[start_idx:end_idx]
    
    items = [
        AnalysisResponseModel(
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
            company_name=a.company_name,
        )
        for a in page_analyses
    ]
    
    return PaginatedAnalysisResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    current_user: CurrentUser,
    session: DBSession,
    analysis_repository: Annotated[AnalysisRepository, Depends(get_analysis_repository)],
    company_repository: Annotated[CompanyRepository, Depends(get_company_repository)],
) -> AnalysisDetailResponse:
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    use_case = GetAnalysisUseCase(
        analysis_repository=analysis_repository,
        company_repository=company_repository,
    )
    
    return await use_case.execute(analysis_id, str(current_user.organization_id))


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    current_user: CurrentUser,
    session: DBSession,
    analysis_repository: Annotated[AnalysisRepository, Depends(get_analysis_repository)],
) -> DashboardSummary:
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    use_case = GetDashboardSummaryUseCase(analysis_repository=analysis_repository)
    
    return await use_case.execute(str(current_user.organization_id))
