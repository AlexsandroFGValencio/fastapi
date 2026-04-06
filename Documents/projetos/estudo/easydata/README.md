# Trivaxion - Plataforma SaaS de Análise de Dados Empresariais

[![CI](https://github.com/your-org/trivaxion/workflows/CI/badge.svg)](https://github.com/your-org/trivaxion/actions)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Trivaxion é uma plataforma SaaS 100% Python para análise de dados empresariais brasileiras, com coleta automatizada de dados públicos, avaliação de risco e geração de relatórios.

## 🚀 Características

- **Arquitetura Hexagonal**: Separação clara entre domínio, aplicação e infraestrutura
- **100% Python**: Backend e frontend no mesmo ecossistema
- **Multi-tenant**: Suporte a múltiplas organizações
- **Scrapers Resilientes**: Coleta de dados da Receita Federal e Certidão Trabalhista
- **Busca Avançada**: Elasticsearch para busca full-text e filtros
- **Risk Engine**: Sistema plugável de avaliação de risco
- **API REST**: Endpoints completos com OpenAPI/Swagger
- **Web Interface**: FastAPI + Jinja2 + HTMX
- **Deploy Flexível**: Suporte para VPS, Railway, Render e Fly.io

## 📋 Requisitos

- Python 3.14+
- PostgreSQL 16+
- Elasticsearch 8.12+
- Redis 7+
- Docker e Docker Compose (recomendado)

## 🛠️ Instalação

### Desenvolvimento Local com Docker

```bash
# Clonar repositório
git clone https://github.com/your-org/trivaxion.git
cd trivaxion

# Copiar configuração
cp .env.example .env

# Iniciar serviços
docker-compose -f docker-compose.local.yml up -d

# Executar migrações
docker-compose -f docker-compose.local.yml exec app alembic upgrade head

# Criar índices Elasticsearch
docker-compose -f docker-compose.local.yml exec app python scripts/bootstrap/create_indices.py

# Seed inicial (opcional)
docker-compose -f docker-compose.local.yml exec app python scripts/seed/initial_data.py
```

Acesse:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Web**: http://localhost:8000

### Desenvolvimento Local sem Docker

```bash
# Instalar UV
pip install uv

# Instalar dependências
uv pip install -r pyproject.toml
uv pip install -e .

# Configurar .env
cp .env.example .env

# Executar migrações
alembic upgrade head

# Criar índices
python scripts/bootstrap/create_indices.py

# Iniciar aplicação
uvicorn trivaxion.main:app --reload
```

## 🏗️ Arquitetura

### Estrutura do Projeto

```
src/trivaxion/
├── domain/              # Entidades e regras de negócio
│   ├── identity/        # Usuários e autenticação
│   ├── organizations/   # Organizações
│   ├── companies/       # Empresas
│   ├── analysis/        # Análises e risk engine
│   ├── reports/         # Relatórios
│   ├── audit/           # Auditoria
│   └── shared/          # Value objects e exceções
├── application/         # Casos de uso e portas
│   ├── use_cases/       # Lógica de aplicação
│   ├── dto/             # Data Transfer Objects
│   └── ports/           # Interfaces (repositories, providers)
├── adapters/            # Adaptadores
│   ├── inbound/         # HTTP, Web
│   └── outbound/        # Persistence, Scrapers, Search
└── infrastructure/      # Configuração e bootstrap
    ├── config/          # Settings
    ├── db/              # Database setup
    ├── di/              # Dependency injection
    ├── logging/         # Structured logging
    └── security/        # JWT, Password hashing
```

### Camadas

1. **Domain**: Lógica de negócio pura, sem dependências externas
2. **Application**: Orquestração via use cases, define ports
3. **Adapters**: Implementações concretas (HTTP, DB, Scrapers)
4. **Infrastructure**: Configuração, DI, logging, security

## 📊 Stack Tecnológica

- **Framework**: FastAPI 0.115+
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 16
- **Search**: Elasticsearch 8.12+
- **Cache**: Redis 7
- **Migrations**: Alembic
- **Templates**: Jinja2
- **Frontend**: HTMX + Alpine.js
- **Auth**: JWT (python-jose)
- **Password**: bcrypt (passlib)
- **Logging**: structlog
- **Testing**: pytest + pytest-asyncio
- **Linting**: ruff + mypy
- **Package Manager**: uv

## 🔐 Autenticação

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@trivaxion.com", "password": "admin123"}'

# Usar token
curl http://localhost:8000/api/v1/analyses \
  -H "Authorization: Bearer <access_token>"
```

## 📡 API Endpoints

### Auth
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Usuário atual

### Análises
- `POST /api/v1/analyses` - Criar análise
- `GET /api/v1/analyses` - Listar análises
- `GET /api/v1/analyses/{id}` - Detalhes da análise
- `GET /api/v1/dashboard/summary` - Dashboard

### Busca
- `GET /api/v1/search/companies` - Buscar empresas
- `GET /api/v1/search/analyses` - Buscar análises

### Admin
- `GET /api/v1/admin/health` - Health check
- `GET /api/v1/admin/audit-events` - Eventos de auditoria

## 🚀 Deploy

### VPS (Produção Completa)

```bash
# Preparar VPS
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clonar e configurar
git clone https://github.com/your-org/trivaxion.git
cd trivaxion
cp .env.example .env
nano .env  # Configurar variáveis

# Deploy
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec app alembic upgrade head
docker-compose -f docker-compose.prod.yml exec app python scripts/bootstrap/create_indices.py
```

### Railway

```bash
railway init
railway add postgresql
railway add redis
railway up
```

### Render

1. Conectar repositório GitHub
2. Criar Web Service
3. Adicionar PostgreSQL database
4. Configurar environment variables
5. Deploy automático

## 🧪 Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=src/trivaxion --cov-report=html

# Apenas unitários
pytest tests/unit/

# Apenas integração
pytest tests/integration/
```

## 🔧 Troubleshooting

### Erro ao buildar Docker
Se encontrar erro de dependências ao buildar:
```bash
# Limpar cache do Docker
docker-compose -f docker-compose.local.yml down -v
docker system prune -a

# Rebuildar sem cache
docker-compose -f docker-compose.local.yml build --no-cache
docker-compose -f docker-compose.local.yml up -d
```

### Elasticsearch não inicia
```bash
# Verificar logs
docker-compose -f docker-compose.local.yml logs elasticsearch

# Aumentar memória se necessário (no docker-compose.local.yml)
# ES_JAVA_OPTS=-Xms1g -Xmx1g
```

### PostgreSQL connection refused
```bash
# Verificar se está rodando
docker-compose -f docker-compose.local.yml ps

# Reiniciar serviço
docker-compose -f docker-compose.local.yml restart postgres
```

### Testar configuração completa
```bash
# Script de teste automatizado
./scripts/test-docker-setup.sh
```

## 📚 Documentação

- [ADRs](docs/adr/) - Architecture Decision Records
- [Arquitetura](docs/architecture/) - Diagramas C4
- [Runbooks](docs/runbooks/) - Guias operacionais
- [API Docs](http://localhost:8000/docs) - OpenAPI/Swagger

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- **Trivaxion Team** - *Trabalho inicial*

## 🙏 Agradecimentos

- Receita Federal pela disponibilização de dados públicos
- Comunidade FastAPI
- Comunidade Python Brasil