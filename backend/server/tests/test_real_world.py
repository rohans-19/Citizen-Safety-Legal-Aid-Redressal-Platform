import pytest
from fastapi.testclient import TestClient
from server.main import app, API_SECRET_TOKEN
from server.verification_service import generate_signed_token, verify_signed_token
from server.zkp_verifier import generate_commitment, verify_commitment
import hashlib

client = TestClient(app)

def test_api_key_protection():
    # 1. No header: should return 401 Unauthorized
    response = client.post("/process-voice", json={"transcript": "hello"})
    assert response.status_code == 401
    assert "Invalid API Secret Token" in response.json()["detail"]

    # 2. Invalid header: should return 401 Unauthorized
    response = client.post("/process-voice", json={"transcript": "hello"}, headers={"X-API-Key": "bad-key"})
    assert response.status_code == 401

    # 3. Valid header: should bypass 401 Auth (returns validation error or similar, but not 401)
    response = client.post("/process-voice", json={"transcript": "a"}, headers={"X-API-Key": API_SECRET_TOKEN})
    assert response.status_code != 401


def test_zkp_token_signing_and_verification():
    aadhaar_hash = hashlib.sha256("123456789012".encode()).hexdigest()
    income = 45000
    eligible = True

    # 1. Sign
    token = generate_signed_token(aadhaar_hash, income, eligible)
    assert token is not None
    assert len(token) > 20

    # 2. Verify valid
    payload = verify_signed_token(token)
    assert payload is not None
    assert payload["aadhaar_hash"] == aadhaar_hash
    assert payload["income"] == income
    assert payload["eligible"] is True

    # 3. Verify bad signature/token
    assert verify_signed_token("bad_token_format") is None


def test_request_verification_and_approval_flow():
    pseudonym = "Citizen-TEST"
    aadhaar_hash = hashlib.sha256("987654321098".encode()).hexdigest()
    income = 35000
    # 1. Submit request
    req_payload = {
        "pseudonym": pseudonym,
        "aadhaar_hash": aadhaar_hash,
        "aadhaar": "987654321098",
        "income": income
    }
    response = client.post(
        "/request-verification", 
        json=req_payload, 
        headers={"X-API-Key": API_SECRET_TOKEN}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # 2. Check pending status
    response = client.get(
        f"/check-verification-status?pseudonym={pseudonym}",
        headers={"X-API-Key": API_SECRET_TOKEN}
    )
    assert response.json()["status"] == "pending"

    # 3. Approve verification
    # Generate token
    token = generate_signed_token(aadhaar_hash, income, eligible=True)
    response = client.get(f"/approve-verification?token={token}&pseudonym={pseudonym}")
    assert response.status_code == 200
    assert "Verification Approved" in response.text

    # 4. Check approved status
    response = client.get(
        f"/check-verification-status?pseudonym={pseudonym}",
        headers={"X-API-Key": API_SECRET_TOKEN}
    )
    assert response.json()["status"] == "approved"
    assert response.json()["credential_token"] == token


def test_process_voice_zkp_validation():
    # 1. Valid ZKP Commitment
    secret_value = hashlib.sha256("987654321098".encode()).hexdigest()
    blinding_factor = "bf_secure_blinding_factor_for_demo_test"
    
    # Generate commitment client-side Message: secret_value + ":" + blinding_factor
    commitment_msg = f"{secret_value}:{blinding_factor}"
    commitment_hash = hashlib.sha256(commitment_msg.encode()).hexdigest()
    
    # Preimages
    value_hash = hashlib.sha256(secret_value.encode()).hexdigest()
    blinding_hash = hashlib.sha256(blinding_factor.encode()).hexdigest()

    payload = {
        "transcript": "my neighbor claims that a part of my land belongs to him",
        "district": "Belagavi",
        "language": "en",
        "incident_type_hint": "land_encroachment",
        "zkp_commitment": commitment_hash,
        "zkp_proof": {
            "value_hash": value_hash,
            "blinding_hash": blinding_hash
        }
    }

    # Should succeed and return zkp_verified: True
    response = client.post(
        "/process-voice", 
        json=payload, 
        headers={"X-API-Key": API_SECRET_TOKEN}
    )
    assert response.status_code == 200
    assert response.json()["zkp_verified"] is True
    # Verify that it triggered simulated escalation email
    assert "email_sent" in response.json()
    assert "officer_email" in response.json()
    assert response.json()["officer_email"] != ""

    # 2. Invalid ZKP Commitment
    payload_bad_zkp = {
        "transcript": "my neighbor claims that a part of my land belongs to him",
        "district": "Belagavi",
        "language": "en",
        "incident_type_hint": "land_encroachment",
        "zkp_commitment": "invalid_commitment_hash_here",
        "zkp_proof": {
            "value_hash": value_hash,
            "blinding_hash": blinding_hash
        }
    }
    response = client.post(
        "/process-voice", 
        json=payload_bad_zkp, 
        headers={"X-API-Key": API_SECRET_TOKEN}
    )
    assert response.status_code == 403
    assert "Invalid Zero-Knowledge Proof commitment" in response.json()["detail"]
