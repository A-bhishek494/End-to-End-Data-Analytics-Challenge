-- Validation controls.

-- Key uniqueness: one row per basket.
SELECT BASKET_ID, COUNT(*) AS n FROM mart_baskets GROUP BY BASKET_ID HAVING COUNT(*) > 1;

-- Rate bounds.
SELECT COUNT(*) AS invalid_discount_rates
FROM mart_baskets WHERE discount_rate < 0 OR discount_rate > 1;

-- Fan-out check: basket count must reconcile before/after product enrichment.
SELECT COUNT(*) AS basket_rows, COUNT(DISTINCT BASKET_ID) AS distinct_baskets
FROM mart_baskets;

-- Demographic coverage.
SELECT COUNT(DISTINCT household_key) AS demographic_households FROM stg_demographic;

-- Transaction/product orphan check.
SELECT COUNT(*) AS transaction_rows_without_product
FROM stg_transactions t LEFT JOIN stg_product p ON t.PRODUCT_ID=p.PRODUCT_ID
WHERE p.PRODUCT_ID IS NULL;

-- Campaign/coupon context check.
SELECT COUNT(*) AS redemptions_without_campaign
FROM stg_coupon_redempt r LEFT JOIN stg_campaign_desc c ON r.CAMPAIGN=c.CAMPAIGN
WHERE c.CAMPAIGN IS NULL;
