from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from trivaxion.domain.shared.entity import Entity
from trivaxion.domain.shared.value_objects import CNPJ, EntityId


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_COMPLETED = "partial_completed"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class DataSource(str, Enum):
    RECEITA_FEDERAL = "receita_federal"
    CERTIDAO_TRABALHISTA = "certidao_trabalhista"


@dataclass
class RiskSignal:
    source: str
    signal_type: str
    severity: str
    description: str
    weight: float
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class SourceResult:
    source: DataSource
    success: bool
    data: dict[str, object] | None = None
    error_message: str | None = None
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class Analysis(Entity):
    cnpj: CNPJ = field(default=None)
    organization_id: EntityId = field(default=None)
    requested_by: EntityId = field(default=None)
    status: AnalysisStatus = field(default=AnalysisStatus.PENDING)
    risk_level: RiskLevel = field(default=RiskLevel.UNKNOWN)
    risk_score: float = field(default=0.0)
    risk_signals: list[RiskSignal] = field(default_factory=list)
    source_results: list[SourceResult] = field(default_factory=list)
    started_at: datetime | None = field(default=None)
    completed_at: datetime | None = field(default=None)
    error_message: str | None = field(default=None)

    def start_processing(self) -> None:
        self.status = AnalysisStatus.PROCESSING
        self.started_at = datetime.now()

    def add_source_result(self, result: SourceResult) -> None:
        self.source_results.append(result)

    def add_risk_signal(self, signal: RiskSignal) -> None:
        self.risk_signals.append(signal)

    def calculate_risk_score(self) -> None:
        if not self.risk_signals:
            self.risk_score = 100.0
            self.risk_level = RiskLevel.LOW
            return

        total_weight = sum(signal.weight for signal in self.risk_signals)
        self.risk_score = max(0.0, 100.0 - total_weight)

        if self.risk_score >= 71:
            self.risk_level = RiskLevel.LOW
        elif self.risk_score >= 31:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.HIGH

    def complete(self) -> None:
        self.calculate_risk_score()
        all_success = all(r.success for r in self.source_results)
        any_success = any(r.success for r in self.source_results)

        if all_success:
            self.status = AnalysisStatus.COMPLETED
        elif any_success:
            self.status = AnalysisStatus.PARTIAL_COMPLETED
        else:
            self.status = AnalysisStatus.FAILED

        self.completed_at = datetime.now()

    def fail(self, error: str) -> None:
        self.status = AnalysisStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now()

    def is_completed(self) -> bool:
        return self.status in [
            AnalysisStatus.COMPLETED,
            AnalysisStatus.PARTIAL_COMPLETED,
            AnalysisStatus.FAILED,
        ]
