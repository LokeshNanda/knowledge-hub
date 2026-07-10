---
name: deep-dive
description: Produce a researched, structured study note on a technical topic (database internals, system design components, cloud services, AI/agent concepts). Use whenever the user runs /deep-dive <topic>, says "explain X in depth and save it", "research X for my notes", "I want to study X properly", or asks how something works internally with intent to keep the material.
---

# Deep-dive on a topic

Build an evergreen-quality study note by combining vault context, verified research, and the standard note structure.

## Procedure

1. **Check the vault first.** Grep `areas/` and `indexes/` for existing notes on or adjacent to the topic. If one exists, propose deepening it rather than duplicating. Adjacent notes become the "Related notes" links and tell you what depth to write at.
2. **Scope with the user** in one exchange if the topic is broad: "Raft" could mean the algorithm, comparison vs Paxos, or a specific implementation. Skip this if the request is already specific.
3. **Research via the `researcher` subagent.** Give it the scoped topic and ask for: mechanism, design rationale/trade-offs, common misconceptions, and where it appears in real systems — with sources, distinguishing official docs/papers from blog opinion. Keeping the raw search results in the subagent protects your context.
4. **Synthesize the note** at `areas/<area>/<topic>.md` using `templates/note.md`. Priorities:
   - "Why it's designed this way" is the heart of the note — trade-offs and rejected alternatives are what interviews and real design work run on.
   - Include a small worked example or ASCII/mermaid diagram where it aids the mechanism section.
   - Cite sources in `source` frontmatter (primary source) and inline links for specific claims.
   - Populate "Open questions" honestly — these seed future dives via the weekly digest.
5. **Cross-link** bidirectionally with the adjacent notes found in step 1, update `indexes/<area>.md`, set `status: growing` (a fresh deep-dive is researched but not yet revisited).
6. **Commit**: `deep-dive: raft-leader-election (databases-internals)`.
7. **End in chat** with a 3-bullet takeaway and one suggested follow-up dive from the open questions.

## Rules

- Do not pad. A tight 150-line note beats an exhaustive 500-line one nobody re-reads.
- Where sources disagree or the field lacks consensus, say so in the note rather than picking a side silently.
