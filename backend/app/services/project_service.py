"""
Project service with business logic.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from html import escape
import logging

from .. import models, schemas
from ..exceptions import ResourceNotFoundError, ResourceAlreadyExistsError
from .base_service import BaseService

logger = logging.getLogger(__name__)


class ProjectService(BaseService[models.Project]):
    """Service for project-related business logic."""
    
    def __init__(self, db: Session):
        super().__init__(db, models.Project)
    
    def create_project(self, project_data: schemas.ProjectCreate) -> models.Project:
        """
        Create a new project with validation.
        
        Args:
            project_data: Project creation data
            
        Returns:
            Created project
            
        Raises:
            ResourceAlreadyExistsError: If project with same name exists
        """
        # Sanitize input
        sanitized_name = escape(project_data.name.strip())
        sanitized_description = escape(project_data.description.strip()) if project_data.description else None
        
        # Check if project with same name exists
        existing = self.db.query(models.Project).filter(
            models.Project.name == sanitized_name
        ).first()
        
        if existing:
            raise ResourceAlreadyExistsError("Project", f"name '{sanitized_name}'")
        
        # Create project
        project_dict = project_data.model_dump()
        project_dict['name'] = sanitized_name
        if sanitized_description:
            project_dict['description'] = sanitized_description
        
        db_project = models.Project(**project_dict)
        
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        
        logger.info(f"Project created: id={db_project.id}, name={db_project.name}")
        return db_project
    
    def update_project(self, project_id: int, project_data: schemas.ProjectUpdate) -> models.Project:
        """
        Update a project.
        
        Args:
            project_id: Project ID to update
            project_data: Updated project data
            
        Returns:
            Updated project
            
        Raises:
            ResourceNotFoundError: If project doesn't exist
            ResourceAlreadyExistsError: If name conflicts with another project
        """
        db_project = self.get_by_id(project_id)
        if not db_project:
            raise ResourceNotFoundError("Project", project_id)
        
        update_dict = project_data.model_dump(exclude_unset=True)
        
        # Sanitize inputs
        if 'name' in update_dict and update_dict['name']:
            sanitized_name = escape(update_dict['name'].strip())
            
            # Check for name conflict
            existing = self.db.query(models.Project).filter(
                models.Project.name == sanitized_name,
                models.Project.id != project_id
            ).first()
            
            if existing:
                raise ResourceAlreadyExistsError("Project", f"name '{sanitized_name}'")
            
            update_dict['name'] = sanitized_name
        
        if 'description' in update_dict and update_dict['description']:
            update_dict['description'] = escape(update_dict['description'].strip())
        
        # Update fields
        for field, value in update_dict.items():
            setattr(db_project, field, value)
        
        self.db.commit()
        self.db.refresh(db_project)
        
        logger.info(f"Project updated: id={project_id}")
        return db_project
    
    def delete_project(self, project_id: int) -> None:
        """
        Delete a project.
        Associated tasks will have their project_id set to NULL due to ON DELETE SET NULL.
        
        Args:
            project_id: Project ID to delete
            
        Raises:
            ResourceNotFoundError: If project doesn't exist
        """
        db_project = self.get_by_id(project_id)
        if not db_project:
            raise ResourceNotFoundError("Project", project_id)
        
        self.delete(db_project)
        logger.info(f"Project deleted: id={project_id}")
    
    def get_all_with_task_count(self) -> List[models.Project]:
        """Get all projects with task count calculated efficiently."""
        from sqlalchemy import func
        
        projects = self.db.query(
            models.Project,
            func.count(models.Task.id).label('task_count')
        ).outerjoin(models.Task).group_by(models.Project.id).all()
        
        # Set task_count attribute on projects
        result = []
        for project, count in projects:
            project.task_count = count
            result.append(project)
        
        return result
