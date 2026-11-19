# Produces results/gss_160_cells.csv: all 160 GSS diagnostic results used in Supplement Appendix D, seed 20261030, 2,000 bootstrap draws.
# Usage: python gss_recompute.py GSS_BUILD results/gss_160_cells.csv
import json,sys,math
import numpy as np,pandas as pd
base=sys.argv[1]; out=sys.argv[2]
TOP={'abany':{1},'cappun':{1},'grass':{1},'gunlaw':{1},'happy':{1},'trust':{1},'helpful':{1},'confinan':{1},'fair':{2},'fefam':{1,2}}
rng=np.random.default_rng(20261030); B=2000; N=300
def stats(Y,F):
    vy=Y.var(); e=Y-F; ve=e.var()
    sf=F.std(); sy=Y.std()
    rho=np.corrcoef(Y,F)[0,1] if sf>0 and sy>0 else 0.0
    full=N*vy/ve if ve>0 else np.inf
    part=N/(1-rho**2)
    return vy,ve,rho,full,part
rows=[]
for m in ['claude-sonnet-4.6','claude-haiku-4.5','llama3.3-70b','llama3.1-8b']:
    df=pd.DataFrame([json.loads(l) for l in open(f'{base}/llm_runs/{m}.jsonl')])
    for q,top in TOP.items():
        for st in ['A','C']:
            for s in [0,1]:
                x=df[(df.question_id==q)&(df.seed==s)&(df['style']==st)]
                ntot=len(x); x=x[x.valid==True]
                Y=x.human_answer.isin(top).astype(float).to_numpy()
                if st=='A': F=x.pred.isin(top).astype(float).to_numpy()
                else: F=np.array([sum(float(d.get(str(k),0)) for k in top)/max(sum(float(v) for v in d.values()),1e-9) for d in x.dist])
                n=len(Y); vy,ve,rho,full,part=stats(Y,F)
                bf=[];bp=[]
                for _ in range(B):
                    i=rng.integers(0,n,n); r=stats(Y[i],F[i]); bf.append(r[3]); bp.append(r[4])
                rows.append(dict(model=m,item=q,style=st,seed=s,n_total=ntot,n=n,human=Y.mean(),pred=F.mean(),
                    agree=(1-np.mean(np.abs(Y-F))) if st=='A' else np.nan,vy=vy,ve=ve,rho=rho,
                    full_eq=full,full_lo=np.percentile(bf,2.5),full_hi=np.percentile(bf,97.5),
                    part_eq=part,part_lo=np.percentile(bp,2.5),part_hi=np.percentile(bp,97.5),
                    passes=ve<vy,clear_full=np.percentile(bf,2.5)>300,clear_part=np.percentile(bp,2.5)>300))
R=pd.DataFrame(rows); R.to_csv(out,index=False)
pd.set_option('display.width',250)
print(R.round(3).to_string(index=False))
