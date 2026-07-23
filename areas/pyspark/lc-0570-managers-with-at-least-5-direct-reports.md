---
title: "LC 570: Managers with at Least 5 Direct Reports — PySpark"
area: pyspark
tags: [pyspark, groupby-agg, filter-as-having, semi-join, difficulty-medium]
source: "https://leetcode.com/problems/managers-with-at-least-5-direct-reports/"
created: 2026-07-23
updated: 2026-07-23
status: seed
---

# LC 570: Managers with at Least 5 Direct Reports — PySpark

**SQL companion:** [LC 570: Managers with at Least 5 Direct Reports](../sql/lc-0570-managers-with-at-least-5-direct-reports.md)

## Problem recap
From a self-referencing `Employee(id, name, department, managerId)` table, return names of managers with ≥ 5 direct reports.

## SQL → DataFrame mapping

| SQL construct | PySpark equivalent |
|---|---|
| `GROUP BY managerId HAVING COUNT(*) >= 5` | `.groupBy("managerId").agg(F.count("*").alias("reports")).filter("reports >= 5")` |
| `WHERE id IN (subquery)` | `.join(subquery_df, on=..., how="left_semi")` |

## Solution
```python
from pyspark.sql import functions as F

managers = (
    employee.groupBy("managerId")
    .agg(F.count("*").alias("reports"))
    .filter(F.col("reports") >= 5)
)

result = employee.join(
    managers, employee["id"] == managers["managerId"], "left_semi"
).select("name")
```

## PySpark-specific gotchas
- There is no `HAVING` in the DataFrame API — it's just a `.filter()` *after* `.agg()`. Position in the chain is what distinguishes WHERE (before) from HAVING (after).
- `left_semi` is the DataFrame spelling of `WHERE id IN (...)`: it keeps left rows with a match and never duplicates them or adds right-side columns. Using an inner join instead works here only because `managerId` groups are unique — semi-join is the habit that stays correct.
- The SQL note's group-by-key lesson carries over unchanged: aggregate on `managerId` (the key), never on `name`.
- `groupBy` puts NULL `managerId` values in their own group (same as SQL); the semi-join on `id == managerId` drops it naturally.

## Similar problems in vault
- [LC 1045: Customers Who Bought All Products — PySpark](./lc-1045-customers-who-bought-all-products.md) — same `groupBy` + post-agg `filter` skeleton, comparing against a set size instead of a threshold.
- [LC 608: Tree Node — PySpark](./lc-0608-tree-node.md) — same self-referencing key; membership there feeds a `when()` label instead of a semi-join filter.
