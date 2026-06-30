import pytest
from server.zkp_verifier import generate_commitment, verify_commitment, anonymize_identity

def test_zkp_flow():
    secret = "Aadhaar-1234-5678"
    blinding = "random-salt-abc"

    # 1. Generate commitment (Client side)
    res = generate_commitment(secret, blinding)
    assert "commitment" in res
    assert len(res["value_hash"]) == 64
    assert len(res["blinding_hash"]) == 64

    # 2. Verify commitment (Server side)
    proof = {
        "value_hash": res["value_hash"],
        "blinding_hash": res["blinding_hash"]
    }
    is_valid = verify_commitment(res["commitment"], proof)
    assert is_valid is True

def test_zkp_invalid():
    secret = "Aadhaar-1234-5678"
    blinding = "random-salt-abc"
    res = generate_commitment(secret, blinding)

    # Missing fields
    assert verify_commitment(res["commitment"], {}) is False
    # Invalid commitment value
    assert verify_commitment("0x0", {"value_hash": res["value_hash"], "blinding_hash": res["blinding_hash"]}) is False

def test_anonymize_identity():
    id1 = anonymize_identity("1234", "Belagavi")
    id2 = anonymize_identity("1234", "Belagavi")
    id3 = anonymize_identity("5678", "Belagavi")

    assert id1 == id2
    assert id1 != id3
    assert id1.startswith("CS-")
