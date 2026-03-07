from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import case
from typing import List

from app.database import get_db
from app.models.fact import Claim, Evidence, EvidenceStrength
from app.schemas.fact import EvidenceCreate, EvidenceResponse
from app.logic.evidence_service import submit_evidence
from app.routers.dependencies import get_claim_or_404

router = APIRouter(tags=["Evidence"])

@router.post("/claims/{claim_id}/evidence", response_model=EvidenceResponse)
def create_evidence(
    evidence_in: EvidenceCreate, 
    claim: Claim = Depends(get_claim_or_404), 
    db: Session = Depends(get_db)
):
    db_evidence = submit_evidence(claim.id, evidence_in.model_dump(), db)
    return db_evidence

@router.get("/claims/{claim_id}/evidence", response_model=List[EvidenceResponse])
def get_evidence_by_claim(claim: Claim = Depends(get_claim_or_404), db: Session = Depends(get_db)):
        
    sort_order = case(
        (Evidence.evidence_strength == EvidenceStrength.HIGH, 1),
        (Evidence.evidence_strength == EvidenceStrength.MEDIUM, 2),
        (Evidence.evidence_strength == EvidenceStrength.LOW, 3),
        else_=4
    )
        
    evidence = db.query(Evidence).filter(
        Evidence.claim_id == claim.id
    ).order_by(
        sort_order,
        Evidence.created_at.desc()
    ).all()
    
    return evidence
