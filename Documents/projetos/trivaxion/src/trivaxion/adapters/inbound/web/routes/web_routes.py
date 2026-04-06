from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import asyncio
import json
from pathlib import Path
import httpx
from typing import Optional

router = APIRouter()

# Adicionar filtro customizado para formatar datas
from datetime import datetime, date

def format_date(value, format_string='%d/%m/%Y'):
    """Formata uma data para o formato brasileiro DD/MM/YYYY"""
    if value is None:
        return '-'
    
    if isinstance(value, str):
        # Tentar parsear string para datetime
        try:
            # Tentar vários formatos comuns
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y']:
                try:
                    value = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue
            else:
                # Se nenhum formato funcionou, retornar a string original
                return value
        except:
            return value
    
    if isinstance(value, (datetime, date)):
        return value.strftime(format_string)
    
    return value

def format_datetime(value):
    """Formata uma data e hora para o formato brasileiro DD/MM/YYYY HH:MM"""
    return format_date(value, '%d/%m/%Y %H:%M')

def format_datetime_full(value):
    """Formata uma data e hora para o formato brasileiro DD/MM/YYYY às HH:MM:SS"""
    if value is None:
        return '-'
    
    if isinstance(value, str):
        # Tentar parsear string para datetime
        try:
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S.%f']:
                try:
                    value = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue
            else:
                return value
        except:
            return value
    
    if isinstance(value, (datetime, date)):
        return value.strftime('%d/%m/%Y às %H:%M:%S')
    
    return value

# Setup templates - criar ambiente completamente novo
from jinja2 import Environment, FileSystemLoader

templates_dir = Path(__file__).parent.parent / "templates"

# Criar ambiente Jinja2 do zero
env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    auto_reload=True,
    cache_size=0  # Desabilitar cache
)

# Registrar filtros
env.filters['format_date'] = format_date
env.filters['format_datetime'] = format_datetime
env.filters['format_datetime_full'] = format_datetime_full

# Criar templates manualmente
class SimpleTemplates:
    def __init__(self, env):
        self.env = env
    
    def TemplateResponse(self, template_name, context):
        from fastapi.responses import HTMLResponse
        template = self.env.get_template(template_name)
        rendered = template.render(**context)
        return HTMLResponse(content=rendered)

templates = SimpleTemplates(env)

def get_user_from_session(request: Request):
    """Get user from session"""
    user = request.session.get("user")
    if not user:
        return None
    return user

def require_auth(request: Request):
    """Require authentication for route"""
    user = get_user_from_session(request)
    if not user:
        raise HTTPException(status_code=302, detail="Not authenticated")
    return user

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    context = {
        "request": request,
        "session": dict(request.session) if request.session else {}
    }
    return templates.TemplateResponse("login.html", context)

@router.post("/web/login")
async def web_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Web login endpoint that stores token in session"""
    
    # Call the API login endpoint
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/v1/auth/login",
                json={"email": username, "password": password}
            )
            
            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"detail": "Invalid credentials"}
                )
            
            data = response.json()
            access_token = data.get("access_token")
            
            # Build user object from response
            user = {
                "id": data.get("user_id"),
                "email": data.get("email"),
                "full_name": data.get("full_name"),
                "role": data.get("role")
            }
            
            # Store in session
            request.session["access_token"] = access_token
            request.session["user"] = user
            
            # Return success response with cookie (NOT httponly so JavaScript can read it)
            response = JSONResponse(
                status_code=200,
                content={
                    "access_token": access_token,
                    "user": user
                }
            )
            # Set token in cookie for HTMX requests - NOT httponly so JS can read it
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=False,  # Allow JavaScript to read the cookie
                max_age=86400,  # 24 hours
                samesite="lax"
            )
            return response
            
        except httpx.HTTPError as e:
            return JSONResponse(
                status_code=500,
                content={"detail": "Login failed"}
            )

@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    # Return HTML that clears localStorage and redirects
    return """
    <html>
    <head><title>Logout</title></head>
    <body>
        <script>
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        </script>
    </body>
    </html>
    """

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page"""
    user = get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "active_page": "dashboard"
    })

@router.get("/analyses/new", response_class=HTMLResponse)
async def new_analysis_page(request: Request):
    """New analysis page"""
    user = get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("new_analysis.html", {
        "request": request,
        "user": user,
        "active_page": "new_analysis"
    })

@router.get("/analyses", response_class=HTMLResponse)
async def analyses_page(request: Request):
    """Analyses history page"""
    user = get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("analyses.html", {
        "request": request,
        "user": user,
        "active_page": "analyses"
    })

@router.get("/analyses/{analysis_id}", response_class=HTMLResponse)
async def analysis_detail_page(request: Request, analysis_id: str):
    """Analysis detail page"""
    user = get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Buscar análise diretamente do banco
    from trivaxion.infrastructure.db.base import async_session_maker
    from trivaxion.adapters.outbound.persistence.sqlalchemy_repositories import SQLAlchemyAnalysisRepository, SQLAlchemyCompanyRepository
    from trivaxion.application.use_cases.analysis_use_cases import GetAnalysisUseCase
    from trivaxion.domain.shared.value_objects import EntityId
    from trivaxion.infrastructure.db.models import CNPJReceitaFederalModel, CNPJSociosModel, UserModel
    from sqlalchemy import select
    
    async with async_session_maker() as session:
        analysis_repo = SQLAlchemyAnalysisRepository(session)
        company_repo = SQLAlchemyCompanyRepository(session)
        
        use_case = GetAnalysisUseCase(
            analysis_repository=analysis_repo,
            company_repository=company_repo
        )
        
        try:
            # Buscar organization_id do usuário
            org_id = user.get("organization_id")
            if not org_id:
                # Se não tiver na sessão, buscar do banco
                user_result = await session.execute(
                    select(UserModel).where(UserModel.id == user["id"])
                )
                user_model = user_result.scalar_one_or_none()
                if user_model:
                    org_id = str(user_model.organization_id)
                else:
                    raise HTTPException(status_code=500, detail="User organization not found")
            
            analysis_response = await use_case.execute(analysis_id, org_id)
            
            # Converter para dict para o template
            analysis = {
                "id": analysis_response.id,
                "cnpj": analysis_response.cnpj,
                "status": analysis_response.status,
                "risk_level": analysis_response.risk_level,
                "risk_score": analysis_response.risk_score,
                "created_at": analysis_response.created_at,
                "completed_at": analysis_response.completed_at,
                "company_data": analysis_response.company_data,
                "risk_signals": analysis_response.risk_signals,
            }
            
            # Limpar CNPJ para busca
            cnpj_limpo = analysis["cnpj"].replace(".", "").replace("/", "").replace("-", "")
            cnpj_basico = cnpj_limpo[:8]
            
            # Buscar QSA (sócios) da Receita Federal
            socios_result = await session.execute(
                select(CNPJSociosModel).where(CNPJSociosModel.cnpj_basico == cnpj_basico)
            )
            socios_models = socios_result.scalars().all()
            
            # Importar mapeamento de qualificação
            from trivaxion.infrastructure.constants import get_qualificacao_descricao, get_qualificacao_completa
            
            # Formatar dados dos sócios
            socios = []
            for socio in socios_models:
                socio_dict = {
                    "nome": socio.nome_socio,
                    "qualificacao_codigo": socio.qualificacao_socio,
                    "qualificacao": get_qualificacao_descricao(socio.qualificacao_socio),
                    "qualificacao_completa": get_qualificacao_completa(socio.qualificacao_socio),
                    "cpf_cnpj": socio.cpf_cnpj_socio,
                    "data_entrada": socio.data_entrada_sociedade.strftime("%d/%m/%Y") if socio.data_entrada_sociedade else None,
                    "pais": socio.pais,
                    "representante_legal": socio.representante_legal,
                    "nome_representante": socio.nome_representante,
                    "faixa_etaria": socio.faixa_etaria,
                }
                socios.append(socio_dict)
            
            # Adicionar sócios ao company_data
            if not analysis.get("company_data"):
                # Se company_data for None, criar um dict básico
                analysis["company_data"] = {"socios": socios}
            elif isinstance(analysis["company_data"], dict):
                # Se já for dict, apenas adicionar socios
                analysis["company_data"]["socios"] = socios
            else:
                # Se company_data for um objeto, converter para dict
                company_data_dict = {
                    "cnpj": getattr(analysis["company_data"], "cnpj", None),
                    "razao_social": getattr(analysis["company_data"], "razao_social", None),
                    "nome_fantasia": getattr(analysis["company_data"], "nome_fantasia", None),
                    "situacao_cadastral": getattr(analysis["company_data"], "situacao_cadastral", None),
                    "data_abertura": getattr(analysis["company_data"], "data_abertura", None),
                    "cnae_principal": getattr(analysis["company_data"], "cnae_principal", None),
                    "cnae_descricao": getattr(analysis["company_data"], "cnae_descricao", None),
                    "natureza_juridica": getattr(analysis["company_data"], "natureza_juridica", None),
                    "logradouro": getattr(analysis["company_data"], "logradouro", None),
                    "numero": getattr(analysis["company_data"], "numero", None),
                    "complemento": getattr(analysis["company_data"], "complemento", None),
                    "bairro": getattr(analysis["company_data"], "bairro", None),
                    "municipio": getattr(analysis["company_data"], "municipio", None),
                    "uf": getattr(analysis["company_data"], "uf", None),
                    "cep": getattr(analysis["company_data"], "cep", None),
                    "capital_social": getattr(analysis["company_data"], "capital_social", None),
                    "porte": getattr(analysis["company_data"], "porte", None),
                    "telefone": getattr(analysis["company_data"], "telefone", None),
                    "email": getattr(analysis["company_data"], "email", None),
                    "socios": socios,
                }
                analysis["company_data"] = company_data_dict
            
            # Buscar filiais (estabelecimentos com mesmo CNPJ básico)
            filiais_result = await session.execute(
                select(CNPJReceitaFederalModel).where(
                    CNPJReceitaFederalModel.cnpj.like(f"{cnpj_basico}%")
                )
            )
            filiais_models = filiais_result.scalars().all()
            
            # Separar matriz e filiais
            matriz = None
            filiais_list = []
            
            for filial_model in filiais_models:
                cnpj_filial = filial_model.cnpj
                # Formatar CNPJ: 00.000.000/0000-00
                cnpj_formatado = f"{cnpj_filial[:2]}.{cnpj_filial[2:5]}.{cnpj_filial[5:8]}/{cnpj_filial[8:12]}-{cnpj_filial[12:14]}"
                
                filial_dict = {
                    "cnpj": cnpj_filial,
                    "cnpj_formatado": cnpj_formatado,
                    "razao_social": filial_model.razao_social,
                    "nome_fantasia": filial_model.nome_fantasia,
                    "situacao_cadastral": filial_model.situacao_cadastral,
                    "logradouro": filial_model.logradouro,
                    "numero": filial_model.numero,
                    "bairro": filial_model.bairro,
                    "municipio": filial_model.municipio,
                    "uf": filial_model.uf,
                    "cep": filial_model.cep,
                }
                
                # Verificar se é matriz (ordem 0001)
                if cnpj_filial[8:12] == "0001":
                    matriz = filial_dict
                else:
                    filiais_list.append(filial_dict)
            
            filiais = {
                "matriz": matriz,
                "filiais": filiais_list,
                "total_filiais": len(filiais_list),
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching analysis: {str(e)}")
    
    return templates.TemplateResponse("analysis_detail.html", {
        "request": request,
        "user": user,
        "analysis": analysis,
        "filiais": filiais,
        "active_page": "analyses"
    })

@router.get("/companies", response_class=HTMLResponse)
async def companies_page(request: Request):
    """Companies page"""
    user = get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("companies.html", {
        "request": request,
        "user": user,
        "active_page": "companies"
    })

@router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    """Users management page"""
    user = get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if user.get("role") not in ["ADMIN", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return templates.TemplateResponse("users.html", {
        "request": request,
        "user": user,
        "active_page": "users"
    })

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Admin page"""
    user = get_user_from_session(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if user.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user,
        "active_page": "admin"
    })

# Partials for HTMX
@router.get("/web/partials/dashboard-stats", response_class=HTMLResponse)
async def dashboard_stats_partial(request: Request):
    """Dashboard statistics partial"""
    user = get_user_from_session(request)
    if not user:
        return HTMLResponse("<p class='text-red-500'>Não autenticado</p>", status_code=401)
    
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<p class='text-red-500'>Token não encontrado</p>", status_code=401)
    
    # Call API to get dashboard summary
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/api/v1/dashboard/summary",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                html = f"""
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                                </svg>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Total de Análises</dt>
                                    <dd class="text-lg font-medium text-gray-900">{data['total_analyses']}</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                                </svg>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Este Mês</dt>
                                    <dd class="text-lg font-medium text-gray-900">{data['analyses_this_month']}</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Em Processamento</dt>
                                    <dd class="text-lg font-medium text-gray-900">{data['processing']}</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-white overflow-hidden shadow rounded-lg">
                    <div class="p-5">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Concluídas Hoje</dt>
                                    <dd class="text-lg font-medium text-gray-900">{data['completed_today']}</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </div>
                """
                return HTMLResponse(html)
            else:
                return HTMLResponse("<p class='text-red-500'>Erro ao carregar estatísticas</p>")
        except Exception as e:
            return HTMLResponse(f"<p class='text-red-500'>Erro: {str(e)}</p>")

@router.get("/web/partials/recent-analyses", response_class=HTMLResponse)
async def recent_analyses_partial(request: Request):
    """Recent analyses partial"""
    user = get_user_from_session(request)
    if not user:
        return HTMLResponse("<li class='px-6 py-4 text-red-500'>Não autenticado</li>", status_code=401)
    
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<li class='px-6 py-4 text-red-500'>Token não encontrado</li>", status_code=401)
    
    # Call API to get recent analyses
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/api/v1/analyses?limit=10",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                
                # Check if data is a list or dict with results
                if isinstance(data, dict):
                    analyses = data.get('items', data.get('results', []))
                else:
                    analyses = data if isinstance(data, list) else []
                
                if not analyses:
                    return HTMLResponse("<li class='px-6 py-4 text-center text-gray-500'>Nenhuma análise encontrada</li>")
                
                html = ""
                for analysis in analyses:
                    # Safely get values with defaults
                    analysis_id = analysis.get('id', '') if isinstance(analysis, dict) else ''
                    cnpj = analysis.get('cnpj', 'N/A') if isinstance(analysis, dict) else 'N/A'
                    status = analysis.get('status', 'N/A') if isinstance(analysis, dict) else 'N/A'
                    risk_level = analysis.get('risk_level', 'N/A') if isinstance(analysis, dict) else 'N/A'
                    risk_score = analysis.get('risk_score', 0) if isinstance(analysis, dict) else 0
                    
                    status_color = "green" if status == "COMPLETED" else "yellow" if status == "PROCESSING" else "gray"
                    risk_color = "red" if risk_level == "HIGH" else "yellow" if risk_level == "MEDIUM" else "green"
                    
                    html += f"""
                    <li>
                        <a href="/analyses/{analysis_id}" class="block hover:bg-gray-50">
                            <div class="px-4 py-4 sm:px-6">
                                <div class="flex items-center justify-between">
                                    <p class="text-sm font-medium text-blue-600 truncate">{cnpj}</p>
                                    <div class="ml-2 flex-shrink-0 flex">
                                        <p class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-{status_color}-100 text-{status_color}-800">
                                            {status}
                                        </p>
                                    </div>
                                </div>
                                <div class="mt-2 sm:flex sm:justify-between">
                                    <div class="sm:flex">
                                        <p class="flex items-center text-sm text-gray-500">
                                            Score: {risk_score:.1f}
                                        </p>
                                    </div>
                                    <div class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                                        <p class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-{risk_color}-100 text-{risk_color}-800">
                                            {risk_level}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </a>
                    </li>
                    """
                return HTMLResponse(html)
            else:
                return HTMLResponse("<li class='px-6 py-4 text-red-500'>Erro ao carregar análises</li>")
        except Exception as e:
            return HTMLResponse(f"<li class='px-6 py-4 text-red-500'>Erro: {str(e)}</li>")

@router.get("/web/partials/analyses-list", response_class=HTMLResponse)
async def analyses_list_partial(request: Request):
    """Analyses list partial"""
    user = get_user_from_session(request)
    if not user:
        return HTMLResponse("<li class='px-6 py-4 text-red-500'>Não autenticado</li>", status_code=401)
    
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<li class='px-6 py-4 text-red-500'>Token não encontrado</li>", status_code=401)
    
    # Call API to get all analyses
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/api/v1/analyses?limit=100",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                
                # Check if data is a list or dict with results
                if isinstance(data, dict):
                    analyses = data.get('items', data.get('results', []))
                else:
                    analyses = data if isinstance(data, list) else []
                
                if not analyses:
                    return HTMLResponse("<li class='px-6 py-4 text-center text-gray-500'>Nenhuma análise encontrada. Crie sua primeira análise!</li>")
                
                html = ""
                for analysis in analyses:
                    # Safely get values with defaults
                    analysis_id = analysis.get('id', '') if isinstance(analysis, dict) else ''
                    cnpj = analysis.get('cnpj', 'N/A') if isinstance(analysis, dict) else 'N/A'
                    status = analysis.get('status', 'N/A') if isinstance(analysis, dict) else 'N/A'
                    risk_level = analysis.get('risk_level', 'N/A') if isinstance(analysis, dict) else 'N/A'
                    risk_score = analysis.get('risk_score', 0) if isinstance(analysis, dict) else 0
                    created_at = analysis.get('created_at', '') if isinstance(analysis, dict) else ''
                    
                    # Format date
                    date_str = created_at[:10] if created_at else 'N/A'
                    if date_str != 'N/A' and '-' in date_str:
                        parts = date_str.split('-')
                        date_str = f"{parts[2]}/{parts[1]}/{parts[0]}"
                    
                    status_color = "green" if status == "COMPLETED" else "yellow" if status == "PROCESSING" else "gray"
                    risk_color = "red" if risk_level == "HIGH" else "yellow" if risk_level == "MEDIUM" else "green"
                    
                    html += f"""
                    <li>
                        <a href="/analyses/{analysis_id}" class="block hover:bg-gray-50">
                            <div class="px-4 py-4 sm:px-6">
                                <div class="flex items-center justify-between">
                                    <p class="text-sm font-medium text-blue-600 truncate">{cnpj}</p>
                                    <div class="ml-2 flex-shrink-0 flex">
                                        <p class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-{status_color}-100 text-{status_color}-800">
                                            {status}
                                        </p>
                                    </div>
                                </div>
                                <div class="mt-2 sm:flex sm:justify-between">
                                    <div class="sm:flex">
                                        <p class="flex items-center text-sm text-gray-500">
                                            Score: {risk_score:.1f} | Criada em: {date_str}
                                        </p>
                                    </div>
                                    <div class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                                        <p class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-{risk_color}-100 text-{risk_color}-800">
                                            {risk_level}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </a>
                    </li>
                    """
                return HTMLResponse(html)
            else:
                return HTMLResponse("<li class='px-6 py-4 text-red-500'>Erro ao carregar análises</li>")
        except Exception as e:
            return HTMLResponse(f"<li class='px-6 py-4 text-red-500'>Erro: {str(e)}</li>")
    
@router.get("/web/partials/companies-list", response_class=HTMLResponse)
async def companies_list_partial(request: Request):
    """Companies list partial"""
    user = get_user_from_session(request)
    if not user:
        return HTMLResponse("<li class='px-6 py-4 text-red-500'>Não autenticado</li>", status_code=401)
    
    token = request.session.get("access_token")
    if not token:
        return HTMLResponse("<li class='px-6 py-4 text-red-500'>Token não encontrado</li>", status_code=401)
    
    # Get search query if provided
    search_query = request.query_params.get('search', '')
    
    # Call API to get companies
    async with httpx.AsyncClient() as client:
        try:
            url = "http://localhost:8000/api/v1/search/companies"
            if search_query:
                url += f"?q={search_query}"
            
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                
                # SearchResult returns {total, items, page, page_size, query}
                if isinstance(data, dict):
                    companies = data.get('items', [])
                else:
                    companies = data if isinstance(data, list) else []
                
                if not companies:
                    return HTMLResponse("<li class='px-6 py-4 text-center text-gray-500'>Nenhuma empresa encontrada.</li>")
                
                html = ""
                for company in companies:
                    # Safely get values
                    cnpj = company.get('cnpj', 'N/A') if isinstance(company, dict) else 'N/A'
                    razao_social = company.get('razao_social', 'N/A') if isinstance(company, dict) else 'N/A'
                    nome_fantasia = company.get('nome_fantasia', '') if isinstance(company, dict) else ''
                    situacao = company.get('situacao_cadastral', 'N/A') if isinstance(company, dict) else 'N/A'
                    porte = company.get('porte', 'N/A') if isinstance(company, dict) else 'N/A'
                    
                    # Format CNPJ
                    if cnpj != 'N/A' and len(cnpj) == 14:
                        cnpj_formatted = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
                    else:
                        cnpj_formatted = cnpj
                    
                    # Status color
                    status_color = "green" if situacao == "ATIVA" else "red" if situacao == "BAIXADA" else "yellow"
                    
                    html += f"""
                    <li class="hover:bg-gray-50">
                        <div class="px-4 py-4 sm:px-6">
                            <div class="flex items-center justify-between">
                                <div class="flex-1">
                                    <p class="text-sm font-medium text-gray-900 truncate">{razao_social}</p>
                                    {f'<p class="text-sm text-gray-500">{nome_fantasia}</p>' if nome_fantasia else ''}
                                </div>
                                <div class="ml-2 flex-shrink-0">
                                    <p class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-{status_color}-100 text-{status_color}-800">
                                        {situacao}
                                    </p>
                                </div>
                            </div>
                            <div class="mt-2 sm:flex sm:justify-between">
                                <div class="sm:flex">
                                    <p class="flex items-center text-sm text-gray-500">
                                        CNPJ: {cnpj_formatted}
                                    </p>
                                </div>
                                <div class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                                    <p>Porte: {porte}</p>
                                </div>
                            </div>
                            <div class="mt-2">
                                <button onclick="requestAnalysis('{cnpj}')" class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                    Solicitar Análise
                                </button>
                            </div>
                        </div>
                    </li>
                    """
                return HTMLResponse(html)
            else:
                return HTMLResponse("<li class='px-6 py-4 text-red-500'>Erro ao carregar empresas</li>")
        except Exception as e:
            return HTMLResponse(f"<li class='px-6 py-4 text-red-500'>Erro: {str(e)}</li>")
    
    token = request.session.get("access_token")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/api/v1/analyses?limit=5",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            data = response.json()
            analyses = data.get("items", [])
        except httpx.HTTPError:
            analyses = []
    
    return templates.TemplateResponse("partials/recent_analyses.html", {
        "request": request,
        "analyses": analyses
    })

@router.get("/web/partials/analyses-table", response_class=HTMLResponse)
async def analyses_table_partial(
    request: Request,
    page: int = 1,
    search: Optional[str] = None,
    status: Optional[str] = None
):
    """Analyses table partial with pagination"""
    user = get_user_from_session(request)
    if not user:
        return HTMLResponse(content="<div>Not authenticated</div>", status_code=401)
    
    token = request.session.get("access_token")
    
    # Build query params
    params = {"page": page, "per_page": 10}
    if search:
        params["search"] = search
    if status:
        params["status"] = status
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://localhost:8000/api/v1/analyses",
                headers={"Authorization": f"Bearer {token}"},
                params=params
            )
            response.raise_for_status()
            analyses = response.json()
        except httpx.HTTPError:
            analyses = {"items": [], "total": 0, "page": 1, "per_page": 10, "pages": 0}
    
    return templates.TemplateResponse("partials/analyses_table.html", {
        "request": request,
        "analyses": analyses
    })


@router.get("/api/analyses/{analysis_id}/events")
async def analysis_events(request: Request, analysis_id: str):
    """
    Endpoint SSE (Server-Sent Events) para enviar atualizações em tempo real
    sobre o status de uma análise.
    """
    async def event_generator():
        """Gerador de eventos SSE"""
        from trivaxion.infrastructure.db.base import async_session_maker
        from trivaxion.adapters.outbound.persistence.sqlalchemy_repositories import SQLAlchemyAnalysisRepository
        from trivaxion.infrastructure.db.models import AnalysisModel
        from sqlalchemy import select
        
        # Enviar evento inicial de conexão
        yield f"data: {json.dumps({'type': 'connected', 'analysis_id': analysis_id})}\n\n"
        
        last_status = None
        last_risk_level = None
        max_iterations = 60  # Máximo de 5 minutos (60 * 5 segundos)
        iteration = 0
        
        while iteration < max_iterations:
            try:
                async with async_session_maker() as session:
                    # Buscar análise atualizada
                    result = await session.execute(
                        select(AnalysisModel).where(AnalysisModel.id == analysis_id)
                    )
                    analysis = result.scalar_one_or_none()
                    
                    if not analysis:
                        yield f"data: {json.dumps({'type': 'error', 'message': 'Análise não encontrada'})}\n\n"
                        break
                    
                    # Verificar se houve mudança no status
                    if last_status != analysis.status:
                        last_status = analysis.status
                        yield f"data: {json.dumps({'type': 'status_changed', 'status': analysis.status})}\n\n"
                        
                        if analysis.status == 'completed':
                            yield f"data: {json.dumps({'type': 'analysis_completed'})}\n\n"
                            break
                    
                    # Verificar se o risk_level foi calculado
                    if last_risk_level != analysis.risk_level and analysis.risk_level != 'unknown':
                        last_risk_level = analysis.risk_level
                        yield f"data: {json.dumps({'type': 'risk_calculated', 'risk_level': analysis.risk_level, 'risk_score': float(analysis.risk_score)})}\n\n"
                    
                    # Se a análise foi concluída, parar de enviar eventos
                    if analysis.status == 'completed':
                        break
                
                # Aguardar 5 segundos antes de verificar novamente
                await asyncio.sleep(5)
                iteration += 1
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                break
        
        # Enviar evento de encerramento
        yield f"data: {json.dumps({'type': 'disconnected'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Desabilitar buffering no nginx
        }
    )
