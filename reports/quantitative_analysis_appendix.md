# Quantitative Analysis Appendix

## Descriptive statistics

- Transaction rows: 2,595,732.
- Distinct baskets: 276,484.
- Distinct households: 2,500.
- Distinct products: 92,353.
- Dataset coverage: 711 day-index values and 102 week-index values.
- Gross sales: 8,057,463.08.
- Mean basket value: 29.14; median basket value: 17.07.
- Mean household average-basket value: 33.29.

## Uncertainty

A 1,000-resample bootstrap for mean household average-basket value gives a 95% interval of approximately 32.50 to 34.10.

The repeat-activity rate is 99.88% of households having activity in more than one week. A normal-approximation interval is approximately 99.74% to 100.02%; because the upper bound exceeds 100%, the interval is clipped to the valid probability range when presented. The high rate should therefore be interpreted alongside the dataset's observation design rather than as a conventional customer-retention estimate.

## Hypothesis test

H0: mean household spend in the second half of the observation period equals mean household spend in the first half.

H1: the means differ.

A paired t-test across 2,476 households with spend in both halves gives mean change of +405.79 and p < 0.001, with a standardized paired effect around 0.23. This is evidence of a broad period-level change, not evidence that any single intervention caused it.

## Campaign comparison

A simple exposed-ever vs unexposed-ever comparison of household half-period spend change is highly statistically different (Mann-Whitney p < 0.001). This result must **not** be interpreted as causal campaign lift because campaign assignment is observational and TypeA targeting is especially vulnerable to prior-behavior selection effects.

## Similarity and dimensionality

A household-by-top-20-commodity spend matrix contains 2,498 households and 20 commodity columns. Approximately 17.9% of cells are zero. PCA on standardized features explains about 61.4% of variance in the first five components. The representation is useful for similarity/segmentation reasoning, but sparse purchase behavior and scale differences can distort nearest-neighbor interpretation.

## Baseline model

An interpretable logistic regression predicts future activity using observation-window features. The in-sample AUC is about 0.89. This is **not** a valid production performance estimate because it is not a held-out temporal evaluation; it is included only to demonstrate feature readiness and coefficient interpretation. Production use requires a true temporal validation split and calibration assessment.

## Business significance

Statistical significance is not sufficient for campaign or category decisions. Effect size, denominator size, cost, operational feasibility, and uncertainty must be considered together.
