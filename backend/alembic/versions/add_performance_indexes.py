"""add_performance_indexes

Revision ID: add_indexes_001
Revises: 6d1392215b4b
Create Date: 2026-01-22

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_indexes_001'
down_revision = '6d1392215b4b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes."""
    
    # Composite index for project + completion filtering
    op.create_index(
        'idx_tasks_project_completed',
        'tasks',
        ['project_id', 'is_completed'],
        unique=False
    )
    
    # Composite index for due date + completion filtering (for smart views)
    op.create_index(
        'idx_tasks_due_completed',
        'tasks',
        ['due_date', 'is_completed'],
        unique=False
    )
    
    # Composite index for task_tags lookups
    op.create_index(
        'idx_task_tags_lookup',
        'task_tags',
        ['task_id', 'tag_id'],
        unique=False
    )
    
    # Index for priority sorting
    op.create_index(
        'idx_tasks_priority',
        'tasks',
        ['priority'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    
    op.drop_index('idx_tasks_priority', table_name='tasks')
    op.drop_index('idx_task_tags_lookup', table_name='task_tags')
    op.drop_index('idx_tasks_due_completed', table_name='tasks')
    op.drop_index('idx_tasks_project_completed', table_name='tasks')
