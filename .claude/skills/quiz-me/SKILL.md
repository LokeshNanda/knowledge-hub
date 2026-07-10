---
name: quiz-me
description: Run an active-recall quiz from the user's own notes, biased toward stale material and past misses. Use whenever the user runs /quiz-me [area], says "quiz me", "test me on X", "interview prep questions", "am I ready for a system design / SQL / cloud interview", or wants to revise before an interview.
---

# Quiz from the vault

Active recall against the user's own notes — the cheapest spaced repetition that exists.

## Selecting material

1. Scope to the requested area, or the whole vault if none given.
2. Read `reviews/quiz-log.md` (create it if missing) for per-note history.
3. Prioritize, in order: past misses due for retry → notes not quizzed in 3+ weeks → `evergreen` notes untouched longest → recent `seed` notes (light touch, they're still fresh). Aim for 5-7 questions per session unless asked otherwise.

## Running the quiz

- Ask **one question at a time** and wait for the answer. Never dump all questions at once — retrieval only works if they answer before seeing the next.
- Question styles to rotate through:
  - Mechanism: "Walk me through what happens when..."
  - Trade-off: "When would you pick X over Y, and what does it cost you?"
  - Recognition (DSA): describe a problem's shape, ask which pattern applies and why.
  - Debug/edge: "This design breaks under Z — where and why?"
  - Interview follow-up: after a correct answer, push one level deeper, like a real interviewer.
- Grade each answer honestly against the note: ✅ solid / 🟡 partial / ❌ miss. On partial/miss, give the correct answer *with a link to the note* so review is one click away.

## Closing the session

1. Append results to `reviews/quiz-log.md`: date, area, per-note question → result, one-line takeaway.
2. Where the quiz exposed a gap the note itself doesn't cover well, say so and offer to `/deep-dive` it.
3. Notes answered ✅ twice across separate sessions can be promoted toward `evergreen` — mention candidates, let the user confirm.
4. Commit: `quiz: dsa + databases-internals, 5/7`.

## Rules

- Questions must be answerable from the vault's notes — this tests *their* knowledge base, not trivia.
- Keep the tone of a good interviewer: probing but encouraging. A miss is a finding, not a failure.
