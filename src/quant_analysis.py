import numpy as np
from scipy import stats

def paired_change_test(first, second):
    t=stats.ttest_rel(second, first, nan_policy='omit')
    diff=np.nanmean(second-first)
    return {'mean_change':float(diff),'p_value':float(t.pvalue)}

def bootstrap_mean(x, n_boot=1000, seed=42):
    rng=np.random.default_rng(seed); x=np.asarray(x)
    means=[rng.choice(x,size=len(x),replace=True).mean() for _ in range(n_boot)]
    return np.quantile(means,[.025,.975])
