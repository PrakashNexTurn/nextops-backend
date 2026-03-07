"""Initial migration - Create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-07 06:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create enums
    tool_type_enum = postgresql.ENUM('custom', 'mcp', name='tool_type_enum', create_type=False)
    tool_type_enum.create(op.get_bind(), checkfirst=True)
    
    mcp_type_enum = postgresql.ENUM('stdio', 'sse', name='mcp_type_enum', create_type=False)
    mcp_type_enum.create(op.get_bind(), checkfirst=True)
    
    cloud_provider_enum = postgresql.ENUM('aws', 'azure', 'gcp', name='cloud_provider_enum', create_type=False)
    cloud_provider_enum.create(op.get_bind(), checkfirst=True)
    
    deployment_type_enum = postgresql.ENUM('new', 'existing', name='deployment_type_enum', create_type=False)
    deployment_type_enum.create(op.get_bind(), checkfirst=True)
    
    deployment_status_enum = postgresql.ENUM('pending', 'deployed', name='deployment_status_enum', create_type=False)
    deployment_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create tables
    op.create_table(
        'mcps',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('type', mcp_type_enum, nullable=False),
        sa.Column('command', sa.String(255), nullable=True),
        sa.Column('url', sa.String(255), nullable=True),
        sa.Column('args', sa.JSON(), nullable=True),
        sa.Column('headers', sa.JSON(), nullable=True),
        sa.Column('env_vars', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'tools',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tool_type', tool_type_enum, nullable=False),
        sa.Column('python_code', sa.Text(), nullable=True),
        sa.Column('mcp_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['mcp_id'], ['mcps.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'mcp_tools',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mcp_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tool_name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('input_schema', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['mcp_id'], ['mcps.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'cloud_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', cloud_provider_enum, nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('credentials', sa.JSON(), nullable=True),
        sa.Column('region', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('system_prompt', sa.Text(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'agent_tools',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tool_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['tool_id'], ['tools.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'planners',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('system_prompt', sa.Text(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'planner_agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('planner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['planner_id'], ['planners.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'deployments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bedrock_agent_id', sa.String(255), nullable=True),
        sa.Column('deployment_type', deployment_type_enum, nullable=False),
        sa.Column('status', deployment_status_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('planner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['planner_id'], ['planners.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('sessions')
    op.drop_table('deployments')
    op.drop_table('planner_agents')
    op.drop_table('planners')
    op.drop_table('agent_tools')
    op.drop_table('agents')
    op.drop_table('cloud_accounts')
    op.drop_table('mcp_tools')
    op.drop_table('tools')
    op.drop_table('mcps')
    
    op.execute('DROP TYPE IF EXISTS tool_type_enum')
    op.execute('DROP TYPE IF EXISTS mcp_type_enum')
    op.execute('DROP TYPE IF EXISTS cloud_provider_enum')
    op.execute('DROP TYPE IF EXISTS deployment_type_enum')
    op.execute('DROP TYPE IF EXISTS deployment_status_enum')
