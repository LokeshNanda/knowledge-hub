---
name: connect
description: Vault maintenance — find and add missing cross-links between related notes, fix broken links, flag duplicates and orphans, refresh stale indexes. Use whenever the user runs /connect, says "clean up the vault", "link my notes", "find duplicates", "vault health check", or roughly monthly when notes have accumulated without maintenance.
---

# Connect & maintain the vault

Cross-links are what turn a pile of notes into a knowledge base. This skill audits and repairs the graph.

## Procedure

1. **Delegate the audit** to the `librarian` subagent. Ask it to walk `areas/` and `indexes/` and report:
   - Candidate link pairs: notes sharing tags/keywords/topics that don't link to each other (with a one-line reason per pair)
   - Broken relative links and links into `_archive/`
   - Near-duplicates (same `source` or heavily overlapping content)
   - Orphans (no inbound or outbound links)
   - Index drift (notes missing from their `indexes/<area>.md`, or index entries pointing nowhere)
   - Misfiled suspects (note content that fits a different area better)
2. **Triage the report with the user.** Present findings grouped by category with your recommendation per item. Cheap, obvious fixes (broken links, index drift) — just do them. Judgment calls (merging duplicates, moving a note between areas) — get a yes/no per item before acting.
3. **Apply approved fixes:**
   - Add cross-links bidirectionally, under "Related notes", each with a two-or-three-word reason ("same trade-off", "prerequisite").
   - Merge duplicates by folding the weaker note into the stronger one; move the husk to `_archive/` with a pointer to the survivor. Never delete.
   - Moves between areas: `git mv`, update frontmatter `area`, fix inbound links, update both indexes.
   - Regenerate any drifted index in full.
4. **Commit**: `connect: 9 links added, 2 merged, indexes refreshed` — one commit, so the whole maintenance pass is one reviewable diff.
5. **Report** a short before/after: links added, duplicates merged, orphans remaining (some orphans are fine — new topics start alone).

## Rules

- Only link notes that are *genuinely* related; a fully-connected graph is as useless as an unconnected one. When unsure, leave it out.
- Respect hard rules in CLAUDE.md: no deletions, archive instead.
