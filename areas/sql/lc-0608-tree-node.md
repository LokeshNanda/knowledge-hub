---
title: "LC 608: Tree Node"
area: sql
tags: [sql, case-when, conditional-classification, membership-subquery, self-reference, null-handling, difficulty-medium]
source: "https://leetcode.com/problems/tree-node/"
created: 2026-07-14
updated: 2026-07-14
status: seed
solved_unaided: partially
time_taken_min:
---

# LC 608: Tree Node

**Problem:** `Tree(id, p_id)` stores a tree as an adjacency list — each row is a node pointing at its parent. Label every node `Root` (no parent), `Inner` (has a parent *and* is a parent of someone), or `Leaf` (has a parent, is nobody's parent).

## Pattern
**Row classification with `CASE`, where one branch is a membership test against the same table.** Recognize it when every row must get exactly one label out of several mutually exclusive categories, and at least one category depends on *other rows* ("is this id anyone's parent?") rather than on the row's own columns. Each category becomes a `WHEN`; the relational condition becomes `id IN (SELECT p_id ...)` or an `EXISTS`.

## My approach
Needed hints to get there. Final query — `Root` first, then the parent-membership check, `Leaf` as the fallback:

```sql
select id,
    CASE
        WHEN p_id IS NULL then 'Root'
        WHEN id IN (select p_id from Tree) THEN 'Inner'
        ELSE 'Leaf'
    END AS type
from Tree
```

This is the canonical solution. The two ideas the hints supplied:
1. Three mutually exclusive labels → one `CASE` walked in order of cheapest/most-specific condition first.
2. "Is a parent" is not a column — it's membership of `id` in the set of `p_id` values, i.e. a subquery against the same table.

## Optimal approach
Same shape as mine. A correlated `EXISTS` is the common alternative and lets the optimizer stop at the first matching child instead of building the whole `p_id` set:

```sql
SELECT t.id,
       CASE
           WHEN t.p_id IS NULL THEN 'Root'
           WHEN EXISTS (SELECT 1 FROM Tree c WHERE c.p_id = t.id) THEN 'Inner'
           ELSE 'Leaf'
       END AS type
FROM Tree t;
```

Why `CASE` order matters: the root node is normally also somebody's parent, so if the `IN` branch were tested first, the root would be mislabeled `Inner`. `CASE` short-circuits top-down — put `Root` first.

Why the `NULL` doesn't bite *here* but would in reverse: the `p_id` column contains a `NULL` (the root's row). For a leaf, `id IN (…, NULL)` evaluates to `UNKNOWN`, not `FALSE` — but `CASE` treats `UNKNOWN` as "not matched" and falls through to `ELSE`, so the query is still correct. Flip it to `id NOT IN (SELECT p_id FROM Tree)` and everything breaks: `NOT IN` against a list containing `NULL` is `UNKNOWN` for *every* row, so no node would ever classify as `Leaf`. If you need the negative form, write `NOT IN (SELECT p_id FROM Tree WHERE p_id IS NOT NULL)` or `NOT EXISTS`.

## Complexity
- Time: O(n) — one scan of `Tree`, with a hash semijoin (or per-row `EXISTS` probe on an index) for the parent-set test.
- Space: O(n) for the materialized set of `p_id` values.

## The mistake to remember
**When a label depends on other rows, reach for a membership subquery (`IN` / `EXISTS`) inside the `CASE` — and order the `WHEN`s so the most specific condition wins first.** And any time that subquery's column can contain `NULL`, remember `NOT IN` + `NULL` returns `UNKNOWN` for every row; use `NOT EXISTS` or filter the `NULL`s out.

## Similar problems in vault
- [LC 570: Managers with at Least 5 Direct Reports](./lc-0570-managers-with-at-least-5-direct-reports.md) — same self-referencing parent key (`managerId` → `id` vs `p_id` → `id`); there the child side is aggregated per parent, here mere existence of a child decides a label.
- [LC 585: Investments in 2016](./lc-0585-investments-in-2016.md) — same "build a value set with a subquery, filter rows by `IN` membership" machinery, used in `WHERE` to filter rows rather than in `CASE` to label them.

## Solution
```sql
select id,
    CASE
        WHEN p_id IS NULL then 'Root'
        WHEN id IN (select p_id from Tree) THEN 'Inner'
        ELSE 'Leaf'
    END AS type
from Tree
```
