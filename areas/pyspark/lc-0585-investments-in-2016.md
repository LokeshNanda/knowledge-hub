---
title: "LC 585: Investments in 2016 — PySpark"
area: pyspark
tags: [pyspark, window-functions, partitioned-count, duplicate-detection, difficulty-medium]
source: "https://leetcode.com/problems/investments-in-2016/"
created: 2026-07-23
updated: 2026-07-23
status: seed
---

# LC 585: Investments in 2016 — PySpark

**SQL companion:** [LC 585: Investments in 2016](../sql/lc-0585-investments-in-2016.md)

## Problem recap
Sum `tiv_2016` (2 decimals) over policyholders whose `tiv_2015` is shared with someone else but whose `(lat, lon)` is unique.

## SQL → DataFrame mapping
The SQL note's *window* variant is the natural DataFrame shape — the `IN`-subquery version has no direct equivalent because the DataFrame API lacks `IN (subquery)`.

| SQL construct | PySpark equivalent |
|---|---|
| `COUNT(*) OVER (PARTITION BY tiv_2015)` | `F.count("*").over(Window.partitionBy("tiv_2015"))` |
| `COUNT(*) OVER (PARTITION BY lat, lon)` | `F.count("*").over(Window.partitionBy("lat", "lon"))` |
| `(lat, lon) IN (subquery)` | multi-column `partitionBy` (or a multi-key join) |
| `ROUND(SUM(...), 2)` | `F.round(F.sum(...), 2)` |

## Solution
```python
from pyspark.sql import Window, functions as F

result = (
    insurance
    .withColumn("tiv_cnt", F.count("*").over(Window.partitionBy("tiv_2015")))
    .withColumn("loc_cnt", F.count("*").over(Window.partitionBy("lat", "lon")))
    .filter((F.col("tiv_cnt") > 1) & (F.col("loc_cnt") == 1))
    .agg(F.round(F.sum("tiv_2016"), 2).alias("tiv_2016"))
)
```

## PySpark-specific gotchas
- No row-tuple `IN`: SQL's `(lat, lon) IN (...)` becomes either `Window.partitionBy("lat", "lon")` (as here) or a join on both keys. Same composite-key discipline, different spelling — and the SQL note's `CONCAT(lat, lon)` warning applies equally to concatenating columns to fake a composite key in Spark.
- Combine filter conditions with `&`/`|` and parenthesize each comparison — Python's `and`/`or` on Columns raises `PySparkValueError` (truth value of a Column is ambiguous).
- A `partitionBy` window with no `orderBy` computes over the *whole* partition — exactly SQL's unframed `COUNT(*) OVER (PARTITION BY ...)`. Adding `orderBy` would silently switch to a running count (default frame = unbounded preceding → current row).

## Similar problems in vault
- [LC 570: Managers with at Least 5 Direct Reports — PySpark](./lc-0570-managers-with-at-least-5-direct-reports.md) — the same classify-by-group-count job done with `groupBy` + semi-join instead of windows.
- [LC 1070: Product Sales Analysis III — PySpark](./lc-1070-product-sales-analysis-iii.md) — the other place a SQL tuple-`IN` turns into a multi-key construct.
