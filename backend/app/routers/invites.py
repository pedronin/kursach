from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user, require_manager
from app.models.invite import Invite
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.invite import InviteCreate, InviteOut

router = APIRouter(tags=["invites"])


@router.post("/projects/{project_id}/invites", response_model=InviteOut, status_code=status.HTTP_201_CREATED)
def send_invite(
    project_id: int,
    data: InviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.role != "admin":
        is_owner = project.owner_id == current_user.id
        is_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        ).first()
        if not is_owner and not is_member:
            raise HTTPException(status_code=403, detail="Not your project")

    invitee = db.query(User).filter(User.username == data.username).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="User not found")

    if invitee.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot invite yourself")

    already_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == invitee.id
    ).first()
    if already_member:
        raise HTTPException(status_code=400, detail="User is already a member")

    existing = db.query(Invite).filter(
        Invite.project_id == project_id,
        Invite.invitee_id == invitee.id,
        Invite.status == "pending"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Invite already sent")

    invite = Invite(project_id=project_id, inviter_id=current_user.id, invitee_id=invitee.id)
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.get("/invites/my", response_model=List[InviteOut])
def get_my_invites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invites = db.query(Invite).filter(
        Invite.invitee_id == current_user.id,
        Invite.status == "pending"
    ).all()
    for inv in invites:
        inv.project_title = inv.project.title
    return invites


@router.post("/invites/{invite_id}/accept", response_model=InviteOut)
def accept_invite(invite_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invite = db.query(Invite).filter(Invite.id == invite_id, Invite.invitee_id == current_user.id).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    if invite.status != "pending":
        raise HTTPException(status_code=400, detail="Invite already handled")

    invite.status = "accepted"
    member = ProjectMember(project_id=invite.project_id, user_id=current_user.id)
    db.add(member)
    db.commit()
    db.refresh(invite)
    return invite


@router.post("/invites/{invite_id}/decline", response_model=InviteOut)
def decline_invite(invite_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invite = db.query(Invite).filter(Invite.id == invite_id, Invite.invitee_id == current_user.id).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    if invite.status != "pending":
        raise HTTPException(status_code=400, detail="Invite already handled")

    invite.status = "declined"
    db.commit()
    db.refresh(invite)
    return invite
