"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
import json
import os
from pathlib import Path

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('creation_date', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create nodes table
    op.create_table(
        'nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('config_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_nodes_id'), 'nodes', ['id'], unique=False)

    # Insert initial node definitions from JSON metadata files
    # Get the path to nodes_metadata directory (relative to this migration file)
    migration_dir = Path(__file__).parent
    app_dir = migration_dir.parent.parent  # Go up: versions -> alembic -> app
    metadata_dir = app_dir / 'nodes_metadata'
    
    nodes_data = []
    node_id = 1
    
    # Load all JSON files from nodes_metadata directory
    if metadata_dir.exists():
        json_files = sorted(metadata_dir.glob('*.json'))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    node_metadata = json.load(f)
                
                # Extract required fields from the JSON
                node_data = {
                    'id': node_id,
                    'name': node_metadata.get('name', ''),
                    'type': node_metadata.get('type', ''),
                    'category': node_metadata.get('category', ''),
                    'config_metadata': node_metadata.get('config_metadata', {})
                }
                
                # Validate required fields
                if not all([node_data['name'], node_data['type'], node_data['category']]):
                    print(f"Warning: Skipping {json_file.name} - missing required fields (name, type, or category)")
                    continue
                
                nodes_data.append(node_data)
                node_id += 1
                
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse {json_file.name}: {e}")
                continue
            except Exception as e:
                print(f"Warning: Error loading {json_file.name}: {e}")
                continue
    else:
        print(f"Warning: nodes_metadata directory not found at {metadata_dir}")
    
    # Insert nodes if any were loaded
    if nodes_data:
        nodes_table = sa.table(
            'nodes',
            sa.column('id', sa.Integer),
            sa.column('name', sa.String),
            sa.column('type', sa.String),
            sa.column('category', sa.String),
            sa.column('config_metadata', postgresql.JSON)
        )
        op.bulk_insert(nodes_table, nodes_data)

    # Create workflows table
    op.create_table(
        'workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflows_id'), 'workflows', ['id'], unique=False)

    # Create workflow_nodes table
    op.create_table(
        'workflow_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('position_x', sa.Float(), nullable=False),
        sa.Column('position_y', sa.Float(), nullable=False),
        sa.Column('custom_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['node_id'], ['nodes.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_nodes_id'), 'workflow_nodes', ['id'], unique=False)

    # Create workflow_connections table
    op.create_table(
        'workflow_connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.Integer(), nullable=False),
        sa.Column('from_step_id', sa.Integer(), nullable=False),
        sa.Column('to_step_id', sa.Integer(), nullable=False),
        sa.Column('condition', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['from_step_id'], ['workflow_nodes.id'], ),
        sa.ForeignKeyConstraint(['to_step_id'], ['workflow_nodes.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_connections_id'), 'workflow_connections', ['id'], unique=False)

    # Create user_credentials table
    op.create_table(
        'user_credentials',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('service', sa.String(length=100), nullable=False),
        sa.Column('auth_type', sa.String(length=50), nullable=False),
        sa.Column('credentials', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('user_credentials')
    op.drop_table('workflow_connections')
    op.drop_table('workflow_nodes')
    op.drop_table('workflows')
    op.drop_table('nodes')
    op.drop_table('users')

