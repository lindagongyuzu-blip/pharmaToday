from enum import Enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Decision(str, Enum):
    ACCEPT = "ACCEPT"
    UNSURE = "UNSURE"
    REJECT = "REJECT"

class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class QueueStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"

class UserJudgment(Base):
    __tablename__ = "user_judgments"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"), index=True, nullable=False)
    decision: Mapped[Decision] = mapped_column(SQLEnum(Decision), nullable=False)
    confidence: Mapped[Confidence] = mapped_column(SQLEnum(Confidence), nullable=False)
    reason_tag: Mapped[str | None] = mapped_column(String, nullable=True)
    warning: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    claim: Mapped["Claim"] = relationship("Claim")

class ReviewQueue(Base):
    __tablename__ = "review_queue"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"), index=True, nullable=False)
    review_date: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    status: Mapped[QueueStatus] = mapped_column(SQLEnum(QueueStatus), index=True, default=QueueStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    source_judgment_id: Mapped[int | None] = mapped_column(ForeignKey("user_judgments.id"), nullable=True)

    claim: Mapped["Claim"] = relationship("Claim")
    source_judgment: Mapped["UserJudgment"] = relationship("UserJudgment")
