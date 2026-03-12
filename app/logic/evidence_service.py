from sqlalchemy.orm import Session
from app.models.fact import Evidence, Claim
from app.logic.evidence_rules import calculate_evidence_strength
from app.logic.topic_rules import update_topic_conflict

def submit_evidence(claim_id: int, evidence_data: dict, db: Session) -> Evidence:
    """
    Handles business logic for creating evidence:
    - Sets claim_id
    - Calculates evidence strength
    - Persists to database
    - Updates topic conflict flag
    """
    evidence_data["claim_id"] = claim_id
    
    # Server-side evaluation of strength based on rules
    assigned_strength = calculate_evidence_strength(
        source_type=evidence_data["source_type"], 
        source_url=evidence_data["source_url"]
    )
    evidence_data["evidence_strength"] = assigned_strength
    
    try:
        db_evidence = Evidence(**evidence_data)
        db.add(db_evidence)
        db.flush()
        
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if claim:
            update_topic_conflict(claim.topic_id, db)
            
        db.commit()
        db.refresh(db_evidence)
        return db_evidence
    except Exception as e:
        db.rollback()
        raise e

def delete_evidence_service(evidence_id: int, db: Session):
    ev = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not ev:
        return None
        
    topic_id = db.query(Claim.topic_id).filter(Claim.id == ev.claim_id).scalar()
    
    try:
        db.delete(ev)
        db.flush()
        update_topic_conflict(topic_id, db)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
