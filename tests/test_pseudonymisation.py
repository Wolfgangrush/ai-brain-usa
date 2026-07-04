"""Tests for Pseudonymisation Gateway (Usa · v0.2)."""

from __future__ import annotations

from ailawfirm_usa.pseudonymisation import PseudonymisationGateway


def test_aadhaar_redacted():
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("Aadhaar 9999 9999 0019 belongs to the client.")
    assert "9999 9999 0019" not in clean
    assert "[AADHAAR_1]" in clean


def test_pan_redacted():
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("PAN ABFPK1234L is on file.")
    assert "ABFPK1234L" not in clean
    assert "[PAN_1]" in clean


def test_gstin_redacted():
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("GSTIN 27AAPFU0939F1ZV verified.")
    assert "27AAPFU0939F1ZV" not in clean
    assert "[GSTIN_1]" in clean


def test_phone_redacted():
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("Call client at +91 9876543210 or 9123456789.")
    assert "9876543210" not in clean
    assert "9123456789" not in clean


def test_person_with_honorific_redacted():
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("Mr. John Smith filed the writ.")
    assert "John Smith" not in clean
    assert "[PERSON_1]" in clean
    # Honorific preserved
    assert "Mr." in clean


def test_amount_redacted():
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("Quantum is ₹4,50,000 plus costs.")
    assert "4,50,000" not in clean
    assert "[AMOUNT_1]" in clean


def test_email_redacted():
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("Email client at client@example.com please.")
    assert "client@example.com" not in clean
    assert "[EMAIL_1]" in clean


def test_case_number_redacted():
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("Civil Appeal No. 1234 of 2024 listed for hearing.")
    assert "1234 of 2024" not in clean
    assert "[CASE_NO_1]" in clean


def test_desanitize_roundtrip():
    gw = PseudonymisationGateway()
    original = "Mr. John Smith filed Aadhaar 9999 9999 0019 with ₹4,50,000."
    clean, token_map = gw.sanitize(original)
    # Simulate cloud returning the sanitized text (with placeholders intact)
    cloud_response = f"Note: {clean} please verify."
    restored = gw.desanitize(cloud_response, token_map)
    assert "John Smith" in restored
    assert "9999 9999 0019" in restored
    assert "4,50,000" in restored


def test_deterministic_placeholder_within_session():
    """Same entity mentioned twice gets the same placeholder."""
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("Mr. John Smith filed it. Later Mr. John Smith attended.")
    # Both occurrences of "John Smith" should map to [PERSON_1]
    assert clean.count("[PERSON_1]") == 2
    assert "[PERSON_2]" not in clean


def test_multiple_distinct_entities():
    """Distinct entities get distinct placeholders."""
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("Mr. John Smith vs Adv. Sarah Jones in matter X.")
    assert "[PERSON_1]" in clean
    assert "[PERSON_2]" in clean


def test_is_safe_for_cloud_detects_pii():
    gw = PseudonymisationGateway()
    safe, detected = gw.is_safe_for_cloud("Mr. John Smith with Aadhaar 9999 9999 0019")
    assert safe is False
    assert "AADHAAR" in detected
    assert "PERSON" in detected


def test_is_safe_for_cloud_clears_clean_text():
    gw = PseudonymisationGateway()
    safe, detected = gw.is_safe_for_cloud(
        "What is the limitation period for a money suit under CPC?"
    )
    assert safe is True
    assert detected == []


def test_vehicle_registration_redacted():
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("Vehicle MH-12-AB-1234 was involved.")
    assert "MH-12-AB-1234" not in clean
    assert "[VEHICLE_1]" in clean


def test_no_collateral_damage_on_legal_terms():
    """Legal/statutory terms must NOT be pseudonymised as person names."""
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("The CPC governs civil procedure. The IPC was replaced by BNS in 2024.")
    # No personal-name placeholder should appear; only generic legal-text content
    assert "[PERSON_" not in clean
    assert "CPC" in clean
    assert "IPC" in clean
