# Performance and Scalability Note

The largest source is `causal_data.csv` at approximately 664 MB in the supplied archive and 36.8M rows after extraction. The transaction source contains 2.6M item-level rows.

## Current strategy

1. Read transaction data in chunks rather than loading every raw source into memory simultaneously.
2. Aggregate transactions to basket, household-week, product-week, and day grain before downstream analysis.
3. Keep causal promotion data separate from transaction facts unless an exact product-store-week analytical question requires it.
4. Never perform an uncontrolled transaction × coupon × causal join.
5. Push grain-changing aggregation into SQL in the reproducible SQL layer; Python consumes analysis-ready aggregates.

## Production recommendation

Use a columnar warehouse (DuckDB/BigQuery/Snowflake/Databricks equivalent), partition large facts by week, cluster/index by household/product/store, and materialize basket and household-period facts. For causal_data, first filter to the relevant weeks/products/stores and aggregate promotion exposure before joining to transaction-derived facts.
