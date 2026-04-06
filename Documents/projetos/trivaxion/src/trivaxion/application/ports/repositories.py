from abc import ABC, abstractmethod
from uuid import UUID

from trivaxion.domain.analysis.analysis import Analysis
from trivaxion.domain.audit.audit_event import AuditEvent
from trivaxion.domain.companies.company import Company
from trivaxion.domain.identity.user import User
from trivaxion.domain.organizations.organization import Organization
from trivaxion.domain.reports.report import Report
from trivaxion.domain.shared.value_objects import CNPJ, Email, EntityId


class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> User:
        pass

    @abstractmethod
    async def find_by_id(self, user_id: EntityId) -> User | None:
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> User | None:
        pass

    @abstractmethod
    async def find_by_organization(self, organization_id: EntityId) -> list[User]:
        pass

    @abstractmethod
    async def delete(self, user_id: EntityId) -> None:
        pass


class OrganizationRepository(ABC):
    @abstractmethod
    async def save(self, organization: Organization) -> Organization:
        pass

    @abstractmethod
    async def find_by_id(self, organization_id: EntityId) -> Organization | None:
        pass

    @abstractmethod
    async def find_all(self) -> list[Organization]:
        pass


class CompanyRepository(ABC):
    @abstractmethod
    async def save(self, company: Company) -> Company:
        pass

    @abstractmethod
    async def find_by_id(self, company_id: EntityId) -> Company | None:
        pass

    @abstractmethod
    async def find_by_cnpj(self, cnpj: CNPJ) -> Company | None:
        pass

    @abstractmethod
    async def find_by_organization(self, organization_id: EntityId) -> list[Company]:
        pass


class AnalysisRepository(ABC):
    @abstractmethod
    async def save(self, analysis: Analysis) -> Analysis:
        pass

    @abstractmethod
    async def find_by_id(self, analysis_id: EntityId) -> Analysis | None:
        pass

    @abstractmethod
    async def find_by_organization(
        self, organization_id: EntityId, limit: int = 50
    ) -> list[Analysis]:
        pass

    @abstractmethod
    async def find_recent(self, organization_id: EntityId, limit: int = 10) -> list[Analysis]:
        pass


class ReportRepository(ABC):
    @abstractmethod
    async def save(self, report: Report) -> Report:
        pass

    @abstractmethod
    async def find_by_id(self, report_id: EntityId) -> Report | None:
        pass

    @abstractmethod
    async def find_by_analysis(self, analysis_id: EntityId) -> list[Report]:
        pass


class AuditRepository(ABC):
    @abstractmethod
    async def save(self, event: AuditEvent) -> AuditEvent:
        pass

    @abstractmethod
    async def find_by_organization(
        self, organization_id: EntityId, limit: int = 100
    ) -> list[AuditEvent]:
        pass

    @abstractmethod
    async def find_by_user(self, user_id: EntityId, limit: int = 100) -> list[AuditEvent]:
        pass
