from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Text, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Article(Base):
    """ Article model """
    __tablename__ = "articles"

    # ID
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Fields
    description: Mapped[str] = mapped_column(String(225), nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    excerpt: Mapped[str] = mapped_column(String(225), nullable=True)
    image: Mapped[str] = mapped_column(String(225), nullable=True)
    imageAlt: Mapped[str] = mapped_column(String(225), nullable=True)

    # Ownership
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship with User
    owner: Mapped["User"] = relationship("User", back_populates="articles")
