from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import case
from typing import List

from app.database import get_db
from app.models.fact import Claim, Evidence, EvidenceStrength
from app.schemas.fact import EvidenceCreate, EvidenceResponse
from app.logic.evidence_rules import calculate_evidence_strength

router = APIRouter(tags=["Evidence"])

@router.post("/claims/{claim_id}/evidence", response_model=EvidenceResponse)
def create_evidence(claim_id: int, evidence_in: EvidenceCreate, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    evidence_data = evidence_in.model_dump()
    evidence_data["claim_id"] = claim_id
    
    # Server-side evaluation of strength based on rules
    assigned_strength = calculate_evidence_strength(
        source_type=evidence_data["source_type"], 
        source_url=evidence_data["source_url"]
    )
    evidence_data["evidence_strength"] = assigned_strength
    
    db_evidence = Evidence(**evidence_data)
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    return db_evidence

@router.get("/claims/{claim_id}/evidence", response_model=List[EvidenceResponse])
def get_evidence_by_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    sort_order = case(
        (Evidence.evidence_strength == EvidenceStrength.HIGH, 1),
        (Evidence.evidence_strength == EvidenceStrength.MEDIUM, 2),
        (Evidence.evidence_strength == EvidenceStrength.LOW, 3),
        else_=4
    )
        
    evidence = db.query(Evidence).filter(
        Evidence.claim_id == claim_id
    ).order_by(
        sort_order,
        Evidence.created_at.desc()
    ).all()
    
    return evidence
