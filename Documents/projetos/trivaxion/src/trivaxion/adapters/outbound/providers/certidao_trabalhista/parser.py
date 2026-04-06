from datetime import datetime

from bs4 import BeautifulSoup

from trivaxion.adapters.outbound.providers.certidao_trabalhista.models import (
    CertidaoTrabalhistaRawData,
)
from trivaxion.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CertidaoTrabalhistaParser:
    @staticmethod
    def parse_html(html: str, cnpj: str) -> CertidaoTrabalhistaRawData:
        soup = BeautifulSoup(html, "html.parser")
        
        data = CertidaoTrabalhistaRawData(cnpj=cnpj, raw_html=html)
        
        try:
            data.status = CertidaoTrabalhistaParser._extract_status(soup)
            data.numero_certidao = CertidaoTrabalhistaParser._extract_field(soup, "número")
            data.codigo_validacao = CertidaoTrabalhistaParser._extract_field(soup, "código")
            data.mensagem_oficial = CertidaoTrabalhistaParser._extract_message(soup)
            
            emissao_str = CertidaoTrabalhistaParser._extract_field(soup, "emissão")
            if emissao_str:
                data.data_emissao = CertidaoTrabalhistaParser._parse_date(emissao_str)
            
            validade_str = CertidaoTrabalhistaParser._extract_field(soup, "validade")
            if validade_str:
                data.data_validade = CertidaoTrabalhistaParser._parse_date(validade_str)
            
        except Exception as e:
            logger.warning("error_parsing_certidao_trabalhista", error=str(e), cnpj=cnpj)
        
        return data

    @staticmethod
    def _extract_status(soup: BeautifulSoup) -> str:
        status_keywords = {
            "negativa": "negativa",
            "positiva": "positiva",
            "sem débito": "negativa",
            "com débito": "positiva",
            "nada consta": "negativa",
        }
        
        text = soup.get_text().lower()
        for keyword, status in status_keywords.items():
            if keyword in text:
                return status
        
        return "desconhecida"

    @staticmethod
    def _extract_field(soup: BeautifulSoup, field_name: str) -> str | None:
        field_name_lower = field_name.lower()
        
        for tag in soup.find_all(["td", "th", "span", "div", "label", "strong"]):
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
    def _extract_message(soup: BeautifulSoup) -> str | None:
        for tag in soup.find_all(["p", "div"], class_=lambda x: x and "mensagem" in x.lower()):
            return tag.get_text(strip=True)
        
        return None

    @staticmethod
    def _parse_date(date_str: str) -> datetime | None:
        date_formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y %H:%M:%S"]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
