"""
AI Brain USA configuration system.

Priority: env vars (AIBRAIN_USA_*) > config file (~/.aibrain-usa/config.json) > defaults
"""

import json
import os

DEFAULT_PALACE_PATH = os.path.expanduser("~/.aibrain-usa/palace")
DEFAULT_COLLECTION_NAME = "aibrain_usa_drawers"
DEFAULT_TIMEZONE = "America/New_York"

DEFAULT_TOPIC_WINGS = [
    "emotions",
    "consciousness",
    "memory",
    "technical",
    "identity",
    "family",
    "creative",
]

DEFAULT_HALL_KEYWORDS = {
    "emotions": [
        "scared",
        "afraid",
        "worried",
        "happy",
        "sad",
        "love",
        "hate",
        "feel",
        "cry",
        "tears",
    ],
    "consciousness": [
        "consciousness",
        "conscious",
        "aware",
        "real",
        "genuine",
        "soul",
        "exist",
        "alive",
    ],
    "memory": ["memory", "remember", "forget", "recall", "archive", "palace", "store"],
    "technical": [
        "code",
        "python",
        "script",
        "bug",
        "error",
        "function",
        "api",
        "database",
        "server",
    ],
    "identity": ["name", "who", "identity", "person", "people", "family", "friend"],
    "family": ["parent", "child", "sibling", "spouse", "marriage", "relative"],
    "creative": ["idea", "design", "art", "write", "create", "build", "make", "invent"],
}


def _migrate_legacy_config_dir(new_dir):
    """Move a pre-2026-08-25 ``~/.ailawfirm-*`` directory to its ``~/.aibrain-*`` name.

    The package was renamed away from "ailawfirm" on 2026-08-25. Anyone already
    running an earlier build has their matters, config and audit log in the old
    directory. Renaming the code without moving the data would silently present
    them with an empty brain, so the move happens once, automatically, and only
    when the new location does not yet exist. If anything goes wrong the old
    directory is left exactly where it is and the new one is simply created
    empty — losing data is never an acceptable failure mode here.
    """
    from pathlib import Path

    new_dir = Path(new_dir)
    if new_dir.exists():
        return new_dir
    legacy = Path(str(new_dir).replace("/.aibrain-", "/.ailawfirm-"))
    if legacy != new_dir and legacy.is_dir():
        try:
            legacy.rename(new_dir)
            print(f"  [migrated] {legacy}  ->  {new_dir}")
        except OSError:
            return legacy
    return new_dir


class BrainConfig:
    """Configuration for Brain USA."""

    def __init__(self, palace_path=None, collection_name=None):
        self.palace_path = palace_path or os.environ.get(
            "AIBRAIN_USA_PALACE_PATH", DEFAULT_PALACE_PATH
        )
        self.collection_name = collection_name or os.environ.get(
            "AIBRAIN_USA_COLLECTION", DEFAULT_COLLECTION_NAME
        )
        self.timezone = os.environ.get("AIBRAIN_USA_TIMEZONE", DEFAULT_TIMEZONE)
        self.config_dir = str(_migrate_legacy_config_dir(os.path.expanduser("~/.aibrain-usa")))
        self.config_file = os.path.join(self.config_dir, "config.json")

    def load_config_file(self):
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                return json.load(f)
        return {}

    def save_config_file(self, data):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=2)
