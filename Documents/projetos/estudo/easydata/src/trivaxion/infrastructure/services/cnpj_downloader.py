"""
Serviço para download e processamento dos dados públicos de CNPJ da Receita Federal.

Baseado nos dados disponíveis em:
- Dados: https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9
- Metadados: https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf
"""
import asyncio
import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trivaxion.infrastructure.db.models import CNPJReceitaFederalModel
from trivaxion.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CNPJDownloader:
    """Serviço para download e processamento dos dados de CNPJ da Receita Federal"""
    
    def __init__(self, download_dir: str = "/tmp/cnpj_data"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # URL base dos arquivos da Receita Federal
        # Formato: https://dadosabertos.rfb.gov.br/CNPJ/[arquivo].zip
        self.base_url = "https://dadosabertos.rfb.gov.br/CNPJ"
        
        # Lista de arquivos conhecidos (atualizar conforme necessário)
        self.estabelecimentos_files = [f"Estabelecimentos{i}.zip" for i in range(10)]
        self.empresas_files = [f"Empresas{i}.zip" for i in range(10)]
        self.simples_files = ["Simples.zip"]
        self.socios_files = [f"Socios{i}.zip" for i in range(10)]
        
    async def download_file(self, url: str, filename: str) -> Path:
        """Download de um arquivo específico"""
        filepath = self.download_dir / filename
        
        if filepath.exists():
            logger.info("file_already_exists", filename=filename)
            return filepath
        
        logger.info("downloading_file", url=url, filename=filename)
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                
                with open(filepath, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
        
        logger.info("download_complete", filename=filename, size=filepath.stat().st_size)
        return filepath
    
    async def extract_zip(self, zip_path: Path) -> list[Path]:
        """Extrai arquivos de um ZIP"""
        extract_dir = self.download_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        logger.info("extracting_zip", zip_file=zip_path.name)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        extracted_files = list(extract_dir.glob("*.csv")) + list(extract_dir.glob("*.CSV"))
        logger.info("extraction_complete", files_count=len(extracted_files))
        
        return extracted_files
    
    async def parse_estabelecimentos_csv(self, csv_path: Path) -> AsyncGenerator[dict, None]:
        """
        Parser para arquivos de Estabelecimentos (contém os dados principais das empresas)
        
        Layout conforme metadados da Receita Federal:
        1. CNPJ Básico
        2. CNPJ Ordem
        3. CNPJ DV
        4. Identificador Matriz/Filial
        5. Nome Fantasia
        6. Situação Cadastral
        7. Data Situação Cadastral
        8. Motivo Situação Cadastral
        9. Nome da Cidade no Exterior
        10. Código País
        11. Data Início Atividade
        12. CNAE Fiscal Principal
        13. CNAE Fiscal Secundária
        14. Tipo Logradouro
        15. Logradouro
        16. Número
        17. Complemento
        18. Bairro
        19. CEP
        20. UF
        21. Código Município
        22. Município
        23. DDD Telefone 1
        24. Telefone 1
        25. DDD Telefone 2
        26. Telefone 2
        27. DDD Fax
        28. Fax
        29. Email
        30. Situação Especial
        31. Data Situação Especial
        """
        import csv
        
        logger.info("parsing_csv", file=csv_path.name)
        
        with open(csv_path, 'r', encoding='latin1') as f:
            reader = csv.reader(f, delimiter=';')
            
            for row in reader:
                if len(row) < 30:
                    continue
                
                try:
                    # Construir CNPJ completo
                    cnpj_basico = row[0].strip()
                    cnpj_ordem = row[1].strip().zfill(4)
                    cnpj_dv = row[2].strip().zfill(2)
                    cnpj = f"{cnpj_basico}{cnpj_ordem}{cnpj_dv}"
                    
                    # Apenas estabelecimentos matriz (ordem 0001)
                    if cnpj_ordem != "0001":
                        continue
                    
                    # Parsear data de situação cadastral
                    data_situacao = None
                    if row[7].strip():
                        try:
                            data_situacao = datetime.strptime(row[7].strip(), "%Y%m%d")
                        except:
                            pass
                    
                    # Parsear data de início de atividade
                    data_inicio = None
                    if row[11].strip():
                        try:
                            data_inicio = datetime.strptime(row[11].strip(), "%Y%m%d")
                        except:
                            pass
                    
                    yield {
                        "cnpj": cnpj,
                        "nome_fantasia": row[4].strip() or None,
                        "situacao_cadastral": row[5].strip() or None,
                        "data_situacao_cadastral": data_situacao,
                        "motivo_situacao_cadastral": row[7].strip() or None,
                        "data_inicio_atividade": data_inicio,
                        "cnae_fiscal_principal": row[12].strip() or None,
                        "cnae_fiscal_secundaria": row[13].strip() or None,
                        "tipo_logradouro": row[14].strip() or None,
                        "logradouro": row[15].strip() or None,
                        "numero": row[16].strip() or None,
                        "complemento": row[17].strip() or None,
                        "bairro": row[18].strip() or None,
                        "cep": row[19].strip() or None,
                        "uf": row[20].strip() or None,
                        "municipio": row[22].strip() or None,
                        "ddd_telefone_1": f"{row[23]}{row[24]}".strip() or None,
                        "ddd_telefone_2": f"{row[25]}{row[26]}".strip() or None,
                        "ddd_fax": f"{row[27]}{row[28]}".strip() or None,
                        "email": row[29].strip() or None,
                    }
                except Exception as e:
                    logger.warning("error_parsing_row", error=str(e), row=row[:5])
                    continue
    
    async def parse_empresas_csv(self, csv_path: Path) -> dict[str, dict]:
        """
        Parser para arquivos de Empresas (contém razão social e dados complementares)
        
        Layout:
        1. CNPJ Básico
        2. Razão Social
        3. Natureza Jurídica
        4. Qualificação do Responsável
        5. Capital Social
        6. Porte da Empresa
        7. Ente Federativo Responsável
        """
        import csv
        
        logger.info("parsing_empresas_csv", file=csv_path.name)
        empresas = {}
        
        with open(csv_path, 'r', encoding='latin1') as f:
            reader = csv.reader(f, delimiter=';')
            
            for row in reader:
                if len(row) < 6:
                    continue
                
                try:
                    cnpj_basico = row[0].strip()
                    
                    capital_social = None
                    if row[4].strip():
                        try:
                            capital_social = float(row[4].strip().replace(',', '.'))
                        except:
                            pass
                    
                    empresas[cnpj_basico] = {
                        "razao_social": row[1].strip() or None,
                        "natureza_juridica": row[2].strip() or None,
                        "qualificacao_responsavel": row[3].strip() or None,
                        "capital_social": capital_social,
                        "porte_empresa": row[5].strip() or None,
                    }
                except Exception as e:
                    logger.warning("error_parsing_empresa_row", error=str(e))
                    continue
        
        logger.info("empresas_parsed", count=len(empresas))
        return empresas
    
    async def parse_simples_csv(self, csv_path: Path) -> dict[str, dict]:
        """
        Parser para arquivos de Simples Nacional
        
        Layout:
        1. CNPJ Básico
        2. Opção pelo Simples
        3. Data Opção Simples
        4. Data Exclusão Simples
        5. Opção MEI
        6. Data Opção MEI
        7. Data Exclusão MEI
        """
        import csv
        
        logger.info("parsing_simples_csv", file=csv_path.name)
        simples_data = {}
        
        with open(csv_path, 'r', encoding='latin1') as f:
            reader = csv.reader(f, delimiter=';')
            
            for row in reader:
                if len(row) < 5:
                    continue
                
                try:
                    cnpj_basico = row[0].strip()
                    
                    data_opcao_simples = None
                    if row[2].strip():
                        try:
                            data_opcao_simples = datetime.strptime(row[2].strip(), "%Y%m%d")
                        except:
                            pass
                    
                    data_exclusao_simples = None
                    if row[3].strip():
                        try:
                            data_exclusao_simples = datetime.strptime(row[3].strip(), "%Y%m%d")
                        except:
                            pass
                    
                    simples_data[cnpj_basico] = {
                        "opcao_simples": row[1].strip() or None,
                        "data_opcao_simples": data_opcao_simples,
                        "data_exclusao_simples": data_exclusao_simples,
                        "opcao_mei": row[4].strip() or None,
                    }
                except Exception as e:
                    logger.warning("error_parsing_simples_row", error=str(e))
                    continue
        
        logger.info("simples_parsed", count=len(simples_data))
        return simples_data
    
    async def parse_socios_csv(self, csv_path: Path) -> AsyncGenerator[dict, None]:
        """
        Parser para arquivos de Sócios (QSA - Quadro de Sócios e Administradores)
        
        Layout conforme metadados da Receita Federal:
        1. CNPJ Básico
        2. Identificador de Sócio
        3. Nome do Sócio
        4. CPF/CNPJ do Sócio
        5. Qualificação do Sócio
        6. Data de Entrada Sociedade
        7. País
        8. Representante Legal
        9. Nome do Representante
        10. Qualificação do Representante
        11. Faixa Etária
        """
        import csv
        
        logger.info("parsing_socios_csv", file=csv_path.name)
        
        with open(csv_path, 'r', encoding='latin1') as f:
            reader = csv.reader(f, delimiter=';')
            
            for row in reader:
                if len(row) < 9:
                    continue
                
                try:
                    cnpj_basico = row[0].strip()
                    
                    # Parsear data de entrada na sociedade
                    data_entrada = None
                    if row[5].strip():
                        try:
                            data_entrada = datetime.strptime(row[5].strip(), "%Y%m%d")
                        except:
                            pass
                    
                    yield {
                        "cnpj_basico": cnpj_basico,
                        "identificador_socio": row[1].strip() or None,
                        "nome_socio": row[2].strip() or None,
                        "cpf_cnpj_socio": row[3].strip() or None,
                        "qualificacao_socio": row[4].strip() or None,
                        "data_entrada_sociedade": data_entrada,
                        "pais": row[6].strip() or None,
                        "representante_legal": row[7].strip() or None,
                        "nome_representante": row[8].strip() if len(row) > 8 else None,
                        "qualificacao_representante": row[9].strip() if len(row) > 9 else None,
                        "faixa_etaria": row[10].strip() if len(row) > 10 else None,
                    }
                except Exception as e:
                    logger.warning("error_parsing_socio_row", error=str(e), row=row[:5])
                    continue
    
    async def import_to_database(
        self,
        session: AsyncSession,
        estabelecimentos_files: list[Path],
        empresas_files: list[Path],
        simples_files: list[Path],
        batch_size: int = 1000
    ) -> int:
        """Importa dados dos CSVs para o PostgreSQL"""
        
        logger.info("starting_import", 
                   estabelecimentos=len(estabelecimentos_files),
                   empresas=len(empresas_files),
                   simples=len(simples_files))
        
        # Parsear dados complementares
        empresas_data = {}
        for empresas_file in empresas_files:
            data = await self.parse_empresas_csv(empresas_file)
            empresas_data.update(data)
        
        simples_data = {}
        for simples_file in simples_files:
            data = await self.parse_simples_csv(simples_file)
            simples_data.update(data)
        
        # Processar estabelecimentos
        total_imported = 0
        batch = []
        
        for estabelecimentos_file in estabelecimentos_files:
            async for estabelecimento in self.parse_estabelecimentos_csv(estabelecimentos_file):
                cnpj = estabelecimento["cnpj"]
                cnpj_basico = cnpj[:8]
                
                # Combinar dados de diferentes arquivos
                empresa_info = empresas_data.get(cnpj_basico, {})
                simples_info = simples_data.get(cnpj_basico, {})
                
                record = CNPJReceitaFederalModel(
                    cnpj=cnpj,
                    razao_social=empresa_info.get("razao_social"),
                    nome_fantasia=estabelecimento.get("nome_fantasia"),
                    situacao_cadastral=estabelecimento.get("situacao_cadastral"),
                    data_situacao_cadastral=estabelecimento.get("data_situacao_cadastral"),
                    motivo_situacao_cadastral=estabelecimento.get("motivo_situacao_cadastral"),
                    data_inicio_atividade=estabelecimento.get("data_inicio_atividade"),
                    cnae_fiscal_principal=estabelecimento.get("cnae_fiscal_principal"),
                    cnae_fiscal_secundaria=estabelecimento.get("cnae_fiscal_secundaria"),
                    tipo_logradouro=estabelecimento.get("tipo_logradouro"),
                    logradouro=estabelecimento.get("logradouro"),
                    numero=estabelecimento.get("numero"),
                    complemento=estabelecimento.get("complemento"),
                    bairro=estabelecimento.get("bairro"),
                    cep=estabelecimento.get("cep"),
                    uf=estabelecimento.get("uf"),
                    municipio=estabelecimento.get("municipio"),
                    ddd_telefone_1=estabelecimento.get("ddd_telefone_1"),
                    ddd_telefone_2=estabelecimento.get("ddd_telefone_2"),
                    ddd_fax=estabelecimento.get("ddd_fax"),
                    email=estabelecimento.get("email"),
                    qualificacao_responsavel=empresa_info.get("qualificacao_responsavel"),
                    capital_social=empresa_info.get("capital_social"),
                    porte_empresa=empresa_info.get("porte_empresa"),
                    opcao_simples=simples_info.get("opcao_simples"),
                    data_opcao_simples=simples_info.get("data_opcao_simples"),
                    data_exclusao_simples=simples_info.get("data_exclusao_simples"),
                    opcao_mei=simples_info.get("opcao_mei"),
                    natureza_juridica=empresa_info.get("natureza_juridica"),
                )
                
                batch.append(record)
                
                if len(batch) >= batch_size:
                    session.add_all(batch)
                    await session.commit()
                    total_imported += len(batch)
                    logger.info("batch_imported", count=total_imported)
                    batch = []
        
        # Importar último batch
        if batch:
            session.add_all(batch)
            await session.commit()
            total_imported += len(batch)
        
        logger.info("import_complete", total=total_imported)
        return total_imported
    
    async def download_and_import(self, limit: int | None = None) -> int:
        """
        Download completo e importação dos dados da Receita Federal
        
        Args:
            limit: Limite de registros para importar (None = todos)
        
        Returns:
            Total de registros importados
        """
        logger.info("starting_full_download_and_import", limit=limit)
        
        estabelecimentos_files = []
        empresas_files = []
        simples_files = []
        
        # Download de estabelecimentos
        logger.info("downloading_estabelecimentos")
        for filename in self.estabelecimentos_files:
            try:
                url = f"{self.base_url}/{filename}"
                zip_path = await self.download_file(url, filename)
                extracted = await self.extract_zip(zip_path)
                estabelecimentos_files.extend(extracted)
            except Exception as e:
                logger.warning("failed_to_download_file", filename=filename, error=str(e))
                continue
        
        # Download de empresas
        logger.info("downloading_empresas")
        for filename in self.empresas_files:
            try:
                url = f"{self.base_url}/{filename}"
                zip_path = await self.download_file(url, filename)
                extracted = await self.extract_zip(zip_path)
                empresas_files.extend(extracted)
            except Exception as e:
                logger.warning("failed_to_download_file", filename=filename, error=str(e))
                continue
        
        # Download de simples
        logger.info("downloading_simples")
        for filename in self.simples_files:
            try:
                url = f"{self.base_url}/{filename}"
                zip_path = await self.download_file(url, filename)
                extracted = await self.extract_zip(zip_path)
                simples_files.extend(extracted)
            except Exception as e:
                logger.warning("failed_to_download_file", filename=filename, error=str(e))
                continue
        
        # Importar para o banco
        logger.info("starting_database_import", 
                   estabelecimentos=len(estabelecimentos_files),
                   empresas=len(empresas_files),
                   simples=len(simples_files))
        
        async with async_session_maker() as session:
            total = await self.import_to_database(
                session,
                estabelecimentos_files,
                empresas_files,
                simples_files,
                batch_size=1000
            )
        
        return total
