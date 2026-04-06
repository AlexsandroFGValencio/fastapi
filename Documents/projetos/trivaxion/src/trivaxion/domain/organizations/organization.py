from dataclasses import dataclass, field
from enum import Enum

from trivaxion.domain.shared.entity import Entity
from trivaxion.domain.shared.value_objects import CNPJ


class OrganizationStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"


class PlanType(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class Organization(Entity):
    name: str = field(default="")
    cnpj: CNPJ | None = field(default=None)
    status: OrganizationStatus = field(default=OrganizationStatus.TRIAL)
    plan: PlanType = field(default=PlanType.FREE)
    max_users: int = field(default=5)
    max_analyses_per_month: int = field(default=100)
    analyses_count_current_month: int = field(default=0)

    def is_active(self) -> bool:
        return self.status == OrganizationStatus.ACTIVE

    def can_create_analysis(self) -> bool:
        if not self.is_active():
            return False
        return self.analyses_count_current_month < self.max_analyses_per_month

    def increment_analysis_count(self) -> None:
        self.analyses_count_current_month += 1

    def reset_monthly_count(self) -> None:
        self.analyses_count_current_month = 0

    def upgrade_plan(self, plan: PlanType) -> None:
        self.plan = plan
        self._update_limits()

    def _update_limits(self) -> None:
        limits = {
            PlanType.FREE: (5, 100),
            PlanType.STARTER: (10, 500),
            PlanType.PROFESSIONAL: (50, 2000),
            PlanType.ENTERPRISE: (999, 99999),
        }
        self.max_users, self.max_analyses_per_month = limits[self.plan]
