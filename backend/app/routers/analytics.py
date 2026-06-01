from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from collections import defaultdict
from app.dependencies import get_db, get_current_user
from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _check_access(project_id: int, current_user: User, db: Session):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.role == "admin":
        return
    is_owner = project.owner_id == current_user.id
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not is_owner and not is_member:
        raise HTTPException(status_code=403, detail="No access to this project")


@router.get("/{project_id}/summary")
def get_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_access(project_id, current_user, db)

    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    now = datetime.utcnow()
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    overdue = 0
    for t in tasks:
        if t.status in by_status:
            by_status[t.status] += 1
        if t.deadline and t.deadline < now and t.status != "done":
            overdue += 1
    return {"total": len(tasks), "by_status": by_status, "overdue": overdue}


@router.get("/{project_id}/timeline")
def get_timeline(
    project_id: int,
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_access(project_id, current_user, db)

    since = datetime.utcnow() - timedelta(days=days)
    tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.created_at >= since,
    ).all()

    counts = defaultdict(int)
    for t in tasks:
        counts[t.created_at.strftime("%Y-%m-%d")] += 1

    base = datetime.utcnow()
    return [
        {
            "date": (base - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d"),
            "count": counts.get((base - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d"), 0),
        }
        for i in range(days)
    ]


@router.get("/{project_id}/workload")
def get_workload(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_access(project_id, current_user, db)

    now = datetime.utcnow()

    # один запрос за всеми задачами проекта с исполнителем
    tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.assignee_id.isnot(None),
    ).all()

    # группируем по исполнителю в Python
    task_map: dict[int, list] = defaultdict(list)
    for t in tasks:
        task_map[t.assignee_id].append(t)

    if not task_map:
        return []

    # один запрос за всеми нужными пользователями
    users = {
        u.id: u
        for u in db.query(User).filter(User.id.in_(task_map.keys())).all()
    }

    result = []
    for user_id, user_tasks in task_map.items():
        user = users[user_id]
        result.append({
            "user_id": user.id,
            "username": user.username,
            "total": len(user_tasks),
            "todo": sum(1 for t in user_tasks if t.status == "todo"),
            "in_progress": sum(1 for t in user_tasks if t.status == "in_progress"),
            "done": sum(1 for t in user_tasks if t.status == "done"),
            "overdue": sum(
                1 for t in user_tasks
                if t.deadline and t.deadline < now and t.status != "done"
            ),
        })
    return result


@router.get("/{project_id}/risks")
def get_risks(
    project_id: int,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_access(project_id, current_user, db)

    now = datetime.utcnow()
    soon = now + timedelta(days=days)
    tasks = (
        db.query(Task)
        .filter(
            Task.project_id == project_id,
            Task.deadline.isnot(None),
            Task.deadline <= soon,
            Task.status != "done",
        )
        .order_by(Task.deadline)
        .all()
    )
    return [
        {
            "id": t.id,
            "title": t.title,
            "deadline": t.deadline.isoformat(),
            "status": t.status,
            "priority": t.priority,
            "assignee": t.assignee.username if t.assignee else None,
            "is_overdue": t.deadline < now,
        }
        for t in tasks
    ]
