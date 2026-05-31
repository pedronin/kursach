from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from typing import List, Optional
from datetime import datetime
from app.dependencies import get_db, get_current_user, require_manager
from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskOut])
def get_tasks(
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee_id: Optional[int] = Query(None),
    deadline_before: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_dir: Optional[str] = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task)

    # сотрудник видит все задачи проекта, но фильтр по исполнителю по умолчанию на него
    if current_user.role == "employee":
        if not assignee_id:
            assignee_id = current_user.id

    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    if deadline_before:
        query = query.filter(Task.deadline <= deadline_before)
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    sort_col = {
        "deadline": Task.deadline,
        "priority": Task.priority,
        "created_at": Task.created_at,
    }.get(sort_by, Task.created_at)

    query = query.order_by(desc(sort_col) if sort_dir == "desc" else asc(sort_col))

    return query.all()


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    project = db.query(Project).filter(
        Project.id == data.project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project and current_user.role != "admin":
        raise HTTPException(status_code=404, detail="Project not found")

    task = Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role == "employee":
        if task.assignee_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not your task")
        allowed = data.model_dump(exclude_none=True)
        if set(allowed.keys()) - {"status"}:
            raise HTTPException(status_code=403, detail="Employees can only change status")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
