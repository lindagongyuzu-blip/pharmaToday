import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.fact import Topic, Claim, Evidence, SourceType, EvidenceStrength
from app.models.user import UserJudgment, ReviewQueue, Decision, Confidence

# Setup in-memory SQLite database for testing models
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_fact_models(db_session):
    # Create Topic
    topic = Topic(name="Test Topic")
    db_session.add(topic)
    db_session.commit()
    
    assert topic.id is not None
    assert topic.conflict_flag is False

    # Create Claim
    claim = Claim(topic_id=topic.id, text="Test Claim Text")
    db_session.add(claim)
    db_session.commit()
    
    assert claim.id is not None
    assert claim.topic_id == topic.id

    # Create Evidence using Enums
    evidence = Evidence(
        claim_id=claim.id,
        source_type=SourceType.CLINICAL,
        source_url="http://example.com",
        evidence_strength=EvidenceStrength.HIGH,
        extracted_summary="Test Summary"
    )
    db_session.add(evidence)
    db_session.commit()

    assert evidence.id is not None
    assert evidence.source_type == SourceType.CLINICAL
    assert evidence.evidence_strength == EvidenceStrength.HIGH

def test_create_user_models(db_session):
    # Need a claim to associate judgments
    topic = Topic(name="User Test Topic")
    db_session.add(topic)
    db_session.commit()
    
    claim = Claim(topic_id=topic.id, text="User Test Claim")
    db_session.add(claim)
    db_session.commit()

    # Create UserJudgment
    judgment = UserJudgment(
        user_id=1,
        claim_id=claim.id,
        decision=Decision.ACCEPT,
        confidence=Confidence.HIGH,
        reason_tag="Strong evidence"
    )
    db_session.add(judgment)
    db_session.commit()

    assert judgment.id is not None
    assert judgment.decision == Decision.ACCEPT
    assert judgment.warning is False

    # Create ReviewQueue
    # review_date must be provided
    from datetime import datetime, timedelta
    queue_item = ReviewQueue(
        user_id=1,
        claim_id=claim.id,
        review_date=datetime.utcnow() + timedelta(days=90),
        source_judgment_id=judgment.id
    )
    db_session.add(queue_item)
    db_session.commit()

    assert queue_item.id is not None
    assert queue_item.status == "PENDING"
