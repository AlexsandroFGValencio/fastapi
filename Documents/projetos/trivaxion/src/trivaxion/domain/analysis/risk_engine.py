from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from trivaxion.domain.analysis.analysis import RiskSignal
from trivaxion.domain.companies.company import Company, CompanyStatus


class RiskRule(ABC):
    @abstractmethod
    def evaluate(self, company: Company, external_data: dict[str, object]) -> list[RiskSignal]:
        pass


class InactiveCompanyRule(RiskRule):
    def evaluate(self, company: Company, external_data: dict[str, object]) -> list[RiskSignal]:
        signals = []
        if company.status != CompanyStatus.ATIVA:
            signals.append(
                RiskSignal(
                    source="company_status",
                    signal_type="inactive_company",
                    severity="high",
                    description=f"Empresa com situação cadastral: {company.status.value}",
                    weight=40.0,
                )
            )
        return signals


class RecentCompanyRule(RiskRule):
    def __init__(self, threshold_days: int = 365) -> None:
        self.threshold_days = threshold_days

    def evaluate(self, company: Company, external_data: dict[str, object]) -> list[RiskSignal]:
        signals = []
        if company.is_recent(self.threshold_days):
            age_days = company.age_in_days()
            signals.append(
                RiskSignal(
                    source="company_age",
                    signal_type="recent_company",
                    severity="medium",
                    description=f"Empresa recente com {age_days} dias de abertura",
                    weight=15.0,
                )
            )
        return signals


class LaborCertificateRule(RiskRule):
    def evaluate(self, company: Company, external_data: dict[str, object]) -> list[RiskSignal]:
        signals = []
        labor_cert = external_data.get("certidao_trabalhista")
        if labor_cert and isinstance(labor_cert, dict):
            status = labor_cert.get("status")
            if status == "positiva":
                signals.append(
                    RiskSignal(
                        source="certidao_trabalhista",
                        signal_type="positive_labor_certificate",
                        severity="high",
                        description="Certidão trabalhista positiva - empresa possui débitos trabalhistas",
                        weight=35.0,
                    )
                )
        return signals


class IncompleteDataRule(RiskRule):
    def evaluate(self, company: Company, external_data: dict[str, object]) -> list[RiskSignal]:
        signals = []
        missing_fields = []

        if not company.razao_social:
            missing_fields.append("razão social")
        if not company.cnae_principal:
            missing_fields.append("CNAE")
        if not company.address:
            missing_fields.append("endereço")

        if missing_fields:
            signals.append(
                RiskSignal(
                    source="data_quality",
                    signal_type="incomplete_data",
                    severity="medium",
                    description=f"Dados incompletos: {', '.join(missing_fields)}",
                    weight=10.0,
                )
            )
        return signals


@dataclass
class RiskEngine:
    rules: list[RiskRule]

    @classmethod
    def default(cls) -> "RiskEngine":
        return cls(
            rules=[
                InactiveCompanyRule(),
                RecentCompanyRule(),
                LaborCertificateRule(),
                IncompleteDataRule(),
            ]
        )

    def evaluate(self, company: Company, external_data: dict[str, object]) -> list[RiskSignal]:
        all_signals = []
        for rule in self.rules:
            signals = rule.evaluate(company, external_data)
            all_signals.extend(signals)
        return all_signals

    def add_rule(self, rule: RiskRule) -> None:
        self.rules.append(rule)
