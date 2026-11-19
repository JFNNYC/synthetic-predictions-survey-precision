import numpy as np, csv
rng=np.random.default_rng(20261029)
n=300; R=5000; z=1.96
rows=[]
for p in (.20,.35,.50,.65):
  for d in (.05,.15,.30):
    for b in (0.0,0.03):
      p10=(d+b)/2; p01=(d-b)/2; p11=p-p01; p00=1-p11-p10-p01
      probs=[p11,p10,p01,p00]; mu_f=p+b
      Y=np.empty((R,n)); F=np.empty((R,n))
      cat=rng.choice(4,size=(R,n),p=probs)
      F=np.isin(cat,[0,1]).astype(float); Y=np.isin(cat,[0,2]).astype(float)
      # human-only
      h=Y.mean(1); hse=np.sqrt(Y.var(1,ddof=1)/n)
      # full weight
      e=F-Y; fw=mu_f-e.mean(1); fse=np.sqrt(e.var(1,ddof=1)/n)
      # partial weight (regression / PPI++ with estimated weight)
      cfy=((F-F.mean(1,keepdims=True))*(Y-Y.mean(1,keepdims=True))).sum(1)/(n-1)
      vf=F.var(1,ddof=1); lam=cfy/vf
      pw=h+lam*(mu_f-F.mean(1)); res=Y-lam[:,None]*F
      pse=np.sqrt(res.var(1,ddof=1)/n)
      vy=p*(1-p); vf0=mu_f*(1-mu_f); cov0=p11-p*mu_f; rho2=cov0**2/(vy*vf0)
      def st(est,se):
        return est.mean()-p, est.std(), np.mean(np.abs(est-p)<=z*se)
      out=dict(p=p,disagree=d,bias=b)
      for k,(est,se) in dict(human=(h,hse),full=(fw,fse),partial=(pw,pse)).items():
        bi,sd,cv=st(est,se); out[k+'_bias']=bi; out[k+'_sd']=sd; out[k+'_cov']=cv
      out['full_neq_formula']=n*vy/(d-b*b); out['partial_neq_formula']=n/(1-rho2)
      out['full_neq_sim']=vy/out['full_sd']**2; out['partial_neq_sim']=vy/out['partial_sd']**2
      rows.append(out)
with open('sim_results.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
for r in rows:
  print(f"p={r['p']:.2f} d={r['disagree']:.2f} b={r['bias']:.2f} | H sd={100*r['human_sd']:.2f} cov={r['human_cov']:.3f} | FW bias={100*r['full_bias']:+.2f} sd={100*r['full_sd']:.2f} cov={r['full_cov']:.3f} neq f={r['full_neq_formula']:.0f} s={r['full_neq_sim']:.0f} | PW bias={100*r['partial_bias']:+.2f} cov={r['partial_cov']:.3f} neq f={r['partial_neq_formula']:.0f} s={r['partial_neq_sim']:.0f}")
