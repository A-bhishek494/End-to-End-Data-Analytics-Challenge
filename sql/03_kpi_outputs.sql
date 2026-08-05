-- KPI definitions are intentionally explicit about numerator/denominator.

-- Active household: household with >=1 basket in the reporting period.
SELECT WEEK_NO, COUNT(DISTINCT household_key) AS active_households
FROM mart_household_period GROUP BY WEEK_NO ORDER BY WEEK_NO;

-- Basket: distinct BASKET_ID.
SELECT COUNT(*) AS baskets, AVG(basket_spend) AS avg_basket_value,
       SUM(basket_spend) AS gross_sales
FROM mart_baskets;

-- Repeat activity rate: households active in >1 reporting period / all active households.
WITH x AS (
 SELECT household_key, COUNT(DISTINCT WEEK_NO) AS active_weeks
 FROM mart_household_period GROUP BY household_key
)
SELECT AVG(CASE WHEN active_weeks > 1 THEN 1.0 ELSE 0.0 END) AS repeat_activity_rate,
       COUNT(*) AS denominator_households
FROM x;

-- Discount rate: total positive discount amount / gross sales.
SELECT SUM(discount_amount) / NULLIF(SUM(basket_spend),0) AS discount_rate
FROM mart_baskets;

-- Campaign redemption household rate: redeemed households / exposed households.
SELECT c.CAMPAIGN,
       c.exposed_households,
       COALESCE(r.redemption_households,0) AS redemption_households,
       COALESCE(r.redemption_households,0)*1.0/NULLIF(c.exposed_households,0) AS redemption_rate
FROM mart_campaigns c
LEFT JOIN mart_coupon_redemptions r ON c.CAMPAIGN=r.CAMPAIGN;
