---
title: "LC 626: Exchange Seats — PySpark"
area: pyspark
tags: [pyspark, when-otherwise, parity, key-remapping, driver-side-scalar, lead-lag, difficulty-medium]
source: "https://leetcode.com/problems/exchange-seats/"
created: 2026-07-23
updated: 2026-07-23
status: seed
---

# LC 626: Exchange Seats — PySpark

**SQL companion:** [LC 626: Exchange Seats](../sql/lc-0626-exchange-seats.md)

## Problem recap
Swap every two consecutive students by id (1↔2, 3↔4, …); an odd last student stays put; return ordered by id.

## SQL → DataFrame mapping

| SQL construct | PySpark equivalent |
|---|---|
| parity `CASE` remapping `id` | `F.when(...).when(...).otherwise(...)` in `withColumn` |
| uncorrelated scalar `(SELECT COUNT(*) FROM Seat)` | driver-side action: `seat.count()`, embedded as a Python literal |
| `ORDER BY id` (on the new key) | `.orderBy("id")` after the remap |

## Solution
```python
from pyspark.sql import functions as F

total = seat.count()  # scalar subquery -> driver-side action

result = (
    seat.withColumn(
        "id",
        F.when((F.col("id") % 2 == 1) & (F.col("id") == total), F.col("id"))
        .when(F.col("id") % 2 == 1, F.col("id") + 1)
        .otherwise(F.col("id") - 1),
    )
    .orderBy("id")
)
```

Window alternative (keep ids, swap students — the SQL note's LEAD/LAG variant):

```python
from pyspark.sql import Window, functions as F

w = Window.orderBy("id")
result = seat.select(
    "id",
    F.coalesce(
        F.when(F.col("id") % 2 == 1, F.lead("student").over(w))
        .otherwise(F.lag("student").over(w)),
        F.col("student"),
    ).alias("student"),
)
```

## PySpark-specific gotchas
- SQL's uncorrelated scalar subquery becomes an **action** (`count()`): it triggers a job and pulls the value to the driver, and the plan bakes it in as a literal. Fine at LeetCode scale; on real pipelines prefer a cross-join with an aggregated 1-row frame if you must stay lazy.
- The remap-then-sort rule survives translation: without the final `.orderBy("id")` the swap "doesn't exist" — Spark makes this worse than MySQL because row order after any shuffle is explicitly undefined, so nothing ever passes by accident.
- `Window.orderBy("id")` with **no** `partitionBy` funnels the whole DataFrame through a single partition (Spark even warns). Acceptable for a puzzle, a scalability bug in production.
- The SQL attempt's leftover `GROUP BY id` reflex has no PySpark analogue — `groupBy` without `agg` doesn't even produce a DataFrame, so the API stops you from writing it.

## Similar problems in vault
- [LC 608: Tree Node — PySpark](./lc-0608-tree-node.md) — same `when()` chain machinery, assigning labels instead of remapping a key.
- [LC 550: Game Play Analysis IV — PySpark](./lc-0550-game-play-analysis-iv.md) — the problem where reflex `lead`/`lag` was the trap; here the window variant is legitimate.
