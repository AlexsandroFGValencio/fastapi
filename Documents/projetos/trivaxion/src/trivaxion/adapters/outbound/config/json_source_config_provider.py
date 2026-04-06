import json
from pathlib import Path
from typing import List, Dict, Any

from trivaxion.application.ports.source_config import SourceConfigProvider, SourceInfo
from trivaxion.infrastructure.config.settings import Settings


class JsonSourceConfigProvider(SourceConfigProvider):
    """JSON file implementation of source configuration provider"""
    
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        # Direct path to the JSON configuration file
        self._config_path = Path("/app/src/trivaxion/infrastructure/config/sources_config.json")
        self._sources_cache: List[SourceInfo] | None = None
    
    async def _load_config(self) -> List[SourceInfo]:
        """Load and parse the JSON configuration file"""
        if self._sources_cache is not None:
            return self._sources_cache
        
        try:
            with open(self._config_path, 'r', encoding='utf-8') as file:
                config_data = json.load(file)
            
            sources = []
            for source_data in config_data.get('sources', []):
                source = SourceInfo(**source_data)
                sources.append(source)
            
            self._sources_cache = sources
            return sources
            
        except FileNotFoundError:
            raise RuntimeError(f"Source configuration file not found: {self._config_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in source configuration: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading source configuration: {e}")
    
    async def get_all_sources(self) -> List[SourceInfo]:
        """Get all available sources"""
        return await self._load_config()
    
    async def get_source_by_id(self, source_id: str) -> SourceInfo | None:
        """Get a specific source by ID"""
        sources = await self._load_config()
        for source in sources:
            if source.id == source_id:
                return source
        return None
    
    async def get_available_sources(self) -> List[SourceInfo]:
        """Get only sources that are currently available"""
        sources = await self._load_config()
        return [source for source in sources if source.status == "available"]
