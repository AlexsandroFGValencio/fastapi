from dataclasses import dataclass, field


@dataclass
class CreateAnalysisRequest:
    cnpj: str
    sources: list[str] = field(default_factory=list)


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
    processing: int
    completed_today: int
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    recent_analyses: list[AnalysisResponse] = field(default_factory=list)
