# Technical Knowledge Base

This repository is a personal technical knowledge base. Claude Code acts as the
librarian: it ingests raw material, writes structured notes, maintains indexes,
and keeps everything cross-linked. The human dumps material and studies; Claude
organizes.

## Scope

Technical learning only:

| Area folder | Covers |
|---|---|
| `areas/dsa/` | LeetCode & competitive practice, algorithms, data structures, patterns |
| `areas/system-design/` | HLD, LLD, design patterns, case studies, interview prep |
| `areas/sql/` | SQL techniques, query optimization, window functions, practice problems |
| `areas/databases-internals/` | Storage engines, indexing, transactions, replication, how DBs work inside |
| `areas/cloud/gcp/`, `areas/cloud/aws/`, `areas/cloud/azure/` | Cloud services, architectures, certifications |
| `areas/ai-agents/` | LLMs, agentic systems, fine-tuning, RAG, MCP, self-hosting models |
| `areas/pyspark/` | PySpark DataFrame-API companions to the SQL problems, Spark idioms and gotchas |

If material clearly belongs to none of these, ask the user rather than inventing
a new top-level area. New areas are a human decision.

## Directory contract

- `inbox/` — raw drops (PDFs, images of handwritten notes, pasted clippings, links in `.md`/`.txt` files). Never organize content directly here.
- `inbox/processed/` — originals moved here after ingestion. Never re-ingest anything already in this folder.
- `areas/` — the organized vault. All notes live here.
- `indexes/` — one map-of-content file per area (e.g. `indexes/dsa.md`). Regenerated, never hand-edited history.
- `reviews/` — weekly digests (`reviews/digest-YYYY-WW.md`) and the quiz log (`reviews/quiz-log.md`).
- `templates/` — canonical note templates. Read the relevant template before writing any note.
- `_archive/` — retired notes. Nothing in this repo is ever deleted; superseded or wrong notes move here with a one-line reason appended.

## Note conventions

- Filenames: `kebab-case.md`, descriptive, no dates in the name (dates live in frontmatter). Example: `b-tree-vs-lsm-tree.md`.
- Every note starts with YAML frontmatter:

```yaml
---
title: B-Tree vs LSM-Tree
area: databases-internals
tags: [storage-engine, indexing, write-amplification]
source: "Designing Data-Intensive Applications, ch. 3"   # or URL, or "own notes"
created: 2026-07-10
updated: 2026-07-10
status: seed | growing | evergreen
---
```

- `status` meaning: `seed` = raw summary, unreviewed; `growing` = revisited at least once, has links; `evergreen` = distilled, trusted, interview-ready.
- Cross-link related notes with relative markdown links: `[LSM compaction](../databases-internals/lsm-compaction.md)`. Wiki-style `[[links]]` are also acceptable (Obsidian-compatible) but be consistent within a note.
- Standard note body structure is defined in `templates/note.md`. LeetCode entries use `templates/leetcode-entry.md`.
- **PySpark pairing rule:** every LeetCode SQL note in `areas/sql/` gets a companion note in `areas/pyspark/` with the *same filename*, written from `templates/pyspark-entry.md`. Claude authors the PySpark translation (the SQL note holds the problem statement and the user's honest solve review; the companion holds only the SQL→DataFrame mapping, idiomatic solution, and Spark-specific gotchas). Cross-link both ways (`**PySpark companion:**` line in the SQL note, `**SQL companion:**` line in the PySpark note) and update `indexes/pyspark.md` in the same session — whenever a new SQL problem is ingested, the companion is created in that same session.
- Write summaries in your own words. Quote sources sparingly (short fragments only) and always attribute. A note should teach the concept, not mirror the source's structure.

## Hard rules

1. **Never delete a note.** Move it to `_archive/` with a reason. Only files inside `inbox/processed/` may ever be cleaned up, and only when the user explicitly asks.
2. **Never rewrite history.** No `git reset --hard`, no force pushes, no `git clean`. (Hooks enforce this — do not try to work around them.)
3. **Commit after every organizing operation** with a message like `ingest: 3 notes (dsa, cloud/gcp)` or `digest: week 2026-28`.
4. **Idempotency.** Before ingesting a file, confirm it is not already in `inbox/processed/` and no note with the same `source` exists in the target area.
5. **Ask, don't guess** when a piece of material is ambiguous between two areas or seems out of scope.
6. **Keep indexes fresh.** Any operation that adds, moves, or archives a note must update the corresponding `indexes/<area>.md` in the same session.

## Delegation guidance

- Reading long PDFs or images of handwritten notes → delegate to the `note-processor` subagent (read-only); the main session writes the resulting note.
- Web research for deep-dives → delegate to the `researcher` subagent; the main session synthesizes.
- Full-vault audits (link checks, duplicate detection) → delegate to the `librarian` subagent.

Subagents are read-only by design. All file writes happen in the main session so the user can steer them.
