"""
AI Brain USA configuration system.

Priority: env vars (AILAWFIRM_USA_*) > config file (~/.ailawfirm-usa/config.json) > defaults
"""

import json
import os

DEFAULT_PALACE_PATH = os.path.expanduser("~/.ailawfirm-usa/palace")
DEFAULT_COLLECTION_NAME = "ailawfirm_usa_drawers"
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


class BrainConfig:
    """Configuration for Brain USA."""

    def __init__(self, palace_path=None, collection_name=None):
        self.palace_path = palace_path or os.environ.get(
            "AILAWFIRM_USA_PALACE_PATH", DEFAULT_PALACE_PATH
        )
        self.collection_name = collection_name or os.environ.get(
            "AILAWFIRM_USA_COLLECTION", DEFAULT_COLLECTION_NAME
        )
        self.timezone = os.environ.get("AILAWFIRM_USA_TIMEZONE", DEFAULT_TIMEZONE)
        self.config_dir = os.path.expanduser("~/.ailawfirm-usa")
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
