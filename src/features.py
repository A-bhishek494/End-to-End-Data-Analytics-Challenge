import numpy as np

def add_discount_rate(df, spend_col='total_spend', discount_col='discount_amount'):
    out=df.copy()
    out['discount_rate']=np.where(out[spend_col]>0,out[discount_col]/out[spend_col],np.nan)
    return out
