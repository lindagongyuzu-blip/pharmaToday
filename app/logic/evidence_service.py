from sqlalchemy.orm import Session
from app.models.fact import Evidence
from app.logic.evidence_rules import calculate_evidence_strength

def submit_evidence(claim_id: int, evidence_data: dict, db: Session) -> Evidence:
    """
    Handles business logic for creating evidence:
    - Sets claim_id
    - Calculates evidence strength
    - Persists to database
    """
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
