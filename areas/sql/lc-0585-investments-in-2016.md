---
title: "LC 585: Investments in 2016"
area: sql
tags: [sql, group-by-having, duplicate-detection, tuple-comparison, difficulty-medium]
source: "https://leetcode.com/problems/investments-in-2016/"
created: 2026-07-13
updated: 2026-07-13
status: seed
solved_unaided: partially
time_taken_min:
---

# LC 585: Investments in 2016

**Problem:** From `Insurance(pid, tiv_2015, tiv_2016, lat, lon)`, report the sum of `tiv_2016` (rounded to 2 decimals) over policyholders who (a) share their `tiv_2015` value with at least one other policyholder, and (b) sit at a location `(lat, lon)` no other policyholder occupies.

## Pattern
**GROUP BY / HAVING as a set classifier: build the set of duplicated values (`HAVING COUNT(*) > 1`) and the set of unique values (`HAVING COUNT(*) = 1`), then filter rows by membership with `IN`.** Recognize it when the filter condition is about *how many other rows* share a value — "same as at least one other" or "not the same as any other" — rather than about the value itself. Each condition becomes one grouped subquery.

## My approach
Two membership tests, one per condition. `tiv_2015` must fall in the duplicated set; `(lat, lon)` must fall in the singleton set, compared as a row tuple:

```sql
select ROUND(SUM(tiv_2016), 2) as tiv_2016
from Insurance
where tiv_2015 in (
    select tiv_2015 from Insurance
    group by tiv_2015
    having count(1) > 1
)
and (lat, lon) in (
    select lat, lon from Insurance
    group by lat, lon
    having count(1) = 1
);
```

Solved without assistance — but I had studied the solution the day before, so this was a successful next-day recall, not a cold solve. Worth a cold re-attempt in a few weeks before counting the pattern as owned.

## Optimal approach
Same asymptotic cost, but window functions do it in a single scan instead of two grouped subqueries plus semijoins: count peers per `tiv_2015` and per `(lat, lon)` partition, then filter.

```sql
SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM (
    SELECT tiv_2016,
           COUNT(*) OVER (PARTITION BY tiv_2015)  AS tiv_cnt,
           COUNT(*) OVER (PARTITION BY lat, lon)  AS loc_cnt
    FROM Insurance
) t
WHERE tiv_cnt > 1 AND loc_cnt = 1;
```

The `IN`-subquery version is arguably more readable and performs fine here; the window version generalizes better when more per-group conditions pile up.

## Complexity
- Time: O(n) — hash aggregates over `tiv_2015` and `(lat, lon)`, then a semijoin per condition (or one windowed scan).
- Space: O(d) for the distinct-value sets.

## The mistake to remember
Nothing cost time this round, but the trap to avoid: **don't compare composite keys via `CONCAT(lat, lon)`** — string concatenation collides (`12.3 + 4.5` vs `12.34 + .5`). MySQL's row constructor `(lat, lon) IN (...)` compares the tuple properly; grouping by both columns in a window partition does too.

## Similar problems in vault
- [LC 570: Managers with at Least 5 Direct Reports](./lc-0570-managers-with-at-least-5-direct-reports.md) — same GROUP BY / HAVING membership-set machinery, there used to find keys with ≥ N children rather than to split duplicated vs unique values.
- [LC 608: Tree Node](./lc-0608-tree-node.md) — same subquery-membership machinery, used inside a `CASE` to label rows instead of inside `WHERE` to filter them.
- [LC 1045: Customers Who Bought All Products](./lc-1045-customers-who-bought-all-products.md) — HAVING COUNT again, but compared against an external set's cardinality to test "bought all" (relational division) instead of classifying duplicated vs unique.
- [LC 1070: Product Sales Analysis III](./lc-1070-product-sales-analysis-iii.md) — same tuple `(a, b) IN (subquery)` row-constructor trick, there matching each product's `(product_id, MIN(year))` anchor instead of detecting duplicate locations.

## Solution
```sql
select ROUND(SUM(tiv_2016), 2) as tiv_2016
from Insurance
where tiv_2015 in (
    select tiv_2015 from Insurance
    group by tiv_2015
    having count(1) > 1
)
and (lat, lon) in (
    select lat, lon from Insurance
    group by lat, lon
    having count(1) = 1
);
```
