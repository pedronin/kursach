from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from collections import defaultdict
from app.dependencies import get_db, get_current_user
from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember

router = APIRouter(prefix="/analytics", tags=["analytics"])

PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}


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


def _calc_task_risk(task, now: datetime, assignee_workload: int) -> int:
    """
    Индивидуальный риск задачи (0–100%).
    R = min(100, round(D × Kp × Kw))
      D  — базовый балл срочности по дедлайну
      Kp — коэффициент приоритета задачи
      Kw — коэффициент загруженности исполнителя
    """
    if task.deadline:
        hours_left = (task.deadline - now).total_seconds() / 3600
        if hours_left < 0:
            D = 80   # просрочена
        elif hours_left < 24:
            D = 65   # меньше суток
        elif hours_left < 72:
            D = 45   # 1–3 дня
        elif hours_left < 168:
            D = 25   # 3–7 дней
        else:
            D = 10   # более недели
    else:
        D = 10

    Kp = {"high": 1.3, "medium": 1.0, "low": 0.7}.get(task.priority, 1.0)

    if assignee_workload >= 10:
        Kw = 1.4    # перегружен
    elif assignee_workload >= 5:
        Kw = 1.15   # умеренная нагрузка
    else:
        Kw = 1.0    # свободен

    return min(100, round(D * Kp * Kw))


def _calc_risk_index(tasks: list, now: datetime) -> int:
    """
    Индекс риска проекта 0–100.
    Факторы:
      40% — доля просроченных задач среди незакрытых
      35% — доля незакрытых высокоприоритетных задач
      25% — доля задач с дедлайном в ближайшие 3 дня среди незакрытых
    """
    if not tasks:
        return 0

    not_done = [t for t in tasks if t.status != "done"]
    if not not_done:
        return 0

    # фактор 1: просроченные
    overdue = sum(1 for t in not_done if t.deadline and t.deadline < now)
    overdue_ratio = overdue / len(not_done)

    # фактор 2: незакрытые high-priority
    high_total = sum(1 for t in tasks if t.priority == "high")
    high_undone = sum(1 for t in not_done if t.priority == "high")
    high_ratio = high_undone / high_total if high_total else 0

    # фактор 3: срочные (дедлайн в ближайшие 3 дня)
    urgent = sum(
        1 for t in not_done
        if t.deadline and now < t.deadline <= now + timedelta(days=3)
    )
    urgency_ratio = urgent / len(not_done)

    return round(40 * overdue_ratio + 35 * high_ratio + 25 * urgency_ratio)


@router.get("/{project_id}/summary")
def get_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_access(project_id, current_user, db)

    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    now = datetime.utcnow()

    total = len(tasks)
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    overdue = 0

    for t in tasks:
        if t.status in by_status:
            by_status[t.status] += 1
        if t.deadline and t.deadline < now and t.status != "done":
            overdue += 1

    completion_rate = round(by_status["done"] / total * 100) if total else 0
    risk_index = _calc_risk_index(tasks, now)

    return {
        "total": total,
        "by_status": by_status,
        "overdue": overdue,
        "completion_rate": completion_rate,
        "risk_index": risk_index,
    }


@router.get("/{project_id}/timeline")
def get_timeline(
    project_id: int,
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_access(project_id, current_user, db)

    now = datetime.utcnow()
    since = now - timedelta(days=days)
    tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.created_at >= since,
    ).all()

    counts = defaultdict(int)
    for t in tasks:
        counts[t.created_at.strftime("%Y-%m-%d")] += 1

    return [
        {
            "date": (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d"),
            "count": counts.get((now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d"), 0),
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

    tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.assignee_id.isnot(None),
    ).all()

    task_map: dict[int, list] = defaultdict(list)
    for t in tasks:
        task_map[t.assignee_id].append(t)

    if not task_map:
        return []

    users = {
        u.id: u
        for u in db.query(User).filter(User.id.in_(task_map.keys())).all()
    }

    result = []
    for user_id, user_tasks in task_map.items():
        user = users.get(user_id)
        if not user:
            continue
        active = [t for t in user_tasks if t.status != "done"]

        # индекс нагрузки: сумма весов активных задач по приоритету
        workload_index = sum(PRIORITY_WEIGHT.get(t.priority, 1) for t in active)

        result.append({
            "user_id": user.id,
            "username": user.username,
            "total": len(user_tasks),
            "todo": sum(1 for t in user_tasks if t.status == "todo"),
            "in_progress": sum(1 for t in user_tasks if t.status == "in_progress"),
            "done": sum(1 for t in user_tasks if t.status == "done"),
            "overdue": sum(
                1 for t in active
                if t.deadline and t.deadline < now
            ),
            "workload_index": workload_index,
        })

    # сортируем по индексу нагрузки — самые загруженные сверху
    result.sort(key=lambda x: x["workload_index"], reverse=True)
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

    # считаем индекс нагрузки по каждому исполнителю одним запросом
    all_active = db.query(Task).filter(
        Task.project_id == project_id,
        Task.assignee_id.isnot(None),
        Task.status != "done",
    ).all()

    workload_map: dict[int, int] = defaultdict(int)
    for t in all_active:
        workload_map[t.assignee_id] += PRIORITY_WEIGHT.get(t.priority, 1)

    tasks = (
        db.query(Task)
        .options(joinedload(Task.assignee))
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
            "assignee_workload": workload_map.get(t.assignee_id, 0),
            "is_overdue": t.deadline < now,
            "task_risk": _calc_task_risk(t, now, workload_map.get(t.assignee_id, 0)),
        }
        for t in tasks
    ]
