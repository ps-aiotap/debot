"""Add RBAC tables and tenant isolation

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)

    # Create user_org_memberships table
    op.create_table('user_org_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'ANALYST', 'VIEWER', name='role'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_id', 'user_id', name='unique_user_org')
    )
    op.create_index(op.f('ix_user_org_memberships_id'), 'user_org_memberships', ['id'], unique=False)

    # Add org_id to existing tables for tenant isolation
    op.add_column('documents', sa.Column('org_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_documents_org_id'), 'documents', ['org_id'], unique=False)
    
    op.add_column('chat_history', sa.Column('org_id', sa.Integer(), nullable=False))
    op.add_column('chat_history', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_chat_history_org_id'), 'chat_history', ['org_id'], unique=False)
    op.create_index(op.f('ix_chat_history_user_id'), 'chat_history', ['user_id'], unique=False)

def downgrade() -> None:
    # Remove tenant isolation columns
    op.drop_index(op.f('ix_chat_history_user_id'), table_name='chat_history')
    op.drop_index(op.f('ix_chat_history_org_id'), table_name='chat_history')
    op.drop_column('chat_history', 'user_id')
    op.drop_column('chat_history', 'org_id')
    
    op.drop_index(op.f('ix_documents_org_id'), table_name='documents')
    op.drop_column('documents', 'org_id')

    # Drop RBAC tables
    op.drop_index(op.f('ix_user_org_memberships_id'), table_name='user_org_memberships')
    op.drop_table('user_org_memberships')
    
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')