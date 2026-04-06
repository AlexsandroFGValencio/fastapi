from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SearchType(str, Enum):
    COMPANY = "company"
    ANALYSIS = "analysis"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass
class SearchFilter:
    field: str
    value: object
    operator: str = "eq"


@dataclass
class SearchQuery:
    query: str
    search_type: SearchType
    filters: list[SearchFilter] = field(default_factory=list)
    sort_by: str | None = None
    sort_order: SortOrder = SortOrder.DESC
    page: int = 1
    page_size: int = 20
    organization_id: str | None = None

    def add_filter(self, field: str, value: object, operator: str = "eq") -> None:
        self.filters.append(SearchFilter(field=field, value=value, operator=operator))


@dataclass
class SearchResult:
    total: int
    items: list[dict[str, object]]
    page: int
    page_size: int
    query: str
    took_ms: float = 0.0

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1
