import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from app.models import Project, User
from app.schemas import ProjectCreate, ProjectOut, ProjectUpdate
from app.deps import get_db
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=list[ProjectOut])
async def get_my_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.users))
        .join(Project.users)
        .where(User.id == current_user.id)
    )
    projects = result.scalars().all()

    return [
        ProjectOut(
            id=p.id,
            name=p.name,
            users=[u.email for u in p.users]
        ) for p in projects
    ]

@router.post("/", response_model=ProjectOut)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project_id = uuid.uuid4().hex
    project = Project(id=project_id, name=data.name, users=[current_user])
    db.add(project)
    await db.commit()
    await db.refresh(project, attribute_names=["users"])
    return ProjectOut(
        id=project.id,
        name=project.name,
        users=[user.email for user in project.users]
    )

@router.get("/{project_id}", response_model=ProjectOut)
async def get_project_by_id(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.users))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project or current_user not in project.users:
        raise HTTPException(status_code=403, detail="Access denied")

    return ProjectOut(
        id=project.id,
        name=project.name,
        users=[u.email for u in project.users]
    )

@router.put("/{project_id}", response_model=ProjectOut)
async def update_project_by_id(
    project_id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.users))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project or current_user not in project.users:
        raise HTTPException(status_code=403, detail="Access denied")

    if data.name:
        project.name = data.name

    await db.commit()
    await db.refresh(project, attribute_names=["name", "users"])

    return ProjectOut(
        id=project.id,
        name=project.name,
        users=[u.email for u in project.users]
    )


@router.put("/{project_id}/add-user", response_model=ProjectOut)
async def add_user_to_project(
    project_id: str,
    email: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.users))
        .where(Project.id == project_id)
    )
    project = result.scalars().first()

    if not project or current_user not in project.users:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(User).where(User.email == email))
    user_to_add = result.scalar_one_or_none()

    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found")

    if user_to_add not in project.users:
        project.users.append(user_to_add)
        await db.commit()
        await db.refresh(project)

    return ProjectOut(
        id=project.id,
        name=project.name,
        users=[u.email for u in project.users]
    )


@router.put("/{project_id}/remove-user", response_model=ProjectOut)
async def remove_user_from_project(
    project_id: str,
    email: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.users))
        .where(Project.id == project_id)
    )
    project = result.scalars().first()

    if not project or current_user not in project.users:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(select(User).where(User.email == email))
    user_to_remove = result.scalar_one_or_none()

    if not user_to_remove or user_to_remove not in project.users:
        raise HTTPException(status_code=404, detail="User not found or not part of project")

    project.users.remove(user_to_remove)
    await db.commit()
    await db.refresh(project)

    return ProjectOut(
        id=project.id,
        name=project.name,
        users=[u.email for u in project.users]
    )

@router.delete("/{project_id}", response_model=dict)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await db.get(Project, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.refresh(project, attribute_names=["users"])

    if current_user not in project.users:
        raise HTTPException(status_code=403, detail="Access denied")

    await db.delete(project)
    await db.commit()

    return {"detail": "Project deleted"}

