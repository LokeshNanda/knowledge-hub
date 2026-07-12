# SQL — map of content

Organized by pattern. ✅ = clean unaided solve, ⚠️ = struggled / needed help.
Tally per pattern: clean / total.

## Aggregation: first-event anchor (0/1 clean)
- ⚠️ [LC 550: Game Play Analysis IV](../areas/sql/lc-0550-game-play-analysis-iv.md) — day-after-first-login retention; used LEAD over any adjacent pair instead of anchoring to MIN(event_date), plus `date + 1` integer-arithmetic trap.

## Aggregation: group-by / having on a key (1/1 clean)
- ✅ [LC 570: Managers with at Least 5 Direct Reports](../areas/sql/lc-0570-managers-with-at-least-5-direct-reports.md) — self-join on managerId, HAVING COUNT ≥ 5; first attempt grouped by name instead of id (non-unique names merge entities), self-corrected fast.
