from sqlalchemy.orm import Session
from app.models.fact import Topic, Claim, Evidence

def update_topic_conflict(topic_id: int, db: Session) -> bool:
    """
    Updates the conflict_flag on a Topic based on evidence signals.
    A conflict exists if both positive and negative signals are found
    across all evidence summaries for the topic's claims.
    Returns the computed conflict flag.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        return
        
    all_evidence = db.query(Evidence).join(Claim).filter(Claim.topic_id == topic_id).all()
    
    positive_signals = ["met primary endpoint", "approved"]
    negative_signals = ["did not meet primary endpoint", "crl", "rejected"]
    
    has_positive = False
    has_negative = False
    
    for ev in all_evidence:
        summary = ev.extracted_summary.lower()
        if not has_positive and any(sig in summary for sig in positive_signals):
            has_positive = True
        if not has_negative and any(sig in summary for sig in negative_signals):
            has_negative = True
            
        if has_positive and has_negative:
            break
            
    topic.conflict_flag = has_positive and has_negative
    
    return topic.conflict_flag
