"""Tests for brain classifier — USA v0.1."""

from ailawfirm_usa.brain.classifier import classify
from ailawfirm_usa.brain.intents import Intent


def test_classifies_calendar_query():
    assert classify("what's on my calendar tomorrow") == Intent.CALENDAR_QUERY


def test_classifies_citation_lookup():
    assert classify("validate citation 347 U.S. 483") == Intent.CITATION_LOOKUP


def test_classifies_court_query():
    assert classify("what is the ninth circuit") == Intent.COURT_QUERY


def test_classifies_drafting_need():
    assert classify("draft a motion to dismiss") == Intent.DRAFTING_NEED


def test_classifies_deadline_check():
    assert classify("what is the statute of limitations for copyright") == Intent.DEADLINE_CHECK


def test_classifies_client_comm():
    assert classify("client said they want to settle") == Intent.CLIENT_COMM


def test_classifies_compliance_flag_aba():
    assert classify("is this advertising okay under aba rules") == Intent.COMPLIANCE_FLAG


def test_classifies_compliance_flag_ccpa():
    assert classify("ccpa compliance requirements") == Intent.COMPLIANCE_FLAG


def test_classifies_compliance_flag_ai_ethics():
    assert classify("aba opinion 512 ai ethics") == Intent.COMPLIANCE_FLAG


def test_classifies_matter_update():
    assert classify("update the matter for the hearing next week") == Intent.MATTER_UPDATE


def test_classifies_calendar_add():
    assert classify("add to calendar: client deposition June 15") == Intent.CALENDAR_ADD


def test_unknown_fallback():
    assert classify("hello how are you") == Intent.UNKNOWN
