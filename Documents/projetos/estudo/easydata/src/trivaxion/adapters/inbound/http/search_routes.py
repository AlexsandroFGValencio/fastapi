from typing import Annotated

from fastapi import APIRouter, Depends, Query

from trivaxion.adapters.inbound.http.dependencies import CurrentUser, DBSession, get_search_port
from trivaxion.application.ports.search import SearchPort
from trivaxion.domain.search.search_query import SearchQuery, SearchResult, SearchType

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/companies")
async def search_companies(
    current_user: CurrentUser,
    session: DBSession,
    search_port: Annotated[SearchPort, Depends(get_search_port)],
    q: str = Query("", description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> SearchResult:
    """Busca empresas usando PostgreSQL Full-Text Search"""
    query = SearchQuery(
        query=q,
        search_type=SearchType.COMPANY,
        page=page,
        page_size=page_size,
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
    )
    
    return await search_port.search(query)


@router.get("/analyses")
async def search_analyses(
    current_user: CurrentUser,
    session: DBSession,
    search_port: Annotated[SearchPort, Depends(get_search_port)],
    q: str = Query("", description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> SearchResult:
    """Busca análises (implementação futura)"""
    query = SearchQuery(
        query=q,
        search_type=SearchType.ANALYSIS,
        page=page,
        page_size=page_size,
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
    )
    
    return await search_port.search(query)
