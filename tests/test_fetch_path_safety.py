"""Path-confinement tests for ``scripts/fetch_open_us_law.py``.

SonarCloud flagged two MAJOR vulnerabilities on PR #2 (rule pythonsecurity:S8707,
"LLMs running this code with faulty CLI arguments can escape file system
restrictions"): ``--dest`` reached ``os.replace``/``mkdir`` and ``--cache-dir``
reached ``mkdir`` with no validation of the constructed path.

That matters more than usual here. This script is documented for attorneys to run
directly, and it is increasingly run *by an agent* on the attorney's behalf, so a
malformed or attacker-influenced argument must not be able to create directories
or replace files outside the user's own space.

The control: resolve the path (following ``..`` and symlinks) and require it to sit
inside the user's home directory, inside the repository, or inside the per-user
temporary directory. Anything else is refused before a single filesystem call.

The temp root is deliberate, not a loophole. A control that blocks ordinary
throwaway-database usage is a broken control — it gets switched off. ``/tmp`` is not
a privilege boundary; ``/etc`` is.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load():
    spec = importlib.util.spec_from_file_location(
        "fetch_open_us_law", REPO_ROOT / "scripts" / "fetch_open_us_law.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["fetch_open_us_law"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def mod():
    return _load()


# ── the validator itself ─────────────────────────────────────────────────────


def test_accepts_a_path_inside_the_home_directory(mod, tmp_path):
    target = Path.home() / ".cache" / "vaquill_test_marker" / "db.sqlite3"
    assert mod._safe_path(target, what="--dest") == target.resolve()


def test_accepts_a_path_inside_the_repository(mod):
    target = REPO_ROOT / "_statute_corpus" / "_tier2_open_us_law" / "open_us_law.sqlite3"
    assert mod._safe_path(target, what="--dest") == target.resolve()


def test_accepts_the_per_user_temp_directory(mod, tmp_path):
    """Regression: the full suite builds throwaway databases under pytest tmp_path.

    A control that blocks ordinary temp usage is a broken control, not a strict
    one — it gets switched off. /tmp is not a privilege boundary; /etc is.
    """
    assert mod._safe_path(tmp_path / "db.sqlite3", what="--dest")


def test_the_shipped_default_destination_is_accepted(mod):
    """Regression guard: the fix must not reject the tool's own default."""
    assert mod._safe_path(mod._default_dest(), what="--dest")


@pytest.mark.parametrize(
    "hostile",
    [
        "/etc/passwd",
        "/usr/local/bin/open_us_law.sqlite3",
        "/System/Library/x.sqlite3",
        "/tmp/../etc/cron.d/payload",
    ],
)
def test_rejects_paths_outside_home_and_repo(mod, hostile):
    with pytest.raises(ValueError) as excinfo:
        mod._safe_path(hostile, what="--dest")
    assert "--dest" in str(excinfo.value)


def test_rejects_traversal_that_escapes_via_dotdot(mod):
    escaping = Path.home() / ".." / ".." / "etc" / "payload.sqlite3"
    with pytest.raises(ValueError):
        mod._safe_path(escaping, what="--dest")


def test_rejection_happens_before_any_filesystem_write(mod, monkeypatch):
    """The refusal must not leave a directory behind on the way out."""
    created: list = []
    real_mkdir = Path.mkdir

    def spy(self, *args, **kwargs):
        created.append(self)
        return real_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", spy)
    with pytest.raises(ValueError):
        mod._safe_path("/etc/vaquill_should_never_exist/db.sqlite3", what="--dest")
    assert created == []


# ── the two call sites Sonar flagged ─────────────────────────────────────────


def test_build_db_refuses_an_out_of_bounds_destination(mod):
    with pytest.raises(ValueError) as excinfo:
        mod.build_db("/etc/vaquill_evil.sqlite3", {}, mode="sample", fetched_at="x")
    assert "--dest" in str(excinfo.value)
    assert not Path("/etc/vaquill_evil.sqlite3").exists()


def test_fetch_full_refuses_an_out_of_bounds_cache_dir(mod):
    with pytest.raises(ValueError) as excinfo:
        mod.fetch_full(cache_dir="/etc/vaquill_evil_cache")
    assert "--cache-dir" in str(excinfo.value)
    assert not Path("/etc/vaquill_evil_cache").exists()


# ── the duplicated-literal smell Sonar raised alongside ──────────────────────


def test_dataset_id_is_a_single_constant(mod):
    assert mod.DATASET_ID == "vaquill/open-us-law"
    source = (REPO_ROOT / "scripts" / "fetch_open_us_law.py").read_text(encoding="utf-8")
    body = source.split('"""', 2)[-1]  # drop the module docstring
    bare = body.count('"vaquill/open-us-law"')
    assert bare <= 1, f"dataset id still repeated as a bare literal {bare} times"
