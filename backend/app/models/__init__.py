import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectStatus(enum.StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"


class GenerationStatus(enum.StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    comfyui_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    comfyui_workflow: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    generations: Mapped[list["Generation"]] = relationship("Generation", back_populates="project", cascade="all, delete-orphan")
    storyboards: Mapped[list["Storyboard"]] = relationship("Storyboard", back_populates="project", cascade="all, delete-orphan")


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameters: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[GenerationStatus] = mapped_column(SQLEnum(GenerationStatus), default=GenerationStatus.PENDING, nullable=False)
    comfyui_prompt_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    result_images: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="generations")


class Storyboard(Base):
    __tablename__ = "storyboards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    fountain_source: Mapped[str] = mapped_column(Text, nullable=False)
    scenes_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    frames_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    export_formats: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="storyboards")
