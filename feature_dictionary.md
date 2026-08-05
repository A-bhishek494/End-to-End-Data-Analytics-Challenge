# Feature Dictionary

The feature-ready table uses weeks 1-76 as the observation window and weeks 77-102 as the future label window.

- `recency_weeks`: weeks since last observed purchase at the end of week 76.
- `frequency_baskets`: baskets during observation window.
- `monetary_spend`: gross sales during observation window.
- `units`: raw quantity during observation window.
- `active_weeks`: number of distinct active weeks.
- `avg_basket_value`: mean basket value by active week.
- `discount_amount`: positive transformed discount amount.
- `discount_rate`: discount amount / monetary spend.
- `coupon_used_lines`: transaction lines with coupon discount.
- `coupon_engagement`: coupon-used lines / units.
- `distinct_products`: summed distinct products by household-week; retained as engagement proxy.
- `future_active_flag`: target-like label; any activity in weeks 77-102.
- `future_spend_decline_flag`: future spend below 80% of observation-window spend.
- `missing_demographic_flag`: demographic record unavailable.

Leakage control: every feature is calculated using weeks <=76; labels use weeks >76 only.
