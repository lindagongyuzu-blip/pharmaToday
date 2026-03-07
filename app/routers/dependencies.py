from fastapi import Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.fact import Topic, Claim

def get_topic_or_404(topic_id: int = Path(...), db: Session = Depends(get_db)) -> Topic:
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

def get_claim_or_404(claim_id: int = Path(...), db: Session = Depends(get_db)) -> Claim:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim
