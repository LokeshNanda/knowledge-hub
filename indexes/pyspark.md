# PySpark — map of content

DataFrame-API companions to the LeetCode SQL notes. Each note links back to its
SQL twin (which holds the problem statement, pattern analysis, and honest solve
review); these notes carry only the translation, the idiomatic Spark solution,
and API-specific gotchas. Organized by the DataFrame idiom the translation
teaches.

## groupBy + agg + filter (SQL GROUP BY / HAVING)
- [LC 570: Managers with at Least 5 Direct Reports](../areas/pyspark/lc-0570-managers-with-at-least-5-direct-reports.md) — post-agg `.filter()` as HAVING, `left_semi` join as `WHERE id IN (...)`.
- [LC 1045: Customers Who Bought All Products](../areas/pyspark/lc-1045-customers-who-bought-all-products.md) — relational division via `F.countDistinct` compared to a driver-side `product.count()` scalar.

## Pre-aggregate + left join + coalesce/fillna (zero-preserving counts)
- [LC 1158: Market Analysis I](../areas/pyspark/lc-1158-market-analysis-i.md) — filter the fact frame *before* the left join; a post-join filter silently re-drops the zero-count users (the ON-vs-WHERE trap, DataFrame edition).

## Multi-key join replacing tuple IN
- [LC 1070: Product Sales Analysis III](../areas/pyspark/lc-1070-product-sales-analysis-iii.md) — `(product_id, year) IN (...)` becomes an inner join on both keys; `F.rank()` (never `row_number`) for the window variant; duplicate-column disambiguation after self-referential joins.
- [LC 550: Game Play Analysis IV](../areas/pyspark/lc-0550-game-play-analysis-iv.md) — min-anchor per player, `F.date_add` + conditional `countDistinct(F.when(...))` for the one-row fraction.

## Window functions (partitioned counts, lead/lag)
- [LC 585: Investments in 2016](../areas/pyspark/lc-0585-investments-in-2016.md) — `F.count("*").over(Window.partitionBy(...))` as the group-count classifier; multi-column `partitionBy` replaces tuple `IN`; beware `orderBy` silently adding a running frame.
- [LC 626: Exchange Seats](../areas/pyspark/lc-0626-exchange-seats.md) *(window variant)* — `lead`/`lag` + `coalesce` student swap; unpartitioned `Window.orderBy` = single-partition warning.

## union as UNION ALL unpivot
- [LC 602: Friend Requests II — Who Has the Most Friends](../areas/pyspark/lc-0602-friend-requests-ii-most-friends.md) — `df.union()` is UNION **ALL** (the SQL dedupe trap inverted); positional matching vs `unionByName`.

## when() chains (CASE) + join-based membership
- [LC 608: Tree Node](../areas/pyspark/lc-0608-tree-node.md) — no `IN`/`EXISTS` inside expressions: membership that feeds a label = left join + `isNotNull()`; `when()` order matters exactly like CASE.
- [LC 626: Exchange Seats](../areas/pyspark/lc-0626-exchange-seats.md) — parity `when()` chain remapping the sort key; uncorrelated scalar subquery = driver-side `count()` action.
