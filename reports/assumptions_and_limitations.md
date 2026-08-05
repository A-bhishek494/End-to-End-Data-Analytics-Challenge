# Assumptions and Limitations

- `WEEK_NO` and `DAY` are dataset indexes, not real calendar dates.
- No weekday, month, holiday, or true calendar seasonality is inferred.
- Gross sales use `SALES_VALUE` as supplied.
- Discounts are converted from negative raw signs to positive reporting amounts.
- Active household means at least one observed basket in the period.
- Repeat activity is not equivalent to contractual retention.
- Demographic analysis is limited by 32.04% demographic coverage.
- Campaign exposure is not equivalent to reading, treatment adherence, or causal assignment.
- TypeA campaigns are targeted and should not be interpreted identically to TypeB/TypeC.
- Coupon redemption is sparse and rates use explicit exposed-household denominators where available.
- Very large quantities are flagged rather than silently deleted.
- Category growth is based on a first-half/second-half week split, not calendar periods.
- The feature-ready dataset uses weeks 1-76 for features and 77-102 for labels.
- Observational campaign comparisons are evidence of association/hypothesis, not proof of causality.
- The baseline logistic model is illustrative and requires temporal holdout validation before production use.
