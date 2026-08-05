from pathlib import Path
import pandas as pd

def iter_transactions(raw_dir, chunksize=500_000):
    path=Path(raw_dir)/'transaction_data.csv'
    cols=['household_key','BASKET_ID','DAY','PRODUCT_ID','QUANTITY','SALES_VALUE','STORE_ID','RETAIL_DISC','TRANS_TIME','WEEK_NO','COUPON_DISC','COUPON_MATCH_DISC']
    yield from pd.read_csv(path,usecols=cols,chunksize=chunksize)
