# Produces results/twin_13_binary.csv: the 13 Twin-2K-500 two-option outcomes used in Supplement Appendix D, seed 20261030, 2,000 bootstrap draws.
# Usage: python twin_recompute.py TWIN_DIR results/twin_13_binary.csv
import pandas as pd,glob,numpy as np,sys
root=sys.argv[1]; out=sys.argv[2]
D=pd.concat([pd.read_csv(f) for f in glob.glob(root+'/*/test/*individual level.csv')])
rng=np.random.default_rng(20261030); B=2000; N=300
def stats(Y,F):
    vy=Y.var(); ve=(Y-F).var()
    rho=np.corrcoef(Y,F)[0,1] if Y.std()>0 and F.std()>0 else 0.0
    return vy,ve,rho,(N*vy/ve if ve>0 else np.inf),N/(1-rho**2)
rows=[]
for (s,v),x in D.groupby(['study_name','variable_name']):
    h=x[x.respondent_type=='human']; t=x[x.respondent_type=='twin']
    if h.value.dropna().nunique()!=2: continue
    dup=h.TWIN_ID.duplicated().sum()+t.TWIN_ID.duplicated().sum()
    m=h[['TWIN_ID','value']].merge(t[['TWIN_ID','value']],on='TWIN_ID',suffixes=('_h','_t')).dropna()
    Y=m.value_h.to_numpy(float); F=m.value_t.to_numpy(float); n=len(Y)
    vy,ve,rho,full,part=stats(Y,F)
    bf=[];bp=[]
    for _ in range(B):
        i=rng.integers(0,n,n); r=stats(Y[i],F[i]); bf.append(r[3]); bp.append(r[4])
    rows.append(dict(study=s,item=v,n=n,dup_ids=int(dup),human=Y.mean(),twin=F.mean(),agree=(Y==F).mean(),vy=vy,ve=ve,rho=rho,
        full_eq=full,full_lo=np.percentile(bf,2.5),full_hi=np.percentile(bf,97.5),part_eq=part,part_lo=np.percentile(bp,2.5),part_hi=np.percentile(bp,97.5),passes=ve<vy))
R=pd.DataFrame(rows); R.to_csv(out,index=False)
pd.set_option('display.width',250); print(R.round(3).to_string(index=False))
print('passes',R.passes.sum(),'of',len(R),'median full',R.full_eq.median().round(),'median part',R.part_eq.median().round())
