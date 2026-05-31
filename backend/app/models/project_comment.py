from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ProjectComment(Base):
    __tablename__ = "project_comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="comments")
    author = relationship("User", back_populates="project_comments")
