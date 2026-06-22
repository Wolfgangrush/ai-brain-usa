# 🍎 Mac Install Guide — AI Brain India

Total time: ~10 minutes. macOS already has Python; you mostly just install the tool.

---

## What is "Terminal"?

Terminal is Mac's command-line. It's where you type commands and the computer does them.

**To open Terminal:**
- Press `Cmd + Space` → type `Terminal` → press Enter

OR

- Open Finder → Applications → Utilities → Terminal

A dark window opens. That's Terminal.

---

## Step 1 — Verify Python (1 minute)

macOS comes with Python pre-installed. Open Terminal and paste:

```
python3 --version
```

You should see `Python 3.11.x` or higher.

**If you see `Python 3.9` or older OR "command not found":**

Install via Homebrew (recommended):
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Follow the on-screen prompts. After it finishes:
```
brew install python@3.12
```

OR install from the official installer at https://www.python.org/downloads/macos/

---

## Step 2 — Install AI Brain India (2 minutes)

In Terminal, paste:

```
pip3 install git+https://github.com/Wolfgangrush/ai-law-firm-india.git
```

Wait 1-2 minutes for the download + install (~200 MB).

**Verify it worked:**
```
python3 -c "import ailawfirm_india; print('OK')"
```

You should see `OK`.

---

## Step 3 — Install Git (if Step 2 failed because Git was missing)

If Step 2 errored with "git not found":

```
xcode-select --install
```

Wait for the installer prompt, click Install, wait 5 minutes. Then re-run Step 2.

---

## Step 4 — Choose your AI brain

### Option A — Local Ollama (recommended for client work)

**Privacy: perfect. Cost: ₹0 forever.**

```
brew install ollama
ollama pull qwen3:14b
```

(Or download Ollama installer from https://ollama.com/download/Mac if you don't use Homebrew.)

Wait 10-20 minutes for the model download (~10 GB, one-time).

### Option B — DeepSeek API (cheap with mandatory privacy setup)

⚠️ DeepSeek may use API inputs for training BY DEFAULT. You MUST opt out first.

1. Go to https://platform.deepseek.com → sign up · top up $10-20
2. Settings → Privacy → turn OFF "Improve the model for everyone"
3. Settings → API keys → Create → copy `sk-...` string
4. See [MODEL_SETUP.md](MODEL_SETUP.md).

### Option C — Claude API or Gemini API

See [MODEL_SETUP.md](MODEL_SETUP.md).

---

## Step 5 — Run

```
ailawfirm-india
```

Try:
```
> tell me about Bombay HC
> validate AIR 1973 SC 1461
> check this language: "Best advocate in Mumbai"
```

---

## 📁 Where your data lives on Mac

```
~/.ailawfirm-india/             ← Mac shortcut for /Users/YourName/.ailawfirm-india/
├── palace/                     ← all matter/client/citation memory
├── config.json                 ← AI model settings
└── people_map.json             ← optional client alias system
```

**To see it in Finder:**
- Press `Cmd + Shift + .` (period) — this toggles showing hidden files
- Navigate to your home folder (Cmd+Shift+H)
- You'll see `.ailawfirm-india`

**Backup:**
```
cp -R ~/.ailawfirm-india ~/Dropbox/ailawfirm-india-backup
```

Or via Finder: drag the `.ailawfirm-india` folder to iCloud Drive / Dropbox.

---

## 🆘 Common Mac problems + fixes

### "command not found: ailawfirm-india" after install
Your shell can't find Python's scripts directory. Add to your PATH:
```
echo 'export PATH="$HOME/Library/Python/3.13/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```
(adjust the Python version to match what you installed)

### "pip3 not found"
Use:
```
python3 -m pip install git+https://github.com/Wolfgangrush/ai-law-firm-india.git
```

### Permission errors during pip install
Either:
- Use `--user` flag: `pip3 install --user git+https://github.com/Wolfgangrush/ai-law-firm-india.git`
- OR use Homebrew Python (which doesn't need sudo): `brew install python@3.12` then re-run pip install

### "SSL: CERTIFICATE_VERIFY_FAILED"
Run:
```
/Applications/Python\ 3.13/Install\ Certificates.command
```
(adjust version)

### Slow ChromaDB on Apple Silicon (M1/M2/M3/M4/M5)
This is expected for first-run indexing. Subsequent operations are fast. If it stays slow, check Activity Monitor for memory pressure — you may need to close other apps.

---

## Done?

Go to [GETTING_STARTED.md](GETTING_STARTED.md) for the tour.

Issues: https://github.com/Wolfgangrush/ai-law-firm-india/issues
