"""add socios table

Revision ID: 004
Revises: 003
Create Date: 2026-03-27 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('cnpj_socios',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('cnpj_basico', sa.String(length=8), nullable=False),
    sa.Column('identificador_socio', sa.String(length=1), nullable=True),
    sa.Column('nome_socio', sa.String(length=500), nullable=True),
    sa.Column('cpf_cnpj_socio', sa.String(length=14), nullable=True),
    sa.Column('qualificacao_socio', sa.String(length=10), nullable=True),
    sa.Column('data_entrada_sociedade', sa.DateTime(), nullable=True),
    sa.Column('pais', sa.String(length=100), nullable=True),
    sa.Column('representante_legal', sa.String(length=500), nullable=True),
    sa.Column('nome_representante', sa.String(length=500), nullable=True),
    sa.Column('qualificacao_representante', sa.String(length=10), nullable=True),
    sa.Column('faixa_etaria', sa.String(length=10), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cnpj_socios_cnpj_basico'), 'cnpj_socios', ['cnpj_basico'], unique=False)
    op.create_index(op.f('ix_cnpj_socios_cpf_cnpj_socio'), 'cnpj_socios', ['cpf_cnpj_socio'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_cnpj_socios_cpf_cnpj_socio'), table_name='cnpj_socios')
    op.drop_index(op.f('ix_cnpj_socios_cnpj_basico'), table_name='cnpj_socios')
    op.drop_table('cnpj_socios')
