from abc import ABC, abstractmethod

from trivaxion.domain.analysis.analysis import Analysis
from trivaxion.domain.companies.company import Company
from trivaxion.domain.search.search_query import SearchQuery, SearchResult
from trivaxion.domain.shared.value_objects import EntityId


class SearchPort(ABC):
    @abstractmethod
    async def index_company(self, company: Company) -> None:
        pass

    @abstractmethod
    async def index_analysis(self, analysis: Analysis) -> None:
        pass

    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResult:
        pass

    @abstractmethod
    async def delete_company(self, company_id: EntityId) -> None:
        pass

    @abstractmethod
    async def delete_analysis(self, analysis_id: EntityId) -> None:
        pass

    @abstractmethod
    async def reindex_all(self) -> None:
        pass
