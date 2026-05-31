from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user
from app.models.project_comment import ProjectComment
from app.models.project import Project
from app.models.user import User
from app.schemas.project_comment import ProjectCommentCreate, ProjectCommentOut

router = APIRouter(prefix="/projects", tags=["project-comments"])


@router.get("/{project_id}/comments", response_model=List[ProjectCommentOut])
def get_project_comments(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.query(ProjectComment).filter(ProjectComment.project_id == project_id).all()


@router.post("/{project_id}/comments", response_model=ProjectCommentOut, status_code=status.HTTP_201_CREATED)
def add_project_comment(
    project_id: int,
    data: ProjectCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    comment = ProjectComment(text=data.text, project_id=project_id, author_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
