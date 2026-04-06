from datetime import datetime

from bs4 import BeautifulSoup

from trivaxion.adapters.outbound.providers.receita_federal.models import ReceitaFederalRawData
from trivaxion.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class ReceitaFederalParser:
    @staticmethod
    def parse_html(html: str, cnpj: str) -> ReceitaFederalRawData:
        soup = BeautifulSoup(html, "html.parser")
        
        data = ReceitaFederalRawData(cnpj=cnpj, raw_html=html)
        
        try:
            data.razao_social = ReceitaFederalParser._extract_field(soup, "razão social")
            data.nome_fantasia = ReceitaFederalParser._extract_field(soup, "nome fantasia")
            data.situacao_cadastral = ReceitaFederalParser._extract_field(soup, "situação cadastral")
            data.cnae_fiscal = ReceitaFederalParser._extract_field(soup, "cnae fiscal principal")
            data.natureza_juridica = ReceitaFederalParser._extract_field(soup, "natureza jurídica")
            data.logradouro = ReceitaFederalParser._extract_field(soup, "logradouro")
            data.numero = ReceitaFederalParser._extract_field(soup, "número")
            data.complemento = ReceitaFederalParser._extract_field(soup, "complemento")
            data.bairro = ReceitaFederalParser._extract_field(soup, "bairro")
            data.municipio = ReceitaFederalParser._extract_field(soup, "município")
            data.uf = ReceitaFederalParser._extract_field(soup, "uf")
            data.cep = ReceitaFederalParser._extract_field(soup, "cep")
            data.capital_social = ReceitaFederalParser._extract_field(soup, "capital social")
            data.porte = ReceitaFederalParser._extract_field(soup, "porte")
            
            data_abertura_str = ReceitaFederalParser._extract_field(soup, "data de abertura")
            if data_abertura_str:
                data.data_abertura = ReceitaFederalParser._parse_date(data_abertura_str)
            
        except Exception as e:
            logger.warning("error_parsing_receita_federal", error=str(e), cnpj=cnpj)
        
        return data

    @staticmethod
    def _extract_field(soup: BeautifulSoup, field_name: str) -> str | None:
        field_name_lower = field_name.lower()
        
        for tag in soup.find_all(["td", "th", "span", "div", "label"]):
            text = tag.get_text(strip=True).lower()
            if field_name_lower in text:
                next_sibling = tag.find_next_sibling()
                if next_sibling:
                    value = next_sibling.get_text(strip=True)
                    return value if value else None
                
                parent = tag.parent
                if parent:
                    all_text = parent.get_text(separator="|", strip=True)
                    parts = all_text.split("|")
                    for i, part in enumerate(parts):
                        if field_name_lower in part.lower() and i + 1 < len(parts):
                            return parts[i + 1].strip()
        
        return None

    @staticmethod
    def _parse_date(date_str: str) -> datetime | None:
        date_formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
