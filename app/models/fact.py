from enum import Enum
from datetime import datetime, date
from sqlalchemy import String, Boolean, DateTime, Date, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from app.database import Base

class SourceType(str, Enum):
    REGULATORY = "REGULATORY"
    CLINICAL = "CLINICAL"
    CORPORATE = "CORPORATE"
    PATENT = "PATENT"
    MEDIA = "MEDIA"

class EvidenceStrength(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Topic(Base):
    __tablename__ = "topics"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    conflict_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="topic", cascade="all, delete-orphan")

class Claim(Base):
    __tablename__ = "claims"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), index=True, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    topic: Mapped["Topic"] = relationship("Topic", back_populates="claims")
    evidence: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="claim", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"), index=True, nullable=False)
    source_type: Mapped[SourceType] = mapped_column(SQLEnum(SourceType), index=True, nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_title: Mapped[str | None] = mapped_column(String, nullable=True)
    evidence_strength: Mapped[EvidenceStrength] = mapped_column(SQLEnum(EvidenceStrength), index=True, nullable=False)
    extracted_summary: Mapped[str] = mapped_column(Text, nullable=False)
    published_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    claim: Mapped["Claim"] = relationship("Claim", back_populates="evidence")
