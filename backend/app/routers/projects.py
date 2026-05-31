from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user, require_manager
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectOut])
def get_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        return db.query(Project).all()

    if current_user.role == "manager":
        owned = db.query(Project).filter(Project.owner_id == current_user.id).all()
        member_of = (
            db.query(Project)
            .join(ProjectMember)
            .filter(ProjectMember.user_id == current_user.id)
            .all()
        )
        seen = {p.id for p in owned}
        return owned + [p for p in member_of if p.id not in seen]

    return (
        db.query(Project)
        .join(ProjectMember)
        .filter(ProjectMember.user_id == current_user.id)
        .all()
    )


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    project = Project(title=data.title, description=data.description, owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    query = db.query(Project).filter(Project.id == project_id)
    if current_user.role != "admin":
        query = query.filter(Project.owner_id == current_user.id)
    project = query.first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    query = db.query(Project).filter(Project.id == project_id)
    if current_user.role != "admin":
        query = query.filter(Project.owner_id == current_user.id)
    project = query.first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
