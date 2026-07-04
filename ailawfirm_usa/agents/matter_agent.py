"""
matter_agent — active matter context handler (v0.1 stub).

v0.1: returns a structured placeholder. v0.2+: loads matter from
local matter store, applies entity-aliasing compression, returns relevant context.

PROVENANCE: STUB — v0.2+ real implementation.
"""


def handle(payload: str) -> dict:
    return {
        "agent": "matter_agent",
        "status": "v0.1 stub",
        "payload_received": payload,
        "note": "matter context loading lands in v0.2+",
    }
