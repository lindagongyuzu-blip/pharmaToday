def test_counter_query_endpoint(client):
    # Setup
    res = client.post("/topics", json={"name": "Test Topic Counter"})
    topic_id = res.json()["id"]
    res = client.post(f"/topics/{topic_id}/claims", json={"text": "Aspirin cures everything"})
    claim_id = res.json()["id"]

    # Test
    response = client.get(f"/claims/{claim_id}/counter_query")
    assert response.status_code == 200
    
    data = response.json()
    assert "counter_query" in data
    assert "counter_url" in data
    assert "Aspirin cures everything" in data["counter_query"]
    assert "failed" in data["counter_query"]
    assert "CRL" in data["counter_query"]
    assert "lawsuit" in data["counter_query"]
    assert "google.com" in data["counter_url"]

def test_primary_source_endpoint(client):
    # Setup
    res = client.post("/topics", json={"name": "Test Topic Primary"})
    topic_id = res.json()["id"]
    res = client.post(f"/topics/{topic_id}/claims", json={"text": "Primary source test claim"})
    claim_id = res.json()["id"]

    # Add LOW evidence (should be ignored)
    res = client.post(
        f"/claims/{claim_id}/evidence",
        json={"source_type": "MEDIA", "source_url": "http://news.com", "extracted_summary": "A"}
    )
    # Add MEDIUM evidence
    res = client.post(
        f"/claims/{claim_id}/evidence",
        json={"source_type": "PATENT", "source_url": "http://patent.com", "extracted_summary": "B"}
    )
    # Add HIGH evidence
    res = client.post(
        f"/claims/{claim_id}/evidence",
        json={"source_type": "REGULATORY", "source_url": "http://fda.gov", "extracted_summary": "C"}
    )

    # Test
    response = client.get(f"/claims/{claim_id}/primary_source")
    assert response.status_code == 200
    data = response.json()
    assert data["evidence_strength"] == "HIGH"
    assert data["source_url"] == "http://fda.gov"

def test_topic_conflict_flag(client):
    # Setup
    res = client.post("/topics", json={"name": "Test Topic Conflict"})
    topic_id = res.json()["id"]
    res = client.post(f"/topics/{topic_id}/claims", json={"text": "Drug works"})
    claim_id = res.json()["id"]
    
    res = client.get(f"/topics/{topic_id}")
    assert res.json()["conflict_flag"] is False

    # Add positive evidence (lowercase the substring intentionally to verify case insensitivity handling)
    res = client.post(
        f"/claims/{claim_id}/evidence",
        json={
            "source_type": "REGULATORY",
            "source_url": "http://fda.gov",
            "extracted_summary": "MET primary endpoint in trials"
        }
    )
    assert res.status_code == 200
    
    res = client.get(f"/topics/{topic_id}")
    assert res.json()["conflict_flag"] is False
    
    # Add negative evidence
    res = client.post(
        f"/claims/{claim_id}/evidence",
        json={
            "source_type": "REGULATORY",
            "source_url": "http://fda.gov/crl",
            "extracted_summary": "Company received a CRL."
        }
    )
    assert res.status_code == 200
    
    res = client.get(f"/topics/{topic_id}")
    assert res.json()["conflict_flag"] is True
