from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class SourceInfo:
    """Information about a data source"""
    id: str
    name: str
    icon: str
    category: str
    price: float
    status: str
    delivery_description: str
    simple_description: str
    what_it_is: str
    why_important: str
    main_data: List[str]
    who_needs: List[str]
    color: str
    badge_text: str


class SourceConfigProvider(ABC):
    """Port for providing source configuration data"""
    
    @abstractmethod
    async def get_all_sources(self) -> List[SourceInfo]:
        """Get all available sources"""
        pass
    
    @abstractmethod
    async def get_source_by_id(self, source_id: str) -> SourceInfo | None:
        """Get a specific source by ID"""
        pass
    
    @abstractmethod
    async def get_available_sources(self) -> List[SourceInfo]:
        """Get only sources that are currently available"""
        pass
