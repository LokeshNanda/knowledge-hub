---
title: "LC 550: Game Play Analysis IV — PySpark"
area: pyspark
tags: [pyspark, window-functions, date-add, conditional-count-distinct, first-event-anchor, difficulty-medium]
source: "https://leetcode.com/problems/game-play-analysis-iv/"
created: 2026-07-23
updated: 2026-07-23
status: seed
---

# LC 550: Game Play Analysis IV — PySpark

**SQL companion:** [LC 550: Game Play Analysis IV](../sql/lc-0550-game-play-analysis-iv.md)

## Problem recap
Fraction of players (2 decimals) who logged in again exactly one day after their first login.

## SQL → DataFrame mapping

| SQL construct | PySpark equivalent |
|---|---|
| `MIN(event_date) OVER (PARTITION BY player_id)` | `F.min("event_date").over(Window.partitionBy("player_id"))` |
| `DATE_ADD(first_login, INTERVAL 1 DAY)` | `F.date_add("first_login", 1)` |
| `COUNT(DISTINCT CASE WHEN ... THEN player_id END)` | `F.countDistinct(F.when(cond, F.col("player_id")))` |
| `ROUND(x / y, 2)` | `F.round(x / y, 2)` |

## Solution
```python
from pyspark.sql import Window, functions as F

flagged = activity.withColumn(
    "first_login",
    F.min("event_date").over(Window.partitionBy("player_id")),
)

result = flagged.agg(
    F.round(
        F.countDistinct(
            F.when(
                F.col("event_date") == F.date_add("first_login", 1),
                F.col("player_id"),
            )
        )
        / F.countDistinct("player_id"),
        2,
    ).alias("fraction")
)
```

Join alternative (mirrors the SQL note's canonical answer): pre-aggregate `groupBy("player_id").agg(F.min("event_date").alias("first_login"))`, inner-join back to `activity` on `player_id` and `event_date == F.date_add("first_login", 1)`, then divide the matched count by `activity.select("player_id").distinct().count()`.

## PySpark-specific gotchas
- The SQL note's `date + 1` integer-arithmetic trap has no direct PySpark analogue, but stay explicit anyway: `F.date_add(col, 1)` is the unambiguous form, and it keeps the column a proper `date`.
- `F.when(cond, value)` **without** `.otherwise()` yields `NULL` for non-matching rows, and `countDistinct` skips NULLs — that pairing is exactly SQL's conditional `COUNT(DISTINCT CASE ...)`.
- The single `agg` over the whole DataFrame collapses to one row; no `groupBy` needed for a global aggregate.

## Similar problems in vault
- [LC 1070: Product Sales Analysis III — PySpark](./lc-1070-product-sales-analysis-iii.md) — same min-anchor idiom, but the anchor filters full rows via a two-key join instead of feeding a next-day check.
- [LC 626: Exchange Seats — PySpark](./lc-0626-exchange-seats.md) — its window variant uses the `lead`/`lag` machinery that was the wrong tool here.
