"""
Tag service with business logic.
"""
from sqlalchemy.orm import Session
from typing import List
from html import escape
import logging

from .. import models, schemas
from ..exceptions import ResourceNotFoundError, ResourceAlreadyExistsError
from .base_service import BaseService

logger = logging.getLogger(__name__)


class TagService(BaseService[models.Tag]):
    """Service for tag-related business logic."""
    
    def __init__(self, db: Session):
        super().__init__(db, models.Tag)
    
    def create_tag(self, tag_data: schemas.TagCreate) -> models.Tag:
        """
        Create a new tag with validation.
        
        Args:
            tag_data: Tag creation data
            
        Returns:
            Created tag
            
        Raises:
            ResourceAlreadyExistsError: If tag with same name exists
        """
        # Sanitize input (tag names are normalized to lowercase in schema)
        sanitized_name = escape(tag_data.name.strip().lower())
        
        # Check if tag with same name exists
        existing = self.db.query(models.Tag).filter(
            models.Tag.name == sanitized_name
        ).first()
        
        if existing:
            raise ResourceAlreadyExistsError("Tag", f"name '{sanitized_name}'")
        
        # Create tag
        tag_dict = tag_data.model_dump()
        tag_dict['name'] = sanitized_name
        
        db_tag = models.Tag(**tag_dict)
        
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        
        logger.info(f"Tag created: id={db_tag.id}, name={db_tag.name}")
        return db_tag
    
    def update_tag(self, tag_id: int, tag_data: schemas.TagUpdate) -> models.Tag:
        """
        Update a tag.
        
        Args:
            tag_id: Tag ID to update
            tag_data: Updated tag data
            
        Returns:
            Updated tag
            
        Raises:
            ResourceNotFoundError: If tag doesn't exist
            ResourceAlreadyExistsError: If name conflicts with another tag
        """
        db_tag = self.get_by_id(tag_id)
        if not db_tag:
            raise ResourceNotFoundError("Tag", tag_id)
        
        update_dict = tag_data.model_dump(exclude_unset=True)
        
        # Sanitize name if provided
        if 'name' in update_dict and update_dict['name']:
            sanitized_name = escape(update_dict['name'].strip().lower())
            
            # Check for name conflict
            existing = self.db.query(models.Tag).filter(
                models.Tag.name == sanitized_name,
                models.Tag.id != tag_id
            ).first()
            
            if existing:
                raise ResourceAlreadyExistsError("Tag", f"name '{sanitized_name}'")
            
            update_dict['name'] = sanitized_name
        
        # Update fields
        for field, value in update_dict.items():
            setattr(db_tag, field, value)
        
        self.db.commit()
        self.db.refresh(db_tag)
        
        logger.info(f"Tag updated: id={tag_id}")
        return db_tag
    
    def delete_tag(self, tag_id: int) -> None:
        """
        Delete a tag.
        Associated task_tags entries will be removed due to CASCADE.
        
        Args:
            tag_id: Tag ID to delete
            
        Raises:
            ResourceNotFoundError: If tag doesn't exist
        """
        db_tag = self.get_by_id(tag_id)
        if not db_tag:
            raise ResourceNotFoundError("Tag", tag_id)
        
        self.delete(db_tag)
        logger.info(f"Tag deleted: id={tag_id}")
    
    def get_all_with_task_count(self) -> List[models.Tag]:
        """Get all tags with task count calculated efficiently."""
        from sqlalchemy import func
        
        tags = self.db.query(
            models.Tag,
            func.count(models.task_tags.c.task_id).label('task_count')
        ).outerjoin(models.task_tags).group_by(models.Tag.id).all()
        
        # Set task_count attribute on tags
        result = []
        for tag, count in tags:
            tag.task_count = count
            result.append(tag)
        
        return result
