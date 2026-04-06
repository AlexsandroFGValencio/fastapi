from datetime import datetime
from typing import Any

from elasticsearch import AsyncElasticsearch

from trivaxion.application.ports.search import SearchPort
from trivaxion.domain.analysis.analysis import Analysis
from trivaxion.domain.companies.company import Company
from trivaxion.domain.search.search_query import SearchQuery, SearchResult, SearchType
from trivaxion.domain.shared.value_objects import EntityId
from trivaxion.infrastructure.config.settings import Settings
from trivaxion.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class ElasticsearchAdapter(SearchPort):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncElasticsearch([settings.elasticsearch_url])
        self._company_index = f"{settings.elasticsearch_index_prefix}_companies"
        self._analysis_index = f"{settings.elasticsearch_index_prefix}_analyses"

    async def index_company(self, company: Company) -> None:
        try:
            document = {
                "id": str(company.id),
                "cnpj": str(company.cnpj),
                "razao_social": company.razao_social,
                "nome_fantasia": company.nome_fantasia,
                "status": company.status.value,
                "opening_date": company.opening_date.isoformat() if company.opening_date else None,
                "cnae_principal": company.cnae_principal,
                "cnae_description": company.cnae_description,
                "legal_nature": company.legal_nature,
                "city": company.address.city if company.address else None,
                "state": company.address.state if company.address else None,
                "indexed_at": datetime.utcnow().isoformat(),
            }
            
            await self._client.index(
                index=self._company_index,
                id=str(company.id),
                document=document,
            )
            
            logger.info("company_indexed", company_id=str(company.id), cnpj=str(company.cnpj))
            
        except Exception as e:
            logger.error("error_indexing_company", company_id=str(company.id), error=str(e))
            raise

    async def index_analysis(self, analysis: Analysis) -> None:
        try:
            document = {
                "id": str(analysis.id),
                "cnpj": str(analysis.cnpj),
                "organization_id": str(analysis.organization_id),
                "status": analysis.status.value,
                "risk_level": analysis.risk_level.value,
                "risk_score": analysis.risk_score,
                "created_at": analysis.created_at.isoformat(),
                "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
                "risk_signals_count": len(analysis.risk_signals),
                "indexed_at": datetime.utcnow().isoformat(),
            }
            
            await self._client.index(
                index=self._analysis_index,
                id=str(analysis.id),
                document=document,
            )
            
            logger.info("analysis_indexed", analysis_id=str(analysis.id), cnpj=str(analysis.cnpj))
            
        except Exception as e:
            logger.error("error_indexing_analysis", analysis_id=str(analysis.id), error=str(e))
            raise

    async def search(self, query: SearchQuery) -> SearchResult:
        start_time = time.time()
        
        try:
            index = self._company_index if query.search_type == SearchType.COMPANY else self._analysis_index
            
            es_query: dict[str, Any] = {
                "bool": {
                    "must": [],
                    "filter": [],
                }
            }
            
            if query.query:
                es_query["bool"]["must"].append({
                    "multi_match": {
                        "query": query.query,
                        "fields": self._get_search_fields(query.search_type),
                        "fuzziness": "AUTO",
                    }
                })
            else:
                es_query["bool"]["must"].append({"match_all": {}})
            
            if query.organization_id:
                es_query["bool"]["filter"].append({
                    "term": {"organization_id": query.organization_id}
                })
            
            for filter_item in query.filters:
                es_query["bool"]["filter"].append({
                    "term": {filter_item.field: filter_item.value}
                })
            
            sort_field = query.sort_by or "indexed_at"
            sort_order = "asc" if query.sort_order.value == "asc" else "desc"
            
            from_offset = (query.page - 1) * query.page_size
            
            response = await self._client.search(
                index=index,
                query=es_query,
                from_=from_offset,
                size=query.page_size,
                sort=[{sort_field: {"order": sort_order}}],
            )
            
            hits = response["hits"]
            total = hits["total"]["value"]
            items = [hit["_source"] for hit in hits["hits"]]
            
            took_ms = (time.time() - start_time) * 1000
            
            logger.info(
                "search_completed",
                query=query.query,
                search_type=query.search_type.value,
                total=total,
                took_ms=took_ms,
            )
            
            return SearchResult(
                total=total,
                items=items,
                page=query.page,
                page_size=query.page_size,
                query=query.query,
                took_ms=took_ms,
            )
            
        except Exception as e:
            logger.error("search_error", query=query.query, error=str(e))
            raise

    async def delete_company(self, company_id: EntityId) -> None:
        try:
            await self._client.delete(index=self._company_index, id=str(company_id))
            logger.info("company_deleted_from_index", company_id=str(company_id))
        except Exception as e:
            logger.warning("error_deleting_company", company_id=str(company_id), error=str(e))

    async def delete_analysis(self, analysis_id: EntityId) -> None:
        try:
            await self._client.delete(index=self._analysis_index, id=str(analysis_id))
            logger.info("analysis_deleted_from_index", analysis_id=str(analysis_id))
        except Exception as e:
            logger.warning("error_deleting_analysis", analysis_id=str(analysis_id), error=str(e))

    async def reindex_all(self) -> None:
        logger.info("reindex_all_started")
        
        try:
            await self._client.indices.delete(index=self._company_index, ignore=[404])
            await self._client.indices.delete(index=self._analysis_index, ignore=[404])
            
            await self._create_indices()
            
            logger.info("reindex_all_completed")
            
        except Exception as e:
            logger.error("reindex_all_error", error=str(e))
            raise

    async def _create_indices(self) -> None:
        company_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "cnpj": {"type": "keyword"},
                    "razao_social": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "nome_fantasia": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "status": {"type": "keyword"},
                    "opening_date": {"type": "date"},
                    "cnae_principal": {"type": "keyword"},
                    "cnae_description": {"type": "text"},
                    "legal_nature": {"type": "keyword"},
                    "city": {"type": "keyword"},
                    "state": {"type": "keyword"},
                    "indexed_at": {"type": "date"},
                }
            }
        }
        
        analysis_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "cnpj": {"type": "keyword"},
                    "organization_id": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "risk_level": {"type": "keyword"},
                    "risk_score": {"type": "float"},
                    "created_at": {"type": "date"},
                    "completed_at": {"type": "date"},
                    "risk_signals_count": {"type": "integer"},
                    "indexed_at": {"type": "date"},
                }
            }
        }
        
        # Check if indices exist before creating
        if not await self._client.indices.exists(index=self._company_index):
            await self._client.indices.create(index=self._company_index, **company_mapping)
        
        if not await self._client.indices.exists(index=self._analysis_index):
            await self._client.indices.create(index=self._analysis_index, **analysis_mapping)
        
        logger.info("elasticsearch_indices_created")

    def _get_search_fields(self, search_type: SearchType) -> list[str]:
        if search_type == SearchType.COMPANY:
            return ["cnpj", "razao_social^2", "nome_fantasia^2", "cnae_description"]
        else:
            return ["cnpj", "id"]

    async def close(self) -> None:
        await self._client.close()
