"""
Implementação de busca usando PostgreSQL Full-Text Search
"""
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from trivaxion.application.ports.search import SearchPort
from trivaxion.domain.search.search_query import SearchQuery, SearchResult, SearchType
from trivaxion.infrastructure.db.models import CNPJReceitaFederalModel
from trivaxion.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class PostgreSQLSearchAdapter(SearchPort):
    """Adapter de busca usando PostgreSQL Full-Text Search"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def search(self, query: SearchQuery) -> SearchResult:
        """Executa busca usando PostgreSQL Full-Text Search"""
        logger.info("executing_postgresql_search", 
                   query=query.query, 
                   search_type=query.search_type.value)
        
        if query.search_type == SearchType.COMPANY:
            return await self._search_companies(query)
        elif query.search_type == SearchType.ANALYSIS:
            return await self._search_analyses(query)
        else:
            return SearchResult(
                items=[],
                total=0,
                page=query.page,
                page_size=query.page_size,
                query=query.query,
            )
    
    async def _search_companies(self, query: SearchQuery) -> SearchResult:
        """Busca empresas usando Full-Text Search"""
        
        if not query.query or len(query.query.strip()) == 0:
            # Sem query, retornar lista paginada
            stmt = select(CNPJReceitaFederalModel).limit(query.page_size).offset(
                (query.page - 1) * query.page_size
            )
            count_stmt = select(func.count(CNPJReceitaFederalModel.cnpj))
        else:
            # Com query, usar Full-Text Search
            search_query = query.query.strip()
            
            # Criar tsquery
            ts_query = func.plainto_tsquery('portuguese', search_query)
            
            # Buscar usando tsvector
            stmt = (
                select(CNPJReceitaFederalModel)
                .where(
                    or_(
                        # Full-text search
                        CNPJReceitaFederalModel.search_vector.op('@@')(ts_query),
                        # Busca exata em CNPJ (sem formatação)
                        CNPJReceitaFederalModel.cnpj.like(f"%{search_query.replace('.', '').replace('/', '').replace('-', '')}%"),
                        # Busca parcial em razão social
                        CNPJReceitaFederalModel.razao_social.ilike(f"%{search_query}%"),
                        # Busca parcial em nome fantasia
                        CNPJReceitaFederalModel.nome_fantasia.ilike(f"%{search_query}%"),
                    )
                )
                .order_by(
                    func.ts_rank(
                        CNPJReceitaFederalModel.search_vector,
                        ts_query
                    ).desc()
                )
                .limit(query.page_size)
                .offset((query.page - 1) * query.page_size)
            )
            
            count_stmt = (
                select(func.count(CNPJReceitaFederalModel.cnpj))
                .where(
                    or_(
                        CNPJReceitaFederalModel.search_vector.op('@@')(ts_query),
                        CNPJReceitaFederalModel.cnpj.like(f"%{search_query.replace('.', '').replace('/', '').replace('-', '')}%"),
                        CNPJReceitaFederalModel.razao_social.ilike(f"%{search_query}%"),
                        CNPJReceitaFederalModel.nome_fantasia.ilike(f"%{search_query}%"),
                    )
                )
            )
        
        # Executar queries
        result = await self._session.execute(stmt)
        companies = result.scalars().all()
        
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Converter para formato de resposta
        items = [
            {
                "id": company.cnpj,
                "cnpj": company.cnpj,
                "razao_social": company.razao_social,
                "nome_fantasia": company.nome_fantasia,
                "situacao_cadastral": company.situacao_cadastral,
                "municipio": company.municipio,
                "uf": company.uf,
            }
            for company in companies
        ]
        
        logger.info("search_completed", total=total, returned=len(items))
        
        return SearchResult(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size,
            query=query.query,
        )
    
    async def _search_analyses(self, query: SearchQuery) -> SearchResult:
        """Busca análises (implementação futura)"""
        # TODO: Implementar busca de análises
        return SearchResult(
            items=[],
            total=0,
            page=query.page,
            page_size=query.page_size,
            query=query.query,
        )
    
    async def index_company(self, company) -> None:
        """Não necessário - PostgreSQL atualiza automaticamente via trigger"""
        pass
    
    async def index_analysis(self, analysis) -> None:
        """Não necessário - PostgreSQL atualiza automaticamente via trigger"""
        pass
    
    async def delete_company(self, company_id: str) -> None:
        """Não necessário - dados são mantidos no PostgreSQL"""
        pass
    
    async def delete_analysis(self, analysis_id: str) -> None:
        """Não necessário - dados são mantidos no PostgreSQL"""
        pass
    
    async def reindex_all(self) -> None:
        """Não necessário - PostgreSQL mantém índices automaticamente via trigger"""
        pass
