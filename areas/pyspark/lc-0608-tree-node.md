---
title: "LC 608: Tree Node — PySpark"
area: pyspark
tags: [pyspark, when-otherwise, join-as-membership, left-join-null-check, null-handling, difficulty-medium]
source: "https://leetcode.com/problems/tree-node/"
created: 2026-07-23
updated: 2026-07-23
status: seed
---

# LC 608: Tree Node — PySpark

**SQL companion:** [LC 608: Tree Node](../sql/lc-0608-tree-node.md)

## Problem recap
Label each node of an adjacency-list tree `Root` (no parent), `Inner` (parent and child of someone), or `Leaf`.

## SQL → DataFrame mapping

| SQL construct | PySpark equivalent |
|---|---|
| `CASE WHEN ... WHEN ... ELSE ... END` | `F.when(...).when(...).otherwise(...)` |
| `id IN (SELECT p_id FROM Tree)` inside the CASE | left join against distinct parent ids, then null-check the joined column |

## Solution
```python
from pyspark.sql import functions as F

parents = (
    tree.select(F.col("p_id").alias("parent_id"))
    .where(F.col("p_id").isNotNull())
    .distinct()
)

result = (
    tree.join(parents, tree["id"] == parents["parent_id"], "left")
    .select(
        "id",
        F.when(F.col("p_id").isNull(), "Root")
        .when(F.col("parent_id").isNotNull(), "Inner")
        .otherwise("Leaf")
        .alias("type"),
    )
)
```

## PySpark-specific gotchas
- The DataFrame API has no `IN (subquery)`/`EXISTS` **inside an expression** — a membership test that feeds a label must become a left join plus `isNotNull()` on the joined key. (`left_semi`/`left_anti` cover the WHERE-filter cases but discard the non-members, so they can't label.)
- `F.when` chains short-circuit top-down exactly like SQL `CASE`, so the same ordering rule applies: `Root` first, or the root (usually also a parent) gets labeled `Inner`.
- The SQL note's `NOT IN` + NULL landmine translates too: filtering the NULL out of `parents` before joining isn't optional hygiene here — joining on a NULL key never matches, but keeping the row would still waste a skewed null partition, and an `isin()` against a collected list containing `None` misbehaves the same way SQL's `NOT IN` does.
- `F.col("p_id")` vs the joined `parent_id`: after the join both frames' columns coexist; distinct names (via the `alias` on the parents side) avoid ambiguous-column errors.

## Similar problems in vault
- [LC 626: Exchange Seats — PySpark](./lc-0626-exchange-seats.md) — same `when()` chain machinery, remapping a sort key instead of assigning a label.
- [LC 570: Managers with at Least 5 Direct Reports — PySpark](./lc-0570-managers-with-at-least-5-direct-reports.md) — same self-referencing key, membership done as a pure filter (`left_semi`) since nothing needs labeling.
