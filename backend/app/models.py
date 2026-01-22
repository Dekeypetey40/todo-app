"""
SQLAlchemy ORM models for the todo application.
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base


class PriorityEnum(str, enum.Enum):
    """Priority levels for tasks."""
    low = "low"
    medium = "medium"
    high = "high"


# Association table for many-to-many relationship between tasks and tags
task_tags = Table(
    'task_tags',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
)


class Project(Base):
    """Project model for organizing tasks."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(7), nullable=True, default='#3B82F6')  # Hex color
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Tag(Base):
    """Tag model for flexible task categorization."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    color = Column(String(7), nullable=True, default='#6B7280')  # Hex color
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tasks = relationship("Task", secondary=task_tags, back_populates="tags")


class Task(Base):
    """Task model representing a to-do item."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(String(2000), nullable=True)
    priority = Column(SQLEnum(PriorityEnum), nullable=False, default=PriorityEnum.medium)
    due_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, nullable=False, default=False, index=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")
