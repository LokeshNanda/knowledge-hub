---
title: "LC 1045: Customers Who Bought All Products — PySpark"
area: pyspark
tags: [pyspark, relational-division, count-distinct, groupby-agg, driver-side-scalar, difficulty-medium]
source: "https://leetcode.com/problems/customers-who-bought-all-products/"
created: 2026-07-23
updated: 2026-07-23
status: seed
---

# LC 1045: Customers Who Bought All Products — PySpark

**SQL companion:** [LC 1045: Customers Who Bought All Products](../sql/lc-1045-customers-who-bought-all-products.md)

## Problem recap
Return customers whose distinct purchased products cover the entire `Product` table (relational division).

## SQL → DataFrame mapping

| SQL construct | PySpark equivalent |
|---|---|
| `GROUP BY customer_id` | `.groupBy("customer_id")` |
| `COUNT(DISTINCT product_key)` | `F.countDistinct("product_key")` |
| `HAVING cnt = (SELECT COUNT(*) FROM Product)` | `.filter()` after `.agg()`, against a driver-side `product.count()` |

## Solution
```python
from pyspark.sql import functions as F

total_products = product.count()  # scalar subquery -> driver-side action

result = (
    customer.groupBy("customer_id")
    .agg(F.countDistinct("product_key").alias("cnt"))
    .filter(F.col("cnt") == total_products)
    .select("customer_id")
)
```

## PySpark-specific gotchas
- `F.countDistinct` is the load-bearing call, same as SQL's `DISTINCT`: `F.count` would let duplicate purchases fake completeness. (Approximation exists as `F.approx_count_distinct` — never for an exact-equality test like this.)
- The set-size comparison uses a **driver-side scalar** (`product.count()`); to stay fully lazy, cross-join a 1-row `product.agg(F.count("*"))` frame instead and compare columns.
- HAVING = `.filter()` placed after `.agg()`; the SQL attempt's redundant outer `SELECT` wrapper has no analogue — method chaining makes the "derived table" invisible.

## Similar problems in vault
- [LC 570: Managers with at Least 5 Direct Reports — PySpark](./lc-0570-managers-with-at-least-5-direct-reports.md) — same `groupBy` + post-agg `filter` skeleton, thresholding instead of matching a set size.
- [LC 585: Investments in 2016 — PySpark](./lc-0585-investments-in-2016.md) — group counts used to classify duplicated vs unique values, via windows.
