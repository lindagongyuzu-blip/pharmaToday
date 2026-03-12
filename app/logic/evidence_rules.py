from app.models.fact import SourceType, EvidenceStrength
from sqlalchemy import case

def get_evidence_sort_order(strength_col):
    return case(
        (strength_col == EvidenceStrength.HIGH, 1),
        (strength_col == EvidenceStrength.MEDIUM, 2),
        (strength_col == EvidenceStrength.LOW, 3),
        else_=4
    )

def calculate_evidence_strength(source_type: SourceType, source_url: str) -> EvidenceStrength:
    """
    Deterministically calculates evidence strength based on rule definitions:
    - REGULATORY → HIGH
    - CLINICAL + (DOI/PubMed in URL) → HIGH, else MEDIUM
    - CORPORATE + (SEC/official in URL) → HIGH, else MEDIUM
    - PATENT → MEDIUM
    - MEDIA → LOW
    """
    url_lower = source_url.lower()
    
    if source_type == SourceType.REGULATORY:
        return EvidenceStrength.HIGH
        
    elif source_type == SourceType.CLINICAL:
        if "doi.org" in url_lower or "pubmed" in url_lower:
            return EvidenceStrength.HIGH
        return EvidenceStrength.MEDIUM
        
    elif source_type == SourceType.CORPORATE:
        if "sec.gov" in url_lower or "official" in url_lower:
            return EvidenceStrength.HIGH
        return EvidenceStrength.MEDIUM
        
    elif source_type == SourceType.PATENT:
        return EvidenceStrength.MEDIUM
        
    elif source_type == SourceType.MEDIA:
        return EvidenceStrength.LOW
        
    # Fallback just in case
    return EvidenceStrength.LOW
