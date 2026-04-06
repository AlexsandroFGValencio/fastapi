"""add fulltext search indexes

Revision ID: 003
Revises: 002
Create Date: 2026-03-26 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar coluna tsvector para busca full-text
    op.execute("""
        ALTER TABLE cnpj_receita_federal 
        ADD COLUMN search_vector tsvector;
    """)
    
    # Criar índice GIN para busca full-text
    op.execute("""
        CREATE INDEX idx_cnpj_search_vector 
        ON cnpj_receita_federal 
        USING GIN(search_vector);
    """)
    
    # Criar função para atualizar search_vector
    op.execute("""
        CREATE OR REPLACE FUNCTION cnpj_search_vector_update() 
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('portuguese', COALESCE(NEW.cnpj, '')), 'A') ||
                setweight(to_tsvector('portuguese', COALESCE(NEW.razao_social, '')), 'A') ||
                setweight(to_tsvector('portuguese', COALESCE(NEW.nome_fantasia, '')), 'B') ||
                setweight(to_tsvector('portuguese', COALESCE(NEW.municipio, '')), 'C') ||
                setweight(to_tsvector('portuguese', COALESCE(NEW.uf, '')), 'C');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Criar trigger para atualizar automaticamente
    op.execute("""
        CREATE TRIGGER tsvector_update_trigger
        BEFORE INSERT OR UPDATE ON cnpj_receita_federal
        FOR EACH ROW EXECUTE FUNCTION cnpj_search_vector_update();
    """)
    
    # Atualizar registros existentes
    op.execute("""
        UPDATE cnpj_receita_federal SET search_vector = 
            setweight(to_tsvector('portuguese', COALESCE(cnpj, '')), 'A') ||
            setweight(to_tsvector('portuguese', COALESCE(razao_social, '')), 'A') ||
            setweight(to_tsvector('portuguese', COALESCE(nome_fantasia, '')), 'B') ||
            setweight(to_tsvector('portuguese', COALESCE(municipio, '')), 'C') ||
            setweight(to_tsvector('portuguese', COALESCE(uf, '')), 'C');
    """)
    
    # Adicionar índices adicionais para performance
    op.create_index('idx_cnpj_razao_social', 'cnpj_receita_federal', ['razao_social'])
    op.create_index('idx_cnpj_nome_fantasia', 'cnpj_receita_federal', ['nome_fantasia'])
    op.create_index('idx_cnpj_municipio', 'cnpj_receita_federal', ['municipio'])
    op.create_index('idx_cnpj_uf', 'cnpj_receita_federal', ['uf'])


def downgrade() -> None:
    op.drop_index('idx_cnpj_uf', table_name='cnpj_receita_federal')
    op.drop_index('idx_cnpj_municipio', table_name='cnpj_receita_federal')
    op.drop_index('idx_cnpj_nome_fantasia', table_name='cnpj_receita_federal')
    op.drop_index('idx_cnpj_razao_social', table_name='cnpj_receita_federal')
    
    op.execute("DROP TRIGGER IF EXISTS tsvector_update_trigger ON cnpj_receita_federal;")
    op.execute("DROP FUNCTION IF EXISTS cnpj_search_vector_update();")
    op.execute("DROP INDEX IF EXISTS idx_cnpj_search_vector;")
    op.execute("ALTER TABLE cnpj_receita_federal DROP COLUMN IF EXISTS search_vector;")
