from sqlalchemy.orm import Session
from app.models.fact import Evidence, EvidenceStrength

def get_claim_insight(claim_id: int, db: Session) -> dict:
    """
    Computes deterministic insight coverage and guidance for a given claim.
    """
    evidence_list = db.query(Evidence).filter(Evidence.claim_id == claim_id).all()
    
    # Coverage Rule
    high = 0
    medium = 0
    low = 0
    for ev in evidence_list:
        if ev.evidence_strength == EvidenceStrength.HIGH:
            high += 1
        elif ev.evidence_strength == EvidenceStrength.MEDIUM:
            medium += 1
        elif ev.evidence_strength == EvidenceStrength.LOW:
            low += 1
            
    total = high + medium + low
    
    # Conflict Rule (Claim level)
    positive_signals = ["met primary endpoint", "approved"]
    negative_signals = ["did not meet primary endpoint", "crl", "rejected"]
    
    has_pos = False
    has_neg = False
    
    for ev in evidence_list:
        summary_lower = ev.extracted_summary.lower() if ev.extracted_summary else ""
        if any(pos in summary_lower for pos in positive_signals):
            has_pos = True
        if any(neg in summary_lower for neg in negative_signals):
            has_neg = True

    has_conflict = has_pos and has_neg
    
    # Guidance Label Rule
    if has_conflict:
        guidance_label = "CONFLICTING_EVIDENCE"
        guidance_text = "Both supportive and contradictory evidence signals are present for this claim."
    elif high >= 1:
        guidance_label = "STRONG_SUPPORT"
        guidance_text = "At least one high-strength source is available and no direct conflict is detected."
    elif medium >= 1:
        guidance_label = "LIMITED_SUPPORT"
        guidance_text = "Evidence exists, but current support relies on medium-strength sources without high-strength confirmation."
    else:
        guidance_label = "INSUFFICIENT_EVIDENCE"
        guidance_text = "Current evidence is weak or missing, so the claim should be treated cautiously."
        
    return {
        "claim_id": claim_id,
        "coverage": {
            "high": high,
            "medium": medium,
            "low": low,
            "total": total
        },
        "has_conflict": has_conflict,
        "guidance_label": guidance_label,
        "guidance_text": guidance_text
    }
