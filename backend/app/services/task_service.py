"""
Task service with business logic.
"""
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_, and_, func, case
from typing import List, Optional
from datetime import date, timedelta
import logging
from html import escape

from .. import models, schemas
from ..exceptions import ResourceNotFoundError, ValidationError
from .base_service import BaseService

logger = logging.getLogger(__name__)


class TaskService(BaseService[models.Task]):
    """Service for task-related business logic."""
    
    def __init__(self, db: Session):
        super().__init__(db, models.Task)
    
    def create_task(self, task_data: schemas.TaskCreate) -> models.Task:
        """
        Create a new task with validation.
        
        Args:
            task_data: Task creation data
            
        Returns:
            Created task
            
        Raises:
            ResourceNotFoundError: If project or tags don't exist
            ValidationError: If data is invalid
        """
        # Sanitize inputs to prevent XSS
        sanitized_title = escape(task_data.title.strip())
        sanitized_description = escape(task_data.description.strip()) if task_data.description else None
        
        # Validate project exists if provided
        if task_data.project_id:
            project = self.db.query(models.Project).filter(
                models.Project.id == task_data.project_id
            ).first()
            if not project:
                raise ResourceNotFoundError("Project", task_data.project_id)
        
        # Validate tags exist if provided
        tags = []
        if task_data.tag_ids:
            tags = self.db.query(models.Tag).filter(
                models.Tag.id.in_(task_data.tag_ids)
            ).all()
            if len(tags) != len(task_data.tag_ids):
                found_ids = {tag.id for tag in tags}
                missing_ids = set(task_data.tag_ids) - found_ids
                raise ResourceNotFoundError("Tag", list(missing_ids)[0])
        
        # Create task
        task_dict = task_data.model_dump(exclude={'tag_ids'})
        task_dict['title'] = sanitized_title
        if sanitized_description:
            task_dict['description'] = sanitized_description
        
        db_task = models.Task(**task_dict)
        db_task.tags = tags
        
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        
        logger.info(f"Task created: id={db_task.id}, title={db_task.title}")
        return db_task
    
    def update_task(self, task_id: int, task_data: schemas.TaskUpdate) -> models.Task:
        """
        Update a task with validation.
        
        Args:
            task_id: Task ID to update
            task_data: Updated task data
            
        Returns:
            Updated task
            
        Raises:
            ResourceNotFoundError: If task, project, or tags don't exist
        """
        db_task = self.get_task_with_relations(task_id)
        if not db_task:
            raise ResourceNotFoundError("Task", task_id)
        
        # Validate project if being updated
        if task_data.project_id is not None:
            project = self.db.query(models.Project).filter(
                models.Project.id == task_data.project_id
            ).first()
            if not project:
                raise ResourceNotFoundError("Project", task_data.project_id)
        
        # Validate tags if being updated
        if task_data.tag_ids is not None:
            tags = self.db.query(models.Tag).filter(
                models.Tag.id.in_(task_data.tag_ids)
            ).all()
            if len(tags) != len(task_data.tag_ids):
                found_ids = {tag.id for tag in tags}
                missing_ids = set(task_data.tag_ids) - found_ids
                raise ResourceNotFoundError("Tag", list(missing_ids)[0])
            db_task.tags = tags
        
        # Update fields
        update_dict = task_data.model_dump(exclude_unset=True, exclude={'tag_ids'})
        
        # Sanitize title and description if provided
        if 'title' in update_dict and update_dict['title']:
            update_dict['title'] = escape(update_dict['title'].strip())
        if 'description' in update_dict and update_dict['description']:
            update_dict['description'] = escape(update_dict['description'].strip())
        
        for field, value in update_dict.items():
            setattr(db_task, field, value)
        
        self.db.commit()
        self.db.refresh(db_task)
        
        logger.info(f"Task updated: id={task_id}")
        return db_task
    
    def get_task_with_relations(self, task_id: int) -> Optional[models.Task]:
        """Get a task with all its relationships loaded."""
        return self.db.query(models.Task).options(
            joinedload(models.Task.project),
            selectinload(models.Task.tags)  # Use selectinload for many-to-many
        ).filter(models.Task.id == task_id).first()
    
    def get_tasks_filtered(
        self,
        completed: Optional[bool] = None,
        project_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None,
        search: Optional[str] = None,
        view: Optional[str] = 'all',
        sort: str = 'created_at_desc',
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[models.Task], int]:
        """
        Get tasks with comprehensive filtering, sorting, and pagination.
        Returns tuple of (tasks, total_count).
        
        Args:
            completed: Filter by completion status
            project_id: Filter by project ID
            tag_ids: Filter by tag IDs (task must have all specified tags)
            search: Search in title and description (case-insensitive)
            view: Smart view - 'all', 'today', 'week', 'overdue'
            sort: Sort order
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
        """
        try:
            logger.info(f"Fetching tasks: sort={sort}, view={view}, skip={skip}, limit={limit}")
            
            # Base query with optimized relationship loading
            query = self.db.query(models.Task).options(
                joinedload(models.Task.project),
                selectinload(models.Task.tags)  # Better for many-to-many
            )
            
            # Filter by completion status
            if completed is not None:
                query = query.filter(models.Task.is_completed == completed)
            
            # Filter by project
            if project_id is not None:
                query = query.filter(models.Task.project_id == project_id)
            
            # FIXED: Efficient tag filtering using proper SQL
            if tag_ids and len(tag_ids) > 0:
                # Use subquery to find tasks that have ALL specified tags
                tag_subquery = (
                    self.db.query(models.task_tags.c.task_id)
                    .filter(models.task_tags.c.tag_id.in_(tag_ids))
                    .group_by(models.task_tags.c.task_id)
                    .having(func.count(models.task_tags.c.tag_id.distinct()) == len(tag_ids))
                    .subquery()
                )
                query = query.filter(models.Task.id.in_(tag_subquery))
            
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
            
            # Count total before pagination
            total_count = query.count()
            
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
                query = query.order_by(
                    case(
                        (models.Task.priority == models.PriorityEnum.high, 1),
                        (models.Task.priority == models.PriorityEnum.medium, 2),
                        (models.Task.priority == models.PriorityEnum.low, 3),
                    )
                )
            elif sort == 'title':
                query = query.order_by(models.Task.title.asc())
            
            # Apply pagination
            tasks = query.offset(skip).limit(limit).all()
            
            logger.info(f"Retrieved {len(tasks)} tasks out of {total_count} total")
            return tasks, total_count
        
        except Exception as e:
            logger.error(f"Error in get_tasks_filtered: {e}", exc_info=True)
            raise
    
    def delete_task(self, task_id: int) -> None:
        """
        Delete a task.
        
        Args:
            task_id: Task ID to delete
            
        Raises:
            ResourceNotFoundError: If task doesn't exist
        """
        db_task = self.get_by_id(task_id)
        if not db_task:
            raise ResourceNotFoundError("Task", task_id)
        
        self.delete(db_task)
        logger.info(f"Task deleted: id={task_id}")
