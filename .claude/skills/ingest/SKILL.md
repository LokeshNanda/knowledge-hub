---
name: ingest
description: Process everything in inbox/ into organized, cross-linked notes in areas/. Use whenever the user runs /ingest, says "process my inbox", "organize these files", "I dropped some PDFs/notes/clippings", mentions new material to file, or asks to summarize an uploaded document into the knowledge base — even if they don't say the word "ingest".
---

# Ingest inbox material

Turn raw drops in `inbox/` into structured notes in `areas/`, safely and idempotently.

## Procedure

1. **Inventory.** List `inbox/` (excluding `inbox/processed/`). If empty, say so and stop. Present the list of items found before processing.
2. **For each item, classify** it into one area from the taxonomy in CLAUDE.md. Use filename, a quick skim of content, and existing vault context. If genuinely ambiguous between two areas or out of scope, ask the user — one grouped question at the end of inventory, not one interruption per file.
3. **Extract content:**
   - Short text/markdown clippings: read directly.
   - PDFs longer than ~10 pages, images/photos of handwritten notes, or anything content-heavy: delegate to the `note-processor` subagent with the file path. It returns a structured summary + suggested tags; you do the writing. This keeps the main context clean.
4. **Check for duplicates** before writing: search the target area for an existing note with the same `source` or clearly the same topic. If found, *update* that note (append/merge, bump `updated`, upgrade `status` if warranted) instead of creating a sibling.
5. **Write the note** using `templates/note.md`. Fill every frontmatter field. Summarize in your own words — the note should stand alone without the original.
6. **Cross-link.** Search the vault (grep by tags/keywords) for 1-3 genuinely related notes and add them to "Related notes" in both directions.
7. **Update the index.** Add/adjust the entry in `indexes/<area>.md` (create the index from scratch if the area has none: a grouped, one-line-per-note map of content).
8. **Move the original** to `inbox/processed/`, preserving the filename (prefix with `YYYY-MM-DD-` if a name collision occurs).
9. **Commit** everything with a message like `ingest: 4 notes (2 databases-internals, 1 dsa, 1 ai-agents)`.
10. **Report.** End with a short table: original file → note path → area → one-line gist, plus anything skipped and why.

## Rules

- Never modify files in `inbox/` other than moving them to `processed/` at the end.
- Never re-ingest anything already in `inbox/processed/`.
- One note per distinct concept. A 40-page PDF covering three topics becomes three notes, all pointing at the same `source`.
- If an item is just a URL, fetch and summarize the page; the URL becomes `source`.
