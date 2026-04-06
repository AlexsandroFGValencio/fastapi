from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from trivaxion.domain.analysis.analysis import AnalysisStatus, RiskLevel
from trivaxion.domain.audit.audit_event import EventType
from trivaxion.domain.companies.company import CompanySize, CompanyStatus
from trivaxion.domain.identity.user import UserRole, UserStatus
from trivaxion.domain.organizations.organization import OrganizationStatus, PlanType
from trivaxion.domain.reports.report import ReportFormat, ReportStatus
from trivaxion.infrastructure.db.base import Base


class CNPJReceitaFederalModel(Base):
    """Modelo para armazenar dados públicos de CNPJs da Receita Federal"""
    __tablename__ = "cnpj_receita_federal"

    cnpj = Column(String(14), primary_key=True, index=True)
    razao_social = Column(String(500), nullable=True)
    nome_fantasia = Column(String(500), nullable=True)
    situacao_cadastral = Column(String(100), nullable=True)
    data_situacao_cadastral = Column(DateTime, nullable=True)
    motivo_situacao_cadastral = Column(String(200), nullable=True)
    data_inicio_atividade = Column(DateTime, nullable=True)
    cnae_fiscal_principal = Column(String(20), nullable=True)
    cnae_fiscal_secundaria = Column(Text, nullable=True)
    tipo_logradouro = Column(String(100), nullable=True)
    logradouro = Column(String(500), nullable=True)
    numero = Column(String(50), nullable=True)
    complemento = Column(String(200), nullable=True)
    bairro = Column(String(200), nullable=True)
    cep = Column(String(10), nullable=True)
    uf = Column(String(2), nullable=True)
    municipio = Column(String(200), nullable=True)
    ddd_telefone_1 = Column(String(20), nullable=True)
    ddd_telefone_2 = Column(String(20), nullable=True)
    ddd_fax = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    qualificacao_responsavel = Column(String(200), nullable=True)
    capital_social = Column(Float, nullable=True)
    porte_empresa = Column(String(50), nullable=True)
    opcao_simples = Column(String(10), nullable=True)
    data_opcao_simples = Column(DateTime, nullable=True)
    data_exclusao_simples = Column(DateTime, nullable=True)
    opcao_mei = Column(String(10), nullable=True)
    natureza_juridica = Column(String(200), nullable=True)
    search_vector = Column(sa.dialects.postgresql.TSVECTOR, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class CNPJSociosModel(Base):
    """Modelo para armazenar QSA (Quadro de Sócios e Administradores) da Receita Federal"""
    __tablename__ = "cnpj_socios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cnpj_basico = Column(String(8), nullable=False, index=True)
    identificador_socio = Column(String(1), nullable=True)
    nome_socio = Column(String(500), nullable=True)
    cpf_cnpj_socio = Column(String(14), nullable=True, index=True)
    qualificacao_socio = Column(String(10), nullable=True)
    data_entrada_sociedade = Column(DateTime, nullable=True)
    pais = Column(String(100), nullable=True)
    representante_legal = Column(String(500), nullable=True)
    nome_representante = Column(String(500), nullable=True)
    qualificacao_representante = Column(String(10), nullable=True)
    faixa_etaria = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    organization = relationship("OrganizationModel", back_populates="users")


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(14), nullable=True, unique=True)
    status = Column(Enum(OrganizationStatus), nullable=False, default=OrganizationStatus.TRIAL)
    plan = Column(Enum(PlanType), nullable=False, default=PlanType.FREE)
    max_users = Column(Integer, nullable=False, default=5)
    max_analyses_per_month = Column(Integer, nullable=False, default=100)
    analyses_count_current_month = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    users = relationship("UserModel", back_populates="organization")
    analyses = relationship("AnalysisModel", back_populates="organization")


class CompanyModel(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    cnpj = Column(String(18), unique=True, nullable=False, index=True)
    razao_social = Column(String(500), nullable=False)
    nome_fantasia = Column(String(500), nullable=True)
    status = Column(Enum(CompanyStatus), nullable=False, default=CompanyStatus.ATIVA)
    opening_date = Column(DateTime, nullable=True)
    cnae_principal = Column(String(20), nullable=True)
    cnae_description = Column(String(500), nullable=True)
    legal_nature = Column(String(200), nullable=True)
    address_street = Column(String(500), nullable=True)
    address_number = Column(String(50), nullable=True)
    address_complement = Column(String(200), nullable=True)
    address_neighborhood = Column(String(200), nullable=True)
    address_city = Column(String(200), nullable=True)
    address_state = Column(String(2), nullable=True)
    address_zipcode = Column(String(10), nullable=True)
    capital_social = Column(Float, nullable=True)
    company_size = Column(Enum(CompanySize), nullable=True)
    partners_data = Column("partners", JSON, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AnalysisModel(Base):
    __tablename__ = "analysis_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    cnpj = Column(String(14), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.PENDING)
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.UNKNOWN)
    risk_score = Column(Float, nullable=False, default="-")
    risk_signals_data = Column("risk_signals", JSON, nullable=True)
    source_results_data = Column("source_results", JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    organization = relationship("OrganizationModel", back_populates="analyses")
    user = relationship("UserModel")
    reports = relationship("ReportModel", back_populates="analysis")


class ReportModel(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_requests.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    format = Column(Enum(ReportFormat), nullable=False)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.PENDING)
    content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    generated_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    analysis = relationship("AnalysisModel", back_populates="reports")


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type = Column(Enum(EventType), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    event_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
