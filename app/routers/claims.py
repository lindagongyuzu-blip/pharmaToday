from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.fact import Claim, Topic
from app.schemas.fact import ClaimCreate, ClaimResponse
from app.routers.dependencies import get_topic_or_404

router = APIRouter(tags=["Claims"])

@router.post("/topics/{topic_id}/claims", response_model=ClaimResponse)
def create_claim(
    claim_in: ClaimCreate,
    topic: Topic = Depends(get_topic_or_404),
    db: Session = Depends(get_db)
):
    # Enforce topic_id from path
    claim_data = claim_in.model_dump()
    claim_data["topic_id"] = topic.id
    
    db_claim = Claim(**claim_data)
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim

@router.get("/topics/{topic_id}/claims", response_model=List[ClaimResponse])
def get_claims_by_topic(topic: Topic = Depends(get_topic_or_404), db: Session = Depends(get_db)):
    claims = db.query(Claim).filter(Claim.topic_id == topic.id).all()
    return claims

from app.routers.dependencies import get_claim_or_404

@router.get("/claims/{claim_id}", response_model=ClaimResponse)
def get_claim(claim: Claim = Depends(get_claim_or_404)):
    return claim

from app.schemas.fact import EvidenceResponse
from app.logic.claim_rules import get_primary_source, generate_counter_query

@router.get("/claims/{claim_id}/primary_source", response_model=EvidenceResponse)
def get_primary_source_endpoint(claim: Claim = Depends(get_claim_or_404), db: Session = Depends(get_db)):
    primary_source = get_primary_source(claim.id, db)
    if not primary_source:
        raise HTTPException(status_code=404, detail="No valid primary source found")
        
    return primary_source

@router.get("/claims/{claim_id}/counter_query")
def get_counter_query_endpoint(claim: Claim = Depends(get_claim_or_404)):
    return generate_counter_query(claim.text)

from app.logic.insight_rules import get_claim_insight

@router.get("/claims/{claim_id}/insight")
def get_claim_insight_endpoint(claim: Claim = Depends(get_claim_or_404), db: Session = Depends(get_db)):
    return get_claim_insight(claim.id, db)
