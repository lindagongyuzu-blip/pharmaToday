from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import List, Optional
from app.models.fact import SourceType, EvidenceStrength

# Evidence Schemas
class EvidenceBase(BaseModel):
    source_type: SourceType
    source_url: str = Field(..., min_length=1, pattern=r"^\s*\S")
    source_title: Optional[str] = None
    extracted_summary: str
    published_date: Optional[date] = None

class EvidenceCreate(EvidenceBase):
    pass

class EvidenceResponse(EvidenceBase):
    id: int
    claim_id: int
    evidence_strength: EvidenceStrength
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Claim Schemas
class ClaimBase(BaseModel):
    text: str

class ClaimCreate(ClaimBase):
    pass

class ClaimResponse(ClaimBase):
    id: int
    topic_id: int
    created_at: datetime
    evidence: List[EvidenceResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)

# Topic Schemas
class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int
    conflict_flag: bool
    created_at: datetime
    claims: List[ClaimResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
