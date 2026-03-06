from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.fact import Claim
from app.models.user import UserJudgment, Decision, Confidence, ReviewQueue
from app.schemas.user import UserJudgmentCreate, UserJudgmentResponse
from app.logic.judgment_rules import evaluate_judgment_warning, calculate_review_date

router = APIRouter(tags=["Judgments"])

@router.post("/claims/{claim_id}/judgment", response_model=UserJudgmentResponse)
def create_judgment(claim_id: int, judgment_in: UserJudgmentCreate, db: Session = Depends(get_db)):
    # 1. Verify Fact Layer matches
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    judgment_data = judgment_in.model_dump()
    judgment_data["claim_id"] = claim_id
    
    # 2. Rule: Reason tag required for ACCEPT/REJECT
    if judgment_data["decision"] in (Decision.ACCEPT, Decision.REJECT):
        if not judgment_data.get("reason_tag") or not str(judgment_data["reason_tag"]).strip():
            raise HTTPException(status_code=400, detail="reason_tag is required for ACCEPT or REJECT decisions")
            
    # 3. Rule: Compute snapshot warning 
    warning_flag = evaluate_judgment_warning(
        claim_id=claim_id, 
        confidence=judgment_data["confidence"], 
        db=db
    )
    judgment_data["warning"] = warning_flag

    # Assemble UserJudgment Object
    db_judgment = UserJudgment(**judgment_data)
    db.add(db_judgment)
    db.commit()
    db.refresh(db_judgment)
    
    # 4. Rule: Create ReviewQueue if HIGH confidence
    if db_judgment.confidence == Confidence.HIGH:
        queue_item = ReviewQueue(
            user_id=db_judgment.user_id,
            claim_id=claim_id,
            review_date=calculate_review_date(),
            source_judgment_id=db_judgment.id
        )
        db.add(queue_item)
        db.commit()
        
    return db_judgment

@router.get("/claims/{claim_id}/judgments", response_model=List[UserJudgmentResponse])
def get_judgments_by_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    judgments = db.query(UserJudgment).filter(
        UserJudgment.claim_id == claim_id
    ).order_by(UserJudgment.created_at.desc()).all()
    
    return judgments
