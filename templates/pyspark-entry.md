---
title: "LC {number}: {Problem Name} — PySpark"
area: pyspark
tags: [pyspark, api-concept-tags, difficulty-easy|medium|hard]
source: "https://leetcode.com/problems/..."
created:
updated:
status: seed
---

# LC {number}: {Problem Name} — PySpark

**SQL companion:** [LC {number}: {Problem Name}](../sql/lc-{number}-{name}.md)

## Problem recap
One line only — the full problem statement, pattern analysis, and solve review live in the SQL companion. Don't duplicate them.

## SQL → DataFrame mapping
How each construct of the SQL solution translates. Table preferred:

| SQL construct | PySpark equivalent |
|---|---|
| `GROUP BY x HAVING cond` | `.groupBy("x").agg(...).filter(cond)` |

## Solution
```python
# assumes: from pyspark.sql import functions as F
# (and from pyspark.sql import Window when windows are used)
```

## PySpark-specific gotchas
Where the DataFrame API behaves differently from SQL for *this* problem — null semantics, `union` vs `UNION`, no `IN`/`EXISTS` subqueries, driver-side scalars, unpartitioned windows, duplicate column names after joins, etc.

## Similar problems in vault
- [example](./lc-xxxx-example.md)
