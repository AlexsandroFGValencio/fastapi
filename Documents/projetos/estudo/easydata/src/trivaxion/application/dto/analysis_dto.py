from dataclasses import dataclass


@dataclass
class CreateAnalysisRequest:
    cnpj: str


@dataclass
class AnalysisResponse:
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


@dataclass
class AnalysisDetailResponse:
    id: str
    cnpj: str
    status: str
    risk_level: str
    risk_score: float
    organization_id: str
    requested_by: str
    created_at: str
    completed_at: str | None
    risk_signals: list[dict[str, object]]
    source_results: list[dict[str, object]]
    company_data: dict[str, object] | None


@dataclass
class DashboardSummary:
    total_analyses: int
    analyses_this_month: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    recent_analyses: list[AnalysisResponse]
