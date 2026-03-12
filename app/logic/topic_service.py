from sqlalchemy.orm import Session
from app.models.fact import Topic, Claim
from app.models.user import UserJudgment, ReviewQueue

def delete_topic_service(topic_id: int, db: Session):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        return None
    
    try:
        claim_ids = [row[0] for row in db.query(Claim.id).filter(Claim.topic_id == topic_id).all()]
        if claim_ids:
            # Delete models that lack DB-level cascades to Claim
            db.query(ReviewQueue).filter(ReviewQueue.claim_id.in_(claim_ids)).delete(synchronize_session=False)
            db.query(UserJudgment).filter(UserJudgment.claim_id.in_(claim_ids)).delete(synchronize_session=False)
            
        # Deleting topic leverages existing all, delete-orphan on Topic.claims -> Claim.evidence
        db.delete(topic)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
