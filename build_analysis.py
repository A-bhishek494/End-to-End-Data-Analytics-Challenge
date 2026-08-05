import os, json, math, sqlite3, warnings
import pandas as pd, numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

BASE='/mnt/data/capstone'
RAW=f'{BASE}/data/raw'; OUT=f'{BASE}/outputs'; TAB=f'{OUT}/tables'; CH=f'{OUT}/charts'; REP=f'{BASE}/reports'
for d in [TAB,CH,REP,f'{BASE}/sql',f'{BASE}/notebooks',f'{BASE}/src',f'{BASE}/data/processed']:
    os.makedirs(d,exist_ok=True)

# Small source tables
prod=pd.read_csv(f'{RAW}/product.csv')
demo=pd.read_csv(f'{RAW}/hh_demographic.csv')
camp_desc=pd.read_csv(f'{RAW}/campaign_desc.csv')
camp_table=pd.read_csv(f'{RAW}/campaign_table.csv')
coupon=pd.read_csv(f'{RAW}/coupon.csv')
red=pd.read_csv(f'{RAW}/coupon_redempt.csv')

# Normalize text
for c in ['DEPARTMENT','COMMODITY_DESC','SUB_COMMODITY_DESC','BRAND']:
    prod[c]=prod[c].fillna('UNKNOWN').astype(str).str.strip()

# First pass transaction aggregates
cols=['household_key','BASKET_ID','DAY','PRODUCT_ID','QUANTITY','SALES_VALUE','STORE_ID','RETAIL_DISC','TRANS_TIME','WEEK_NO','COUPON_DISC','COUPON_MATCH_DISC']
basket_parts=[]; hhweek_parts=[]; product_parts=[]; day_parts=[]
row_count=0; bad_qty=0; bad_sales=0; missing_prod=0; dup_lines=0
prod_ids=set(prod.PRODUCT_ID.astype(str))
for chunk in pd.read_csv(f'{RAW}/transaction_data.csv',usecols=cols,chunksize=500_000):
    row_count += len(chunk)
    bad_qty += int((chunk.QUANTITY<=0).sum())
    bad_sales += int((chunk.SALES_VALUE<=0).sum())
    missing_prod += int((~chunk.PRODUCT_ID.isin(prod.PRODUCT_ID)).sum())
    # positive discount amounts
    for c in ['RETAIL_DISC','COUPON_DISC','COUPON_MATCH_DISC']:
        chunk[c+'_AMT']=-chunk[c]
    chunk['DISCOUNT_AMT']=chunk['RETAIL_DISC_AMT']+chunk['COUPON_DISC_AMT']+chunk['COUPON_MATCH_DISC_AMT']
    chunk['COUPON_USED']=(chunk['COUPON_DISC']<0)|(chunk['COUPON_MATCH_DISC']<0)
    b=chunk.groupby(['BASKET_ID','household_key','DAY','WEEK_NO','STORE_ID'],as_index=False).agg(
        basket_spend=('SALES_VALUE','sum'), basket_units=('QUANTITY','sum'), basket_item_line_count=('PRODUCT_ID','size'),
        distinct_product_count=('PRODUCT_ID','nunique'), retail_discount=('RETAIL_DISC_AMT','sum'), coupon_discount=('COUPON_DISC_AMT','sum'),
        matched_coupon_discount=('COUPON_MATCH_DISC_AMT','sum'), discount_amount=('DISCOUNT_AMT','sum'), coupon_used=('COUPON_USED','max'),
        trans_time_min=('TRANS_TIME','min'), trans_time_max=('TRANS_TIME','max'))
    b['discount_rate']=np.where(b['basket_spend']>0,b['discount_amount']/b['basket_spend'],np.nan)
    basket_parts.append(b)
    hw=chunk.groupby(['household_key','WEEK_NO'],as_index=False).agg(total_spend=('SALES_VALUE','sum'),total_units=('QUANTITY','sum'),basket_count=('BASKET_ID','nunique'),distinct_product_count=('PRODUCT_ID','nunique'),retail_discount=('RETAIL_DISC_AMT','sum'),coupon_discount=('COUPON_DISC_AMT','sum'),matched_coupon_discount=('COUPON_MATCH_DISC_AMT','sum'),coupon_used_lines=('COUPON_USED','sum'))
    hhweek_parts.append(hw)
    p=chunk.groupby(['PRODUCT_ID','WEEK_NO'],as_index=False).agg(product_sales=('SALES_VALUE','sum'),units=('QUANTITY','sum'),households=('household_key','nunique'),baskets=('BASKET_ID','nunique'),discount_amount=('DISCOUNT_AMT','sum'))
    product_parts.append(p)
    d=chunk.groupby(['DAY','WEEK_NO'],as_index=False).agg(sales=('SALES_VALUE','sum'),units=('QUANTITY','sum'),baskets=('BASKET_ID','nunique'),households=('household_key','nunique'))
    day_parts.append(d)

baskets=pd.concat(basket_parts,ignore_index=True).groupby(['BASKET_ID'],as_index=False).agg(
    household_key=('household_key','first'),DAY=('DAY','first'),WEEK_NO=('WEEK_NO','first'),STORE_ID=('STORE_ID','first'),
    basket_spend=('basket_spend','sum'),basket_units=('basket_units','sum'),basket_item_line_count=('basket_item_line_count','sum'),
    distinct_product_count=('distinct_product_count','sum'),retail_discount=('retail_discount','sum'),coupon_discount=('coupon_discount','sum'),
    matched_coupon_discount=('matched_coupon_discount','sum'),discount_amount=('discount_amount','sum'),coupon_used=('coupon_used','max'),
    trans_time_min=('trans_time_min','min'),trans_time_max=('trans_time_max','max'))
baskets['discount_rate']=np.where(baskets.basket_spend>0,baskets.discount_amount/baskets.basket_spend,np.nan)
# household-week: aggregate across chunks then weeks
hhw=pd.concat(hhweek_parts,ignore_index=True).groupby(['household_key','WEEK_NO'],as_index=False).agg(total_spend=('total_spend','sum'),total_units=('total_units','sum'),basket_count=('basket_count','sum'),distinct_product_count=('distinct_product_count','sum'),retail_discount=('retail_discount','sum'),coupon_discount=('coupon_discount','sum'),matched_coupon_discount=('matched_coupon_discount','sum'),coupon_used_lines=('coupon_used_lines','sum'))
hhw['avg_basket_value']=hhw.total_spend/hhw.basket_count
hhw['discount_amount']=hhw.retail_discount+hhw.coupon_discount+hhw.matched_coupon_discount
hhw['discount_rate']=np.where(hhw.total_spend>0,hhw.discount_amount/hhw.total_spend,np.nan)
hhw=hhw.sort_values(['household_key','WEEK_NO'])
hhw['prior_period_spend']=hhw.groupby('household_key').total_spend.shift(1)
hhw['spend_change']=hhw.total_spend-hhw.prior_period_spend
hhw['repeat_flag']=(hhw.prior_period_spend.notna()).astype(int)
hhw['active_flag']=1

pw=pd.concat(product_parts,ignore_index=True).groupby(['PRODUCT_ID','WEEK_NO'],as_index=False).agg(product_sales=('product_sales','sum'),units=('units','sum'),households=('households','sum'),baskets=('baskets','sum'),discount_amount=('discount_amount','sum'))
# Merge product hierarchy and overall product mart
pm=pw.groupby('PRODUCT_ID',as_index=False).agg(product_sales=('product_sales','sum'),units=('units','sum'),households=('households','sum'),baskets=('baskets','sum'),discount_amount=('discount_amount','sum'),active_weeks=('WEEK_NO','nunique'))
pm=pm.merge(prod,on='PRODUCT_ID',how='left')
pm['discount_rate']=np.where(pm.product_sales>0,pm.discount_amount/pm.product_sales,np.nan)
# growth based on first/last half of weeks
wmax=int(pw.WEEK_NO.max()); split=wmax//2
first=pw[pw.WEEK_NO<=split].groupby('PRODUCT_ID').product_sales.sum().rename('first_sales')
last=pw[pw.WEEK_NO>split].groupby('PRODUCT_ID').product_sales.sum().rename('last_sales')
pm=pm.merge(first,left_on='PRODUCT_ID',right_index=True,how='left').merge(last,left_on='PRODUCT_ID',right_index=True,how='left')
pm['sales_growth']=np.where(pm.first_sales>0,(pm.last_sales-pm.first_sales)/pm.first_sales,np.nan)

# category mart
cat=pm.groupby(['DEPARTMENT','COMMODITY_DESC'],dropna=False,as_index=False).agg(product_sales=('product_sales','sum'),units=('units','sum'),households=('households','sum'),product_count=('PRODUCT_ID','nunique'),discount_amount=('discount_amount','sum'))
cat['discount_rate']=np.where(cat.product_sales>0,cat.discount_amount/cat.product_sales,np.nan)
# weekly category sales and growth
cw=pw.merge(prod[['PRODUCT_ID','DEPARTMENT','COMMODITY_DESC']],on='PRODUCT_ID',how='left').groupby(['DEPARTMENT','COMMODITY_DESC','WEEK_NO'],as_index=False).product_sales.sum()
firstc=cw[cw.WEEK_NO<=split].groupby(['DEPARTMENT','COMMODITY_DESC']).product_sales.sum().rename('first_sales')
lastc=cw[cw.WEEK_NO>split].groupby(['DEPARTMENT','COMMODITY_DESC']).product_sales.sum().rename('last_sales')
cat=cat.merge(firstc,left_on=['DEPARTMENT','COMMODITY_DESC'],right_index=True,how='left').merge(lastc,left_on=['DEPARTMENT','COMMODITY_DESC'],right_index=True,how='left')
cat['sales_growth']=np.where(cat.first_sales>0,(cat.last_sales-cat.first_sales)/cat.first_sales,np.nan)

# Campaign marts
camp_exp=camp_table.merge(camp_desc,on='CAMPAIGN',how='left',suffixes=('','_desc'))
camp_mart=camp_exp.groupby(['CAMPAIGN','DESCRIPTION','START_DAY','END_DAY'],as_index=False).agg(exposed_households=('household_key','nunique'),exposure_records=('household_key','size'))
red_mart=red.groupby(['CAMPAIGN'],as_index=False).agg(redemption_count=('COUPON_UPC','size'),redemption_households=('household_key','nunique'),redemption_days=('DAY','nunique'))
red_mart=red_mart.merge(camp_desc,on='CAMPAIGN',how='left')
# denominator based redemption household / exposed households where applicable
camp_mart=camp_mart.merge(red_mart[['CAMPAIGN','redemption_count','redemption_households']],on='CAMPAIGN',how='left')
camp_mart['redemption_household_rate']=camp_mart.redemption_households/camp_mart.exposed_households

# Demographic coverage
all_hh=int(baskets.household_key.nunique()); demo_hh=int(demo.household_key.nunique())

# Household customer features: observation all history, plus trend from halves
hf=hhw.groupby('household_key',as_index=False).agg(total_spend=('total_spend','sum'),total_units=('total_units','sum'),basket_count=('basket_count','sum'),active_weeks=('WEEK_NO','nunique'),avg_basket_value=('avg_basket_value','mean'),distinct_product_count=('distinct_product_count','sum'),discount_amount=('discount_amount','sum'),coupon_used_lines=('coupon_used_lines','sum'),first_week=('WEEK_NO','min'),last_week=('WEEK_NO','max'))
hf['recency_weeks']=wmax-hf.last_week
hf['frequency_per_active_week']=hf.basket_count/hf.active_weeks
hf['discount_rate']=np.where(hf.total_spend>0,hf.discount_amount/hf.total_spend,np.nan)
hf['coupon_engagement_rate']=np.where(hf.total_units>0,hf.coupon_used_lines/hf.total_units,np.nan)
hf['high_value_flag']=(hf.total_spend>=hf.total_spend.quantile(.8)).astype(int)
# half-period trend
h1=hhw[hhw.WEEK_NO<=split].groupby('household_key').total_spend.sum().rename('first_half_spend')
h2=hhw[hhw.WEEK_NO>split].groupby('household_key').total_spend.sum().rename('second_half_spend')
hf=hf.merge(h1,left_on='household_key',right_index=True,how='left').merge(h2,left_on='household_key',right_index=True,how='left')
hf['spend_change_pct']=np.where(hf.first_half_spend>0,(hf.second_half_spend-hf.first_half_spend)/hf.first_half_spend,np.nan)
hf['declining_flag']=(hf.spend_change_pct<-0.2).astype(int)
hf=hf.merge(demo,on='household_key',how='left',suffixes=('','_demo'))
hf['missing_demographics_flag']=hf.AGE_DESC.isna().astype(int)
# simple risk score
hf['at_risk_flag']=((hf.recency_weeks>=4)&(hf.declining_flag==1)).astype(int)

# Temporal feature-ready dataset: observation weeks <= 76, future weeks >76
obs_end=76
obs=hhw[hhw.WEEK_NO<=obs_end]
future=hhw[hhw.WEEK_NO>obs_end]
feat=obs.groupby('household_key',as_index=False).agg(recency_weeks=('WEEK_NO',lambda x: obs_end-x.max()),frequency_baskets=('basket_count','sum'),monetary_spend=('total_spend','sum'),units=('total_units','sum'),active_weeks=('WEEK_NO','nunique'),avg_basket_value=('avg_basket_value','mean'),discount_amount=('discount_amount','sum'),coupon_used_lines=('coupon_used_lines','sum'),distinct_products=('distinct_product_count','sum'))
feat['discount_rate']=np.where(feat.monetary_spend>0,feat.discount_amount/feat.monetary_spend,np.nan)
feat['coupon_engagement']=np.where(feat.units>0,feat.coupon_used_lines/feat.units,np.nan)
fu=future.groupby('household_key').total_spend.sum().rename('future_spend')
fa=future.groupby('household_key').size().rename('future_active_weeks')
feat=feat.merge(fu,left_on='household_key',right_index=True,how='left').merge(fa,left_on='household_key',right_index=True,how='left')
feat['future_active_flag']=feat.future_active_weeks.fillna(0).gt(0).astype(int)
feat['future_spend_decline_flag']=np.where(feat.monetary_spend>0,feat.future_spend.fillna(0)<0.8*feat.monetary_spend,0).astype(int)
feat=feat.merge(demo,on='household_key',how='left')
feat['missing_demographic_flag']=feat.AGE_DESC.isna().astype(int)

# Category customer matrix: top 20 commodities by sales, household spend
trans_cat_parts=[]
for chunk in pd.read_csv(f'{RAW}/transaction_data.csv',usecols=['household_key','PRODUCT_ID','SALES_VALUE'],chunksize=500_000):
    x=chunk.merge(prod[['PRODUCT_ID','COMMODITY_DESC']],on='PRODUCT_ID',how='left')
    topcats=[]
    trans_cat_parts.append(x.groupby(['household_key','COMMODITY_DESC'],as_index=False).SALES_VALUE.sum())
hc=pd.concat(trans_cat_parts,ignore_index=True).groupby(['household_key','COMMODITY_DESC'],as_index=False).SALES_VALUE.sum()
topc=hc.groupby('COMMODITY_DESC').SALES_VALUE.sum().nlargest(20).index.tolist()
mat=hc[hc.COMMODITY_DESC.isin(topc)].pivot_table(index='household_key',columns='COMMODITY_DESC',values='SALES_VALUE',fill_value=0)
X=mat.values
sparsity=float((X==0).mean())
Xn=X/(np.linalg.norm(X,axis=1,keepdims=True)+1e-12)
# PCA on standardized nonzero-ish matrix
Xs=StandardScaler().fit_transform(mat)
pca=PCA(n_components=min(5,Xs.shape[1])).fit(Xs)

# Statistical analyses
# Bootstrap mean basket value household-level
rng=np.random.default_rng(42)
vals=hf.avg_basket_value.dropna().values
boot=np.array([rng.choice(vals,size=len(vals),replace=True).mean() for _ in range(1000)])
ci_basket=np.quantile(boot,[.025,.975])
# CI for repeat household rate: households with >1 active week
repeat_rate=(hf.active_weeks>1).mean(); n=len(hf); se=math.sqrt(repeat_rate*(1-repeat_rate)/n); ci_repeat=(repeat_rate-1.96*se,repeat_rate+1.96*se)
# Hypothesis test: first vs second half household spend paired, households with both
paired=hf.dropna(subset=['first_half_spend','second_half_spend']).copy(); t=stats.ttest_rel(paired.second_half_spend,paired.first_half_spend); diff=(paired.second_half_spend-paired.first_half_spend).mean(); effect_d=diff/paired[['first_half_spend','second_half_spend']].stack().std()
# Campaign bias-aware: exposed households vs matched-ish baseline prior spend, using pre-period spend and post-period spend
# derive per household around each campaign; aggregate exposure ever and compare change using household baseline spend quartiles
exp_hh=camp_table[['household_key','CAMPAIGN']].drop_duplicates()
exp_set=set(exp_hh.household_key)
hf2=hf.copy(); hf2['exposed_ever']=hf2.household_key.isin(exp_set).astype(int)
# baseline/future proxy using halves
hf2['change']=hf2.second_half_spend-hf2.first_half_spend
ex=hf2[hf2.exposed_ever==1].change.dropna(); un=hf2[hf2.exposed_ever==0].change.dropna(); mw=stats.mannwhitneyu(ex,un,alternative='two-sided') if len(un) else None
# logistic baseline on feature-ready dataset
model_cols=['recency_weeks','frequency_baskets','monetary_spend','avg_basket_value','discount_rate','coupon_engagement','distinct_products','missing_demographic_flag']
md=feat.dropna(subset=['future_active_flag']).copy()
for c in model_cols: md[c]=md[c].fillna(md[c].median())
sc=StandardScaler(); XX=sc.fit_transform(md[model_cols]); yy=md.future_active_flag
lr=LogisticRegression(max_iter=500).fit(XX,yy); pred=lr.predict_proba(XX)[:,1]; auc=roc_auc_score(yy,pred)

# Save tables
baskets.to_csv(f'{TAB}/mart_baskets.csv',index=False)
hhw.to_csv(f'{TAB}/mart_household_period.csv',index=False)
pm.to_csv(f'{TAB}/mart_products.csv',index=False)
cat.to_csv(f'{TAB}/mart_categories.csv',index=False)
camp_mart.to_csv(f'{TAB}/mart_campaigns.csv',index=False)
red.to_csv(f'{TAB}/mart_coupon_redemptions.csv',index=False)
hf.to_csv(f'{TAB}/mart_customer_features.csv',index=False)
feat.to_csv(f'{TAB}/feature_ready_households.csv',index=False)
mat.to_csv(f'{TAB}/customer_category_matrix.csv')

# Visuals
plt.figure(figsize=(9,5)); dayagg=pd.concat(day_parts).groupby('DAY',as_index=False).agg(sales=('sales','sum'),baskets=('baskets','sum')); plt.plot(dayagg.DAY,dayagg.sales); plt.title('Sales coverage over dataset day index'); plt.xlabel('DAY'); plt.ylabel('Sales'); plt.tight_layout(); plt.savefig(f'{CH}/01_sales_coverage.png',dpi=150); plt.close()
plt.figure(figsize=(9,5)); plt.hist(hf.total_spend.clip(upper=hf.total_spend.quantile(.99)),bins=40); plt.title('Household spend distribution (capped at 99th percentile)'); plt.xlabel('Total spend'); plt.ylabel('Households'); plt.tight_layout(); plt.savefig(f'{CH}/02_household_spend_distribution.png',dpi=150); plt.close()
plt.figure(figsize=(9,5)); plt.hist(hf.basket_count.clip(upper=hf.basket_count.quantile(.99)),bins=30); plt.title('Basket frequency distribution'); plt.xlabel('Baskets per household'); plt.ylabel('Households'); plt.tight_layout(); plt.savefig(f'{CH}/03_basket_frequency.png',dpi=150); plt.close()
# concentration
sv=np.sort(hf.total_spend.values)[::-1]; cum=np.cumsum(sv)/sv.sum(); x=np.arange(1,len(sv)+1)/len(sv); plt.figure(figsize=(7,6)); plt.plot(x,cum); plt.plot([0,1],[0,1],linestyle='--'); plt.title('Customer value concentration'); plt.xlabel('Share of households'); plt.ylabel('Share of spend'); plt.tight_layout(); plt.savefig(f'{CH}/04_value_concentration.png',dpi=150); plt.close()
# retention matrix by first active week cohort and later activity
cohort=hhw.groupby('household_key').WEEK_NO.min().rename('cohort'); tmp=hhw.merge(cohort,on='household_key'); tmp['age']=tmp.WEEK_NO-tmp.cohort; ret=tmp[tmp.age.between(0,12)].groupby(['cohort','age']).household_key.nunique().unstack(fill_value=0); ret=ret.div(ret[0],axis=0); plt.figure(figsize=(10,7)); plt.imshow(ret.iloc[:30,:13],aspect='auto'); plt.colorbar(label='Repeat active rate'); plt.title('Retention / repeat activity heatmap'); plt.xlabel('Weeks since first activity'); plt.ylabel('Cohort week'); plt.tight_layout(); plt.savefig(f'{CH}/05_retention_heatmap.png',dpi=150); plt.close()
# category trend
trend=cw[cw['DEPARTMENT'].notna()].groupby(['DEPARTMENT','WEEK_NO']).product_sales.sum().reset_index(); topdept=cat.groupby('DEPARTMENT').product_sales.sum().nlargest(8).index; plt.figure(figsize=(10,6));
for d in topdept: q=trend[trend.DEPARTMENT==d]; plt.plot(q.WEEK_NO,q.product_sales,label=str(d))
plt.legend(fontsize=7); plt.title('Top department sales trends'); plt.xlabel('Week'); plt.ylabel('Sales'); plt.tight_layout(); plt.savefig(f'{CH}/06_category_trends.png',dpi=150); plt.close()
# penetration vs spend: use unique household counts approximated across whole period; better category households from transaction aggregation sums over weeks overcounts. Recompute distinct households per category via hc.
cat_hh=hc.groupby('COMMODITY_DESC').household_key.nunique() if 'household_key' in hc.columns else None
# use commodity table from hc
chh=hc.groupby('COMMODITY_DESC').agg(households=('household_key','nunique'),sales=('SALES_VALUE','sum')).reset_index(); chh['penetration']=chh.households/all_hh; chh['avg_spend_per_hh']=chh.sales/chh.households
plt.figure(figsize=(9,6)); plt.scatter(chh.penetration,chh.avg_spend_per_hh,s=20); plt.title('Category household penetration vs spend per buyer'); plt.xlabel('Household penetration'); plt.ylabel('Spend per purchasing household'); plt.tight_layout(); plt.savefig(f'{CH}/07_category_penetration_spend.png',dpi=150); plt.close()
# discount vs spend
plt.figure(figsize=(8,6)); plt.scatter(hf.discount_rate.clip(0,.5),hf.total_spend.clip(0,hf.total_spend.quantile(.99)),s=8,alpha=.3); plt.title('Discount rate vs household spend'); plt.xlabel('Discount rate'); plt.ylabel('Total spend (99th percentile capped)'); plt.tight_layout(); plt.savefig(f'{CH}/08_discount_vs_spend.png',dpi=150); plt.close()
# campaign funnel
cm=camp_mart.copy(); plt.figure(figsize=(9,5)); plt.bar(cm.CAMPAIGN.astype(str),cm.exposed_households); plt.title('Campaign exposed households'); plt.xlabel('Campaign'); plt.ylabel('Exposed households'); plt.tight_layout(); plt.savefig(f'{CH}/09_campaign_exposure.png',dpi=150); plt.close()
# coefficients
coef=pd.Series(lr.coef_[0],index=model_cols).sort_values(); plt.figure(figsize=(8,5)); plt.barh(coef.index,coef.values); plt.title('Baseline logistic model coefficients: future active flag'); plt.xlabel('Coefficient'); plt.tight_layout(); plt.savefig(f'{CH}/10_feature_coefficients.png',dpi=150); plt.close()
# uncertainty
plt.figure(figsize=(7,5)); plt.errorbar(['Avg basket value'],[vals.mean()],yerr=[[vals.mean()-ci_basket[0]],[ci_basket[1]-vals.mean()]],fmt='o'); plt.title('Bootstrap 95% CI for household average basket value'); plt.ylabel('Value'); plt.tight_layout(); plt.savefig(f'{CH}/11_bootstrap_uncertainty.png',dpi=150); plt.close()

summary={
 'transaction_rows':row_count,'bad_quantity_rows':bad_qty,'nonpositive_sales_rows':bad_sales,'transactions_missing_product':missing_prod,
 'distinct_baskets':int(baskets.BASKET_ID.nunique()),'distinct_households':all_hh,'distinct_products':int(prod.PRODUCT_ID.nunique()),'stores':int(baskets.STORE_ID.nunique()),
 'campaigns':int(camp_desc.CAMPAIGN.nunique()),'campaign_exposure_rows':int(len(camp_table)),'coupons':int(coupon.COUPON_UPC.nunique()),'coupon_redemptions':int(len(red)),
 'causal_rows':int(sum(1 for _ in open(f'{RAW}/causal_data.csv'))-1),'weeks':wmax,'days':int(baskets.DAY.max()),'demo_households':demo_hh,
 'demo_coverage':demo_hh/all_hh,'total_sales':float(baskets.basket_spend.sum()),'total_units':float(baskets.basket_units.sum()),'avg_basket':float(baskets.basket_spend.mean()),'median_basket':float(baskets.basket_spend.median()),
 'repeat_rate':float(repeat_rate),'repeat_ci':list(map(float,ci_repeat)),'bootstrap_avg_basket_ci':list(map(float,ci_basket)),
 'paired_spend_mean_change':float(diff),'paired_t_pvalue':float(t.pvalue),'paired_effect_d':float(effect_d),'paired_n':int(len(paired)),
 'exposed_households':int(len(ex)),'unexposed_households':int(len(un)),'exposed_vs_unexposed_change_p':float(mw.pvalue) if mw else None,
 'customer_category_matrix_rows':int(mat.shape[0]),'customer_category_matrix_cols':int(mat.shape[1]),'matrix_sparsity':sparsity,'pca_explained_5_or_less':float(pca.explained_variance_ratio_.sum()),
 'feature_rows':int(len(feat)),'future_active_rate':float(feat.future_active_flag.mean()),'baseline_model_auc_in_sample':float(auc),
 'discount_rate_median':float(hf.discount_rate.median()),'high_value_threshold':float(hf.total_spend.quantile(.8)), 'at_risk_count':int(hf.at_risk_flag.sum()),
 'coupon_redemption_total':int(len(red)), 'campaign_types':camp_desc.DESCRIPTION.value_counts().to_dict()
}
with open(f'{REP}/data_summary.json','w') as f: json.dump(summary,f,indent=2)
print(json.dumps(summary,indent=2))
