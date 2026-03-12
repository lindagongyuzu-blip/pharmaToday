from sqlalchemy.orm import Session
from app.models.fact import Claim
from app.models.user import UserJudgment, ReviewQueue
from app.logic.topic_rules import update_topic_conflict

def delete_claim_service(claim_id: int, db: Session):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        return None
        
    topic_id = claim.topic_id
    
    try:
        # Delete models that lack DB-level cascades to Claim
        db.query(ReviewQueue).filter(ReviewQueue.claim_id == claim_id).delete(synchronize_session=False)
        db.query(UserJudgment).filter(UserJudgment.claim_id == claim_id).delete(synchronize_session=False)
        
        # Deleting claim leverages existing all, delete-orphan on Claim.evidence
        db.delete(claim)
        
        # Recalculate parent topic conflict flag inside same transaction
        db.flush()
        update_topic_conflict(topic_id, db)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
