import asyncio

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from trivaxion.infrastructure.config.settings import Settings
from trivaxion.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CertidaoTrabalhistaClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base_url = settings.certidao_trabalhista_url
        self._timeout = settings.scraper_timeout_seconds * 1000  # Playwright usa milissegundos
        self._max_retries = settings.scraper_max_retries
        self._retry_delay = settings.scraper_retry_delay_seconds

    async def fetch_certificate(self, cnpj: str) -> str:
        for attempt in range(self._max_retries):
            try:
                logger.info(
                    "fetching_certidao_trabalhista",
                    cnpj=cnpj,
                    attempt=attempt + 1,
                    max_retries=self._max_retries,
                )
                
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    context = await browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    )
                    page = await context.new_page()
                    
                    # Navegar para a página principal
                    await page.goto("https://www.tst.jus.br/certidao", timeout=self._timeout)
                    logger.info("certidao_page_loaded", cnpj=cnpj)
                    
                    # Aceitar cookies
                    try:
                        cookie_button = page.locator("a:has-text('Aceitar')")
                        if await cookie_button.is_visible(timeout=3000):
                            await cookie_button.click()
                            logger.info("cookies_accepted", cnpj=cnpj)
                            await page.wait_for_timeout(2000)
                    except:
                        logger.info("no_cookie_banner", cnpj=cnpj)
                    
                    # Acessar diretamente a URL do formulário (mais confiável que iframe)
                    await page.goto("https://cndt-certidao.tst.jus.br/inicio.faces", timeout=self._timeout)
                    await page.wait_for_load_state("networkidle")
                    logger.info("form_page_loaded", cnpj=cnpj)
                    
                    # Clicar no botão "Emitir certidão"
                    try:
                        emitir_button = page.locator("input[name='j_id_jsp_992698495_2:j_id_jsp_992698495_3']")
                        await emitir_button.wait_for(state="visible", timeout=10000)
                        await emitir_button.click()
                        logger.info("emitir_button_clicked", cnpj=cnpj)
                        await page.wait_for_load_state("networkidle")
                        await page.wait_for_timeout(2000)
                    except Exception as e:
                        logger.error("emitir_button_not_found", cnpj=cnpj, error=str(e))
                        raise ValueError(f"Botão 'Emitir certidão' não encontrado: {e}")
                    
                    # Preencher CNPJ
                    try:
                        cnpj_input = page.locator("input[type='text']").first
                        await cnpj_input.wait_for(state="visible", timeout=10000)
                        await cnpj_input.fill(cnpj)
                        logger.info("cnpj_filled", cnpj=cnpj)
                        await page.wait_for_timeout(1000)
                    except Exception as e:
                        logger.error("cnpj_input_not_found", cnpj=cnpj, error=str(e))
                        raise ValueError(f"Campo CNPJ não encontrado: {e}")
                    
                    # TODO: Implementar quebra de captcha
                    # Por enquanto, retornar HTML da página para análise
                    logger.warning("captcha_not_implemented", cnpj=cnpj)
                    
                    # Capturar HTML da página atual
                    html = await page.content()
                    
                    await browser.close()
                    
                    logger.info(
                        "certidao_trabalhista_fetch_success",
                        cnpj=cnpj,
                    )
                    return html
                    
            except PlaywrightTimeout:
                logger.warning("certidao_trabalhista_timeout", cnpj=cnpj, attempt=attempt + 1)
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise ValueError(f"Timeout fetching certificate for CNPJ {cnpj}")
                    
            except Exception as e:
                logger.error("certidao_trabalhista_unexpected_error", cnpj=cnpj, error=str(e))
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise
        
        raise ValueError(f"Failed to fetch certificate for CNPJ {cnpj} after {self._max_retries} attempts")
