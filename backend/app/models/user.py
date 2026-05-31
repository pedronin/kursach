from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="employee")

    projects = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="assignee")
    comments = relationship("Comment", back_populates="author")
    project_comments = relationship("ProjectComment", back_populates="author")
    memberships = relationship("ProjectMember", back_populates="user")
    sent_invites = relationship("Invite", foreign_keys="Invite.inviter_id", back_populates="inviter")
    received_invites = relationship("Invite", foreign_keys="Invite.invitee_id", back_populates="invitee")
