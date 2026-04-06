melhor?

# Constitution - Trivaxion Platform

## Software Design Document (SDD)

**Versão:** 1.0.0  
**Data:** Abril 2026
**Projeto:** trivaxion
**Domínio:** Plataforma SaaS de Análise de Dados Empresariais Brasileiras via CNPJ

---

## Termos Normativos (RFC 2119)

Este documento utiliza os seguintes termos normativos conforme definido na [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119):

| Termo | Significado |
|-------|-------------|
| **MUST** / **DEVE** | Requisito absoluto e obrigatório |
| **MUST NOT** / **NÃO DEVE** | Proibição absoluta |
| **SHOULD** / **DEVERIA** | Recomendação forte, mas pode haver exceções justificadas |
| **SHOULD NOT** / **NÃO DEVERIA** | Não recomendado, mas pode haver exceções justificadas |
| **MAY** / **PODE** | Opcional, a critério do desenvolvedor |

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura do Sistema](#2-arquitetura-do-sistema)
3. [Estrutura de Diretórios](#3-estrutura-de-diretórios)
4. [Camadas da Arquitetura Hexagonal](#4-camadas-da-arquitetura-hexagonal)
5. [Componentes Principais](#5-componentes-principais)
6. [Padrões de Design](#6-padrões-de-design)
7. [Princípios de Engenharia de Software](#7-princípios-de-engenharia-de-software)
8. [Fluxo de Dados](#8-fluxo-de-dados)
9. [Integrações Externas](#9-integrações-externas)
10. [Configuração e Ambientes](#10-configuração-e-ambientes)
11. [Testes](#11-testes)
12. [Segurança](#12-segurança)
13. [Convenções de Código e Nomenclatura](#13-convenções-de-código-e-nomenclatura)
14. [Guia de Implementação de Novas Funcionalidades](#14-guia-de-implementação-de-novas-funcionalidades)
15. [Estratégia de Cache](#15-estratégia-de-cache)
16. [SLA, SLO e Latência](#16-sla-slo-e-latência)
17. [Performance e Scaling](#17-performance-e-scaling)
18. [Observabilidade](#18-observabilidade)
19. [Decisões Arquiteturais (ADRs)](#19-decisões-arquiteturais-adrs)
20. [Glossário](#20-glossário)

---

## 1. Visão Geral

### 1.1 Propósito

A **Trivaxion Platform** é uma plataforma SaaS especializada em análise de dados empresariais brasileiras através do CNPJ. O sistema permite que clientes insiram o CNPJ de uma empresa e recebam dados completos e estruturados da empresa na plataforma, incluindo informações cadastrais, sócios, situação fiscal, e análise de risco. O sistema foi projetado seguindo os princípios da **Arquitetura Hexagonal (Ports and Adapters)**, garantindo alta coesão, baixo acoplamento e facilidade de manutenção.

### 1.2 Escopo

- **Consulta por CNPJ**: Input do CNPJ pelo cliente e retorno de dados completos da empresa
- **Coleta de Dados**: Extração automatizada de dados da Receita Federal e fontes públicas
- **Análise de Risco**: Sistema inteligente de avaliação de risco empresarial com score detalhado
- **Dados Estruturados**: Informações sobre razão social, nome fantasia, situação cadastral, sócios (QSA), endereço, CNAE, capital social
- **Gestão de Organizações**: Multi-tenant com suporte a múltiplas organizações clientes
- **Controle de Acesso**: Autenticação e autorização baseada em planos (FREE, PRO, ENTERPRISE)
- **Auditoria**: Registro completo de operações e consultas realizadas
- **Web Interface**: Interface web moderna com FastAPI + Jinja2 + HTMX
- **API REST**: Endpoints completos para integração via API

### 1.3 Stack Tecnológica

| Categoria | Tecnologia | Versão |
|-----------|------------|--------|
| **Linguagem** | Python | 3.14+ |
| **Framework Web** | FastAPI | 0.115+ |
| **Banco de Dados** | PostgreSQL | 16+ |
| **Cache** | Redis | 7+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Validação** | Pydantic | 2.10+ |
| **Migrações** | Alembic | 1.14+ |
| **HTTP Client** | httpx, aiohttp | 0.28+, 3.11+ |
| **Autenticação** | python-jose, passlib | 3.3+, 1.7+ |
| **Logging** | structlog | 24.4+ |
| **Templates** | Jinja2 | 3.1.4+ |
| **Frontend** | HTMX + Alpine.js | - |
| **Cache L1** | cachetools | 5.3+ |
| **Gerenciador de Dependências** | uv | - |

### 1.4 Volumetria e Performance

- **Throughput:** ~20 RPM (baixa volumetria, foco em qualidade de dados)
- **Latência Alvo:** P95 ≤ 500ms, P99 ≤ 1000ms
- **Disponibilidade:** 99.5%
- **Escalabilidade:** Horizontal via containers

### 1.5 Ambientes

| Ambiente | URL |
|----------|-----|
| Development | `http://localhost:8000` |
| Staging | `https://staging.trivaxion.com` |
| Production | `https://app.trivaxion.com` |

---

## 2. Arquitetura do Sistema

### 2.1 Arquitetura Hexagonal (Ports and Adapters)

A arquitetura hexagonal organiza o código em três camadas principais, isolando a lógica de negócio das dependências externas:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ADAPTERS (INBOUND)                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         HTTP Controllers                            │    │
│  │   • AuthController      • AnalysisController   • DashboardController │    │
│  │   • UserController       • SearchController    • AdminController    │    │
│  │   • FiliaisController                                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PORTS (INBOUND)                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Interfaces/Contracts                         │    │
│  │   • AuthService       • AnalysisService     • SearchService          │    │
│  │   • UserService       • DashboardService    • AdminService           │    │
│  │   • FiliaisService                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 DOMAIN                                       │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────────────┐  ┌─────────┐    │
│  │   User    │  │   Org     │  │ Company   │  │    Analysis     │  │ Audit   │    │
│  │ Entity    │  │ Entity    │  │ Entity    │  │    Entity       │  │ Entity  │    │
│  └───────────┘  └───────────┘  └───────────┘  └─────────────────┘  └─────────┘    │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────────────┐  ┌─────────┐    │
│  │   Auth    │  │   Mgmt    │  │   Data    │  │    Risk         │  │ Search  │    │
│  │ Use Cases │  │ Use Cases │  │ Use Cases │  │   Use Cases     │  │Use Cases│    │
│  └───────────┘  └───────────┘  └───────────┘  └─────────────────┘  └─────────┘    │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────────────┐  ┌─────────┐    │
│  │   Value   │  │  Entity   │  │   CNPJ    │  │   Exceptions    │  │ Shared  │    │
│  │ Objects   │  │    ID     │  │   Value   │  │                 │  │ Kernel  │    │
│  └───────────┘  └───────────┘  └───────────┘  └─────────────────┘  └─────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PORTS (OUTBOUND)                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Interfaces/Contracts                         │    │
│  │   • DatabasePort      • CachePort                 │    │
│  │   • EmailPort         • CNPJDataPort              │    │
│  │   • DomainEventBus    • IdempotencyStore          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ADAPTERS (OUTBOUND)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                 Infrastructure Implementations                        │    │
│  │   • PostgreSQL      • Redis                 • TTLCache (cachetools)     │    │
│  │   • EmailService    • CNPJDataAPI          • JWTAuth                   │    │
│  │   • DomainEventDispatcher • IdempotencyRedis                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Estrutura de Diretórios

```
src/trivaxion/
├── adapters/
│   ├── inbound/
│   │   ├── http/
│   │   │   ├── controllers/          # HTTP Controllers
│   │   │   │   ├── auth_routes.py
│   │   │   │   ├── analysis_routes.py
│   │   │   │   ├── dashboard_routes.py
│   │   │   │   ├── search_routes.py
│   │   │   │   ├── admin_routes.py
│   │   │   │   ├── user_routes.py
│   │   │   │   └── filiais_routes.py
│   │   │   ├── dependencies.py       # Dependency injection
│   │   │   └── schemas/              # Request/Response schemas
│   │   └── web/                      # Web interface (HTML)
│   │       ├── routes/
│   │       ├── templates/
│   │       └── static/
│   └── outbound/
│       ├── database/                 # Database adapters
│       ├── cache/                    # Redis and TTLCache adapters
│       ├── email/                    # Email adapters
│       ├── cnpj/                     # CNPJ data adapters
│       ├── events/                   # Domain events adapters
│       └── idempotency/              # Idempotency adapters
├── application/
│   ├── services/                     # Application services
│   ├── dto/                         # Data Transfer Objects
│   └── ports/                       # Port interfaces
├── domain/
│   ├── entities/                     # Domain entities
│   │   ├── companies/               # Company entity
│   │   ├── analysis/                # Analysis entity
│   │   ├── identity/                # User entity
│   │   ├── organizations/           # Organization entity
│   │   ├── audit/                   # Audit entity
│   │   ├── reports/                 # Report entity
│   │   └── shared/                  # Shared entities
│   ├── events/                       # Domain events
│   │   ├── company_events.py
│   │   ├── analysis_events.py
│   │   └── user_events.py
│   ├── use_cases/                    # Use cases
│   ├── ports/                        # Ports (interfaces)
│   └── exceptions/                   # Domain exceptions
├── infrastructure/
│   ├── config/                       # Configuration
│   ├── db/                          # Database setup
│   ├── di/                          # Dependency injection
│   ├── logging/                     # Logging setup
│   ├── security/                    # Security utilities
│   └── services/                    # External services
└── main.py                           # Application entry point
```

---

## 4. Camadas da Arquitetura Hexagonal

### 4.1 Domain Layer (Core Business Logic)

**Responsabilidade:** Conter toda a lógica de negócio pura, sem dependências externas.

**Componentes:**
- **Entities:** Objetos de negócio com identidade e comportamento
- **Use Cases:** Casos de uso que orquestram entidades
- **Ports:** Interfaces que definem contratos com o mundo exterior
- **Exceptions:** Exceções específicas do domínio

**Regras:**
- **MUST NOT** importar de adapters ou infrastructure
- **MUST** conter apenas lógica de negócio
- **MUST** ser testável sem dependências externas

### 4.2 Application Layer

**Responsabilidade:** Orquestrar use cases e coordenar fluxos de aplicação.

**Componentes:**
- **Services:** Serviços que implementam os use cases
- **DTOs:** Objetos para transferência de dados entre camadas

**Regras:**
- **MUST** depender apenas de domain e ports
- **MUST NOT** conter lógica de negócio complexa
- **MUST** coordenar use cases e adapters

### 4.3 Adapters Layer

**Responsabilidade:** Implementar ports e conectar com tecnologias externas.

**Tipos:**
- **Inbound Adapters:** Recebem requisições do mundo exterior (HTTP, CLI)
- **Outbound Adapters:** Implementam ports para tecnologias externas

**Regras:**
- **MUST** implementar interfaces definidas nos ports
- **MUST NOT** conter lógica de negócio
- **MUST** converter dados entre formatos externos e internos

---

## 5. Componentes Principais

### 5.1 Domain Entities

| Entidade | Descrição | Atributos Principais |
|---------|-----------|---------------------|
| **User** | Usuário da plataforma | id, email, password, organization_id, created_at |
| **Organization** | Organização/empresa cliente | id, name, plan_type, analysis_count, settings |
| **Company** | Empresa analisada via CNPJ | id, cnpj, razao_social, nome_fantasia, status, opening_date, cnae_principal, address, capital_social, partners |
| **Analysis** | Análise de CNPJ solicitada | id, cnpj, organization_id, requested_by, status, risk_level, risk_score, risk_signals, source_results |
| **AuditEvent** | Eventos de auditoria do sistema | id, action, entity_type, entity_id, user_id, timestamp, metadata |

### 5.2 Value Objects

| Value Object | Descrição | Atributos |
|-------------|-----------|-----------|
| **CNPJ** | Validador e formatador de CNPJ | value, formatted, is_valid |
| **EntityId** | Identificador único de entidades (UUID v7) | value |
| **Address** | Endereço completo | street, number, city, state, zip_code |
| **Money** | Valores monetários | amount, currency |
| **Partner** | Sócio/QSA da empresa | name, cpf_cnpj, qualification, entry_date |

### 5.3 Entity ID Strategy

**Regras Obrigatórias:**
- **MUST** usar UUID v7 para todas as entidades
- **MUST** gerar IDs no domínio (EntityId.generate())
- **MUST NOT** depender de auto-increment do banco
- **SHOULD** usar monotonic UUID para ordenação temporal

**Implementação:**
```python
from uuid import uuid7

class EntityId:
    def __init__(self, value: str | None = None):
        self.value = value or str(uuid7())
    
    @classmethod
    def generate(cls) -> "EntityId":
        return cls()
    
    def __str__(self) -> str:
        return self.value
```

**Benefícios:**
- Ordenação cronológica natural
- Geração distribuída sem colisões
- Performance superior a UUID v4
- Sortable por timestamp embutido

### 5.4 Enums

| Enum | Valores | Descrição |
|------|---------|-----------|
| **CompanyStatus** | ATIVA, SUSPENSA, INAPTA, BAIXADA, NULA | Situação cadastral da empresa |
| **CompanySize** | MEI, ME, EPP, DEMAIS | Porte da empresa |
| **AnalysisStatus** | PENDING, PROCESSING, COMPLETED, FAILED, PARTIAL_COMPLETED | Status da análise |
| **RiskLevel** | LOW, MEDIUM, HIGH, UNKNOWN | Nível de risco |
| **DataSource** | RECEITA_FEDERAL, CERTIDAO_TRABALHISTA | Fontes de dados |
| **PlanType** | FREE, PRO, ENTERPRISE | Planos da organização |

### 5.5 Domain Events

| Event | Descrição | Quando é disparado |
|-------|-----------|-------------------|
| **CompanyCreated** | Nova empresa criada | Ao salvar novo CNPJ |
| **CompanyUpdated** | Dados da empresa atualizados | Ao atualizar dados CNPJ |
| **AnalysisStarted** | Análise iniciada | Ao criar nova análise |
| **AnalysisCompleted** | Análise concluída | Ao finalizar processamento |
| **RiskCalculated** | Score de risco calculado | Ao processar sinais de risco |
| **UserRegistered** | Novo usuário registrado | Ao criar conta |
| **OrganizationCreated** | Nova organização criada | Ao criar tenant |

**Regras de Processamento:**
- **Domain Events MUST ser assíncronos**
- **Handlers MUST ser non-blocking**
- **Failures MUST NOT quebrar fluxo principal**

**Implementação:**
```python
import asyncio
from typing import List

class DomainEvent:
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.timestamp = datetime.utcnow()

class DomainEventDispatcher:
    async def dispatch(self, events: List[DomainEvent]):
        tasks = []
        for event in events:
            handlers = self.get_handlers(event)
            for handler in handlers:
                # Non-blocking execution com try/catch
                task = asyncio.create_task(self._safe_execute(handler, event))
                tasks.append(task)
        
        # Fire and forget - não espera conclusão
        if tasks:
            asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_execute(self, handler, event):
        try:
            await handler.handle(event)
        except Exception as e:
            logger.error("domain_event_handler_failed", event=event.__class__.__name__, error=str(e))
            # Não propaga erro - fluxo principal continua
```

### 5.6 Use Cases

| Use Case | Descrição | Fluxo Principal |
|---------|-----------|-----------------|
| **AuthenticateUser** | Login e gestão de sessões | Email/Senha → JWT → Sessão |
| **CreateAnalysis** | Criar análise por CNPJ | CNPJ Input → Coleta → Análise → Resultado |
| **ProcessCNPJData** | Processar dados do CNPJ | Busca RF → Parse → Store |
| **CalculateRiskScore** | Calcular score de risco | Signals → Weight → Score |
| **SearchCompanies** | Buscar empresas | Query → Database → Results |
| **ManageOrganization** | Gestão de organizações | CRUD → Plan limits |
| **AuditOperations** | Auditoria de operações | Event capture → Store |
| **ProcessDomainEvents** | Processar eventos de domínio | Event Bus → Handlers |

### 5.7 Idempotency Strategy

| Operação | Idempotency Key | TTL | Implementação |
|----------|----------------|-----|---------------|
| **CreateAnalysis** | `analysis:{cnpj}:{org_id}` | 24h | Redis + request hash |
| **UpdateCompany** | `company:{cnpj}:{data_hash}` | 1h | PostgreSQL unique constraint |
| **UserRegistration** | `user:{email}` | 7d | Database unique constraint |
| **RiskCalculation** | `risk:{cnpj}:{version}` | 6h | Redis cache |

### 5.8 Data Freshness Strategy

| Dado | Fonte | Frequência | Estratégia |
|------|-------|------------|------------|
| **Dados Básicos CNPJ** | Receita Federal | Diária | Scheduled update |
| **Sócios/QSA** | Receita Federal | Semanal | Delta updates |
| **Status Cadastral** | Receita Federal | Horária | Real-time validation |
| **Análises de Risco** | Internal | Sob demanda | Cache com invalidação |
| **Cache L1** | Memory | TTL-based | cachetools.TTLCache |

### 5.9 Adapters

| Adapter | Tipo | Descrição |
|---------|------|-----------|
| **AuthController** | Inbound HTTP | Endpoints de autenticação (/api/v1/auth) |
| **AnalysisController** | Inbound HTTP | Endpoints de análises (/api/v1/analyses) |
| **DashboardController** | Inbound HTTP | Dashboard e resumos (/api/v1/dashboard) |
| **SearchController** | Inbound HTTP | Busca de empresas (/api/v1/search) |
| **FiliaisController** | Inbound HTTP | Consulta de filiais (/filiais) |
| **PostgreSQLAdapter** | Outbound | Persistência de dados |
| **RedisAdapter** | Outbound | Cache distribuído e sessões |
| **TTLCacheAdapter** | Outbound | Cache L1 em memória (cachetools) |
| **CNPJDataAPIAdapter** | Outbound | API de dados CNPJ |
| **EmailAdapter** | Outbound | Envio de notificações |
| **DomainEventDispatcher** | Outbound | Dispatch de eventos de domínio |
| **IdempotencyRedisAdapter** | Outbound | Armazenamento de chaves de idempotência |

### 5.10 Consistency Model

**Regras de Consistência:**
- **Database é source of truth**
- **Cache é eventual consistent**
- **Domain events são at-least-once**
- **Idempotency garante segurança**

**Modelo Híbrido:**
```python
# Strong consistency - Database
class CompanyRepository:
    async def save(self, company: Company) -> Company:
        # ACID transaction garante consistência forte
        async with transaction():
            saved = await self.db.save(company)
            # Cache update é eventual consistent
            await self.cache.invalidate(f"company:{company.cnpj}")
            # Domain events são at-least-once
            await self.event_dispatcher.dispatch(company.domain_events)
            return saved

# Eventual consistency - Cache
@cached(cache)
def get_company_cached(cnpj: str) -> Company:
    # Pode ter stale data por até TTL
    return company_repository.find_by_cnpj(cnpj)

# At-least-once delivery - Events
class EventDispatcher:
    async def dispatch(self, events: List[DomainEvent]):
        # Tenta entregar pelo menos uma vez
        # Idempotency nos handlers garante segurança
        await self.publish_with_retry(events)
```

**Garantias:**
- **Read Your Writes**: Database sempre consistente
- **Cache Staleness**: Máximo de TTL configurado
- **Event Ordering**: UUID v7 garante ordenação
- **Duplicate Processing**: Idempotency previne efeitos colaterais

### 5.11 Processamento Paralelo e Resposta Incremental

### Princípio

As fontes externas de dados MUST ser executadas em paralelo e seus resultados MUST ser enviados ao frontend assim que estiverem disponíveis, sem aguardar a conclusão de todas as fontes.

Este modelo segue o padrão de Progressive Data Delivery.

### Regras Obrigatórias

- As fontes de dados MUST ser executadas em paralelo (async)
- O backend MUST NOT aguardar todas as fontes concluírem
- Cada fonte MUST emitir um resultado parcial independente
- O backend MUST enviar resultados incrementalmente ao frontend
- O frontend MUST renderizar dados assim que recebidos
- Falha em uma fonte MUST NOT bloquear as demais
- Timeout em uma fonte SHOULD gerar resultado parcial com status "unavailable"

### Estratégias de Implementação

Backend MAY usar:

- asyncio.as_completed
- asyncio.gather(return_exceptions=True)
- Server-Sent Events (SSE)
- StreamingResponse (HTTP chunked)
- WebSockets
- Polling (fallback)

### Contrato de Resposta Parcial

Cada fonte MUST retornar resultados no seguinte formato:

```json
{
  "source": "receita_federal",
  "status": "completed",
  "data": { ... },
  "timestamp": "ISO-8601"
}
```

Em caso de erro:

```json
{
  "source": "certidao_trabalhista",
  "status": "failed",
  "error": "timeout",
  "timestamp": "ISO-8601"
}
```

### Regras para Frontend

- Frontend MUST renderizar dados incrementalmente
- Frontend MUST NOT aguardar payload completo
- Frontend SHOULD exibir loading por fonte
- Frontend SHOULD mostrar falhas parciais
- Frontend MUST permitir atualização progressiva da UI

### Benefícios

- Redução de latência percebida
- Melhor experiência do usuário
- Tolerância a falhas
- Paralelismo natural
- Melhor escalabilidade

### 5.12 Frontend Web Interface

| Componente | Tecnologia | Descrição |
|------------|------------|-----------|
| **Landing Page** | HTML + TailwindCSS | Página de marketing (/) |
| **Web App** | Jinja2 + HTMX + Alpine.js | Interface principal (/app) |
| **Dashboard** | HTMX Components | Resumo e métricas |
| **CNPJ Search** | Form + AJAX | Input de CNPJ e resultados |
| **Authentication** | Session-based | Login/logout web |

---

## 6. Padrões de Design

### 6.1 Dependency Injection

**Regra:** **MUST** usar injeção de dependências para todos os ports.

```python
# Use Case recebe ports via construtor
class AnalyzeCompanyUseCase:
    def __init__(
        self,
        company_repository: CompanyRepositoryPort,
        search_service: SearchPort,
        cache_service: CachePort
    ):
        self.company_repository = company_repository
        self.search_service = search_service
        self.cache_service = cache_service
```

### 6.2 Repository Pattern

**Regra:** **MUST** usar Repository Pattern para acesso a dados.

```python
# Port定义
class CompanyRepositoryPort(ABC):
    @abstractmethod
    async def save(self, company: Company) -> Company: ...
    @abstractmethod
    async def find_by_cnpj(self, cnpj: str) -> Optional[Company]: ...

# Adapter实现
class PostgreSQLCompanyAdapter(CompanyRepositoryPort):
    async def save(self, company: Company) -> Company: ...
    async def find_by_cnpj(self, cnpj: str) -> Optional[Company]: ...
```

### 6.3 Factory Pattern

**Regra:** **SHOULD** usar Factory Pattern para criação de objetos complexos.

```python
class AnalysisFactory:
    @staticmethod
    def create_analysis(
        analysis_type: AnalysisType,
        company: Company,
        parameters: Dict[str, Any]
    ) -> Analysis:
        return Analysis(
            type=analysis_type,
            company_id=company.id,
            parameters=parameters
        )
```

---

## 7. Princípios de Engenharia de Software

### 7.1 SOLID

**Regras Obrigatórias:**

1. **Single Responsibility Principle (SRP)**
   - Cada classe **MUST** ter apenas uma responsabilidade
   - Métodos **SHOULD NOT** fazer múltiplas coisas

2. **Open/Closed Principle (OCP)**
   - Classes **MUST** ser abertas para extensão, fechadas para modificação
   - Usar interfaces e polimorfismo

3. **Liskov Substitution Principle (LSP)**
   - Subclasses **MUST** ser substituíveis por suas classes base
   - Contratos de interfaces **MUST** ser respeitados

4. **Interface Segregation Principle (ISP)**
   - Interfaces **SHOULD** ser pequenas e coesas
   - Clientes **SHOULD NOT** depender de métodos que não usam

5. **Dependency Inversion Principle (DIP)**
   - Módulos de alto nível **MUST NOT** depender de módulos de baixo nível
   - Ambos **MUST** depender de abstrações (interfaces)

### 7.2 KISS (Keep It Simple, Stupid)

**Regras:**
- **MUST** escolher a solução mais simples que funciona
- **MUST NOT** adicionar complexidade desnecessária
- **SHOULD** evitar over-engineering

### 7.3 YAGNI (You Aren't Gonna Need It)

**Regras:**
- **MUST NOT** implementar funcionalidades "para o futuro"
- **MUST** implementar apenas o que é necessário agora
- **SHOULD** adicionar código apenas quando há um requisito real

### 7.4 DRY (Don't Repeat Yourself)

**Regras:**
- **MUST NOT** duplicar lógica de negócio
- **SHOULD** extrair código repetido para helpers/mixins
- **MUST** usar composição sobre herança quando possível

---

## 8. Fluxo de Dados

### 8.1 Fluxo Principal: Consulta por CNPJ com Processamento Paralelo

```
1. HTTP Request (POST /api/v1/analyses) → AnalysisController
2. AnalysisController → CreateAnalysisUseCase
3. CreateAnalysisUseCase → IdempotencyStore (verificar duplicidade)
4. CreateAnalysisUseCase → ParallelDataProcessor
5. ParallelDataProcessor → Executar fontes em paralelo:
   - CNPJDataAPIAdapter → Receita Federal API
   - CertidaoTrabalhistaAPI → Certidão Trabalhista
   - QSADataAPI → Quadro de Sócios
6. Cada fonte → Resultado parcial → StreamingResponse
7. Frontend → Renderizar incrementalmente via SSE/WebSocket
8. CreateAnalysisUseCase → RiskAnalysisUseCase (quando dados suficientes)
9. RiskAnalysisUseCase → CalculateRiskScore
10. Analysis entity → AnalysisRepositoryPort → PostgreSQLAdapter
11. Domain Events: CompanyCreated, AnalysisStarted → DomainEventDispatcher
12. AnalysisController → StreamingResponse contínua
```

### 8.2 Fluxo de Resposta Incremental (Backend)

```
1. ParallelDataProcessor → asyncio.gather(return_exceptions=True)
2. Para cada fonte concluída:
   a. Formatar resultado parcial
   b. Enviar via SSE/Streaming
   c. Continuar aguardando outras fontes
3. Em caso de timeout/erro:
   a. Enviar status "failed" ou "unavailable"
   b. Continuar processamento de outras fontes
4. Ao final → Enviar status "completed"
```

### 8.3 Fluxo de Resposta Incremental (Frontend)

```
1. Frontend → Conectar SSE/WebSocket
2. Receber resultado parcial → Atualizar UI
3. Exibir loading por fonte individual
4. Mostrar dados assim que disponíveis
5. Tratar falhas parciais gracefully
6. Permitir retry por fonte específica
```

### 8.4 Fluxo de Autenticação Web

```
1. Web Request (POST /login) → WebRoutes
2. WebRoutes → AuthController (API)
3. AuthController → AuthenticateUserUseCase
4. AuthenticateUserUseCase → UserRepositoryPort
5. UserRepositoryPort → PostgreSQLAdapter
6. PostgreSQLAdapter → Database
7. Database → PostgreSQLAdapter
8. PostgreSQLAdapter → AuthenticateUserUseCase
9. AuthenticateUserUseCase → JWTToken generation
10. AuthController → SessionMiddleware → RedisAdapter
11. Domain Event: UserLoggedIn → DomainEventDispatcher
12. WebRoutes → HTML Response → Dashboard
```

### 8.5 Fluxo de Busca de Empresas

```
1. HTTP Request (GET /api/v1/search/companies) → SearchController
2. SearchController → SearchCompaniesUseCase
3. SearchCompaniesUseCase → TTLCacheAdapter (L1 cache)
4. Se cache miss: CompanyRepositoryPort → PostgreSQLAdapter
5. PostgreSQLAdapter → Database (SQL queries)
6. Database → Results
7. SearchCompaniesUseCase → TTLCacheAdapter (store cache)
8. SearchController → HTTP Response (JSON)
```

### 8.6 Fluxo de Domain Events

```
1. Qualquer operação de domínio → Domain Event creation
2. Domain Event → DomainEventBus
3. DomainEventBus → Event Handlers
4. Handlers →:
   - AuditLogger (registrar evento)
   - EmailNotifier (enviar notificações)
   - CacheInvalidator (invalidar caches)
   - MetricsCollector (registrar métricas)
```

### 8.7 Fluxo de Idempotência

```
1. Request → IdempotencyMiddleware
2. IdempotencyMiddleware → Generate idempotency key
3. IdempotencyMiddleware → IdempotencyStore (Redis)
4. Se key existe: Return cached response
5. Se não existe: Process request → Store response → Return
```

---

## 9. Integrações Externas

### 9.1 Fontes de Dados CNPJ

| Fonte | Tipo | Adapter | Timeout | Formato |
|-------|------|---------|---------|---------|
| **Receita Federal** | HTTP API | CNPJDataAPIAdapter | 30s | JSON |
| **Dados Públicos CNPJ** | REST API | CNPJDataAPIAdapter | 10s | JSON |
| **Validação CNPJ** | HTTP API | CNPJValidationAdapter | 5s | JSON |

### 9.2 Serviços Externos

| Serviço | Propósito | Adapter |
|---------|-----------|---------|
| **Email Service** | Notificações para usuários | EmailAdapter |
| **File Storage** | Armazenamento de backups | StorageAdapter |
| **Monitoring** | Métricas e logs da aplicação | MonitoringAdapter |
| **SMS Service** | Alertas críticos (futuro) | SMSAdapter |

### 9.3 Detalhes da Integração com Receita Federal

**Fontes de Dados:**
- **Dados Abertos CNPJ**: API REST para consulta individual
- **Validação de CNPJ**: Endpoints para verificação de formato e status
- **Atualizações**: Webhooks para mudanças de status (futuro)

**Estrutura dos Dados:**
```json
{
  "cnpj": "12345678901234",
  "razao_social": "Empresa Exemplo Ltda",
  "nome_fantasia": "Exemplo",
  "situacao_cadastral": "ATIVA",
  "data_situacao": "2020-01-01",
  "cnae_principal": "1234567",
  "cnae_descricao": "Atividade principal",
  "endereco": {
    "logradouro": "Rua Exemplo",
    "numero": "123",
    "complemento": "Sala 1",
    "bairro": "Centro",
    "cep": "12345678",
    "municipio": "São Paulo",
    "uf": "SP"
  },
  "capital_social": 1000000.00,
  "porte": "ME",
  "socios": [
    {
      "nome": "João Silva",
      "cpf_cnpj": "12345678901",
      "qualificacao": "Administrador",
      "data_entrada": "2020-01-01"
    }
  ]
}
```

### 9.4 Processamento de Dados

**Pipeline de ETL:**
1. **Extract**: API calls para Receita Federal
2. **Transform**: Parse e validação dos dados
3. **Load**: Inserção em PostgreSQL
4. **Cache**: Store em TTLCache (L1) e Redis (L2)
5. **Events**: Disparar Domain Events para atualizações

---

## 10. Configuração e Ambientes

### 10.1 Variáveis de Ambiente

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/trivaxion
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# Cache Configuration
CACHE_L1_SIZE=1000
CACHE_L1_TTL=300
CACHE_L2_TTL=3600

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# CNPJ Data Sources
CNPJ_RECEITA_FEDERAL_URL=https://api.receita.fazenda.gov.br
CNPJ_API_TIMEOUT=30
CNPJ_CACHE_TTL=3600

# External Services
EMAIL_API_KEY=your-email-api-key
CNPJ_RATE_LIMIT=10

# Application Settings
APP_NAME=Trivaxion
APP_VERSION=0.1.0
DEBUG=false
CORS_ORIGINS=["http://localhost:3000", "https://app.trivaxion.com"]

# Plan Limits
FREE_PLAN_ANALYSIS_LIMIT=10
PRO_PLAN_ANALYSIS_LIMIT=1000
ENTERPRISE_PLAN_ANALYSIS_LIMIT=-1

# Idempotency
IDEMPOTENCY_TTL=86400
IDEMPOTENCY_PREFIX=idemp

# Domain Events
DOMAIN_EVENTS_ENABLED=true
EVENT_BUS_TYPE=redis

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

### 10.2 Configuração por Ambiente

| Ambiente | Database Pool | Cache L1 TTL | Cache L2 TTL | CNPJ Rate | Log Level |
|----------|---------------|-------------|-------------|-----------|-----------|
| **Development** | 5 | 5min | 15min | 100/min | DEBUG |
| **Staging** | 10 | 10min | 30min | 50/min | INFO |
| **Production** | 20 | 5min | 1h | 10/min | INFO |

---

## 11. Testes

### 11.1 Estratégia de Testes

**Regra:** **MUST** ter 100% de coverage para código novo.

### 11.2 Tipos de Testes

| Tipo | Descrição | Ferramenta | Coverage |
|------|-----------|------------|----------|
| **Unit Tests** | Testes unitários de entidades e use cases | pytest + pytest-asyncio | 100% |
| **Integration Tests** | Testes de integração com adapters | pytest + testcontainers | 80% |
| **E2E Tests** | Testes ponta a ponta da web interface | playwright | 70% |
| **Performance Tests** | Testes de performance de operações críticas | pytest | - |

### 11.3 Estrutura de Testes

```
tests/
├── unit/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── test_company.py
│   │   │   ├── test_analysis.py
│   │   │   ├── test_user.py
│   │   │   └── test_organization.py
│   │   └── use_cases/
│   │       ├── test_create_analysis.py
│   │       ├── test_authenticate_user.py
│   │       └── test_calculate_risk.py
│   ├── application/
│   │   └── services/
│   └── infrastructure/
├── integration/
│   ├── adapters/
│   │   ├── database/
│   │   ├── search/
│   │   └── scraping/
│   └── api/
│       ├── test_analysis_api.py
│       ├── test_auth_api.py
│       └── test_search_api.py
├── e2e/
│   └── web/
│       ├── test_login.py
│       ├── test_cnpj_search.py
│       └── test_dashboard.py
├── performance/
│   └── test_performance.py
└── conftest.py
```

### 11.4 Fixtures Principais

**Regra:** **MUST** usar fixtures para setup de testes.

```python
@pytest.fixture
async def company_repository():
    async with PostgreSQLContainer() as postgres:
        yield PostgreSQLCompanyAdapter(postgres.get_connection_url())

@pytest.fixture
async def analysis_repository():
    async with PostgreSQLContainer() as postgres:
        yield PostgreSQLAnalysisAdapter(postgres.get_connection_url())

@pytest.fixture
def sample_company():
    return Company(
        id=EntityId.generate(),
        cnpj=CNPJ("12345678901234"),
        razao_social="Test Company",
        status=CompanyStatus.ATIVA
    )

@pytest.fixture
def sample_analysis():
    return Analysis(
        id=EntityId.generate(),
        cnpj=CNPJ("12345678901234"),
        organization_id=EntityId.generate(),
        requested_by=EntityId.generate()
    )
```

---

## 12. Segurança

### 12.1 Autenticação

**Regras:**
- **MUST** usar JWT para autenticação stateless
- **MUST** usar bcrypt para hash de senhas
- **MUST** ter expiração de tokens (30min)
- **SHOULD** implementar refresh tokens

### 12.2 Autorização

**Regras:**
- **MUST** implementar RBAC (Role-Based Access Control)
- **MUST** verificar permissões em cada endpoint
- **SHOULD** usar decorators para autorização

### 12.3 Validação de Input

**Regras:**
- **MUST** usar Pydantic para validação
- **MUST** sanitizar todos os inputs
- **MUST** validar tipos e formatos

### 12.4 OWASP Top 10

**Controles Implementados:**
- **A01 Broken Access Control:** RBAC em todos os endpoints
- **A02 Cryptographic Failures:** bcrypt, JWT, HTTPS
- **A03 Injection:** SQLAlchemy com parameterized queries
- **A04 Insecure Design:** Arquitetura hexagonal segura
- **A05 Security Misconfiguration:** Headers de segurança
- **A06 Vulnerable Components:** Dependências atualizadas
- **A07 Identification/Authentication Failures:** JWT seguro
- **A08 Software/Data Integrity:** Validação de inputs
- **A09 Logging/Monitoring:** Logs de segurança
- **A10 Server-Side Request Forgery:** Validação de URLs

---

## 13. Convenções de Código e Nomenclatura

### 13.1 Convenções de Nomenclatura

| Elemento | Convenção | Exemplo |
|---------|-----------|---------|
| **Classes** | PascalCase | `CompanyAnalysisUseCase` |
| **Funções/Métodos** | snake_case | `analyze_company_data` |
| **Variáveis** | snake_case | `company_data` |
| **Constantes** | UPPER_SNAKE_CASE | `MAX_RETRY_ATTEMPTS` |
| **Interfaces/Ports** | PascalCase + Port | `CompanyRepositoryPort` |
| **Adapters** | PascalCase + Adapter | `PostgreSQLCompanyAdapter` |
| **DTOs** | PascalCase + DTO | `CompanyAnalysisDTO` |
| **Exceptions** | PascalCase + Error | `CompanyNotFoundError` |

### 13.2 Formatação de Código

**Ferramentas:**
- **ruff** para linting e formatação
- **mypy** para type checking
- **pre-commit** para hooks

**Regras:**
- **MUST** usar type hints em todo código
- **MUST** seguir PEP 8
- **SHOULD** limitar linhas a 88 caracteres (black)
- **MUST** ter complexidade ciclomática ≤ 8

### 13.3 Documentação

**Regras:**
- **MUST** documentar todas as classes públicas
- **MUST** documentar todos os métodos públicos
- **SHOULD** usar docstrings no formato Google

```python
class CompanyAnalysisUseCase:
    """Use case for analyzing company data.
    
    This use case orchestrates the analysis of company data from multiple
    sources, including web scraping and database queries.
    
    Attributes:
        company_repository: Repository for company data access
        scraping_service: Service for web scraping operations
    """
    
    async def analyze(self, cnpj: str) -> AnalysisResult:
        """Analyzes company data using CNPJ.
        
        Args:
            cnpj: The CNPJ number to analyze
            
        Returns:
            AnalysisResult containing the analysis data
            
        Raises:
            CompanyNotFoundError: If company is not found
            ScrapingError: If scraping operation fails
        """
```

---

## 14. Guia de Implementação de Novas Funcionalidades

### 14.1 Fluxo de Implementação

1. **Domain First**
   - Criar/alterar entidades
   - Definir ports (interfaces)
   - Implementar use cases

2. **Application Layer**
   - Criar DTOs
   - Implementar serviços

3. **Adapters**
   - Implementar ports
   - Criar controllers

4. **Tests**
   - Unit tests do domain
   - Integration tests dos adapters
   - E2E tests dos endpoints

### 14.2 Template de Nova Funcionalidade

```python
# 1. Domain Entity
class NewFeature(Entity):
    """New feature entity."""
    
# 2. Port Interface
class NewFeatureRepositoryPort(ABC):
    @abstractmethod
    async def save(self, feature: NewFeature) -> NewFeature: ...

# 3. Use Case
class NewFeatureUseCase:
    def __init__(self, repository: NewFeatureRepositoryPort): ...
    
    async def execute(self, params: NewFeatureParams) -> NewFeatureResult: ...

# 4. Adapter Implementation
class PostgreSQLNewFeatureAdapter(NewFeatureRepositoryPort):
    async def save(self, feature: NewFeature) -> NewFeature: ...

# 5. Controller
class NewFeatureController:
    def __init__(self, use_case: NewFeatureUseCase): ...
    
    async def create_feature(self, request: NewFeatureRequest) -> NewFeatureResponse: ...
```

---

## 15. Estratégia de Cache

### 15.1 Cache Strategy

**Regra:** **SHOULD** usar cache para dados frequentemente acessados e imutáveis.

### 15.2 Cache Layers

| Layer | Tecnologia | TTL | Exemplos | Tipo de Dado |
|-------|------------|-----|----------|--------------|
| **L1: Memory** | cachetools.TTLCache | 5-15min | Sessões de usuário, cálculos temporários | Transientes |
| **L2: Redis** | Redis Cluster | 1-24h | Dados de empresas, resultados de análises | CNPJ cache |
| **L3: Database** | PostgreSQL | N/A | Dados transacionais, auditoria | Persistente |

### 15.3 Cache Keys

**Pattern:** `{service}:{entity}:{id}:{version}`

```python
# Examples para CNPJ
"company:cnpj:12345678901234:v1"
"analysis:result:analysis_123:v2"
"user:session:user_456:v1"
"search:query:empresa_sao_paulo:v1"

# Cache para dados da Receita Federal
"cnpj:rf_data:12345678901234:v1"
"cnpj:socios:12345678901234:v1"
"cnpj:address:12345678901234:v1"
```

### 15.4 TTLCache Implementation (L1)

```python
from cachetools import TTLCache, cached

# Cache L1 em memória
cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutos

@cached(cache)
def get_company_cached(cnpj: str) -> Company:
    return company_repository.find_by_cnpj(cnpj)

# Alternativa com key customizada
@cached(cache, key=lambda cnpj: f"company:{cnpj}")
def get_company_with_custom_key(cnpj: str) -> Company:
    return company_repository.find_by_cnpj(cnpj)
```

### 15.5 Cache Invalidation

**Estratégias:**
- **Time-based**: TTL automático (5min L1, 1h L2 para CNPJ, 24h para análises)
- **Event-based**: Invalidação via Domain Events (CompanyUpdated)
- **Manual**: Limpeza via admin tools

### 15.6 Performance Optimization

**Dados Cacheados:**
- **Dados Básicos CNPJ**: 1h no Redis, 5min no TTLCache
- **Sócios/QSA**: 24h no Redis, 15min no TTLCache
- **Análises de Risco**: 6h no Redis, 10min no TTLCache
- **Resultados de Busca**: 15min no Redis, 5min no TTLCache

---

## 16. SLA, SLO e Latência

### 16.1 Service Level Objectives (SLOs)

| Métrica | Alvo | Descrição |
|---------|------|-----------|
| **Availability** | 99.5% | Uptime do serviço |
| **Latency P95** | ≤ 500ms | 95% das requisições |
| **Latency P99** | ≤ 1000ms | 99% das requisições |
| **Error Rate** | ≤ 1% | Taxa de erros |
| **Throughput** | 20 RPM | Requisições por minuto |

### 16.2 Service Level Agreements (SLAs)

| Cliente | SLA | Penalidade |
|---------|-----|------------|
| **Free Plan** | 99% | Crédito de serviço |
| **Pro Plan** | 99.5% | Reembolso parcial |
| **Enterprise** | 99.9% | Reembolso total |

---

## 17. Performance e Scaling

### 17.1 Performance Targets

Com base na volumetria de ~20 RPM e foco em dados CNPJ:

| Operação | Latência Alvo | Throughput | Complexidade |
|----------|---------------|------------|-------------|
| **Autenticação** | ≤ 200ms | 20 RPM | Baixa |
| **Consulta CNPJ (cache L1)** | ≤ 50ms | 15 RPM | Baixa |
| **Consulta CNPJ (cache L2)** | ≤ 300ms | 15 RPM | Baixa |
| **Consulta CNPJ (sem cache)** | ≤ 2000ms | 5 RPM | Alta |
| **Primeira Fonte Disponível** | ≤ 500ms | 15 RPM | Média |
| **Streaming Response** | ≤ 100ms/chunk | Streaming | Baixa |
| **Análise de Risco** | ≤ 500ms | 10 RPM | Média |
| **Busca Empresas (SQL)** | ≤ 400ms | 20 RPM | Média |
| **Domain Events** | ≤ 100ms | Assíncrono | Baixa |
| **Idempotency Check** | ≤ 10ms | 20 RPM | Baixa |

### 17.2 Bottlenecks Identificados

**Operações Críticas:**
1. **API CNPJ Receita Federal**: I/O bound, pode levar segundos
2. **Parse de dados CNPJ**: CPU intensive, requer validação
3. **Database queries complexas**: Memory intensive, requer indexação
4. **Cálculo de risco**: CPU intensive se múltiplos signals
5. **Domain Events**: I/O bound se muitos handlers
6. **Streaming Response**: Network bound se muitos clientes
7. **Parallel Processing**: Thread pool exhaustion

### 17.3 Scaling Strategy

**Horizontal Scaling:**
- **Application**: Kubernetes HPA (baseado em CPU/memory)
- **Database**: Read replicas para consultas CNPJ
- **Cache**: Redis Cluster para cache distribuído
- **Event Bus**: Redis pub/sub para domain events
- **Streaming**: Load balancer para SSE/WebSocket connections

**Vertical Scaling:**
- **CPU**: 2 cores por pod (4 cores para workers)
- **Memory**: 4GB por pod (8GB para processing)
- **Database**: RDS configurable com storage escalável
- **Cache L1**: TTLCache em memória por instância
- **Thread Pool**: Configurável para parallel processing

### 17.4 Performance Monitoring

**Métricas Chave:**
- Response time por endpoint (API)
- Database query performance (PostgreSQL)
- CNPJ API call time
- Cache hit ratio (TTLCache + Redis)
- Domain Event processing time
- Idempotency check time
- Memory usage em cache L1
- Queue depth para eventos
- Streaming connection count
- Parallel processing latency
- First byte time (TTFB) para streaming

**Alertas:**
- P95 > 1s para consulta CNPJ
- Cache hit ratio < 80%
- Database connections > 80%
- Memory usage > 85%
- Event processing delay > 5s
- Streaming connections > 1000
- Parallel processing timeout > 30s
- First byte time > 500ms

---

## 18. Observabilidade

### 18.1 Logging

**Estrutura:** Usando structlog com contexto

```python
import structlog

logger = structlog.get_logger()

# Logs de negócio CNPJ
logger.info(
    "cnpj_analysis_started",
    cnpj=cnpj,
    user_id=user_id,
    organization_id=organization_id,
    analysis_type=analysis_type
)

# Logs de performance
logger.info(
    "cnpj_data_downloaded",
    cnpj=cnpj,
    source="receita_federal",
    download_time_ms=download_time,
    data_size_bytes=data_size
)

# Logs de erro
logger.error(
    "cnpj_parsing_failed",
    cnpj=cnpj,
    error=error_message,
    source_file=source_file,
    line_number=line_number
)

# Logs de auditoria
logger.info(
    "analysis_completed",
    analysis_id=analysis_id,
    cnpj=cnpj,
    risk_score=risk_score,
    processing_time_ms=processing_time,
    user_id=user_id
)
```

**Níveis de Log:**
- **DEBUG:** Informação detalhada para debugging (parse steps, SQL queries)
- **INFO:** Eventos de negócio importantes (análises criadas, CNPJs processados)
- **WARNING:** Situações anormais mas não críticas (cache miss, retry attempts)
- **ERROR:** Erros que precisam atenção (falha no download, parsing errors)
- **CRITICAL:** Erros críticos que requerem ação imediata (database down, memory exhaustion)

### 18.2 Métricas

**Tipos de Métricas:**
- **Counters:** Número de requisições, análises CNPJ, erros
- **Gauges:** Memória, CPU, conexões ativas, cache size
- **Histograms:** Latência, duração de operações CNPJ
- **Timers:** Tempo de execução de use cases, download CNPJ

**Métricas Específicas CNPJ:**
```python
# Counters
cnpj_analysis_total{status="completed|failed|pending"}
cnpj_api_calls_total{source="receita_federal"}
cnpj_cache_hits_total{cache="l1|l2"}
cnpj_cache_misses_total{cache="l1|l2"}
domain_events_total{event_type="company_created|analysis_completed"}
idempotency_hits_total
idempotency_misses_total
parallel_processing_total
streaming_connections_active
partial_results_sent_total

# Histograms
cnpj_analysis_duration_seconds
cnpj_api_call_duration_seconds
cnpj_parsing_duration_seconds
risk_calculation_duration_seconds
domain_event_processing_duration_seconds
first_result_latency_seconds
streaming_chunk_duration_seconds

# Gauges
cnpj_cache_size{cache="l1|l2"}
active_users_current
database_connections_current
event_queue_depth
ttl_cache_memory_usage_bytes
streaming_connections_count
parallel_processing_queue_depth
```

**Implementação Futura:**
- Prometheus para coleta de métricas
- Grafana para dashboards (CNPJ metrics, system health)
- AlertManager para alertas (failed downloads, high latency)

### 18.3 Tracing

**Implementação Futura:**
- OpenTelemetry para distributed tracing
- Span por use case
- Propagação de contexto entre serviços

---

## 19. Decisões Arquiteturais (ADRs)

### ADR-001: Arquitetura Hexagonal

**Status:** Aceito  
**Data:** 2026-04-01  
**Decisão:** Usar arquitetura hexagonal para isolar lógica de negócio

**Consequências:**
- ✅ Baixo acoplamento
- ✅ Alta testabilidade
- ✅ Facilidade de substituição de tecnologias
- ❌ Curva de aprendizado inicial

### ADR-002: SQLAlchemy como ORM

**Status:** Aceito  
**Data:** 2026-04-01  
**Decisão:** Usar SQLAlchemy 2.0 com async

**Consequências:**
- ✅ Suporte a async/await
- ✅ Maturidade da ferramenta
- ✅ Flexibilidade de queries
- ❌ Verbosidade em casos simples

### ADR-003: FastAPI como Framework Web

**Status:** Aceito  
**Data:** 2026-04-01  
**Decisão:** Usar FastAPI para API REST

**Consequências:**
- ✅ Performance alta
- ✅ Type hints nativos
- ✅ Documentação automática
- ❌ Ecossistema menor que Django

---

## 20. Glossário

| Termo | Definição |
|-------|-----------|
| **Adapter** | Implementação concreta de um port |
| **Domain** | Camada central com lógica de negócio |
| **Entity** | Objeto com identidade e comportamento |
| **Port** | Interface que define um contrato |
| **Use Case** | Caso de uso que orquestra entidades |
| **DTO** | Data Transfer Object |
| **Repository** | Pattern para acesso a dados |
| **SaaS** | Software as a Service |
| **RPM** | Requests Per Minute |
| **SLA** | Service Level Agreement |
| **SLO** | Service Level Objective |
| **CNPJ** | Cadastro Nacional da Pessoa Jurídica |
| **QSA** | Quadro de Sócios e Administradores |
| **Receita Federal** | Fonte oficial de dados CNPJ |
| **Risk Score** | Score de risco calculado (0-100) |
| **Analysis** | Análise completa de um CNPJ |
| **Company** | Empresa com dados CNPJ estruturados |
| **Multi-tenant** | Arquitetura com múltiplas organizações |
| **HTMX** | Biblioteca para interações web sem JavaScript complexo |
| **Alpine.js** | Framework JavaScript minimalista |
| **ETL** | Extract, Transform, Load (pipeline de dados) |
| **TTLCache** | Cache em memória com TTL (cachetools) |
| **Domain Event** | Evento de domínio para desacoplamento |
| **Idempotency** | Propriedade de operações poderem ser repetidas |
| **Data Freshness** | Estratégia de atualização de dados |
| **Event Bus** | Sistema de dispatch de eventos |
| **Cache Hit Ratio** | Proporção de acertos no cache |
| **UUID v7** | UUID time-ordered para IDs de entidades |
| **EntityId** | Value object para identificadores únicos |
| **Consistency Model** | Modelo de consistência de dados |
| **Source of Truth** | Database como única fonte da verdade |
| **Eventual Consistency** | Cache eventualmente consistente |
| **At-least-once** | Garantia de entrega de eventos |
| **Non-blocking** | Operações que não bloqueiam o fluxo principal |
| **Progressive Data Delivery** | Entrega progressiva de dados |
| **Streaming Response** | Resposta HTTP em streaming |
| **Server-Sent Events** | SSE para comunicação unidirecional |
| **Parallel Processing** | Processamento paralelo de fontes |
| **First Byte Time** | Tempo até primeiro byte da resposta |
| **Partial Results** | Resultados parciais de fontes individuais |
| **Incremental Rendering** | Renderização incremental no frontend |

---

## Conclusão

Esta constituição estabelece as regras e diretrizes arquiteturais para a plataforma Trivaxion SaaS de análise de dados empresariais brasileiros via CNPJ. Todos os desenvolvedores **MUST** seguir estas diretrizes e as atualizações futuras **SHOULD** ser feitas através de ADRs.

**Princípios Fundamentais:**
1. **Simplicidade** sobre complexidade (KISS)
2. **Funcionalidade necessária** apenas (YAGNI)
3. **Código limpo** e reutilizável (DRY)
4. **Arquitetura limpa** com hexagonal
5. **Testes abrangentes** com 100% de coverage
6. **Segurança** como prioridade
7. **Performance** adequada à volumetria CNPJ
8. **Dados Brasileiros** como foco principal
9. **Event-Driven** com Domain Events assíncronos
10. **Idempotência** para resiliência
11. **Consistência Híbrida** com database como source of truth
12. **Progressive Data Delivery** para melhor UX

**Foco do Negócio:**
- Input: CNPJ do cliente
- Processamento: Coleta paralela via API, validação, análise de risco
- Output: Dados completos e estruturados da empresa (entrega incremental)
- Valor: Informações empresariais confiáveis e atualizadas com baixa latência

**Arquitetura Simplificada e Resiliente:**
- **IDs**: UUID v7 para ordenação e distribuição
- **Cache L1**: cachetools.TTLCache para performance
- **Cache L2**: Redis para persistência e distribuição
- **Eventos**: Domain Events assíncronos com non-blocking handlers
- **Idempotência**: Redis store para operações seguras
- **Consistência**: Database como source of truth, cache eventual consistent
- **Streaming**: Respostas incrementais via SSE/WebSocket
- **Dados**: PostgreSQL como única fonte da verdade
- **Processamento**: Paralelo com Progressive Data Delivery
