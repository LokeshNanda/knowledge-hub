---
title: "LC 602: Friend Requests II — Who Has the Most Friends"
area: sql
tags: [sql, union-all, unpivot, group-by, top-n, difficulty-medium]
source: "https://leetcode.com/problems/friend-requests-ii-who-has-the-most-friends/"
created: 2026-07-13
updated: 2026-07-13
status: seed
solved_unaided: yes
time_taken_min:
---

# LC 602: Friend Requests II — Who Has the Most Friends

**Problem:** `RequestAccepted(requester_id, accepter_id, accept_date)` records accepted friend requests. Friendship is mutual — one accepted row makes *both* people a friend of the other. Return the id with the most friends and that count (the test data guarantees a unique answer).

## Pattern
**Unpivot a bidirectional edge list with `UNION ALL`, then aggregate per node.** Recognize it when an entity appears in *either of two columns* of the same table and the question asks "per entity, how many rows involve it". Stacking both columns into one turns a two-sided relationship into a plain `GROUP BY` count — no join, no `OR` in a where clause.

## My approach
Stack requester and accepter ids into a single `user` column, count appearances per user, take the top row:

```sql
select f.user as id, count(*) as num
from (
    select requester_id as user from RequestAccepted
    union all
    select accepter_id as user from RequestAccepted
) f
group by user
order by count(*) desc
limit 1;
```

Clean solve; this is essentially the canonical solution.

## Optimal approach
Same as mine — `UNION ALL` + `GROUP BY` + `ORDER BY ... LIMIT 1` is the accepted answer. The follow-up variant (report *all* people tied for the most friends) swaps `LIMIT 1` for a window rank:

```sql
SELECT id, num
FROM (
    SELECT user AS id, COUNT(*) AS num,
           RANK() OVER (ORDER BY COUNT(*) DESC) AS rk
    FROM (
        SELECT requester_id AS user FROM RequestAccepted
        UNION ALL
        SELECT accepter_id AS user FROM RequestAccepted
    ) f
    GROUP BY user
) ranked
WHERE rk = 1;
```

## Complexity
- Time: O(n) — one pass to stack 2n rows, hash aggregate per user; the sort is over distinct users only.
- Space: O(d) for the per-user counts, d = distinct people.

## The mistake to remember
Solved cleanly, but the trap the pattern hides: **`UNION` instead of `UNION ALL` silently breaks the count.** `UNION` deduplicates the stacked rows, so a user's repeated appearances collapse and every count is wrong. When stacking rows *for aggregation*, it is almost always `UNION ALL`.

## Similar problems in vault
- [LC 570: Managers with at Least 5 Direct Reports](./lc-0570-managers-with-at-least-5-direct-reports.md) — also a per-entity appearance count via `GROUP BY` on an id column; there the entity sits in one foreign-key column, here it must first be unpivoted out of two.
- [LC 1045: Customers Who Bought All Products](./lc-1045-customers-who-bought-all-products.md) — also a per-entity aggregate, but testing whether the distinct count covers a whole external set (relational division) rather than ranking for the max.
- [LC 1158: Market Analysis I](./lc-1158-market-analysis-i.md) — another per-entity `COUNT(*)`, but every entity must appear even with zero matches, so the count rides on a LEFT JOIN instead of a plain GROUP BY.

## Solution
```sql
select f.user as id, count(*) as num
from (
    select requester_id as user from RequestAccepted
    union all
    select accepter_id as user from RequestAccepted
) f
group by user
order by count(*) desc
limit 1;
```
