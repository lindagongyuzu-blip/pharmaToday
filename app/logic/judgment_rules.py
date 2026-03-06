from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.fact import Claim, EvidenceStrength
from app.models.user import Confidence

def evaluate_judgment_warning(claim_id: int, confidence: Confidence, db: Session) -> bool:
    """
    Snapshot warning logic: if confidence is HIGH and the strongest evidence
    for the claim is NOT HIGH, return warning = True.
    """
    if confidence != Confidence.HIGH:
        return False
        
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim or not claim.evidence:
        return True # HIGH confidence with no evidence at all triggers a warning
        
    # Check if ANY evidence for this claim has HIGH strength
    has_high_evidence = any(ev.evidence_strength == EvidenceStrength.HIGH for ev in claim.evidence)
    return not has_high_evidence

# We don't need a separate ReviewQueue function if we just instantiate the model directly 
# in the router, but adding here as per architecture docs if it grows.
def calculate_review_date() -> datetime:
    return datetime.utcnow() + timedelta(days=90)
