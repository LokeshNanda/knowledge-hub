---
title: "LC 1045: Customers Who Bought All Products"
area: sql
tags: [sql, relational-division, group-by-having, count-distinct, difficulty-medium]
source: "https://leetcode.com/problems/customers-who-bought-all-products/"
created: 2026-07-16
updated: 2026-07-16
status: seed
solved_unaided: yes
time_taken_min:
---

# LC 1045: Customers Who Bought All Products

**Problem:** Given `Customer(customer_id, product_key)` (with possible duplicate rows) and `Product(product_key)` listing every product, return the ids of customers who bought *every* product in `Product`.

## Pattern
**Relational division — "find entities related to ALL members of a set".** Recognize it from words like "bought *all* products", "attended *every* session", "passed *each* test". SQL has no division operator, so the standard trick is a count comparison: per entity, count its *distinct* matches against the set, and keep entities where that count equals the size of the whole set:

```sql
GROUP BY entity
HAVING COUNT(DISTINCT set_key) = (SELECT COUNT(*) FROM full_set)
```

`DISTINCT` is what makes it correct — duplicate purchases must not inflate the tally toward the target.

## My approach
Grouped `Customer` by `customer_id`, counted distinct products per customer, and kept groups whose distinct count equals the total product count:

```sql
select a.customer_id from (
select customer_id, count(distinct product_key) as product_count
from Customer
where product_key in (select product_key from Product)
group by customer_id
having count(distinct product_key) = (select count(distinct product_key) from Product)
) a
```

Correct on first submission. Two bits of slack worth noticing:

- The `WHERE product_key IN (SELECT ... FROM Product)` filter is defensive but redundant here — `Customer.product_key` is a foreign key into `Product`, so no stray keys can exist. (It *would* matter if the fact table could contain keys outside the reference set — then unmatched keys would inflate the distinct count.)
- The outer `select a.customer_id from (...) a` wrapper adds nothing — same derived-table habit as in [LC 570](./lc-0570-managers-with-at-least-5-direct-reports.md); the inner query can be the whole answer.

## Optimal approach
The bare form of the division-by-counting idiom:

```sql
SELECT customer_id
FROM Customer
GROUP BY customer_id
HAVING COUNT(DISTINCT product_key) = (SELECT COUNT(product_key) FROM Product);
```

`Product.product_key` is the primary key, so plain `COUNT` suffices on that side; the `DISTINCT` on the `Customer` side is non-negotiable because a customer can buy the same product twice.

## Complexity
- Time: O(n) hash aggregate over `Customer` rows; the scalar subquery over `Product` is computed once.
- Space: O(c · p) worst case for the distinct-count state (c = customers, p = products).

## The mistake to remember
Solved cleanly. The rule the problem encodes: **"bought all X" = distinct-count per entity equals the size of X** — and the `DISTINCT` is the load-bearing keyword, since duplicate facts would otherwise fake completeness.

## Similar problems in vault
- [LC 570: Managers with at Least 5 Direct Reports](./lc-0570-managers-with-at-least-5-direct-reports.md) — same GROUP BY / HAVING-on-a-count skeleton, but thresholding a child count (≥ N) instead of matching a set size exactly.
- [LC 585: Investments in 2016](./lc-0585-investments-in-2016.md) — HAVING COUNT used to classify values as duplicated vs unique; here the count is compared against an external set's cardinality instead.
- [LC 602: Friend Requests II — Who Has the Most Friends](./lc-0602-friend-requests-ii-most-friends.md) — also a per-entity aggregate, but ranking for the max rather than testing set coverage.

## Solution
```sql
SELECT customer_id
FROM Customer
GROUP BY customer_id
HAVING COUNT(DISTINCT product_key) = (SELECT COUNT(product_key) FROM Product);
```
