"""Self-contained update module for ailawfirm-usa.

Exposes:
  REPO_URL                       upstream pip source
  cmd_update(args)               pulls latest firm code
  copy_claude_md_template(dir)   seeds CLAUDE.md into project root on init
"""

import shutil
import subprocess
import sys
from pathlib import Path

REPO_URL = "git+https://github.com/Wolfgangrush/ai-law-firm-usa.git"


def cmd_update(args):
    """Pull the latest firm code, skills, and prompts from upstream.

    Touches firm code only — user matter data + project-root CLAUDE.md
    are NEVER overwritten.
    """
    print("\n  Updating firm code from upstream…")
    print(f"  Source: {REPO_URL}")
    print("  Your matter data + your project CLAUDE.md will NOT be touched.\n")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", REPO_URL]
    if getattr(args, "quiet", False):
        cmd.insert(-1, "--quiet")
    rc = subprocess.call(cmd)
    if rc == 0:
        print("\n  ✅ Firm updated. Restart any open session.")
    else:
        print(f"\n  ❌ Update failed (exit code {rc}). Try manually:")
        print(f"       pip install --upgrade {REPO_URL}")
    return rc


def copy_claude_md_template(target_dir) -> None:
    """Copy templates/CLAUDE.md into the user's project root on init.

    No-op if the user already has a CLAUDE.md (their customisations win).
    """
    target = Path(target_dir).expanduser().resolve() / "CLAUDE.md"
    if target.exists():
        print(f"  CLAUDE.md already present at {target} — preserving your version.")
        return
    pkg_dir = Path(__file__).resolve().parent
    candidates = [
        pkg_dir / "templates" / "CLAUDE.md",
        pkg_dir.parent / "templates" / "CLAUDE.md",
    ]
    for s in candidates:
        if s.exists():
            shutil.copy(s, target)
            print(f"  CLAUDE.md template written: {target}")
            print("     Edit it with your firm name + advocate details.")
            return
    print("  (templates/CLAUDE.md not found — skipping CLAUDE.md seed.)")


def main():
    """Allow  standalone."""
    import argparse

    parser = argparse.ArgumentParser(description="Update ailawfirm_usa from upstream.")
    parser.add_argument("--quiet", "-q", action="store_true")
    args = parser.parse_args()
    sys.exit(cmd_update(args))


if __name__ == "__main__":
    main()
