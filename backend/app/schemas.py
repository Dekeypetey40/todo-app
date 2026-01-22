"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class PriorityEnum(str, Enum):
    """Priority levels for tasks."""
    low = "low"
    medium = "medium"
    high = "high"


# Project Schemas
class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    color: Optional[str] = Field(default='#3B82F6', pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")
    description: Optional[str] = Field(None, max_length=500)


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    description: Optional[str] = Field(None, max_length=500)


class ProjectResponse(ProjectBase):
    """Schema for project responses."""
    id: int
    created_at: datetime
    task_count: int = 0

    class Config:
        from_attributes = True


# Tag Schemas
class TagBase(BaseModel):
    """Base tag schema with common fields."""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field(default='#6B7280', pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")

    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Normalize tag name to lowercase."""
        return v.strip().lower()


class TagCreate(TagBase):
    """Schema for creating a new tag."""
    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')

    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: Optional[str]) -> Optional[str]:
        """Normalize tag name to lowercase."""
        return v.strip().lower() if v else None


class TagResponse(TagBase):
    """Schema for tag responses."""
    id: int
    created_at: datetime
    task_count: int = 0

    class Config:
        from_attributes = True


# Task Schemas
class TaskBase(BaseModel):
    """Base task schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000)
    priority: PriorityEnum = Field(default=PriorityEnum.medium)
    due_date: Optional[date] = None
    project_id: Optional[int] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Validate that title is not empty or whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    tag_ids: Optional[List[int]] = Field(default_factory=list, description="List of tag IDs")


class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[PriorityEnum] = None
    due_date: Optional[date] = None
    is_completed: Optional[bool] = None
    project_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate that title is not empty or whitespace."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip() if v else None


class TaskResponse(TaskBase):
    """Schema for task responses."""
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    project: Optional[ProjectResponse] = None
    tags: List[TagResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# AI Schemas
class AIParseRequest(BaseModel):
    """Schema for AI task parsing request."""
    text: str = Field(..., min_length=1, max_length=500, description="Natural language task description")

    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validate that text is not empty or whitespace."""
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace')
        return v.strip()


class AIParseResponse(BaseModel):
    """Schema for AI task parsing response."""
    title: str = Field(..., description="Extracted task title")
    description: Optional[str] = Field(None, description="Extracted task description")
    priority: PriorityEnum = Field(..., description="Extracted priority level")
    due_date: Optional[date] = Field(None, description="Extracted due date")
    suggested_tags: List[str] = Field(default_factory=list, description="AI-suggested tag names")

    class Config:
        from_attributes = True
