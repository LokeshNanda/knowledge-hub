---
title: "LC 1158: Market Analysis I — PySpark"
area: pyspark
tags: [pyspark, left-join, pre-aggregate, coalesce-fillna, zero-preserving-count, difficulty-medium]
source: "https://leetcode.com/problems/market-analysis-i/"
created: 2026-07-23
updated: 2026-07-23
status: seed
---

# LC 1158: Market Analysis I — PySpark

**SQL companion:** [LC 1158: Market Analysis I](../sql/lc-1158-market-analysis-i.md)

## Problem recap
For every user, count their 2019 orders as a buyer — users with zero such orders must still appear with 0.

## SQL → DataFrame mapping

| SQL construct | PySpark equivalent |
|---|---|
| pre-aggregated derived table | a named intermediate DataFrame (`orders_2019`) |
| `LEFT JOIN ... ON` | `.join(..., "left")` |
| `COALESCE(cnt, 0)` | `F.coalesce(col, F.lit(0))` or `.fillna({"col": 0})` |
| sargable date range | plain string comparison on the date column |

## Solution
```python
from pyspark.sql import functions as F

orders_2019 = (
    orders.filter(
        (F.col("order_date") >= "2019-01-01") & (F.col("order_date") <= "2019-12-31")
    )
    .groupBy("buyer_id")
    .agg(F.count("*").alias("orders_in_2019"))
)

result = (
    users.join(orders_2019, users["user_id"] == orders_2019["buyer_id"], "left")
    .select(
        F.col("user_id").alias("buyer_id"),
        "join_date",
        F.coalesce("orders_in_2019", F.lit(0)).alias("orders_in_2019"),
    )
)
```

## PySpark-specific gotchas
- The SQL note's ON-vs-WHERE trap translates directly: a `.filter(F.col("order_date")...)` placed **after** the left join drops the NULL-padded zero-order users, silently turning it into an inner join. The pre-aggregate-then-left-join shape shown here is the natural DataFrame idiom and dodges it — filter the fact frame *before* joining.
- `F.count("*")` here counts rows of the already-filtered fact frame; the SQL alternative `COUNT(o.order_id)`-on-the-joined-frame trick works too (`F.count` skips NULLs), but pre-aggregation reads better in the API.
- `.fillna({"orders_in_2019": 0})` is the frame-level spelling of `COALESCE` — handy when several columns need defaults at once.
- Comparing a date column against ISO-format string literals is safe (Spark casts), and keeping the filter a range rather than `F.year(col) == 2019` preserves partition/predicate pushdown — the same sargability argument as in the SQL note.

## Similar problems in vault
- [LC 570: Managers with at Least 5 Direct Reports — PySpark](./lc-0570-managers-with-at-least-5-direct-reports.md) — per-entity count where zero-count entities are *meant* to drop, so no left join needed.
- [LC 602: Friend Requests II — PySpark](./lc-0602-friend-requests-ii-most-friends.md) — another per-entity count, fed by an unpivot instead of a join.
