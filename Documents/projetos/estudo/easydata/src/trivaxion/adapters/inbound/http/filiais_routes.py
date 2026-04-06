"""
Rotas para buscar filiais de uma empresa
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from trivaxion.adapters.inbound.http.dependencies import CurrentUser, DBSession
from trivaxion.infrastructure.db.models import CNPJReceitaFederalModel

router = APIRouter(prefix="/api/v1/analyses", tags=["filiais"])


@router.get("/{analysis_id}/filiais")
async def get_filiais(
    analysis_id: str,
    current_user: CurrentUser,
    session: DBSession,
):
    """Busca todas as filiais de uma empresa baseado nos 8 primeiros dígitos do CNPJ"""
    
    # Buscar a análise para obter o CNPJ
    from trivaxion.infrastructure.db.models import AnalysisRequestModel
    from sqlalchemy import select
    from uuid import UUID
    
    try:
        analysis_uuid = UUID(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid analysis ID")
    
    result = await session.execute(
        select(AnalysisRequestModel).where(AnalysisRequestModel.id == analysis_uuid)
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Verificar se o usuário tem acesso
    if analysis.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Extrair base do CNPJ (8 primeiros dígitos)
    cnpj_base = analysis.cnpj[:8]
    
    # Buscar todas as empresas com a mesma base
    result = await session.execute(
        select(CNPJReceitaFederalModel).where(
            CNPJReceitaFederalModel.cnpj.like(f"{cnpj_base}%")
        ).order_by(CNPJReceitaFederalModel.cnpj)
    )
    empresas = result.scalars().all()
    
    # Separar matriz e filiais
    matriz = None
    filiais = []
    
    for empresa in empresas:
        # CNPJ formato: 8 dígitos base + 4 dígitos ordem + 2 dígitos DV
        # Ordem 0001 = Matriz
        ordem = empresa.cnpj[8:12]
        
        empresa_data = {
            "cnpj": empresa.cnpj,
            "cnpj_formatado": f"{empresa.cnpj[:2]}.{empresa.cnpj[2:5]}.{empresa.cnpj[5:8]}/{empresa.cnpj[8:12]}-{empresa.cnpj[12:14]}",
            "razao_social": empresa.razao_social,
            "nome_fantasia": empresa.nome_fantasia,
            "situacao_cadastral": empresa.situacao_cadastral,
            "logradouro": empresa.logradouro,
            "numero": empresa.numero,
            "complemento": empresa.complemento,
            "bairro": empresa.bairro,
            "municipio": empresa.municipio,
            "uf": empresa.uf,
            "cep": empresa.cep,
            "is_matriz": ordem == "0001"
        }
        
        if ordem == "0001":
            matriz = empresa_data
        else:
            filiais.append(empresa_data)
    
    return {
        "cnpj_base": cnpj_base,
        "matriz": matriz,
        "filiais": filiais,
        "total_filiais": len(filiais)
    }
