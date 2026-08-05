# Integrated Client Analytics — Final Recommendation Memo

## Executive summary

The supplied two-year retail dataset contains 2.60M item-level transaction rows, 276,484 baskets, 2,500 households, 92,353 products, 30 campaigns, and 36.8M promotion records. The strongest decision signal is not a single campaign winner; it is the combination of customer-value concentration, broad period-level spend movement, sparse campaign redemption, and strong category-level differences.

## Key findings

### 1. Customer value is concentrated
The top 10% of households account for approximately 34.3% of observed spend. Mean household total spend is about 3,223, while the distribution is strongly right-skewed. This supports differentiated high-value and at-risk customer strategies rather than one universal offer.

### 2. The period shows a broad upward spend shift, but this is not automatically an intervention effect
Across 2,476 households with spend in both halves of the dataset, mean second-half spend is about 405.79 higher than first-half spend. A paired test is highly statistically significant, with a standardized effect around 0.23. Because the dataset has no anchored calendar dates and multiple business changes may coexist, this should be treated as a period-level behavioral signal, not a causal campaign claim.

### 3. Campaign redemption is sparse and campaign mechanics differ
Campaign redemption household rates vary substantially. TypeA campaigns have much larger exposed populations than many TypeB/TypeC campaigns, while small campaigns have very small denominators. Campaign comparisons therefore need denominator-aware reporting and selection-bias controls. The next decision should prioritize a randomized test rather than declaring historical exposure causal.

### 4. Grocery dominates sales, while several smaller categories show faster growth
GROCERY contributes about 4.09M in observed sales, materially above the next-largest departments. At commodity level, some categories show strong second-half growth, while a smaller set of mature categories are flat or declining. Category actions should therefore combine sales scale, penetration, growth, discount rate, and denominator thresholds rather than raw sales rank alone.

### 5. A leakage-safe feature layer is feasible
A temporal household dataset was created using weeks 1-76 as the observation window and weeks 77-102 as the future label window. It includes recency, frequency, monetary value, basket, discount, coupon engagement, category/product breadth, demographic missingness, and future activity labels. This provides a suitable foundation for a future churn/value/campaign-targeting model.

## Recommended actions

1. **Protect high-value households:** build a controlled retention treatment for the top-value segment and measure incremental spend/retention rather than response rate alone.
2. **Investigate declining customers:** prioritize the analytical at-risk flag for operational review; do not treat it as a validated churn prediction without future validation.
3. **Rationalize campaign evaluation:** report campaign type, exposed denominator, redemption denominator, prior-value strata, and pre-period behavior together.
4. **Prioritize category experiments:** focus on high-penetration categories with declining/flat growth and high discount dependence, while separately testing high-growth opportunities.
5. **Run a randomized next experiment:** randomize at household level within pre-specified value strata, use incremental spend or repeat activity as the primary outcome, and define guardrails for discount cost and margin.

## What not to conclude

- Campaign exposure did not prove incremental sales.
- Redemption rate is not ROI.
- The broad spend increase did not prove that campaigns caused growth.
- Demographic conclusions cannot be generalized to all households because only 32.04% have demographic records.
- The in-sample model AUC is not production performance.

## Next data to collect

Collect real calendar dates, campaign delivery/open/impression events, treatment assignment, offer cost, margin contribution, and customer-level exposure timestamps. These additions would materially improve causal measurement and experiment monitoring.
