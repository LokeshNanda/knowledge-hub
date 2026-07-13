---
title: "LC 570: Managers with at Least 5 Direct Reports"
area: sql
tags: [sql, self-join, group-by-having, group-by-key, difficulty-medium]
source: "https://leetcode.com/problems/managers-with-at-least-5-direct-reports/"
created: 2026-07-12
updated: 2026-07-12
status: seed
solved_unaided: yes
time_taken_min:
---

# LC 570: Managers with at Least 5 Direct Reports

**Problem:** From a single `Employee(id, name, department, managerId)` table, return the names of managers who have at least five direct reports.

## Pattern
**Self-join + GROUP BY / HAVING on a foreign key that points back into the same table.** Recognize it when a table references itself (`managerId` → `id`) and the question asks "which parents have ≥ N children". Aggregate the child side per parent key, filter with `HAVING`, then map the surviving keys back to display attributes.

## My approach
Self-joined `Employee` as reportee `m` against manager `e` on `e.id = m.managerId`, grouped, and kept groups with `COUNT(m.id) >= 5`:

```sql
select a.name from
(select e.name, e.id, count(m.id) as count_direct_reportee
 from Employee e
 inner join Employee m on e.id = m.managerId
 group by e.name, e.id
 having count(m.id) >= 5
) a
```

First submission failed: I had grouped by `e.name` alone. Two different managers sharing a name get merged into one group (and their report counts pool together), so the count is wrong for both. Adding `e.id` to the `GROUP BY` fixed it quickly. The outer `select a.name from (...) a` wrapper is also unnecessary — the inner query could just select `e.name` directly.

## Optimal approach
Same idea, but skip the join entirely: aggregate `managerId` on its own, then look the names up. Grouping one column of one table is the leanest form of the pattern.

```sql
SELECT name
FROM Employee
WHERE id IN (
    SELECT managerId
    FROM Employee
    GROUP BY managerId
    HAVING COUNT(*) >= 5
);
```

It beats the self-join version only marginally (no join before the aggregate), but it makes the group-by-key rule automatic — you never had the option to group by a name.

## Complexity
- Time: O(n) with a hash aggregate over `managerId`; the `IN` lookup is O(managers).
- Space: O(m) for the per-manager counts, m = number of distinct managers.

## The mistake to remember
**Group by the entity's key, never by a display attribute.** Names are not unique; `GROUP BY name` silently merges distinct entities. Select the extra display columns alongside the key, or fetch them after filtering on the key.

## Similar problems in vault
- [LC 550: Game Play Analysis IV](./lc-0550-game-play-analysis-iv.md) — also per-entity aggregation, but anchored to `MIN()` with date arithmetic instead of a count threshold.
- [LC 585: Investments in 2016](./lc-0585-investments-in-2016.md) — same GROUP BY / HAVING membership-set machinery, used to classify values as duplicated vs unique instead of thresholding child counts.

## Solution
```sql
select e.name
from Employee e
inner join Employee m on e.id = m.managerId
group by e.id, e.name
having count(m.id) >= 5;
```
