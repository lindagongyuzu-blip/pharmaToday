from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import UserJudgment, Decision, Confidence, ReviewQueue
from app.logic.judgment_rules import evaluate_judgment_warning, calculate_review_date

def submit_judgment(claim_id: int, judgment_data: dict, db: Session) -> UserJudgment:
    """
    Handles business logic for creating a user judgment:
    - Validates mandatory reasons for ACCEPT/REJECT
    - Calculates warning snapshot
    - Saves judgment
    - Triggers ReviewQueue item if High Confidence
    Ensures both operations occur in a single transaction.
    """
    judgment_data["claim_id"] = claim_id
    
    # Rule: Reason tag required for ACCEPT/REJECT
    if judgment_data["decision"] in (Decision.ACCEPT, Decision.REJECT):
        if not judgment_data.get("reason_tag") or not str(judgment_data["reason_tag"]).strip():
            raise HTTPException(status_code=400, detail="reason_tag is required for ACCEPT or REJECT decisions")
            
    # Rule: Compute snapshot warning 
    warning_flag = evaluate_judgment_warning(
        claim_id=claim_id, 
        confidence=judgment_data["confidence"], 
        db=db
    )
    judgment_data["warning"] = warning_flag

    try:
        # Assemble UserJudgment Object
        db_judgment = UserJudgment(**judgment_data)
        db.add(db_judgment)
        
        # Need id for source_judgment_id, so flush but don't commit yet
        db.flush()
        
        # Rule: Create ReviewQueue if HIGH confidence
        if db_judgment.confidence == Confidence.HIGH:
            queue_item = ReviewQueue(
                user_id=db_judgment.user_id,
                claim_id=claim_id,
                review_date=calculate_review_date(),
                source_judgment_id=db_judgment.id
            )
            db.add(queue_item)
            
        # Single unified atomic commit for both Judgment and ReviewQueue
        db.commit()
        db.refresh(db_judgment)
            
        return db_judgment
    except Exception as e:
        db.rollback()
        raise e
