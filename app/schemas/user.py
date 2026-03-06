from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.user import Decision, Confidence, QueueStatus

# UserJudgment Schemas
class UserJudgmentBase(BaseModel):
    user_id: int
    claim_id: int
    decision: Decision
    confidence: Confidence
    reason_tag: Optional[str] = None

class UserJudgmentCreate(UserJudgmentBase):
    pass

class UserJudgmentResponse(UserJudgmentBase):
    id: int
    warning: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ReviewQueue Schemas
class ReviewQueueResponse(BaseModel):
    id: int
    user_id: int
    claim_id: int
    review_date: datetime
    status: QueueStatus
    created_at: datetime
    updated_at: datetime
    source_judgment_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# Internal schema for system use only
class ReviewQueueInternalCreate(BaseModel):
    user_id: int
    claim_id: int
    review_date: datetime
    status: QueueStatus = QueueStatus.PENDING
    source_judgment_id: Optional[int] = None
