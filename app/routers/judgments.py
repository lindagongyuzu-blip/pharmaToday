from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.fact import Claim
from app.models.user import UserJudgment
from app.schemas.user import UserJudgmentCreate, UserJudgmentResponse
from app.logic.judgment_service import submit_judgment
from app.routers.dependencies import get_claim_or_404

router = APIRouter(tags=["Judgments"])

@router.post("/claims/{claim_id}/judgment", response_model=UserJudgmentResponse)
def create_judgment(
    judgment_in: UserJudgmentCreate, 
    claim: Claim = Depends(get_claim_or_404), 
    db: Session = Depends(get_db)
):
    db_judgment = submit_judgment(claim.id, judgment_in.model_dump(), db)
    return db_judgment

@router.get("/claims/{claim_id}/judgments", response_model=List[UserJudgmentResponse])
def get_judgments_by_claim(claim: Claim = Depends(get_claim_or_404), db: Session = Depends(get_db)):
        
    judgments = db.query(UserJudgment).filter(
        UserJudgment.claim_id == claim.id
    ).order_by(UserJudgment.created_at.desc()).all()
    
    return judgments
