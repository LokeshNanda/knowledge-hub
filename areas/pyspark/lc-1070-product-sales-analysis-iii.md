---
title: "LC 1070: Product Sales Analysis III — PySpark"
area: pyspark
tags: [pyspark, first-event-anchor, two-key-join, rank-vs-row-number, window-functions, difficulty-medium]
source: "https://leetcode.com/problems/product-sales-analysis-iii/"
created: 2026-07-23
updated: 2026-07-23
status: seed
---

# LC 1070: Product Sales Analysis III — PySpark

**SQL companion:** [LC 1070: Product Sales Analysis III](../sql/lc-1070-product-sales-analysis-iii.md)

## Problem recap
Return all sale rows that happened in each product's first year of sales (ties within the first year all survive).

## SQL → DataFrame mapping

| SQL construct | PySpark equivalent |
|---|---|
| `GROUP BY product_id` + `MIN(year)` | `.groupBy("product_id").agg(F.min("year").alias("first_year"))` |
| `(product_id, year) IN (subquery)` | inner join on **both** keys |
| `RANK() OVER (PARTITION BY ... ORDER BY year)` | `F.rank().over(Window.partitionBy("product_id").orderBy("year"))` |

## Solution
```python
from pyspark.sql import functions as F

firsts = sales.groupBy("product_id").agg(F.min("year").alias("first_year"))

result = sales.join(
    firsts,
    (sales["product_id"] == firsts["product_id"])
    & (sales["year"] == firsts["first_year"]),
    "inner",
).select(sales["product_id"], F.col("first_year"), "quantity", "price")
```

Window alternative:

```python
from pyspark.sql import Window, functions as F

w = Window.partitionBy("product_id").orderBy("year")
result = (
    sales.withColumn("rk", F.rank().over(w))
    .filter(F.col("rk") == 1)
    .select("product_id", F.col("year").alias("first_year"), "quantity", "price")
)
```

## PySpark-specific gotchas
- No tuple `IN` in the DataFrame API — the semi-join on `(product_id, year)` becomes an inner join on both keys. Joining on `year` alone reproduces the SQL note's leak: products borrowing each other's first year.
- After a join on differently-named frames, `product_id` exists **twice**; disambiguate with `sales["product_id"]` (or pre-alias the frames) or `.select` throws an ambiguous-reference error. Aliasing `MIN(year)` to `first_year` on the aggregate side sidesteps half the collisions and directly provides the output column.
- The `RANK`-not-`ROW_NUMBER` rule is identical in Spark: `F.row_number()` would arbitrarily drop first-year ties; `F.rank()` keeps them.

## Similar problems in vault
- [LC 550: Game Play Analysis IV — PySpark](./lc-0550-game-play-analysis-iv.md) — same min-anchor idiom feeding a next-day check instead of a row filter.
- [LC 585: Investments in 2016 — PySpark](./lc-0585-investments-in-2016.md) — the other tuple-`IN` translation (multi-column window partition there, multi-key join here).
