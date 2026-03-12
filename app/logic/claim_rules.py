import urllib.parse
from sqlalchemy.orm import Session
from app.models.fact import Evidence, EvidenceStrength

def get_primary_source(claim_id: int, db: Session) -> Evidence | None:
    """
    Returns the primary source for a claim.
    Prioritizes HIGH strength over MEDIUM, and newest first.
    Filters out LOW strength evidence entirely.
    """
    # 1. Prefer HIGH, newest first
    high_ev = db.query(Evidence).filter(
        Evidence.claim_id == claim_id,
        Evidence.evidence_strength == EvidenceStrength.HIGH
    ).order_by(Evidence.created_at.desc()).first()
    
    if high_ev:
        return high_ev
        
    # 2. Fallback to MEDIUM, newest first
    med_ev = db.query(Evidence).filter(
        Evidence.claim_id == claim_id,
        Evidence.evidence_strength == EvidenceStrength.MEDIUM
    ).order_by(Evidence.created_at.desc()).first()
    
    return med_ev

def generate_counter_query(claim_text: str) -> dict:
    """
    Generates a counter-query struct based on the basic claim text
    using deterministic counter terms.
    """
    terms = [
        "failed",
        '"did not meet"',
        '"safety signal"',
        "CRL",
        '"warning letter"',
        "lawsuit",
        '"adverse event"'
    ]
    terms_str = " OR ".join(terms)
    counter_query = f"{claim_text} AND ({terms_str})"
    counter_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(counter_query)}"
    
    return {
        "counter_query": counter_query,
        "counter_url": counter_url
    }

