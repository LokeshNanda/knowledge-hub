---
name: leetcode
description: Log a solved (or attempted) coding problem into the DSA area with pattern analysis and honest review. Use whenever the user runs /leetcode, pastes a solution, shares a LeetCode/HackerRank/Codeforces problem they worked on, says "I just solved...", "review my solution", or "log this problem" — even if they only paste code with no explanation.
---

# Log a coding problem

Capture each practice problem as a pattern-tagged entry so the vault reveals, over time, which patterns the user has mastered and which keep costing them.

## Inputs to gather

From the user's message (ask only for what's missing, in one question):
- Problem name/link, their solution (pasted or a file path)
- Whether they solved it unaided, and roughly how long it took
- Where they got stuck, if anywhere

## Procedure

1. **Identify the pattern(s)** — the reusable technique, not the topic. "Two pointers on sorted array", not "arrays".
2. **Review the solution honestly.** Correctness, complexity, idiomatic quality, edge cases missed. If their approach is suboptimal, explain the optimal one and, more importantly, the *insight* that leads to it. Do this review conversationally in chat — this is the interactive, valuable part.
3. **Write the entry** to `areas/dsa/lc-{number}-{kebab-name}.md` using `templates/leetcode-entry.md`. Fill "The mistake to remember" with the single costliest error, phrased as a forward-looking rule ("When the array is sorted and you reach for a hashmap, check two pointers first").
4. **Link similar problems.** Grep `areas/dsa/` for entries sharing the pattern tag; add 2-3 to "Similar problems in vault" bidirectionally.
5. **Update `indexes/dsa.md`**, which is organized *by pattern*, each pattern section listing its problems with a ✅ (clean solve) / ⚠️ (struggled) marker and a running tally. This index is the "which patterns do I fumble" dashboard — keep the tallies accurate.
6. **Commit**: `leetcode: LC 239 sliding-window-maximum (monotonic deque)`.

## Rules

- Be honest in the review; a flattering log is a useless log. But review the code, not the person — concrete and constructive.
- If the user only pastes code, infer the problem from it, confirm your guess, then proceed.
- Repeat attempts at a previously logged problem update the existing entry (append an "Attempt 2" section with date) — this repetition history is exactly what `/quiz-me` feeds on.
