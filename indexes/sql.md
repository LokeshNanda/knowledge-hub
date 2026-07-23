# SQL — map of content

Organized by pattern. ✅ = clean unaided solve, ⚠️ = struggled / needed help.
Tally per pattern: clean / total.

Every problem here has a PySpark companion note — see [the PySpark index](./pyspark.md).

## Aggregation: first-event anchor (1/2 clean)
- ⚠️ [LC 550: Game Play Analysis IV](../areas/sql/lc-0550-game-play-analysis-iv.md) — day-after-first-login retention; used LEAD over any adjacent pair instead of anchoring to MIN(event_date), plus `date + 1` integer-arithmetic trap.
- ✅ [LC 1070: Product Sales Analysis III](../areas/sql/lc-1070-product-sales-analysis-iii.md) — rows at each product's first sale year; anchor via GROUP BY + MIN(year), filter with tuple `(product_id, year) IN`; window alternative needs RANK, not ROW_NUMBER (first-year ties must survive).

## Aggregation: group-by / having on a key (1/1 clean)
- ✅ [LC 570: Managers with at Least 5 Direct Reports](../areas/sql/lc-0570-managers-with-at-least-5-direct-reports.md) — self-join on managerId, HAVING COUNT ≥ 5; first attempt grouped by name instead of id (non-unique names merge entities), self-corrected fast.

## Relational division: entity matches ALL of a set (1/1 clean)
- ✅ [LC 1045: Customers Who Bought All Products](../areas/sql/lc-1045-customers-who-bought-all-products.md) — per-customer `COUNT(DISTINCT product_key)` compared to total product count via HAVING; `DISTINCT` is load-bearing (duplicate purchases must not fake completeness); minor slack: redundant IN-filter and derived-table wrapper.

## Reshaping: UNION ALL unpivot + aggregate (1/1 clean)
- ✅ [LC 602: Friend Requests II — Who Has the Most Friends](../areas/sql/lc-0602-friend-requests-ii-most-friends.md) — stack requester/accepter columns with UNION ALL, GROUP BY, top-1; trap: plain UNION dedupes and breaks the count.

## Classification: CASE + membership subquery (0/1 clean)
- ⚠️ [LC 608: Tree Node](../areas/sql/lc-0608-tree-node.md) — label nodes Root/Inner/Leaf via CASE with `id IN (SELECT p_id)`; needed hints for the CASE-plus-subquery shape; trap: `NOT IN` against a NULL-bearing column classifies nothing.

## Transformation: adjacent-swap via parity CASE (0/1 clean)
- ⚠️ [LC 626: Exchange Seats](../areas/sql/lc-0626-exchange-seats.md) — swap consecutive students by remapping id with a parity CASE (`odd → id+1`, `even → id-1`) and sorting on the new key; boundary = odd last id via membership subquery; had to see the approach once; trap: leftover GROUP BY and missing ORDER BY on the remapped id.

## Aggregation: zero-preserving LEFT JOIN count (1/1 clean)
- ✅ [LC 1158: Market Analysis I](../areas/sql/lc-1158-market-analysis-i.md) — orders per user in 2019 with zero-order users kept; pre-aggregated derived table + LEFT JOIN + COALESCE; trap: fact-side filter in `WHERE` after a LEFT JOIN silently makes it INNER; nits: `YEAR()` is non-sargable, prefer a date range.

## Aggregation: duplicate vs unique classification (0/1 clean)
- ⚠️ [LC 585: Investments in 2016](../areas/sql/lc-0585-investments-in-2016.md) — HAVING COUNT > 1 / = 1 to build duplicated- and unique-value sets, tuple `(lat, lon) IN` membership; solved unassisted but only one day after studying the solution — needs a cold re-solve.
