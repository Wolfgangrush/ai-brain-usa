#!/usr/bin/env python3
"""
AI Brain USA — MCP Server
=============================
Install: claude mcp add ailawfirm-usa -- python /path/to/mcp_server.py

Tools:
  usa_court_lookup          — Federal court info by name
  usa_citation_validator    — Bluebook 21st ed citation parsing
  usa_calendar_sync         — ICS calendar entries with US timezone DST
"""

import sys
import json
import logging

from .config import BrainConfig
from .mcp_tools.usa_court_lookup import usa_court_lookup
from .mcp_tools.usa_citation_validator import usa_citation_validator
from .mcp_tools.usa_calendar_sync import usa_calendar_sync

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
logger = logging.getLogger("ailawfirm_usa_mcp")

_config = BrainConfig()

TOOL_TABLE = {
    "usa_court_lookup": usa_court_lookup,
    "usa_citation_validator": usa_citation_validator,
    "usa_calendar_sync": usa_calendar_sync,
}

TOOL_SCHEMAS = {
    "usa_court_lookup": {
        "description": "Look up a US federal court by name. Covers SCOTUS, 13 circuit courts, district courts, bankruptcy, tax, and federal claims courts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Court name fragment, e.g. 'scotus', 'ninth circuit', 'bankruptcy', 'tax'",
                }
            },
            "required": ["query"],
        },
    },
    "usa_citation_validator": {
        "description": "Parse and validate US legal citations in Bluebook 21st ed format. Handles SCOTUS, F.3d/F.4th circuit, F.Supp. district, U.S.C. statutes, and C.F.R. regulations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "citation_string": {
                    "type": "string",
                    "description": "Legal citation string, e.g. '347 U.S. 483 (1954)' or '42 U.S.C. § 1983'",
                }
            },
            "required": ["citation_string"],
        },
    },
    "usa_calendar_sync": {
        "description": "Generate ICS calendar entries for US court deadlines and hearings. Default timezone America/New_York with per-state DST handling via zoneinfo.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_type": {
                    "type": "string",
                    "enum": ["hearing", "deadline", "deposition", "conference", "other"],
                    "description": "Type of legal calendar event",
                },
                "title": {
                    "type": "string",
                    "description": "Event summary / title",
                },
                "date_str": {
                    "type": "string",
                    "description": "ISO date: 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM'",
                },
                "state": {
                    "type": "string",
                    "description": "Optional 2-letter state code for timezone (e.g. 'CA', 'NY')",
                },
                "description": {
                    "type": "string",
                    "description": "Optional event description",
                },
                "location": {
                    "type": "string",
                    "description": "Optional event location",
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "Event duration in minutes (default 60)",
                },
            },
            "required": ["event_type", "title", "date_str"],
        },
    },
}


def handle_request(request: dict) -> dict:
    method = request.get("method", "")
    req_id = request.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": list(TOOL_SCHEMAS.values())},
        }

    if method == "tools/call":
        tool_name = request.get("params", {}).get("name", "")
        arguments = request.get("params", {}).get("arguments", {})

        func = TOOL_TABLE.get(tool_name)
        if func is None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }

        try:
            result = func(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
            }
        except TypeError as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": f"Invalid params: {e}"},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": f"Tool error: {e}"},
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


def main():
    logger.info("AI Brain USA MCP Server v0.1 starting...")
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = handle_request(request)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON received: {line[:100]}")


if __name__ == "__main__":
    main()
