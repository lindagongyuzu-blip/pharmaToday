def test_create_and_read_topic(client):
    response = client.post("/topics", json={"name": "Test Topic Alpha"})
    assert response.status_code == 200
    topic = response.json()
    assert topic["name"] == "Test Topic Alpha"
    assert "id" in topic

    topic_id = topic["id"]
    response = client.get(f"/topics/{topic_id}")
    assert response.status_code == 200
    assert response.json()["id"] == topic_id

def test_create_and_read_claim(client):
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

def test_evidence_strength_server_side_rule(client):
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

def test_evidence_ordering(client):
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

def test_judgment_validation_and_review_queue(client):
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
    
    res = client.post(f"/review_queue/{queue_id}/complete")
    assert res.status_code == 200
    assert res.json()["status"] == "COMPLETED"

def test_phase_4_conflict_flag(client):
    # Setup
    res = client.post("/topics", json={"name": "Test Conflict Phase 4"})
    topic_id = res.json()["id"]
    res = client.post(f"/topics/{topic_id}/claims", json={"text": "Drug X works"})
    claim_id = res.json()["id"]

    # 1. Conflict flag remains False with only positive signals
    res = client.post(
        f"/claims/{claim_id}/evidence",
        json={"source_type": "REGULATORY", "source_url": "http://fda.gov", "extracted_summary": "trials met primary endpoint effectively"}
    )
    res = client.get(f"/topics/{topic_id}")
    assert res.json()["conflict_flag"] is False

    # Create another claim for negative test isolation
    res2 = client.post("/topics", json={"name": "Test Conflict Phase 4 Negative"})
    topic2_id = res2.json()["id"]
    res2 = client.post(f"/topics/{topic2_id}/claims", json={"text": "Drug Y fails"})
    claim2_id = res2.json()["id"]

    # 2. Conflict flag remains False with only negative signals
    client.post(
        f"/claims/{claim2_id}/evidence",
        json={"source_type": "REGULATORY", "source_url": "http://fda.gov", "extracted_summary": "received a crl from agency"}
    )
    res = client.get(f"/topics/{topic2_id}")
    assert res.json()["conflict_flag"] is False

    # 3. Conflict flag becomes True when both exist under the same topic
    client.post(
        f"/claims/{claim_id}/evidence",  # Topic 1 again
        json={"source_type": "REGULATORY", "source_url": "http://fda.gov", "extracted_summary": "received a crl"}
    )
    res = client.get(f"/topics/{topic_id}")
    assert res.json()["conflict_flag"] is True

def test_phase_4_primary_source(client):
    # Setup
    res = client.post("/topics", json={"name": "Test Primary Phase 4"})
    topic_id = res.json()["id"]
    res = client.post(f"/topics/{topic_id}/claims", json={"text": "Primary source testing"})
    claim_id = res.json()["id"]

    # 1. Primary source endpoint returns 404 when no evidence exists
    res = client.get(f"/claims/{claim_id}/primary_source")
    assert res.status_code == 404

    # Add LOW evidence
    client.post(f"/claims/{claim_id}/evidence", json={"source_type": "MEDIA", "source_url": "http://news.com", "extracted_summary": "Low"})
    
    # Still 404 because LOW is ignored
    res = client.get(f"/claims/{claim_id}/primary_source")
    assert res.status_code == 404

    # 2. Add MEDIUM evidence. Falls back to MEDIUM when no HIGH exists
    client.post(f"/claims/{claim_id}/evidence", json={"source_type": "PATENT", "source_url": "http://patent.com", "extracted_summary": "Medium 1"})
    res = client.get(f"/claims/{claim_id}/primary_source")
    assert res.status_code == 200
    assert res.json()["evidence_strength"] == "MEDIUM"

    # Add another MEDIUM evidence. Should pick the newest (this one).
    import time
    time.sleep(0.1) # tiny sleep for newest first
    res_med2 = client.post(f"/claims/{claim_id}/evidence", json={"source_type": "PATENT", "source_url": "http://patent.com/2", "extracted_summary": "Medium 2"})
    
    res = client.get(f"/claims/{claim_id}/primary_source")
    assert res.status_code == 200
    assert res.json()["id"] == res_med2.json()["id"]

    # 3. Add HIGH evidence. Prefers HIGH over MEDIUM/LOW.
    res_high = client.post(f"/claims/{claim_id}/evidence", json={"source_type": "REGULATORY", "source_url": "http://fda.gov", "extracted_summary": "High 1"})
    res = client.get(f"/claims/{claim_id}/primary_source")
    assert res.status_code == 200
    assert res.json()["evidence_strength"] == "HIGH"
    assert res.json()["id"] == res_high.json()["id"]

def test_phase_4_counter_query(client):
    # Setup
    res = client.post("/topics", json={"name": "Test Counter Phase 4"})
    topic_id = res.json()["id"]
    res = client.post(f"/topics/{topic_id}/claims", json={"text": "Aspirin is cool"})
    claim_id = res.json()["id"]

    # 1. Returns both counter_query and counter_url
    res = client.get(f"/claims/{claim_id}/counter_query")
    assert res.status_code == 200
    data = res.json()
    assert "counter_query" in data
    assert "counter_url" in data

    # 2. Contains deterministic counter terms
    assert "Aspirin is cool" in data["counter_query"]
    assert "failed" in data["counter_query"]
    assert "CRL" in data["counter_query"]
    assert "lawsuit" in data["counter_query"]
    
    assert "google.com" in data["counter_url"]
