---
title: "LC 626: Exchange Seats"
area: sql
tags: [sql, case-when, parity, adjacent-swap, key-remapping, membership-subquery, difficulty-medium]
source: "https://leetcode.com/problems/exchange-seats/"
created: 2026-07-15
updated: 2026-07-23
status: seed
solved_unaided: no
time_taken_min:
---

# LC 626: Exchange Seats

**PySpark companion:** [same problem in the DataFrame API](../pyspark/lc-0626-exchange-seats.md)

**Problem:** `Seat(id, student)` with consecutive ids starting at 1. Swap the seats of every two consecutive students (1↔2, 3↔4, …). If the student count is odd, the last student stays put. Return rows ordered by id.

## Pattern
**Adjacent-pair swap by remapping the key with a parity `CASE`, not by moving rows.** Recognize it when the ask is "swap/shift neighboring rows": instead of touching the data, recompute the ordering key — odd id becomes `id + 1`, even id becomes `id - 1` — and let `ORDER BY` on the new key do the "movement". The only real work is the boundary: an odd *last* id has no partner and must keep its id, which turns into an existence check on `id + 1`.

## My approach
Had to look at the approach once before writing it. What I submitted:

```sql
select
    CASE
    WHEN id % 2 = 1 and id+1 in (select id from Seat) then id+1
    WHEN id % 2 = 0 then id - 1
    else id
    end as id, student
FROM Seat
group by id
```

The core is right: parity `CASE` for the swap, and the odd-last-row boundary handled with the membership test `id + 1 IN (SELECT id FROM Seat)` — the same subquery-in-`CASE` machinery as [LC 608](./lc-0608-tree-node.md). Two blemishes:

1. **The `GROUP BY id` is a leftover reflex** — nothing is aggregated and `id` is already unique, so it does nothing (and only parses cleanly because `student` is functionally dependent on the primary key).
2. **No `ORDER BY`.** The problem requires output ordered by id, and after the swap the rows come off the scan in *old*-id order. Old MySQL implicitly sorted `GROUP BY` output, which may be why it passed; MySQL 8.0 removed that guarantee.

## Optimal approach
Same `CASE` shape, with the boundary usually written against `COUNT(*)` (ids are guaranteed consecutive from 1, so "last odd id" ⇔ `id = COUNT(*)` when the count is odd), plus the required sort on the *new* id:

```sql
SELECT
    CASE
        WHEN id % 2 = 1 AND id = (SELECT COUNT(*) FROM Seat) THEN id
        WHEN id % 2 = 1 THEN id + 1
        ELSE id - 1
    END AS id, student
FROM Seat
ORDER BY id;
```

The uncorrelated `COUNT(*)`/`MAX(id)` scalar is computed once, versus my `IN (SELECT id ...)` set-membership probe — equivalent result, and my version is actually more robust if ids weren't consecutive. Two other idioms worth knowing:

- **Bit trick (MySQL):** `(id - 1) XOR 1 + 1` flips the last bit of the 0-based id, swapping each pair in one expression — cute, unreadable in review.
- **Window functions:** keep ids fixed and swap the *students* instead: `COALESCE(CASE WHEN id % 2 = 1 THEN LEAD(student) OVER (ORDER BY id) ELSE LAG(student) OVER (ORDER BY id) END, student)` — the `COALESCE` catches the odd last row, whose `LEAD` is `NULL`. Generalizes to shift-by-k problems where key arithmetic doesn't.

## Complexity
- Time: O(n log n) for the final `ORDER BY` (the `CASE` itself is one O(n) scan; the scalar subquery is O(n) once).
- Space: O(1) beyond the sort (my `IN` variant materializes the id set — O(n)).

## The mistake to remember
**When the ask is "reorder/swap rows", don't move data — recompute the ordering key with `CASE` and sort by it. And always finish with `ORDER BY` on the remapped key: the swap doesn't exist until the sort happens.** Drop reflex `GROUP BY` when nothing aggregates.

## Similar problems in vault
- [LC 608: Tree Node](./lc-0608-tree-node.md) — same `CASE` with a membership subquery against the own table; there membership assigns a label, here it detects the partner-less last seat.
- [LC 550: Game Play Analysis IV](./lc-0550-game-play-analysis-iv.md) — neighboring-row logic done the other way (LEAD/LAG windows); the window variant of this problem is the bridge between the two.

## Solution
```sql
SELECT
    CASE
        WHEN id % 2 = 1 AND id + 1 IN (SELECT id FROM Seat) THEN id + 1
        WHEN id % 2 = 0 THEN id - 1
        ELSE id
    END AS id, student
FROM Seat
ORDER BY id;
```
