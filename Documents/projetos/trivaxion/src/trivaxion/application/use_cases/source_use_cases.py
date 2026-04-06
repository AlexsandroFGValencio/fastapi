from dataclasses import dataclass
from typing import List

from trivaxion.application.ports.source_config import SourceConfigProvider, SourceInfo


@dataclass
class SourcesResponse:
    """Response model for sources data"""
    sources: List[SourceInfo]
    available_count: int
    coming_soon_count: int
    total_count: int


class GetSourcesUseCase:
    """Use case for retrieving source configuration"""
    
    def __init__(self, source_config_provider: SourceConfigProvider) -> None:
        self._source_config_provider = source_config_provider
    
    async def execute(self) -> SourcesResponse:
        """Execute the use case to get all sources"""
        all_sources = await self._source_config_provider.get_all_sources()
        available_sources = await self._source_config_provider.get_available_sources()
        
        return SourcesResponse(
            sources=all_sources,
            available_count=len(available_sources),
            coming_soon_count=len(all_sources) - len(available_sources),
            total_count=len(all_sources)
        )
    
    async def get_available_sources(self) -> List[SourceInfo]:
        """Get only available sources"""
        return await self._source_config_provider.get_available_sources()
    
    async def get_source_by_id(self, source_id: str) -> SourceInfo | None:
        """Get a specific source by ID"""
        return await self._source_config_provider.get_source_by_id(source_id)
