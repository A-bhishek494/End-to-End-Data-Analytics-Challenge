# Validation Report

## Source checks

| Check | Result |
|---|---:|
| Transaction rows | 2,595,732 |
| Distinct baskets | 276,484 |
| Distinct households | 2,500 |
| Distinct products | 92,353 |
| Stores | 582 |
| Campaigns | 30 |
| Campaign exposure records | 7,208 |
| Coupon IDs | 1,135 |
| Coupon redemption rows | 2,318 |
| causal_data rows | 36,786,524 |
| Demographic households | 801 |
| Demographic coverage | 32.04% |
| Transaction rows without product metadata | 0 |
| Weeks | 102 |
| Days | 711 |

## Data quality

- 14,466 transaction rows have non-positive quantity and are flagged for review.
- 18,850 transaction rows have non-positive SALES_VALUE and are flagged for review.
- Quantity is highly right-skewed; the 99.9th percentile is about 16,944 and the maximum is 89,638. These observations should not be treated as ordinary unit demand without business investigation.
- Raw discount fields are negative by convention and are transformed to positive discount amounts for reporting.
- No orphan transaction-to-product rows were found.
- Demographics cover only 801 of 2,500 households; missingness is preserved with an indicator.

## Grain / fan-out controls

- Transaction data is treated as item-receipt-line grain.
- Baskets are defined by distinct BASKET_ID.
- Coupon and campaign data are summarized at campaign/household grain before any customer-level comparison.
- coupon.csv is not directly joined to transaction rows for revenue calculation because one coupon can map to many products and would create fan-out.
- causal_data is not directly joined to item transactions in the main mart. Its product-store-week grain is handled separately because the source contains 36.8M rows.

## Statistical controls

- Confidence intervals and bootstrap uncertainty are included.
- Hypothesis tests report effect size as well as p-values.
- Observational campaign comparisons explicitly discuss selection bias.
- The baseline model is labeled in-sample and not presented as production performance.
