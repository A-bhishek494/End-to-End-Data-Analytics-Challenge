# KPI Definitions

| KPI | Numerator | Denominator | Grain / window | Notes |
|---|---|---|---|---|
| Active household | Households with >=1 basket | Active households universe | Household-period | Period = dataset WEEK_NO |
| Basket | Distinct BASKET_ID | — | Basket | Item rows are never treated as baskets |
| Trip frequency | Basket count | Active households | Household-period | Average baskets per active household |
| Basket size | Units in basket | Baskets | Basket | Raw QUANTITY retained; extreme quantities flagged |
| Spend / gross sales | Sum SALES_VALUE | — | Basket / household-period | Source sales measure |
| Discount amount | -RETAIL_DISC - COUPON_DISC - COUPON_MATCH_DISC | — | Basket / household-period | Reported as positive amount |
| Discount rate | Discount amount | Gross sales | Basket / period | Rates outside [0,1] are validation failures |
| Coupon redemption rate | Redeeming households | Exposed households | Campaign | Sparse denominators explicitly shown |
| Repeat activity | Households active in >1 period | Active households | Household over full window | Not a causal retention measure |
| Customer value | Total household spend | — | Household, full history | Heavy right tail expected |
| High-value customer | Household in top 20% of spend | All households | Full history | Threshold calculated from observed population |
| At-risk customer | Recency >=4 weeks AND spend decline >20% | All households | Full history | Analytical flag, not validated churn label |
| Category penetration | Purchasing households | All observed households | Category, full history | Distinct households, not summed weekly counts |
| Product/category growth | Second-half sales - first-half sales | First-half sales | Product/category | Half split at week 51; calendar months unavailable |
