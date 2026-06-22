"""
usa_calendar_sync MCP tool — v0.1 (ICS calendar integration).

Generates ICS calendar entries for US court deadlines and hearings.
Timezone = America/New_York DEFAULT · per-matter override via state timezone.
DST handled by Python zoneinfo.

PROVENANCE: TRAINED for ICS format + US timezone map.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = "America/New_York"

STATE_TIMEZONE_MAP = {
    # Eastern
    "NY": "America/New_York",
    "FL": "America/New_York",
    "GA": "America/New_York",
    "NC": "America/New_York",
    "SC": "America/New_York",
    "VA": "America/New_York",
    "WV": "America/New_York",
    "MD": "America/New_York",
    "DE": "America/New_York",
    "PA": "America/New_York",
    "NJ": "America/New_York",
    "CT": "America/New_York",
    "RI": "America/New_York",
    "MA": "America/New_York",
    "NH": "America/New_York",
    "VT": "America/New_York",
    "ME": "America/New_York",
    "OH": "America/New_York",
    "IN": "America/Indiana/Indianapolis",
    "MI": "America/Detroit",
    "KY": "America/Kentucky/Louisville",
    # Central
    "TX": "America/Chicago",
    "IL": "America/Chicago",
    "WI": "America/Chicago",
    "MN": "America/Chicago",
    "IA": "America/Chicago",
    "MO": "America/Chicago",
    "AR": "America/Chicago",
    "LA": "America/Chicago",
    "MS": "America/Chicago",
    "AL": "America/Chicago",
    "TN": "America/Chicago",
    "OK": "America/Chicago",
    "KS": "America/Chicago",
    "NE": "America/Chicago",
    "SD": "America/Chicago",
    "ND": "America/Chicago",
    # Mountain
    "CO": "America/Denver",
    "UT": "America/Denver",
    "WY": "America/Denver",
    "MT": "America/Denver",
    "NM": "America/Denver",
    "AZ": "America/Phoenix",  # no DST
    # Pacific
    "CA": "America/Los_Angeles",
    "OR": "America/Los_Angeles",
    "WA": "America/Los_Angeles",
    "NV": "America/Los_Angeles",
    # Alaska/Hawaii
    "AK": "America/Anchorage",
    "HI": "Pacific/Honolulu",
    # DC / territories
    "DC": "America/New_York",
    "PR": "America/Puerto_Rico",
    "VI": "America/Puerto_Rico",
    "GU": "Pacific/Guam",
}


def _get_timezone(state_code: str | None) -> str:
    if state_code and state_code.upper() in STATE_TIMEZONE_MAP:
        return STATE_TIMEZONE_MAP[state_code.upper()]
    return DEFAULT_TIMEZONE


def _ics_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", r"\;").replace(",", "\\,").replace("\n", "\\n")


def usa_calendar_sync(
    event_type: str,
    title: str,
    date_str: str,
    state: str | None = None,
    description: str = "",
    location: str = "",
    duration_minutes: int = 60,
) -> dict:
    """Generate an ICS calendar entry for a US legal event.

    Args:
        event_type: 'hearing', 'deadline', 'deposition', 'conference', 'other'
        title: event summary
        date_str: ISO date string 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM'
        state: optional 2-letter state code for timezone lookup
        description: optional event description
        location: optional event location
        duration_minutes: event duration in minutes (default 60)

    Returns:
        dict with ics_content and metadata
    """
    valid_types = {"hearing", "deadline", "deposition", "conference", "other"}
    if event_type not in valid_types:
        return {
            "success": False,
            "error": f"event_type must be one of {valid_types}",
        }

    tz_name = _get_timezone(state)
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        return {
            "success": False,
            "error": f"Invalid timezone: {tz_name}",
        }

    # Parse date
    try:
        if "T" in date_str:
            dt_start = datetime.fromisoformat(date_str).replace(tzinfo=tz)
        else:
            dt_start = datetime.strptime(date_str, "%Y-%m-%d").replace(
                hour=9, minute=0, second=0, tzinfo=tz
            )
    except ValueError as e:
        return {"success": False, "error": f"Invalid date_str: {e}"}

    dt_end = dt_start + timedelta(minutes=duration_minutes)
    now_utc = datetime.now(tz=ZoneInfo("UTC"))

    uid = f"ailawfirm-usa-{event_type}-{dt_start.strftime('%Y%m%dT%H%M%S')}@ailawfirm-usa"

    ics = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AI Brain USA//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now_utc.strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART;TZID={tz_name}:{dt_start.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND;TZID={tz_name}:{dt_end.strftime('%Y%m%dT%H%M%S')}",
        f"SUMMARY:{_ics_escape(title)}",
    ]

    if description:
        ics.append(f"DESCRIPTION:{_ics_escape(description)}")
    if location:
        ics.append(f"LOCATION:{_ics_escape(location)}")

    ics.append(f"CATEGORIES:{event_type},ailawfirm-usa")
    ics.append("END:VEVENT")
    ics.append("END:VCALENDAR")

    ics_content = "\r\n".join(ics) + "\r\n"

    return {
        "success": True,
        "event_type": event_type,
        "title": title,
        "start": dt_start.isoformat(),
        "end": dt_end.isoformat(),
        "timezone": tz_name,
        "state": state.upper() if state else None,
        "ics_content": ics_content,
    }
