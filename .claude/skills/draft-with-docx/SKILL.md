---
name: draft-with-docx
description: Pair every drafted document with a Word (.docx) file. When the advocate asks for a draft — complaint, petition, affidavit, reply, plaint, sale-deed analysis, advisory note, opinion, anything filed or sent — produce BOTH the markdown AND the .docx in the same directory. Word is what the registry accepts and what clients open. Markdown is what the firm reads and diffs. Both must exist.
allowed-tools: Bash, Read, Write, Edit
---

# /draft-with-docx — Every Draft Ships as .md + .docx

The advocate's filing reality: US courts accept Word, not markdown. The firm reads markdown. Both audiences exist. So every drafted document produces two files, atomically, in the matter's drafts directory.

## When this skill fires

Any time the firm produces a written legal document:

- Pleadings (complaint, plaint, written statement, replication, counter-claim)
- Petitions (writ, SLP, review, curative, transfer, contempt)
- Criminal pleadings (bail, anticipatory bail, 482 CrPC / 528 BNSS, revision, appeal)
- Civil applications (Section 9 Arb, Section 11 Arb, Order 39 R.1-2, O.7 R.11)
- Affidavits (verification, counter-affidavit, rejoinder)
- Replies (to show-cause, notice, affidavit)
- Notices (legal notice, Section 80 CPC, Section 138 NI demand)
- Advisory notes, legal opinions, due-diligence reports
- Sale deed analysis, title search, property reports
- Tax forms (Form 35, Form 36, Section 263 reply, Section 148A objection)

If you wrote it for the matter, it gets paired.

## The pairing rule

For every `<filename>.md` produced, write `<filename>.docx` in the SAME directory in the SAME tool call window. No "I'll add the docx in a second" — both, atomically.

## How to produce the .docx

Use pandoc when available (cleanest output, preserves headings + tables):

```bash
pandoc "<filename>.md" -o "<filename>.docx" \
  --reference-doc=<reference.docx if firm has one> \
  --from=markdown+pipe_tables+yaml_metadata_block
```

If pandoc is unavailable, fall back to python-docx via pypandoc:

```bash
python3 -c "import pypandoc; pypandoc.convert_file('<filename>.md', 'docx', outputfile='<filename>.docx')"
```

If neither is available, install pandoc:

```bash
# macOS
brew install pandoc
# Linux
sudo apt-get install -y pandoc
# Windows (advocate runs this themselves in PowerShell)
winget install --id JohnMacFarlane.Pandoc
```

## Where the files go

Inside the matter's drafts directory:

```
~/Desktop/<firm-name>/<matter-folder>/drafts/
  ├── 2026-05-24-complaint-s138.md
  └── 2026-05-24-complaint-s138.docx        ← ALWAYS paired
```

If the matter folder doesn't have a `drafts/` subdir, create it.

## Verification before reporting "done"

After writing both files, verify both exist:

```bash
ls -la "<filename>.md" "<filename>.docx"
```

Report to the advocate:

```
✍️ Draft ready (paired):
   <filename>.md       — for the firm + diffs
   <filename>.docx     — for the registry + client
```

Never report a draft as "ready" if only one of the two exists.

## Why this rule exists

- **Registry reality:** US court e-filing portals + physical filing windows accept .docx / .pdf, not .md. A markdown-only draft cannot be filed.
- **Client reality:** Clients open Word on their laptop. They cannot read a `.md` file. A markdown-only draft cannot be sent.
- **Firm reality:** Markdown is what the AI brain reads, searches, diffs, and learns from. A docx-only draft is opaque to the firm's brain.

The rule resolves the audience-mismatch by producing both, every time.

## Anti-patterns (do not do)

- ❌ "Here's the draft in markdown. Run pandoc when you need a docx." — pushes friction onto the advocate at filing time
- ❌ Writing only the .docx and skipping the .md — the firm loses search/diff ability
- ❌ Writing the .md, telling the advocate to convert later — they will forget; deadline pressure means it won't happen
- ❌ Producing the .docx in a different directory than the .md — breaks the matter folder convention
