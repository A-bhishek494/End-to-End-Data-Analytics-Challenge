-- SQL dialect: SQLite 3.x
-- Staging layer. Source CSVs are loaded into stg_* tables by the Python runner.

CREATE TABLE IF NOT EXISTS stg_transactions AS SELECT * FROM raw_transactions WHERE 1=0;
CREATE TABLE IF NOT EXISTS stg_product AS SELECT * FROM raw_product WHERE 1=0;
CREATE TABLE IF NOT EXISTS stg_demographic AS SELECT * FROM raw_demographic WHERE 1=0;
CREATE TABLE IF NOT EXISTS stg_campaign_desc AS SELECT * FROM raw_campaign_desc WHERE 1=0;
CREATE TABLE IF NOT EXISTS stg_campaign_table AS SELECT * FROM raw_campaign_table WHERE 1=0;
CREATE TABLE IF NOT EXISTS stg_coupon AS SELECT * FROM raw_coupon WHERE 1=0;
CREATE TABLE IF NOT EXISTS stg_coupon_redempt AS SELECT * FROM raw_coupon_redempt WHERE 1=0;

-- Reporting convention: raw negative discount fields are transformed to positive discount amounts.
-- TRANS_TIME is parsed as HHMM-style integer only; no calendar date is inferred.
