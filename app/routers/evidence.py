from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.fact import Claim, Evidence, EvidenceStrength
from app.schemas.fact import EvidenceCreate, EvidenceResponse
from app.logic.evidence_service import submit_evidence, delete_evidence_service
from app.logic.evidence_rules import get_evidence_sort_order
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
        
    sort_order = get_evidence_sort_order(Evidence.evidence_strength)
        
    evidence = db.query(Evidence).filter(
        Evidence.claim_id == claim.id
    ).order_by(
        sort_order,
        Evidence.created_at.desc()
    ).all()
    
    return evidence

@router.delete("/evidence/{evidence_id}")
def delete_evidence_endpoint(evidence_id: int, db: Session = Depends(get_db)):
    success = delete_evidence_service(evidence_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {"status": "deleted", "entity": "evidence", "id": evidence_id}
