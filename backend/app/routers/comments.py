from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user
from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut

router = APIRouter(prefix="/tasks", tags=["comments"])


@router.get("/{task_id}/comments", response_model=List[CommentOut])
def get_comments(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db.query(Comment).filter(Comment.task_id == task_id).all()


@router.post("/{task_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(
    task_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    comment = Comment(text=data.text, task_id=task_id, author_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
