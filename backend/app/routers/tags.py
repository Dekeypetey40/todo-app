"""
Tag API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import schemas
from ..database import get_db
from ..services.tag_service import TagService
from ..services.task_service import TaskService

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=List[schemas.TagResponse])
def list_tags(db: Session = Depends(get_db)):
    """
    Get all tags with task counts efficiently calculated.
    """
    service = TagService(db)
    return service.get_all_with_task_count()


@router.post("", response_model=schemas.TagResponse, status_code=201)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    """
    Create a new tag.
    
    Tag names are automatically normalized to lowercase and must be unique.
    """
    service = TagService(db)
    db_tag = service.create_tag(tag)
    db_tag.task_count = 0
    return db_tag


@router.get("/{tag_id}", response_model=schemas.TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    Get a single tag by ID with task count.
    """
    service = TagService(db)
    db_tag = service.get_by_id(tag_id)
    if not db_tag:
        from ..exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("Tag", tag_id)
    
    # Calculate task count
    db_tag.task_count = len(db_tag.tasks)
    return db_tag


@router.patch("/{tag_id}", response_model=schemas.TagResponse)
def update_tag(
    tag_id: int,
    tag: schemas.TagUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a tag (partial update).
    """
    service = TagService(db)
    db_tag = service.update_tag(tag_id, tag)
    db_tag.task_count = len(db_tag.tasks)
    return db_tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    Delete a tag.
    
    Associated task_tags entries will be removed automatically.
    """
    service = TagService(db)
    service.delete_tag(tag_id)
    return None


@router.get("/{tag_id}/tasks", response_model=dict)
def get_tag_tasks(tag_id: int, db: Session = Depends(get_db)):
    """
    Get all tasks with this tag.
    """
    # Verify tag exists
    tag_service = TagService(db)
    db_tag = tag_service.get_by_id(tag_id)
    if not db_tag:
        from ..exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("Tag", tag_id)
    
    # Get tasks
    task_service = TaskService(db)
    tasks, total = task_service.get_tasks_filtered(tag_ids=[tag_id], limit=1000)
    
    return {
        "items": tasks,
        "total": total
    }
