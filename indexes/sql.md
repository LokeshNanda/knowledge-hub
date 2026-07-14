# SQL — map of content

Organized by pattern. ✅ = clean unaided solve, ⚠️ = struggled / needed help.
Tally per pattern: clean / total.

## Aggregation: first-event anchor (0/1 clean)
- ⚠️ [LC 550: Game Play Analysis IV](../areas/sql/lc-0550-game-play-analysis-iv.md) — day-after-first-login retention; used LEAD over any adjacent pair instead of anchoring to MIN(event_date), plus `date + 1` integer-arithmetic trap.

## Aggregation: group-by / having on a key (1/1 clean)
- ✅ [LC 570: Managers with at Least 5 Direct Reports](../areas/sql/lc-0570-managers-with-at-least-5-direct-reports.md) — self-join on managerId, HAVING COUNT ≥ 5; first attempt grouped by name instead of id (non-unique names merge entities), self-corrected fast.

## Reshaping: UNION ALL unpivot + aggregate (1/1 clean)
- ✅ [LC 602: Friend Requests II — Who Has the Most Friends](../areas/sql/lc-0602-friend-requests-ii-most-friends.md) — stack requester/accepter columns with UNION ALL, GROUP BY, top-1; trap: plain UNION dedupes and breaks the count.

## Classification: CASE + membership subquery (0/1 clean)
- ⚠️ [LC 608: Tree Node](../areas/sql/lc-0608-tree-node.md) — label nodes Root/Inner/Leaf via CASE with `id IN (SELECT p_id)`; needed hints for the CASE-plus-subquery shape; trap: `NOT IN` against a NULL-bearing column classifies nothing.

## Aggregation: duplicate vs unique classification (0/1 clean)
- ⚠️ [LC 585: Investments in 2016](../areas/sql/lc-0585-investments-in-2016.md) — HAVING COUNT > 1 / = 1 to build duplicated- and unique-value sets, tuple `(lat, lon) IN` membership; solved unassisted but only one day after studying the solution — needs a cold re-solve.
