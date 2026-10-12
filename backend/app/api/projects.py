
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Project, ProjectStatus
from app.schemas import (
    ProjectCreate,
    ProjectList,
    ProjectRead,
    ProjectUpdate,
)

router = APIRouter()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    project = Project(**project_in.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectRead.model_validate(project)


@router.get("", response_model=ProjectList)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> ProjectList:
    query = select(Project)
    count_query = select(func.count(Project.id))

    if status:
        try:
            status_enum = ProjectStatus(status)
            query = query.where(Project.status == status_enum)
            count_query = count_query.where(Project.status == status_enum)
        except ValueError:
            pass  # Invalid status, ignore filter

    if search:
        search_term = f"%{search}%"
        query = query.where(Project.name.ilike(search_term) | Project.description.ilike(search_term))
        count_query = count_query.where(Project.name.ilike(search_term) | Project.description.ilike(search_term))

    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Project.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    projects = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return ProjectList(
        items=[ProjectRead.model_validate(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectRead.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProjectRead:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return ProjectRead.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)
    await db.commit()
