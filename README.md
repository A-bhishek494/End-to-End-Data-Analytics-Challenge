# Integrated Client Analytics Capstone

## Objective
Build a reproducible analytics package from the supplied dunnhumby-style retail data to answer what the retailer should do to improve customer value, campaign effectiveness, and category performance.

## SQL dialect
SQLite 3.x for the submitted SQL layer. Python is used for orchestration, chunked raw-data processing, statistics, feature engineering, and visualization.

## Source files expected
Place these in `data/raw/`:
- transaction_data.csv
- product.csv
- hh_demographic.csv
- campaign_desc.csv
- campaign_table.csv
- coupon.csv
- coupon_redempt.csv
- causal_data.csv

## Run
1. Create a Python environment with pandas, numpy, scipy, scikit-learn, matplotlib, and statsmodels.
2. Place raw CSVs in `data/raw/`.
3. Run `python build_analysis.py`.
4. Review tables under `outputs/tables/` and charts under `outputs/charts/`.
5. Review `final_recommendation_memo.md`, `reports/validation_report.md`, and the quantitative appendix.

## Important design controls
- Item rows are not baskets.
- Coupon/product joins are not performed at uncontrolled transaction grain.
- causal_data is handled separately because it is product-store-week grain and very large.
- Raw discount signs are converted to positive discount amounts for reporting.
- Rates are reported with explicit denominators.
- Campaign analysis is observational and selection bias is discussed.
- Features use a temporal split to prevent future-label leakage.

## Main outputs
- `outputs/tables/mart_baskets.csv`
- `outputs/tables/mart_household_period.csv`
- `outputs/tables/mart_products.csv`
- `outputs/tables/mart_categories.csv`
- `outputs/tables/mart_campaigns.csv`
- `outputs/tables/mart_coupon_redemptions.csv`
- `outputs/tables/mart_customer_features.csv`
- `outputs/tables/feature_ready_households.csv`
- `outputs/tables/customer_category_matrix.csv`

## Limitations
The standard dataset has no anchored calendar date, so weekday/month/holiday seasonality is not inferred. Demographic data is only available for a subset of households. Campaign exposure is not causal treatment.
