from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, require_admin
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    from datetime import datetime
    total_users = db.query(User).count()
    total_projects = db.query(Project).count()
    total_tasks = db.query(Task).count()
    overdue = db.query(Task).filter(
        Task.deadline < datetime.utcnow(),
        Task.status != "done"
    ).count()
    by_status = {
        "todo": db.query(Task).filter(Task.status == "todo").count(),
        "in_progress": db.query(Task).filter(Task.status == "in_progress").count(),
        "done": db.query(Task).filter(Task.status == "done").count(),
    }
    return {
        "total_users": total_users,
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "overdue_tasks": overdue,
        "by_status": by_status,
    }


@router.get("/users", response_model=List[UserOut])
def get_all_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).all()


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot edit yourself")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    db.delete(user)
    db.commit()


@router.get("/projects", response_model=List[dict])
def get_all_projects(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    projects = db.query(Project).all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "owner": {"id": p.owner.id, "username": p.owner.username},
            "task_count": len(p.tasks),
            "created_at": p.created_at.isoformat(),
        }
        for p in projects
    ]


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
