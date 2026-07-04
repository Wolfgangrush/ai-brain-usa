"""Tests for usa_calendar_sync MCP tool — USA v0.1."""

from ailawfirm_usa.mcp_tools.usa_calendar_sync import usa_calendar_sync, _get_timezone


def test_hearing_generates_ics():
    result = usa_calendar_sync(
        event_type="hearing",
        title="Motion to Dismiss",
        date_str="2026-06-15",
        state="NY",
        description="Oral argument on defendant's motion to dismiss",
        location="SDNY Courthouse, 500 Pearl St, Courtroom 15C",
    )
    assert result["success"] is True
    assert result["event_type"] == "hearing"
    assert result["timezone"] == "America/New_York"
    assert "BEGIN:VCALENDAR" in result["ics_content"]
    assert "BEGIN:VEVENT" in result["ics_content"]
    assert "Motion to Dismiss" in result["ics_content"]
    assert "END:VEVENT" in result["ics_content"]


def test_deadline_with_time():
    result = usa_calendar_sync(
        event_type="deadline",
        title="Summary Judgment Filing Deadline",
        date_str="2026-07-01T17:00",
        state="CA",
    )
    assert result["success"] is True
    assert result["timezone"] == "America/Los_Angeles"
    assert "Summary Judgment" in result["ics_content"]


def test_california_timezone():
    tz = _get_timezone("CA")
    assert tz == "America/Los_Angeles"


def test_texas_timezone():
    tz = _get_timezone("TX")
    assert tz == "America/Chicago"


def test_default_timezone_no_state():
    tz = _get_timezone(None)
    assert tz == "America/New_York"


def test_default_timezone_unknown_state():
    tz = _get_timezone("XX")
    assert tz == "America/New_York"


def test_invalid_event_type_rejected():
    result = usa_calendar_sync(
        event_type="birthday",
        title="Party",
        date_str="2026-06-15",
    )
    assert result["success"] is False
    assert "error" in result


def test_invalid_date_rejected():
    result = usa_calendar_sync(
        event_type="hearing",
        title="Bad Date",
        date_str="not-a-date",
    )
    assert result["success"] is False


def test_deposition_event():
    result = usa_calendar_sync(
        event_type="deposition",
        title="Deposition of John Smith",
        date_str="2026-08-20",
        state="IL",
        location="123 Main St, Chicago, IL",
    )
    assert result["success"] is True
    assert result["timezone"] == "America/Chicago"
