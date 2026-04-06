import asyncio
from typing import Any

import httpx

from trivaxion.infrastructure.config.settings import Settings
from trivaxion.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class ReceitaFederalClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base_url = settings.receita_federal_base_url
        self._timeout = settings.scraper_timeout_seconds
        self._max_retries = settings.scraper_max_retries
        self._retry_delay = settings.scraper_retry_delay_seconds

    async def fetch_company_page(self, cnpj: str) -> str:
        url = f"{self._base_url}/cnpj/{cnpj}"
        
        for attempt in range(self._max_retries):
            try:
                logger.info(
                    "fetching_receita_federal",
                    cnpj=cnpj,
                    attempt=attempt + 1,
                    max_retries=self._max_retries,
                )
                
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(url, follow_redirects=True)
                    response.raise_for_status()
                    
                    logger.info("receita_federal_fetch_success", cnpj=cnpj, status_code=response.status_code)
                    return response.text
                    
            except httpx.HTTPStatusError as e:
                logger.warning(
                    "receita_federal_http_error",
                    cnpj=cnpj,
                    status_code=e.response.status_code,
                    attempt=attempt + 1,
                )
                if e.response.status_code == 404:
                    raise ValueError(f"CNPJ {cnpj} not found in Receita Federal")
                
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise
                    
            except httpx.TimeoutException:
                logger.warning("receita_federal_timeout", cnpj=cnpj, attempt=attempt + 1)
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise ValueError(f"Timeout fetching CNPJ {cnpj} from Receita Federal")
                    
            except Exception as e:
                logger.error("receita_federal_unexpected_error", cnpj=cnpj, error=str(e))
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise
        
        raise ValueError(f"Failed to fetch CNPJ {cnpj} after {self._max_retries} attempts")
