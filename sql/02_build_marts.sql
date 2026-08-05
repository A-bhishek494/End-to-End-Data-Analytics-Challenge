-- SQL dialect: SQLite 3.x
-- Core mart transformations. The Python runner loads source CSVs into the staging tables.

DROP TABLE IF EXISTS mart_baskets;
CREATE TABLE mart_baskets AS
SELECT
  BASKET_ID,
  household_key,
  MIN(DAY) AS DAY,
  MIN(WEEK_NO) AS WEEK_NO,
  MIN(STORE_ID) AS STORE_ID,
  SUM(SALES_VALUE) AS basket_spend,
  SUM(QUANTITY) AS basket_units,
  COUNT(*) AS basket_item_line_count,
  COUNT(DISTINCT PRODUCT_ID) AS distinct_product_count,
  SUM(-RETAIL_DISC) AS retail_discount,
  SUM(-COUPON_DISC) AS coupon_discount,
  SUM(-COUPON_MATCH_DISC) AS matched_coupon_discount,
  SUM(-RETAIL_DISC-COUPON_DISC-COUPON_MATCH_DISC) AS discount_amount,
  MAX(CASE WHEN COUPON_DISC < 0 OR COUPON_MATCH_DISC < 0 THEN 1 ELSE 0 END) AS coupon_used
FROM stg_transactions
GROUP BY BASKET_ID, household_key;

DROP TABLE IF EXISTS mart_household_period;
CREATE TABLE mart_household_period AS
SELECT
  household_key,
  WEEK_NO,
  COUNT(DISTINCT BASKET_ID) AS basket_count,
  SUM(SALES_VALUE) AS total_spend,
  SUM(QUANTITY) AS total_units,
  COUNT(DISTINCT PRODUCT_ID) AS distinct_product_count,
  SUM(-RETAIL_DISC-COUPON_DISC-COUPON_MATCH_DISC) AS discount_amount,
  SUM(CASE WHEN COUPON_DISC < 0 OR COUPON_MATCH_DISC < 0 THEN 1 ELSE 0 END) AS coupon_used_lines
FROM stg_transactions
GROUP BY household_key, WEEK_NO;

DROP TABLE IF EXISTS mart_products;
CREATE TABLE mart_products AS
SELECT
  t.PRODUCT_ID,
  p.MANUFACTURER, p.DEPARTMENT, p.BRAND, p.COMMODITY_DESC, p.SUB_COMMODITY_DESC,
  SUM(t.SALES_VALUE) AS product_sales,
  SUM(t.QUANTITY) AS units,
  COUNT(DISTINCT t.household_key) AS household_count,
  COUNT(DISTINCT t.BASKET_ID) AS basket_count,
  SUM(-t.RETAIL_DISC-t.COUPON_DISC-t.COUPON_MATCH_DISC) AS discount_amount
FROM stg_transactions t
LEFT JOIN stg_product p ON t.PRODUCT_ID=p.PRODUCT_ID
GROUP BY t.PRODUCT_ID;

DROP TABLE IF EXISTS mart_campaigns;
CREATE TABLE mart_campaigns AS
SELECT
  ct.CAMPAIGN,
  cd.DESCRIPTION,
  cd.START_DAY,
  cd.END_DAY,
  COUNT(DISTINCT ct.household_key) AS exposed_households,
  COUNT(*) AS exposure_records
FROM stg_campaign_table ct
LEFT JOIN stg_campaign_desc cd ON ct.CAMPAIGN=cd.CAMPAIGN
GROUP BY ct.CAMPAIGN, cd.DESCRIPTION, cd.START_DAY, cd.END_DAY;

DROP TABLE IF EXISTS mart_coupon_redemptions;
CREATE TABLE mart_coupon_redemptions AS
SELECT CAMPAIGN, COUNT(*) AS redemption_count,
       COUNT(DISTINCT household_key) AS redemption_households,
       COUNT(DISTINCT COUPON_UPC) AS coupons_redeemed
FROM stg_coupon_redempt
GROUP BY CAMPAIGN;
