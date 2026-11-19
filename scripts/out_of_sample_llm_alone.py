import json, glob, sys, os, numpy as np, pandas as pd
B, T, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
YES = {'abany':[1],'cappun':[1],'grass':[1],'gunlaw':[1],'happy':[1],'trust':[1],'helpful':[1],'fair':[2],'fefam':[1,2],'confinan':[1]}
def eqs(y, f):
    n = len(y); vy = y.var()
    r = np.corrcoef(y, f)[0, 1] if f.std() > 0 and y.std() > 0 else 0.0
    ins = 300 / (1 - r**2)
    adj = max(0.0, 1 - (1 - r**2) * (n - 1) / (n - 2)); adjeq = 300 / (1 - adj)
    # leave-one-out regression of y on f (intercept + slope), out-of-sample R^2 relative to LOO mean
    e = []; e0 = []
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        yy, ff = y[m], f[m]
        if ff.std() > 0:
            b = np.cov(ff, yy, ddof=1)[0, 1] / ff.var(ddof=1); a = yy.mean() - b * ff.mean()
        else:
            b, a = 0.0, yy.mean()
        e.append(y[i] - (a + b * f[i])); e0.append(y[i] - yy.mean())
    r2o = 1 - np.sum(np.square(e)) / np.sum(np.square(e0))
    return ins, adjeq, 300 / (1 - r2o) if r2o < 1 else np.inf, 300 / (1 - max(0.0, r2o))
rows = []
L = pd.DataFrame([json.loads(l) for p in glob.glob(B + '/llm_runs/*.jsonl') for l in open(p) if l.strip()])
L = L[L.valid.astype(str) == 'True']
for (m, s, sd, q), g in L.groupby(['model_name', 'style', 'seed', 'question_id']):
    y = g.human_answer.astype(int).isin(YES[q]).astype(float).values
    if s == 'A': f = g.pred.astype(int).isin(YES[q]).astype(float).values
    else:
        f = np.array([sum(float(v) for k, v in (d if isinstance(d, dict) else json.loads(d)).items() if int(k) in YES[q]) /
                      sum(float(v) for v in (d if isinstance(d, dict) else json.loads(d)).values()) for d in g.dist])
    a, b, c, d = eqs(y, f); rows.append(dict(src='GSS', style=s, model=m, q=q, seed=sd, n=len(y), ins=a, adj=b, loo=c, loo_floor=d))
for fn in sorted(glob.glob(T + '/*/test/*individual level.csv')):
    dd = pd.read_csv(fn)
    for v, g in dd.groupby('variable_name'):
        h = g[g.respondent_type == 'human'].set_index('TWIN_ID').value
        t = g[g.respondent_type == 'twin'].set_index('TWIN_ID').value
        hv = pd.to_numeric(h, errors='coerce').dropna()
        if hv.nunique() != 2: continue
        mm = pd.concat([h, t], axis=1, keys=['h', 't'], join='inner').apply(pd.to_numeric, errors='coerce').dropna()
        lv = sorted(hv.unique()); y = (mm.h == lv[1]).astype(float).values; f = (mm.t == lv[1]).astype(float).values
        a, b, c, d = eqs(y, f); rows.append(dict(src='Twin', style='A', model='twin', q=v, seed=0, n=len(y), ins=a, adj=b, loo=c, loo_floor=d))
R = pd.DataFrame(rows); R.to_csv(OUT, index=False)
for (src, s), g in R.groupby(['src', 'style']):
    print(src, s, len(g), 'median in-sample %.1f adj %.1f LOO %.1f LOO(floor) %.1f | LOO>300: %d' % (g.ins.median(), g.adj.median(), g.loo.median(), g.loo_floor.median(), (g.loo > 300).sum()))
g = R[(R.src == 'GSS') & (R.model != 'llama3.1-8b')]
for s, h in g.groupby('style'): print('three models', s, 'median LOO %.1f' % h.loo.median())
