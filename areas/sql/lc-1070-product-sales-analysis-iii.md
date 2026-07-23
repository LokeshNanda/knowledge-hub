---
title: "LC 1070: Product Sales Analysis III"
area: sql
tags: [sql, first-event-anchor, group-by-min, tuple-in, semi-join, difficulty-medium]
source: "https://leetcode.com/problems/product-sales-analysis-iii/"
created: 2026-07-23
updated: 2026-07-23
status: seed
solved_unaided: yes
time_taken_min:
---

# LC 1070: Product Sales Analysis III

**PySpark companion:** [same problem in the DataFrame API](../pyspark/lc-1070-product-sales-analysis-iii.md)

**Problem:** Given `Sales(sale_id, product_id, year, quantity, price)`, return `product_id, first_year, quantity, price` for every sale that happened in the *first year* each product was sold. A product can have several sales rows in its first year — all of them must appear.

## Pattern
**First-event anchor via GROUP BY + MIN, filtered with a tuple `IN`.** Recognize it from "first year / first purchase / earliest order *per entity*" where you need the *whole row(s)* at that first event, not just the date. Aggregate to find each entity's anchor, then semi-join the fact table back against `(entity, anchor)` pairs:

```sql
WHERE (entity_id, event_time) IN (
  SELECT entity_id, MIN(event_time) FROM facts GROUP BY entity_id
)
```

The tuple comparison is what keeps entities from borrowing each other's anchor years — matching on year alone would leak rows from any product that happened to sell in another product's first year.

## My approach
Exactly the idiom above — group `Sales` by product, take `MIN(year)`, and keep rows whose `(product_id, year)` pair is in that set:

```sql
select product_id, year as first_year, quantity, price
from Sales
where (product_id, year) IN (
select product_id, min(year) as first_year
from Sales
group by product_id
)
```

Clean solve. One cosmetic nit: the `as first_year` alias inside the `IN` subquery does nothing — tuple membership matches by position, not name; the alias that matters is the one in the outer SELECT.

## Optimal approach
The tuple-`IN` semi-join *is* the canonical MySQL answer. The main alternative is a window function:

```sql
SELECT product_id, year AS first_year, quantity, price
FROM (
  SELECT s.*, RANK() OVER (PARTITION BY product_id ORDER BY year) AS rk
  FROM Sales s
) t
WHERE rk = 1;
```

It must be `RANK` (or `DENSE_RANK`), **not** `ROW_NUMBER` — several sales can share the first year, and `ROW_NUMBER` would arbitrarily keep one and drop the rest. Both approaches are O(n); the tuple-`IN` version reads more directly as "rows at each product's minimum year".

## Complexity
- Time: O(n) hash aggregate over `Sales` for the anchor set, then O(n) semi-join probe.
- Space: O(p) for the per-product minimum (p = products).

## The mistake to remember
Solved cleanly. The rules the problem encodes: **anchor per entity with GROUP BY + MIN, then match the fact table on the full `(entity, anchor)` tuple** — and if you reach for a window instead, first-event filters that must keep ties need `RANK`, never `ROW_NUMBER`.

## Similar problems in vault
- [LC 550: Game Play Analysis IV](./lc-0550-game-play-analysis-iv.md) — same first-event anchor (`MIN(event_date)` per player); there the anchor feeds a next-day existence check instead of a row filter.
- [LC 585: Investments in 2016](./lc-0585-investments-in-2016.md) — same tuple `(a, b) IN (subquery)` membership trick, used there for duplicate-location detection rather than an anchor match.

## Solution
```sql
select product_id, year as first_year, quantity, price
from Sales
where (product_id, year) IN (
  select product_id, min(year)
  from Sales
  group by product_id
);
```
