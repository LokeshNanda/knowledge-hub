---
title: "LC 550: Game Play Analysis IV"
area: sql
tags: [sql, window-functions, first-event-anchor, date-arithmetic, difficulty-medium]
source: "https://leetcode.com/problems/game-play-analysis-iv/"
created: 2026-07-12
updated: 2026-07-12
status: seed
solved_unaided: no
time_taken_min:
---

# LC 550: Game Play Analysis IV

**Problem:** Report the fraction of players who logged in again on the day *right after their first login day*, rounded to 2 decimals.

## Pattern
**First-event anchor.** When a problem says "after the *first* X" (first login, first purchase, signup day), anchor every comparison to `MIN(event_date)` per group. Recognize it by the word *first* in the statement — it means one fixed reference point per entity, not "any adjacent pair of events". Reaching for `LEAD`/`LAG` here is the trap: those find *any* adjacency.

## My approach
Used `LEAD(event_date) OVER (PARTITION BY player_id)` to pair each login with the next one, then counted rows where the next login was `event_date + 1`, divided by distinct player count. Test cases failed.

```sql
with cte as (
  select *, LEAD(event_date) OVER(PARTITION BY player_id) as next_day_event
  FROM Activity
)
select ROUND(
  (select count(cte.player_id) from cte where next_day_event = event_date + 1)
  / (select count(distinct(player_id)) from Activity), 2) as fraction
```

Four distinct bugs, in order of impact:

1. **Wrong anchor (the failing edge case).** The query counts *any* consecutive-day login pair. A player with logins on `03-01`, `03-05`, `03-06` gets counted (05→06 is consecutive) even though they did **not** return the day after their first login (03-01). The comparison must be against `MIN(event_date)` per player only.
2. **`event_date + 1` is numeric, not date, arithmetic.** In MySQL, `'2016-03-31' + 1` evaluates to the integer `20160332`, which never equals `2016-04-01` (`20160401`). Every month/year boundary silently fails. Use `DATE_ADD(event_date, INTERVAL 1 DAY)` or `DATEDIFF(a, b) = 1`.
3. **`LEAD` without `ORDER BY`.** `OVER (PARTITION BY player_id)` with no `ORDER BY event_date` makes "next" row order undefined — results are nondeterministic.
4. **Row count instead of player count.** `COUNT(cte.player_id)` counts matching rows; a player with three consecutive login days would be counted twice. Needs `COUNT(DISTINCT player_id)` (falls out naturally once the anchor is fixed, since each player has one first login).

## Optimal approach
Compute each player's first login, then check whether a row exists exactly one day after it. `(player_id, event_date)` is the primary key, so each player matches at most once — no distinct needed in the numerator.

```sql
SELECT ROUND(
    COUNT(a.player_id)
    / (SELECT COUNT(DISTINCT player_id) FROM Activity),
    2) AS fraction
FROM Activity a
JOIN (
    SELECT player_id, MIN(event_date) AS first_login
    FROM Activity
    GROUP BY player_id
) f ON a.player_id = f.player_id
   AND a.event_date = DATE_ADD(f.first_login, INTERVAL 1 DAY);
```

Window-function variant (closer to the original attempt):

```sql
WITH firsts AS (
  SELECT player_id, event_date,
         MIN(event_date) OVER (PARTITION BY player_id) AS first_login
  FROM Activity
)
SELECT ROUND(
    COUNT(DISTINCT CASE WHEN event_date = DATE_ADD(first_login, INTERVAL 1 DAY)
                        THEN player_id END)
    / COUNT(DISTINCT player_id), 2) AS fraction
FROM firsts;
```

## Complexity
- Time: O(n log n) (group/sort over Activity); one pass with an index on `(player_id, event_date)`.
- Space: O(p) for the per-player first-login set.

## The mistake to remember
When the problem anchors to a *first* event, compare against `MIN()` per group — `LEAD`/`LAG` finds *any* adjacency, not adjacency to the first. And never write `date + 1` in MySQL; it's integer arithmetic that breaks at month boundaries — use `DATE_ADD`.

## Similar problems in vault
- [LC 570: Managers with at Least 5 Direct Reports](./lc-0570-managers-with-at-least-5-direct-reports.md) — also per-entity aggregation, but a simple count threshold via self-join instead of a first-event anchor.

## Solution
```sql
SELECT ROUND(
    COUNT(a.player_id)
    / (SELECT COUNT(DISTINCT player_id) FROM Activity),
    2) AS fraction
FROM Activity a
JOIN (
    SELECT player_id, MIN(event_date) AS first_login
    FROM Activity
    GROUP BY player_id
) f ON a.player_id = f.player_id
   AND a.event_date = DATE_ADD(f.first_login, INTERVAL 1 DAY);
```
