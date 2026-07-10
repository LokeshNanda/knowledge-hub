---
name: weekly-digest
description: Write the weekly learning digest — what was learned, loose threads, contradictions, and suggested next topics. Use whenever the user runs /weekly-digest, asks "what did I learn this week", "summarize my week", "weekly review", or at the start of a study session if more than a week has passed since the last digest in reviews/.
---

# Weekly digest

The digest is the system's feedback loop: it converts a week of scattered activity into direction for the next one.

## Procedure

1. **Establish the window.** Find the latest `reviews/digest-*.md`; the window is from its date (or 7 days ago if none) to today.
2. **Gather evidence:**
   - `git log --since=<window start> --stat` for what changed.
   - Read the notes created/updated in the window (the notes themselves, not just diffs).
   - Read "Open questions" sections across those notes.
   - Skim `reviews/quiz-log.md` for recent misses.
   - If the vault has grown a lot, delegate the full read to the `librarian` subagent and work from its report.
3. **Write `reviews/digest-YYYY-WW.md`** with exactly this structure:

```markdown
# Digest — Week {WW}, {YYYY} ({date range})

## What moved
Per area touched: 2-3 sentences of substance — the *ideas* learned, not file counts.

## Threads left hanging
Notes still at `status: seed`, unanswered open questions, half-finished topics.

## Connections & contradictions
Where this week's material links to or conflicts with older notes. Contradictions are gold — flag them explicitly.

## Pattern check (DSA)
From indexes/dsa.md tallies and quiz misses: which patterns are solid, which are fumbling. Skip if no DSA activity.

## Next week — pick from
2-3 concrete suggestions with a one-line why, drawn from hanging threads and fumbled patterns. Suggestions, not assignments.
```

4. **Promote statuses** where earned: a `seed` note that got revisited/linked this week becomes `growing`; note promotions in the digest.
5. **Commit**: `digest: week 2026-28`.
6. **In chat**, give only the "Next week" section and one sentence of headline — the full digest is for reading in the file.

## Rules

- Ground every claim in what's actually in the notes/log; never invent activity.
- If the week was quiet, say so plainly and keep the digest short. An honest thin digest beats a padded one.
