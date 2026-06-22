#!/usr/bin/env python3
"""
AI Brain — USA · Solo Edition · v0.1
Give your US legal practice a memory. No API key required.

Commands:
    ailawfirm_usa init <dir>              Detect rooms from folder structure
    ailawfirm_usa mine <dir>              Mine project files (default)
    ailawfirm_usa mine <dir> --mode convos    Mine conversation exports
    ailawfirm_usa search "query"          Find anything, exact words
    ailawfirm_usa status                  Show what's been filed
    ailawfirm_usa court "scotus"          Look up a US federal court
    ailawfirm_usa cite "347 U.S. 483"     Validate Bluebook citation
    ailawfirm_usa calendar add ...        Add ICS calendar entry
"""

import argparse
from .update import cmd_update, copy_claude_md_template

WELCOME_BANNER = """
═══════════════════════════════════════════════════════════════════
  AI Brain — USA · Solo Edition · v0.1.0

  Welcome · Bienvenido · 欢迎 · Mabuhay
  Chào mừng · أهلاً وسهلاً · Bienvenue
═══════════════════════════════════════════════════════════════════
  v0.1 = Federal-focused. State-specific modules in v0.2+.
  CURRENCY: ABA Opinion 512 · TCJA Sunset · NextGen Bar · UCC Art 12
═══════════════════════════════════════════════════════════════════
"""


def cmd_init(args):
    print("init:", args.dir)

    # Seed CLAUDE.md template into the user's project root (preserves existing).
    try:
        copy_claude_md_template(args.dir)
    except Exception as _e:
        print(f"  (CLAUDE.md seed skipped: {_e})")


def cmd_mine(args):
    print("mine:", args.dir)


def cmd_search(args):
    print("search:", args.query)


def cmd_status(args):
    print("status: not yet implemented")


def cmd_court(args):
    from ailawfirm_usa.mcp_tools.usa_court_lookup import usa_court_lookup
    import json

    result = usa_court_lookup(args.query)
    print(json.dumps(result, indent=2))


def cmd_cite(args):
    from ailawfirm_usa.mcp_tools.usa_citation_validator import usa_citation_validator
    import json

    result = usa_citation_validator(args.citation)
    print(json.dumps(result, indent=2))


def cmd_calendar(args):
    from ailawfirm_usa.mcp_tools.usa_calendar_sync import usa_calendar_sync
    import json

    result = usa_calendar_sync(
        event_type=args.event_type,
        title=args.title,
        date_str=args.date,
        state=args.state,
        description=getattr(args, "description", "") or "",
        location=getattr(args, "location", "") or "",
    )
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="ailawfirm_usa",
        description="AI Brain — USA · Solo Edition · Federal-focused practice OS",
    )
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init")
    p_init.add_argument("dir")

    p_mine = sub.add_parser("mine")
    p_mine.add_argument("dir")
    p_mine.add_argument("--mode", default="projects")

    p_search = sub.add_parser("search")
    p_search.add_argument("query")

    sub.add_parser("status")

    # update — pull latest firm code from upstream (apt-upgrade style)
    p_update = sub.add_parser(
        "update",
        help="Pull the latest firm code, skills, and prompts from upstream (matter data is NEVER touched)",
    )
    p_update.add_argument(
        "--quiet", "-q", action="store_true", help="suppress pip output (errors still print)"
    )

    p_connect = sub.add_parser(
        "connect-local",
        help="One-command setup: install Ollama + download Qwen3 + write config (local-AI, zero cloud)",
    )
    p_connect.add_argument("--yes", "-y", action="store_true", help="skip confirmation prompts")
    p_connect.add_argument("--model", help="override the recommended model (e.g. qwen3:7b)")

    p_court = sub.add_parser("court")
    p_court.add_argument("query")

    p_cite = sub.add_parser("cite")
    p_cite.add_argument("citation")

    p_cal = sub.add_parser("calendar")
    p_cal.add_argument("action", choices=["add"])
    p_cal.add_argument("--event-type", required=True)
    p_cal.add_argument("--title", required=True)
    p_cal.add_argument("--date", required=True)
    p_cal.add_argument("--state")
    p_cal.add_argument("--description")
    p_cal.add_argument("--location")

    args = parser.parse_args()

    if args.command is None:
        print(WELCOME_BANNER)
        parser.print_help()
        return

    from .connect_local import cmd_connect_local

    dispatch = {
        "init": cmd_init,
        "mine": cmd_mine,
        "search": cmd_search,
        "status": cmd_status,
        "connect-local": cmd_connect_local,
        "court": cmd_court,
        "cite": cmd_cite,
        "calendar": cmd_calendar,
        "update": cmd_update,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
