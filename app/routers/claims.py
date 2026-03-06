from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.fact import Claim, Topic
from app.schemas.fact import ClaimCreate, ClaimResponse

router = APIRouter(tags=["Claims"])

@router.post("/topics/{topic_id}/claims", response_model=ClaimResponse)
def create_claim(topic_id: int, claim_in: ClaimCreate, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Enforce topic_id from path
    claim_data = claim_in.model_dump()
    claim_data["topic_id"] = topic_id
    
    db_claim = Claim(**claim_data)
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim

@router.get("/topics/{topic_id}/claims", response_model=List[ClaimResponse])
def get_claims_by_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    claims = db.query(Claim).filter(Claim.topic_id == topic_id).all()
    return claims

@router.get("/claims/{claim_id}", response_model=ClaimResponse)
def get_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim
