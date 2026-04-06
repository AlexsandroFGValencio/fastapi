"""add cnpj receita federal table

Revision ID: 002
Revises: 001
Create Date: 2026-03-26 01:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('cnpj_receita_federal',
    sa.Column('cnpj', sa.String(length=14), nullable=False),
    sa.Column('razao_social', sa.String(length=500), nullable=True),
    sa.Column('nome_fantasia', sa.String(length=500), nullable=True),
    sa.Column('situacao_cadastral', sa.String(length=100), nullable=True),
    sa.Column('data_situacao_cadastral', sa.DateTime(), nullable=True),
    sa.Column('motivo_situacao_cadastral', sa.String(length=200), nullable=True),
    sa.Column('data_inicio_atividade', sa.DateTime(), nullable=True),
    sa.Column('cnae_fiscal_principal', sa.String(length=20), nullable=True),
    sa.Column('cnae_fiscal_secundaria', sa.Text(), nullable=True),
    sa.Column('tipo_logradouro', sa.String(length=100), nullable=True),
    sa.Column('logradouro', sa.String(length=500), nullable=True),
    sa.Column('numero', sa.String(length=50), nullable=True),
    sa.Column('complemento', sa.String(length=200), nullable=True),
    sa.Column('bairro', sa.String(length=200), nullable=True),
    sa.Column('cep', sa.String(length=10), nullable=True),
    sa.Column('uf', sa.String(length=2), nullable=True),
    sa.Column('municipio', sa.String(length=200), nullable=True),
    sa.Column('ddd_telefone_1', sa.String(length=20), nullable=True),
    sa.Column('ddd_telefone_2', sa.String(length=20), nullable=True),
    sa.Column('ddd_fax', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=200), nullable=True),
    sa.Column('qualificacao_responsavel', sa.String(length=200), nullable=True),
    sa.Column('capital_social', sa.Float(), nullable=True),
    sa.Column('porte_empresa', sa.String(length=50), nullable=True),
    sa.Column('opcao_simples', sa.String(length=10), nullable=True),
    sa.Column('data_opcao_simples', sa.DateTime(), nullable=True),
    sa.Column('data_exclusao_simples', sa.DateTime(), nullable=True),
    sa.Column('opcao_mei', sa.String(length=10), nullable=True),
    sa.Column('natureza_juridica', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('cnpj')
    )
    op.create_index(op.f('ix_cnpj_receita_federal_cnpj'), 'cnpj_receita_federal', ['cnpj'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_cnpj_receita_federal_cnpj'), table_name='cnpj_receita_federal')
    op.drop_table('cnpj_receita_federal')
