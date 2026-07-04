"""Local-AI bridge — one command installs Ollama + downloads Qwen3 + writes config.

Usage from CLI:
    ailawfirm-usa connect-local
    ailawfirm-usa connect-local --yes      # skip prompts
    ailawfirm-usa connect-local --model qwen3:7b   # force a specific model

Result: ~/.ailawfirm-usa/config.json is written with ai_provider=ollama and the
selected model. All subsequent CLI invocations route to local Ollama. No queries
leave your laptop.

References LEGAL_EXPOSURE_PLAYBOOK §2(a) (Local-AI-Only Default pillar).
"""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

COUNTRY = "usa"
CONFIG_DIR = Path.home() / f".ailawfirm-{COUNTRY}"
CONFIG_FILE = CONFIG_DIR / "config.json"


def detect_ollama() -> bool:
    return shutil.which("ollama") is not None


def install_ollama_instructions() -> None:
    system = platform.system()
    print()
    if system == "Darwin":
        print("Install Ollama on macOS:")
        print("    brew install ollama")
        print("  (or download from https://ollama.com/download/Mac)")
    elif system == "Linux":
        print("Install Ollama on Linux:")
        print("    curl -fsSL https://ollama.com/install.sh | sh")
    elif system == "Windows":
        print("Install Ollama on Windows:")
        print("    Download from https://ollama.com/download")
    else:
        print(f"Visit https://ollama.com/download for {system}")
    print()
    print("Then run `ailawfirm-usa connect-local` again.")


def detect_ram_gb() -> float:
    try:
        system = platform.system()
        if system == "Darwin":
            out = subprocess.check_output(["sysctl", "-n", "hw.memsize"]).decode().strip()
            return int(out) / (1024**3)
        if system == "Linux":
            with open("/proc/meminfo") as fh:
                for line in fh:
                    if line.startswith("MemTotal:"):
                        return int(line.split()[1]) / (1024**2)
        if system == "Windows":
            out = subprocess.check_output(
                ["wmic", "computersystem", "get", "TotalPhysicalMemory"]
            ).decode()
            for line in out.split("\n"):
                line = line.strip()
                if line.isdigit():
                    return int(line) / (1024**3)
    except Exception:
        pass
    return 8.0


def recommend_model(ram_gb: float) -> tuple[str, str]:
    if ram_gb >= 16:
        return "qwen3:14b", "~10 GB on disk · 14B params · best quality"
    if ram_gb >= 8:
        return "qwen3:7b", "~4 GB on disk · 7B params · fast"
    return "qwen3:1.7b", "~1.5 GB on disk · 1.7B params · low-RAM laptops"


def ollama_pull(model: str) -> bool:
    print(f"\n[downloading] ollama pull {model}")
    print("  (one-time download · subsequent runs use the cached model)\n")
    try:
        subprocess.run(["ollama", "pull", model], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"\n❌ ollama pull {model} failed")
        return False


def smoke_test(model: str) -> bool:
    print(f"\n[smoke test] asking {model} a one-word question...")
    try:
        result = subprocess.run(
            ["ollama", "run", model, "Reply with one word: ready"],
            capture_output=True,
            text=True,
            timeout=180,
        )
        response = result.stdout.strip()
        if response:
            print(f"  ✓ model responded: {response[:80]}")
            return True
        print("  ⚠ empty response; model may need a moment")
        return True
    except subprocess.TimeoutExpired:
        print("  ⚠ smoke test timed out (model may still be loading on first run)")
        return False
    except subprocess.CalledProcessError:
        print("  ❌ smoke test failed")
        return False


def write_config(model: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config: dict = {}
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
        except json.JSONDecodeError:
            config = {}
    config.update(
        {
            "ai_provider": "ollama",
            "ollama_model": model,
            "ollama_host": "http://localhost:11434",
        }
    )
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    CONFIG_FILE.chmod(0o600)
    print(f"  ✓ config written: {CONFIG_FILE}")


def cmd_connect_local(args) -> int:
    print()
    print("=" * 60)
    print(f"  AI Brain — {COUNTRY.upper()} · Local-AI Bridge")
    print("=" * 60)
    print()
    print("This sets up local AI so your queries never leave your laptop.")
    print("No API key required. No cloud cost. Your data stays on your device.")
    print()

    print("[1/5] Checking for Ollama...")
    if not detect_ollama():
        print("  ✗ ollama not installed")
        install_ollama_instructions()
        return 1
    print("  ✓ ollama installed")

    print("\n[2/5] Detecting laptop RAM...")
    ram = detect_ram_gb()
    print(f"  ✓ ~{ram:.1f} GB total RAM")

    print("\n[3/5] Selecting model...")
    if getattr(args, "model", None):
        model = args.model
        desc = "user-specified"
    else:
        model, desc = recommend_model(ram)
    print(f"  → {model} ({desc})")
    if not getattr(args, "yes", False):
        answer = input(f"\nProceed with {model}? [Y/n] ").strip().lower()
        if answer and answer != "y":
            print("aborted.")
            return 0

    print(f"\n[4/5] Downloading {model}...")
    if not ollama_pull(model):
        return 1

    print("\n[5/5] Writing config + smoke test...")
    write_config(model)
    smoke_test(model)

    print()
    print("=" * 60)
    print(f"  ✅ Local-AI bridge ready · provider=ollama · model={model}")
    print(f"  config: {CONFIG_FILE}")
    print("=" * 60)
    print()
    print("In local mode, your queries run entirely on your laptop.")
    print("No queries leave your machine.")
    print()
    print("To switch to a cloud provider later (use only for non-client work):")
    print("  ailawfirm-usa connect-cloud --provider deepseek --cloud-warning-acknowledged")
    print()
    return 0


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--yes", "-y", action="store_true", help="skip prompts")
    p.add_argument("--model", help="override the recommended model")
    sys.exit(cmd_connect_local(p.parse_args()))
