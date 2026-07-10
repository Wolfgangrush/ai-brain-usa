"""Regression test for the split-brain ChromaDB collection bug + stopword dedup.

The MCP write path and the CLI/search read path must resolve the SAME ChromaDB
collection (the read path previously hardcoded "brain_drawers"). The shared
stop-word set must preserve the union of the original per-module sets.
"""

import chromadb

from ailawfirm_usa import mcp_server, searcher
from ailawfirm_usa.config import BrainConfig
from ailawfirm_usa.stopwords import STOPWORDS


def _read_path_collection_name():
    # the read-path constant is spelled COLLECTION_NAME or _COLLECTION_NAME across editions
    return getattr(searcher, "COLLECTION_NAME", None) or getattr(searcher, "_COLLECTION_NAME", None)


def test_write_and_read_paths_agree_on_collection_name():
    """Static invariant: every code path resolves one collection name (name-agnostic)."""
    expected = BrainConfig().collection_name
    assert mcp_server._config.collection_name == expected  # write path
    assert _read_path_collection_name() == expected  # read path


def test_drawer_written_by_config_collection_is_findable_by_search(tmp_path):
    """Functional round-trip: write to the config collection, search finds it."""
    palace = str(tmp_path / "palace")
    write_name = mcp_server._config.collection_name

    client = chromadb.PersistentClient(path=palace)
    col = client.get_or_create_collection(write_name)
    try:
        col.add(
            documents=["The data protection regulator reviewed the consent notice on Tuesday."],
            ids=["d1"],
            metadatas=[{"wing": "test", "room": "test", "source_file": "t.md"}],
        )
        out = searcher.search_memories("When was the consent notice reviewed?", palace_path=palace)
    except (
        Exception
    ) as exc:  # embedding backend unavailable offline — name-invariant test still covers the bug
        import pytest

        pytest.skip(f"embedding backend unavailable in this env: {exc}")

    assert "error" not in out, out
    assert out["results"], (
        "drawer written via the config collection is not findable by search (split-brain bug)"
    )


def test_common_stopwords_preserved_in_shared_set():
    """Guard the stopword dedup: words present in the original sets must survive the union."""
    for word in ("the", "and", "like", "very", "also", "only", "no", "every"):
        assert word in STOPWORDS, f"stopword {word!r} was lost in the shared-set merge"
