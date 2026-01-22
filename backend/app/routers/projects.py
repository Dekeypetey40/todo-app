"""
Project API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import schemas
from ..database import get_db
from ..services.project_service import ProjectService
from ..services.task_service import TaskService

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[schemas.ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """
    Get all projects with task counts efficiently calculated.
    """
    service = ProjectService(db)
    return service.get_all_with_task_count()


@router.post("", response_model=schemas.ProjectResponse, status_code=201)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project.
    
    Project names must be unique.
    """
    service = ProjectService(db)
    db_project = service.create_project(project)
    db_project.task_count = 0
    return db_project


@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Get a single project by ID with task count.
    """
    service = ProjectService(db)
    db_project = service.get_by_id(project_id)
    if not db_project:
        from ..exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("Project", project_id)
    
    # Calculate task count
    db_project.task_count = len(db_project.tasks)
    return db_project


@router.patch("/{project_id}", response_model=schemas.ProjectResponse)
def update_project(
    project_id: int,
    project: schemas.ProjectUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a project (partial update).
    """
    service = ProjectService(db)
    db_project = service.update_project(project_id, project)
    db_project.task_count = len(db_project.tasks)
    return db_project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Delete a project.
    
    Associated tasks will have their project_id set to NULL.
    """
    service = ProjectService(db)
    service.delete_project(project_id)
    return None


@router.get("/{project_id}/tasks", response_model=dict)
def get_project_tasks(project_id: int, db: Session = Depends(get_db)):
    """
    Get all tasks for a specific project with pagination.
    """
    # Verify project exists
    project_service = ProjectService(db)
    db_project = project_service.get_by_id(project_id)
    if not db_project:
        from ..exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("Project", project_id)
    
    # Get tasks
    task_service = TaskService(db)
    tasks, total = task_service.get_tasks_filtered(project_id=project_id, limit=1000)
    
    return {
        "items": tasks,
        "total": total
    }
