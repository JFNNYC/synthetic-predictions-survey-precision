"""Covariate-only regression estimator vs LLM predictions, GSS benchmark.
For each of the 160 GSS results (model x format x run x question), on that result's usable pairs:
  - LLM alone: OLS of y on f, leave-one-out cross-fitted R^2
  - Covariates alone: ridge regression of y on the seven profile facts, fitted on the same human pairs, LOO
  - Covariates + LLM: ridge on facts plus f, LOO
Equivalent sample size for 300 interviews = 300 / (1 - R2_loo); margin-of-error change = sqrt(300/eq) - 1.
"""
import sys, json, glob
import numpy as np, pandas as pd
B = sys.argv[1]; OUT = sys.argv[2]
YES = {'abany': [1], 'cappun': [1], 'grass': [1], 'gunlaw': [1], 'happy': [1], 'trust': [1],
       'helpful': [1], 'fair': [2], 'fefam': [1, 2], 'confinan': [1]}
S = pd.read_parquet(f'{B}/pilot_sample.parquet')
S['y'] = [int(a in YES[q]) for a, q in zip(S.answer_code, S.question_id)]
L = pd.DataFrame([json.loads(l) for p in glob.glob(f'{B}/llm_runs/*.jsonl') for l in open(p) if l.strip()])
L['respondent_id'] = L['respondent_id'].astype(str)
L = L[L['valid'] == True].copy()
def fpred(r):
    q = r['question_id']
    if r['style'] == 'A':
        return float(int(r['pred']) in YES[q])
    d = r['dist']; tot = sum(float(v) for v in d.values())
    return sum(float(d.get(str(c), 0.0)) for c in YES[q]) / tot
L['f'] = L.apply(fpred, axis=1)
S['respondent_id'] = S['respondent_id'].astype(str)
cov = ['age', 'sex', 'race', 'degree', 'region', 'polviews', 'partyid']
L = L.merge(S[['respondent_id', 'question_id', 'y'] + cov], on=['respondent_id', 'question_id'], validate='m:1')

def facts(d):
    # compact coding: age (scaled), female, race dummies, degree/polviews/partyid as ordinal scores, region dummies
    cols = [(d.age.values - 48) / 17.0, (d.sex.values == 2).astype(float)]
    for lv in [2, 3]: cols.append((d.race.values == lv).astype(float))
    cols += [d.degree.values.astype(float), d.polviews.values.astype(float), np.where(d.partyid.values <= 6, d.partyid.values, 3).astype(float)]
    for lv in range(2, 10): cols.append((d.region.values == lv).astype(float))
    X = np.column_stack(cols)
    return X

def loo_r2(y, X, lam):
    n = len(y)
    if np.var(y) == 0: return 0.0
    Xc = np.column_stack([np.ones(n), X])
    P = lam * np.eye(Xc.shape[1]); P[0, 0] = 0
    pred = np.empty(n)
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        Xt, yt = Xc[m], y[m]
        mu, sd = Xt[:, 1:].mean(0), Xt[:, 1:].std(0); sd[sd == 0] = 1
        Zt = np.column_stack([np.ones(n - 1), (Xt[:, 1:] - mu) / sd])
        b = np.linalg.solve(Zt.T @ Zt + P, Zt.T @ yt)
        pred[i] = np.r_[1, (Xc[i, 1:] - mu) / sd] @ b
    e0 = np.array([y[i] - (y.sum() - y[i]) / (n - 1) for i in range(n)])  # baseline: leave-one-out human mean, as in the paper's out-of-sample analysis
    return 1 - np.sum((y - pred) ** 2) / np.sum(e0 ** 2)

rows = []
for (mo, st, sd, q), g in L.groupby(['model_name', 'style', 'seed', 'question_id']):
    y = g.y.values.astype(float); f = g.f.values.reshape(-1, 1); X = facts(g)
    r_llm = loo_r2(y, f, 1e-8)
    r_cov = loo_r2(y, X, 10.0)
    r_both = loo_r2(y, np.column_stack([X, f]), 10.0)
    rows.append(dict(model=mo, style=st, seed=sd, q=q, n=len(y), r2_llm=r_llm, r2_cov=r_cov, r2_both=r_both))
R = pd.DataFrame(rows)
for c in ['llm', 'cov', 'both']:
    R[f'eq_{c}'] = 300 / (1 - R[f'r2_{c}'])
R.to_csv(f'{OUT}/covariate_benchmark_results.csv', index=False)
moe = lambda e: 100 * (np.sqrt(300 / e) - 1)
def summ(d, lab):
    print(f'{lab}: n results={len(d)}')
    for c in ['llm', 'cov', 'both']:
        e = d[f'eq_{c}']
        print(f'   {c:5s} median eq {e.median():6.1f}  (MOE {moe(e.median()):+.1f}%)   mean eq {e.mean():6.1f}   share>300 {np.mean(e > 300):.2f}')
    print(f'   both minus cov: median {np.median(d.eq_both - d.eq_cov):+.1f}, mean {np.mean(d.eq_both - d.eq_cov):+.1f};  llm>cov in {np.mean(d.eq_llm > d.eq_cov):.2f} of results')
summ(R[R['style'] == 'A'], 'Single answers')
summ(R[R['style'] == 'C'], 'Stated probabilities')
summ(R[(R['style'] == 'C') & (R.model != 'llama3.1-8b')], 'Stated probabilities, without Llama 3.1 8B')
