"""
CRUD operations for tasks, projects, and tags.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func, case
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging
from . import models, schemas

logger = logging.getLogger(__name__)


# Project CRUD Operations
def get_projects(db: Session) -> List[models.Project]:
    """Get all projects with task counts."""
    projects = db.query(models.Project).all()
    return projects


def get_project(db: Session, project_id: int) -> Optional[models.Project]:
    """Get a single project by ID."""
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def create_project(db: Session, project: schemas.ProjectCreate) -> models.Project:
    """Create a new project."""
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(db: Session, project_id: int, project: schemas.ProjectUpdate) -> Optional[models.Project]:
    """Update a project."""
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    
    update_data = project.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int) -> bool:
    """Delete a project (sets tasks.project_id to NULL)."""
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    
    db.delete(db_project)
    db.commit()
    return True


# Tag CRUD Operations
def get_tags(db: Session) -> List[models.Tag]:
    """Get all tags with task counts."""
    tags = db.query(models.Tag).all()
    return tags


def get_tag(db: Session, tag_id: int) -> Optional[models.Tag]:
    """Get a single tag by ID."""
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()


def create_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    """Create a new tag."""
    db_tag = models.Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def update_tag(db: Session, tag_id: int, tag: schemas.TagUpdate) -> Optional[models.Tag]:
    """Update a tag."""
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return None
    
    update_data = tag.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tag, field, value)
    
    db.commit()
    db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, tag_id: int) -> bool:
    """Delete a tag (cascade removes task_tags associations)."""
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return False
    
    db.delete(db_tag)
    db.commit()
    return True


# Task CRUD Operations
def get_tasks(
    db: Session,
    completed: Optional[bool] = None,
    project_id: Optional[int] = None,
    tag_ids: Optional[List[int]] = None,
    search: Optional[str] = None,
    view: Optional[str] = 'all',
    sort: str = 'created_at_desc'
) -> List[models.Task]:
    """
    Get tasks with comprehensive filtering and sorting.
    
    Args:
        db: Database session
        completed: Filter by completion status
        project_id: Filter by project ID
        tag_ids: Filter by tag IDs (task must have all specified tags)
        search: Search in title and description (case-insensitive)
        view: Smart view - 'all', 'today', 'week', 'overdue'
        sort: Sort order - 'created_at_desc', 'created_at_asc', 'due_date_asc', 'due_date_desc', 'priority', 'title'
    """
    try:
        logger.info(f"Fetching tasks with sort={sort}, view={view}, completed={completed}")
        
        query = db.query(models.Task).options(
            joinedload(models.Task.project),
            joinedload(models.Task.tags)
        )
        
        # Filter by completion status
        if completed is not None:
            query = query.filter(models.Task.is_completed == completed)
        
        # Filter by project
        if project_id is not None:
            query = query.filter(models.Task.project_id == project_id)
        
        # Filter by tags (task must have ALL specified tags)
        if tag_ids and len(tag_ids) > 0:
            for tag_id in tag_ids:
                query = query.filter(models.Task.tags.any(models.Tag.id == tag_id))
        
        # Search in title and description
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.Task.title.ilike(search_term),
                    models.Task.description.ilike(search_term)
                )
            )
        
        # Smart views
        today = date.today()
        if view == 'today':
            query = query.filter(
                and_(
                    models.Task.due_date == today,
                    models.Task.is_completed == False
                )
            )
        elif view == 'week':
            week_end = today + timedelta(days=7)
            query = query.filter(
                and_(
                    models.Task.due_date.between(today, week_end),
                    models.Task.is_completed == False
                )
            )
        elif view == 'overdue':
            query = query.filter(
                and_(
                    models.Task.due_date < today,
                    models.Task.is_completed == False
                )
            )
        
        # Sorting
        if sort == 'created_at_asc':
            query = query.order_by(models.Task.created_at.asc())
        elif sort == 'created_at_desc':
            query = query.order_by(models.Task.created_at.desc())
        elif sort == 'due_date_asc':
            query = query.order_by(models.Task.due_date.asc().nullslast())
        elif sort == 'due_date_desc':
            query = query.order_by(models.Task.due_date.desc().nullslast())
        elif sort == 'priority':
            # High > Medium > Low (using correct SQLAlchemy case syntax)
            query = query.order_by(
                case(
                    (models.Task.priority == models.PriorityEnum.high, 1),
                    (models.Task.priority == models.PriorityEnum.medium, 2),
                    (models.Task.priority == models.PriorityEnum.low, 3),
                )
            )
        elif sort == 'title':
            query = query.order_by(models.Task.title.asc())
        
        result = query.all()
        logger.info(f"Retrieved {len(result)} tasks")
        return result
    
    except Exception as e:
        logger.error(f"Error in get_tasks: {e}", exc_info=True)
        raise


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    """Get a single task by ID with relationships."""
    return db.query(models.Task).options(
        joinedload(models.Task.project),
        joinedload(models.Task.tags)
    ).filter(models.Task.id == task_id).first()


def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    """Create a new task with tag associations."""
    # Extract tag_ids from schema
    tag_ids = task.tag_ids if task.tag_ids else []
    task_data = task.model_dump(exclude={'tag_ids'})
    
    # Create task
    db_task = models.Task(**task_data)
    
    # Associate tags
    if tag_ids:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_ids)).all()
        db_task.tags = tags
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: schemas.TaskUpdate) -> Optional[models.Task]:
    """Update a task with partial updates and tag management."""
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    update_data = task.model_dump(exclude_unset=True, exclude={'tag_ids'})
    
    # Update task fields
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    # Update tags if provided
    if task.tag_ids is not None:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(task.tag_ids)).all()
        db_task.tags = tags
    
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Delete a task."""
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    
    db.delete(db_task)
    db.commit()
    return True
