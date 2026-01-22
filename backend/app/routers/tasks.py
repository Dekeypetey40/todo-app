"""
Task API endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas
from ..database import get_db
from ..services.task_service import TaskService
from ..config import settings

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=dict)
def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    tag_ids: Optional[List[int]] = Query(None, description="Filter by tag IDs (must have all)"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    view: Optional[str] = Query('all', description="Smart view: all, today, week, overdue"),
    sort: str = Query('created_at_desc', description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get all tasks with comprehensive filtering, sorting, and pagination.
    
    ## Query Parameters
    - **completed**: Filter by completion status (true/false)
    - **project_id**: Filter by project ID
    - **tag_ids**: Filter by tag IDs (task must have ALL specified tags)
    - **search**: Case-insensitive search in title and description
    - **view**: Smart view - 'all', 'today', 'week', 'overdue'
    - **sort**: Sort order - 'created_at_desc', 'created_at_asc', 'due_date_asc', 'due_date_desc', 'priority', 'title'
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    
    ## Returns
    Paginated response with tasks and metadata:
    ```json
    {
        "items": [...],
        "total": 150,
        "page": 1,
        "page_size": 50,
        "pages": 3
    }
    ```
    """
    service = TaskService(db)
    skip = (page - 1) * page_size
    
    tasks, total = service.get_tasks_filtered(
        completed=completed,
        project_id=project_id,
        tag_ids=tag_ids,
        search=search,
        view=view,
        sort=sort,
        skip=skip,
        limit=page_size
    )
    
    return {
        "items": tasks,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.post("", response_model=schemas.TaskResponse, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task.
    
    Validates that referenced project and tags exist before creating.
    Returns the created task with all relationships loaded.
    """
    service = TaskService(db)
    return service.create_task(task)


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a single task by ID with all relationships loaded.
    """
    service = TaskService(db)
    task = service.get_task_with_relations(task_id)
    if not task:
        from ..exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("Task", task_id)
    return task


@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a task (partial update).
    
    Only provided fields will be updated. Validates that referenced
    project and tags exist if they're being updated.
    """
    service = TaskService(db)
    return service.update_task(task_id, task)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task permanently.
    """
    service = TaskService(db)
    service.delete_task(task_id)
    return None
