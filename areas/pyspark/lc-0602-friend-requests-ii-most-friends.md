---
title: "LC 602: Friend Requests II — Who Has the Most Friends — PySpark"
area: pyspark
tags: [pyspark, union, unpivot, groupby-agg, top-n, difficulty-medium]
source: "https://leetcode.com/problems/friend-requests-ii-who-has-the-most-friends/"
created: 2026-07-23
updated: 2026-07-23
status: seed
---

# LC 602: Friend Requests II — Who Has the Most Friends — PySpark

**SQL companion:** [LC 602: Friend Requests II — Who Has the Most Friends](../sql/lc-0602-friend-requests-ii-most-friends.md)

## Problem recap
Stack both sides of a mutual-friendship edge list and return the id appearing most often, with its count.

## SQL → DataFrame mapping

| SQL construct | PySpark equivalent |
|---|---|
| `SELECT a AS user ... UNION ALL SELECT b AS user ...` | `df.select(F.col("a").alias("id")).union(df.select(F.col("b").alias("id")))` |
| `GROUP BY user` + `COUNT(*)` | `.groupBy("id").agg(F.count("*").alias("num"))` |
| `ORDER BY count DESC LIMIT 1` | `.orderBy(F.desc("num")).limit(1)` |

## Solution
```python
from pyspark.sql import functions as F

edges = (
    request_accepted.select(F.col("requester_id").alias("id"))
    .union(request_accepted.select(F.col("accepter_id").alias("id")))
)

result = (
    edges.groupBy("id")
    .agg(F.count("*").alias("num"))
    .orderBy(F.desc("num"))
    .limit(1)
)
```

Ties variant (report everyone with the max): replace `orderBy().limit(1)` with `F.rank().over(Window.orderBy(F.desc("num")))` and `.filter("rk = 1")` — same `RANK` reasoning as the SQL note.

## PySpark-specific gotchas
- **`df.union()` is SQL's `UNION ALL`, not `UNION`.** The SQL trap runs in reverse here: SQL's default dedupes and breaks the count, while PySpark's default keeps duplicates and is exactly what aggregation-stacking needs. To get SQL-`UNION` semantics you'd have to add `.distinct()` explicitly.
- `union` matches columns **by position**, not name — fine here (single aliased column), but on wider frames `unionByName` is the safe spelling.
- `user` needed backticks as a column name in some SQL dialects; in PySpark any alias is fine, but `id` keeps the output schema matching the expected answer.

## Similar problems in vault
- [LC 570: Managers with at Least 5 Direct Reports — PySpark](./lc-0570-managers-with-at-least-5-direct-reports.md) — same per-entity `groupBy` count, no unpivot needed since the entity lives in one column.
- [LC 1158: Market Analysis I — PySpark](./lc-1158-market-analysis-i.md) — per-entity count where zero-count entities must survive, so the count rides on a left join.
