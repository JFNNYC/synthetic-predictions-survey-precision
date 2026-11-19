# Independent second implementation of the same-facts regression check (Appendix D). Usage: python covariate_independent_check.py GSS_BUILD results
import sys, json, glob, numpy as np, pandas as pd
B = sys.argv[1]
h = pd.read_parquet(B + '/pilot_sample.parquet')
YES = {'abany': [1], 'cappun': [1], 'grass': [1], 'gunlaw': [1], 'happy': [1], 'trust': [1],
       'helpful': [1], 'fair': [2], 'fefam': [1, 2], 'confinan': [1]}
h['y'] = [int(a in YES[q]) for q, a in zip(h.question_id, h.answer_code)]

def z(v): v = np.asarray(v, float); s = v.std(); return (v - v.mean()) / s if s > 0 else v * 0
def dummies(v, drop_first=True):
    cats = sorted(set(v)); cats = cats[1:] if drop_first else cats
    return [np.asarray([int(x == c) for x in v], float) for c in cats]
def X_seven(d):
    cols = [z(d.age), z(np.asarray(d.age, float) ** 2), z(d.sex == 2)]
    cols += dummies(list(d.race)) + [z(d.degree), z(d.polviews), z(d.partyid)] + dummies(list(d.region))
    return np.column_stack(cols)
def X_five(d):
    return np.column_stack([z(d.age), z(d.sex == 2), z(d.degree), z(d.polviews), z(d.partyid)])

def loo_eq(y, X, lam, n_nom=300):
    """Ridge with unpenalized intercept; exact leave-one-out by refitting; baseline = leave-one-out mean."""
    y = np.asarray(y, float); n = len(y); pred = np.empty(n)
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        Xt, yt = X[m], y[m]; mu = Xt.mean(0); ym = yt.mean()
        A = (Xt - mu); beta = np.linalg.solve(A.T @ A + lam * np.eye(X.shape[1]), A.T @ (yt - ym))
        pred[i] = ym + (X[i] - mu) @ beta
    loo_mean = (y.sum() - y) / (n - 1)
    r2 = 1 - ((y - pred) ** 2).sum() / ((y - loo_mean) ** 2).sum()
    return n_nom / (1 - r2)

out = []
for coding, f in [('seven', X_seven), ('five', X_five)]:
    for lam in [1, 10, 50, 200]:
        vals = [loo_eq(g.y.values, f(g), lam) for q, g in h.groupby('question_id')]
        out.append((coding, lam, np.median(vals)))
print('Regression alone, median precision equivalent across 10 questions:')
for c, l, v in out: print(f'  {c:5s} lambda={l:<4d} {v:6.1f}  MOE change {np.sqrt(300 / v) - 1:+.2%}')

# LLM alone (lambda ~ 0) and LLM + seven-fact regression (lambda 10)
recs = []
for fn in glob.glob(B + '/llm_runs/*.jsonl'):
    for l in open(fn):
        d = json.loads(l)
        if str(d['valid']) != 'True': continue
        q = d['question_id']
        if d['style'] == 'A': p = float(int(str(d['pred'])) in YES[q])
        else: p = sum(v for k, v in d['dist'].items() if int(k) in YES[q])
        recs.append((d['model_name'], d['style'], str(d['seed']), d['respondent_id'], q, p))
L = pd.DataFrame(recs, columns=['model', 'style', 'seed', 'respondent_id', 'question_id', 'f'])
res = []
for (m, s, sd, q), g in L.groupby(['model', 'style', 'seed', 'question_id']):
    d = h[h.question_id == q].merge(g[['respondent_id', 'f']], on='respondent_id')
    fz = z(d.f).reshape(-1, 1)
    alone = loo_eq(d.y.values, fz, 1e-8)
    both = loo_eq(d.y.values, np.column_stack([X_seven(d), fz]), 10)
    cov = loo_eq(d.y.values, X_seven(d), 10)
    res.append((m, s, sd, q, len(d), alone, cov, both))
R = pd.DataFrame(res, columns=['model', 'style', 'seed', 'q', 'n', 'alone', 'regression', 'both'])
R.to_csv(sys.argv[2] + '/covariate_independent_check_cells.csv', index=False)
for s, lab in [('A', 'single'), ('C', 'prob, all models'), ('Cx', 'prob, excl. Llama 3.1 8B')]:
    sub = R[R['style'] == s[0]]
    if s == 'Cx': sub = sub[sub.model != 'llama3.1-8b']
    print(f'{lab:26s} n={len(sub):3d} LLM alone median {sub.alone.median():6.1f} ({np.sqrt(300/sub.alone.median())-1:+.2%})  regression alone median {sub.regression.median():6.1f}  LLM+regression median {sub.both.median():6.1f}')
x = R[(R.model == 'llama3.3-70b') & (R.q == 'abany') & (R['style'] == 'A')]; print(x)
x = R[(R.model == 'claude-sonnet-4.6') & (R.q == 'gunlaw') & (R['style'] == 'A')]; print(x)
