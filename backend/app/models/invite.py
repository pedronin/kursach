from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invitee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending | accepted | declined
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="invites")
    inviter = relationship("User", foreign_keys=[inviter_id], back_populates="sent_invites")
    invitee = relationship("User", foreign_keys=[invitee_id], back_populates="received_invites")
