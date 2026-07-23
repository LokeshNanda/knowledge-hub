---
title: "LC 1158: Market Analysis I"
area: sql
tags: [sql, left-join, conditional-aggregation, zero-preserving-count, coalesce, derived-table, difficulty-medium]
source: "https://leetcode.com/problems/market-analysis-i/"
created: 2026-07-23
updated: 2026-07-23
status: seed
solved_unaided: yes
time_taken_min:
---

# LC 1158: Market Analysis I

**Problem:** Given `Users(user_id, join_date, favorite_brand)` and `Orders(order_id, order_date, item_id, buyer_id, seller_id)`, return *every* user's `user_id` (as `buyer_id`), `join_date`, and how many orders they placed as a buyer in 2019 — including users with zero such orders.

## Pattern
**Zero-preserving count: LEFT JOIN from the entity table, with the filter on the joined side kept out of `WHERE`.** Recognize it from "for *each* user/product/store, count X" where entities with no X must still appear with 0. Two equivalent shapes:

1. LEFT JOIN the fact table with the filter *in the `ON` clause*, then `COUNT(fact_column)`:

```sql
FROM Users u
LEFT JOIN Orders o
  ON u.user_id = o.buyer_id AND YEAR(o.order_date) = 2019
GROUP BY u.user_id
```

2. Pre-aggregate the facts in a derived table, LEFT JOIN it, and `COALESCE(count, 0)`.

The trap this pattern encodes: putting the fact-side filter in `WHERE` after a LEFT JOIN silently turns it into an INNER JOIN — unmatched rows have `NULL` in that column, `NULL` fails every comparison, and the zero-count entities vanish.

## My approach
Shape 2 — aggregate 2019 orders per buyer in a derived table, LEFT JOIN it onto `Users`, and default missing counts to 0:

```sql
select u.user_id as buyer_id, u.join_date, COALESCE(o2.orders_in_2019,0) as orders_in_2019
from Users u
left join (
select buyer_id, count(*) as orders_in_2019
from Orders
where YEAR(order_date) = '2019'
group by buyer_id
) o2
on u.user_id = o2.buyer_id
```

Clean solve, and the derived-table shape sidesteps the ON-vs-WHERE trap entirely — inside the subquery `WHERE` is exactly where the filter belongs. Two nits:

- `YEAR(order_date) = '2019'` compares a number to a string; MySQL coerces it silently, but write the literal as a number.
- `YEAR()` wrapped around a column is non-sargable — an index on `order_date` can't be used. The range form `order_date >= '2019-01-01' AND order_date < '2020-01-01'` filters identically and stays index-friendly.

## Optimal approach
Shape 1 is the textbook one-pass answer:

```sql
SELECT u.user_id AS buyer_id, u.join_date, COUNT(o.order_id) AS orders_in_2019
FROM Users u
LEFT JOIN Orders o
  ON u.user_id = o.buyer_id
  AND o.order_date BETWEEN '2019-01-01' AND '2019-12-31'
GROUP BY u.user_id, u.join_date;
```

Note `COUNT(o.order_id)`, not `COUNT(*)`: counting the nullable joined column makes unmatched users count 0 with no `COALESCE` needed, because `COUNT(col)` skips NULLs. Neither shape strictly beats the other — the pre-aggregate version can even win on large data by shrinking `Orders` before the join.

## Complexity
- Time: O(u + o) hash aggregate over 2019 orders plus hash join against users.
- Space: O(b) for per-buyer counts (b = distinct 2019 buyers).

## The mistake to remember
Solved cleanly. The rule the problem encodes: **after a LEFT JOIN, any filter on the right table belongs in `ON` (or in a pre-aggregated derived table) — in `WHERE` it deletes the very zero-count rows the LEFT JOIN existed to keep.** Bonus rule: `COUNT(nullable_col)` counts matches only; `COUNT(*)` counts rows, NULL-padded or not.

## Similar problems in vault
- [LC 570: Managers with at Least 5 Direct Reports](./lc-0570-managers-with-at-least-5-direct-reports.md) — also a per-entity order/child count via join + GROUP BY; there zero-count entities are *meant* to drop, so a plain join suffices.
- [LC 602: Friend Requests II — Who Has the Most Friends](./lc-0602-friend-requests-ii-most-friends.md) — another per-entity `COUNT(*)`, ranking for the max; zero-friend users are irrelevant so no LEFT JOIN gymnastics needed.
- [LC 550: Game Play Analysis IV](./lc-0550-game-play-analysis-iv.md) — same "aggregate facts by date condition per entity" family, and the same non-sargable date-function smell (`date + 1` there, `YEAR()` here).

## Solution
```sql
select u.user_id as buyer_id, u.join_date, COALESCE(o2.orders_in_2019, 0) as orders_in_2019
from Users u
left join (
  select buyer_id, count(*) as orders_in_2019
  from Orders
  where order_date >= '2019-01-01' and order_date < '2020-01-01'
  group by buyer_id
) o2
on u.user_id = o2.buyer_id;
```
