from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models import GenerationStatus, ProjectStatus


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    comfyui_url: str | None = Field(None, max_length=512)
    comfyui_workflow: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: ProjectStatus | None = None
    comfyui_url: str | None = Field(None, max_length=512)
    comfyui_workflow: str | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


class ProjectList(BaseModel):
    items: list[ProjectRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class GenerationBase(BaseModel):
    prompt: str = Field(..., min_length=1)
    negative_prompt: str | None = None
    parameters: str | None = None


class GenerationCreate(GenerationBase):
    pass


class GenerationRead(GenerationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    status: GenerationStatus
    comfyui_prompt_id: str | None = None
    result_images: list[str] | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class StoryboardBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    fountain_source: str = Field(..., min_length=1)


class StoryboardCreate(StoryboardBase):
    pass


class StoryboardRead(StoryboardBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    scenes_data: Any | None = None
    frames_data: Any | None = None
    export_formats: list[str] | None = None
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    environment: str
