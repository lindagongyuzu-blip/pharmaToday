import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import fact, user   # Important to register metadata

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Force loading of models just in case
    from app.models.fact import Topic, Claim, Evidence
    from app.models.user import UserJudgment, ReviewQueue
    
    # Print what tables are known
    print("Tables known to Base metadata:", Base.metadata.tables.keys())
    
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_and_read_topic():
    response = client.post("/topics", json={"name": "Test Topic Alpha"})
    assert response.status_code == 200
    topic = response.json()
    assert topic["name"] == "Test Topic Alpha"
    assert "id" in topic

    topic_id = topic["id"]
    response = client.get(f"/topics/{topic_id}")
    assert response.status_code == 200
    assert response.json()["id"] == topic_id

def test_create_and_read_claim():
    # Setup Topic
    res = client.post("/topics", json={"name": "Test Topic Beta"})
    topic_id = res.json()["id"]

    # Test Claim Create
    res = client.post(
        f"/topics/{topic_id}/claims", 
        json={"text": "This drug works."}
    )
    assert res.status_code == 200
    claim = res.json()
    assert claim["topic_id"] == topic_id
    assert claim["text"] == "This drug works."

    claim_id = claim["id"]
    # Test Claim Get
    res = client.get(f"/claims/{claim_id}")
    assert res.status_code == 200
    assert res.json()["id"] == claim_id

def test_evidence_strength_server_side_rule():
    # Setup Topic & Claim
    res = client.post("/topics", json={"name": "Test Topic Gamma"})
    topic_id = res.json()["id"]
    res = client.post(
        f"/topics/{topic_id}/claims", 
        json={"text": "Claim for Evidence"}
    )
    claim_id = res.json()["id"]

    # Submit Regulatory Evidence
    res = client.post(
        f"/claims/{claim_id}/evidence",
        json={
            "source_type": "REGULATORY",
            "source_url": "https://fda.gov/test",
            "extracted_summary": "Should be high"
        }
    )
    assert res.status_code == 200
    evidence = res.json()
    assert evidence["evidence_strength"] == "HIGH"  # Derived from evidence_rules.py

    # Submitting media
    res = client.post(
        f"/claims/{claim_id}/evidence",
        json={
            "source_type": "MEDIA",
            "source_url": "https://news.com/test",
            "extracted_summary": "Should be low"
        }
    )
    assert res.status_code == 200
    assert res.json()["evidence_strength"] == "LOW"

def test_evidence_ordering():
    res = client.post("/topics", json={"name": "Topic Ordering"})
    topic_id = res.json()["id"]
    res = client.post(f"/topics/{topic_id}/claims", json={"text": "Ordering Claim"})
    claim_id = res.json()["id"]

    # Submit LOW first
    client.post(
        f"/claims/{claim_id}/evidence",
        json={
            "source_type": "MEDIA",
            "source_url": "https://news.com/test",
            "extracted_summary": "Low first"
        }
    )

    # Submit HIGH second
    client.post(
        f"/claims/{claim_id}/evidence",
        json={
            "source_type": "REGULATORY",
            "source_url": "https://fda.gov/test",
            "extracted_summary": "High second"
        }
    )

    # GET and assert HIGH appears before LOW
    res = client.get(f"/claims/{claim_id}/evidence")
    assert res.status_code == 200
    evidence_list = res.json()
    assert len(evidence_list) == 2
    assert evidence_list[0]["evidence_strength"] == "HIGH"
    assert evidence_list[1]["evidence_strength"] == "LOW"

def test_judgment_validation_and_review_queue():
    # Setup Topic & Claim
    res = client.post("/topics", json={"name": "Test Topic Delta"})
    topic_id = res.json()["id"]
    res = client.post(
        f"/topics/{topic_id}/claims", 
        json={"text": "Judgment valid claim"}
    )
    claim_id = res.json()["id"]
    
    # Validation Failure Check
    res = client.post(
        f"/claims/{claim_id}/judgment",
        json={
            "user_id": 1,
            "decision": "ACCEPT",
            "confidence": "HIGH"
            # Missing reason_tag
        }
    )
    assert res.status_code == 400

    # Validation Success Check (High confidence, No Evidence -> Warning TRUE)
    res = client.post(
        f"/claims/{claim_id}/judgment",
        json={
            "user_id": 1,
            "decision": "ACCEPT",
            "confidence": "HIGH",
            "reason_tag": "Because I said so"
        }
    )
    assert res.status_code == 200
    judgment = res.json()
    assert judgment["warning"] is True  # Snapshot computes correctly
    
    # Test Judgments List order
    res = client.post(
        f"/claims/{claim_id}/judgment",
        json={
            "user_id": 2, 
            "decision": "UNSURE", 
            "confidence": "LOW"
        }
    )
    res = client.get(f"/claims/{claim_id}/judgments")
    assert res.status_code == 200
    judgments = res.json()
    assert len(judgments) == 2
    assert judgments[0]["user_id"] == 2  # Newest first
    
    # Test Review Queue created due to previous HIGH confidence
    res = client.get("/review_queue?user_id=1")
    assert res.status_code == 200
    queue_items = res.json()
    assert len(queue_items) == 1
    queue_id = queue_items[0]["id"]
    
    # Test Review Queue completion
    res = client.post(f"/review_queue/{queue_id}/complete")
    assert res.status_code == 200
    assert res.json()["status"] == "COMPLETED"
