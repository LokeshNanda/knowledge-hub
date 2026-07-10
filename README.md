# Technical Knowledge Base — Claude Code Starter Kit

A personal knowledge base where you dump raw material and Claude Code organizes it:
structured notes, cross-links, indexes, weekly digests, and quizzes — all plain
markdown, all versioned in git.

## Setup (once, ~2 minutes)

```bash
cd knowledge-base
git init && git add -A && git commit -m "initial: starter kit"
claude
```

Then inside Claude Code:
- Run `/hooks` to confirm the two hooks loaded (bash guard + commit check).
- Say "list your skills" or just try `/ingest` — with an empty inbox it should report there's nothing to process.

Requires: Claude Code, git, python3 (for the hook scripts). If hook execution
is blocked on first run, mark the scripts executable: `chmod +x .claude/hooks/*.py`.

## The rhythm

| When | Do |
|---|---|
| Anytime | Drop PDFs, screenshots of handwritten notes, clippings, or `.md` files with links into `inbox/` |
| When you sit down | `/ingest` — everything in inbox becomes filed, linked notes |
| After solving a problem | `/leetcode` + paste your solution |
| When studying a topic | `/deep-dive <topic>` |
| Sunday | `/weekly-digest` |
| Before interviews / weekly | `/quiz-me [area]` |
| Monthly | `/connect` |

## What's inside

```
CLAUDE.md                  taxonomy, note conventions, hard rules (read this first)
.claude/skills/            the six workflows above
.claude/agents/            note-processor, researcher, librarian (read-only workers)
.claude/hooks/ + settings.json
                           guard.py blocks rm -rf / git reset --hard / force push
                           commit_check.py stops sessions ending with uncommitted notes
templates/                 note.md and leetcode-entry.md
inbox/ -> areas/ -> indexes/ -> reviews/
                           raw drops -> organized notes -> maps of content -> digests & quiz log
_archive/                  nothing is ever deleted; retired notes land here
```

## Conventions worth knowing

- Every note has frontmatter with a `status`: `seed` → `growing` → `evergreen`.
  Digests and quizzes promote notes as they prove themselves.
- Notes are Obsidian-compatible if you ever want a graph view — just open the
  repo as a vault. Nothing depends on it.
- Review the git diff after `/ingest` and `/connect` for the first couple of
  weeks; correct Claude in chat and tighten CLAUDE.md when you see a pattern
  you dislike. That review loop is how the system gets tuned to you.

## Deliberately not included (add later, once the core is habitual)

- Publishing a curated subset to your domain (a `/publish` skill + Quartz/Hugo)
- Semantic/embedding search (grep goes a long way at personal scale)
- Scheduled headless runs (once you trust `/ingest`, wire `claude -p "/ingest"` into cron)
