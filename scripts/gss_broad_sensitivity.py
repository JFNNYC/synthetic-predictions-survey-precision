"""RECONSTRUCTED RELEASE HELPER.

Broader-recoding GSS sensitivity analysis reported in supplement Appendix D.

Usage:
    python scripts/gss_broad_sensitivity.py GSS_BUILD output.csv

The original later helper script was not recoverable as a standalone file during final package assembly. This convenience implementation follows the recoding and summary definitions documented in the final supplement. The frozen summary CSV is the authoritative released artifact.

The script reads the four released GSS JSONL model-output files and applies the
post-hoc broader binary recoding documented in the supplement. It reports the
summary rows used for the sensitivity diagnostic. Bootstrap intervals use seed
20261030 and 2,000 resamples, matching the article's other cell-level checks.
"""
import json, glob, sys
import numpy as np
import pandas as pd

if len(sys.argv) != 3:
    raise SystemExit("usage: python scripts/gss_broad_sensitivity.py GSS_BUILD output.csv")
BASE, OUT = sys.argv[1], sys.argv[2]
N = 300
B = 2000
SEED = 20261030

# Natural binaries unchanged. Five non-natural binary items use the broader
# yes category described in Appendix D; fefam was already broad (agree/strongly agree).
YES = {
    'abany': {1},
    'cappun': {1},
    'grass': {1},
    'gunlaw': {1},
    'happy': {1, 2},                 # very or pretty happy
    'trust': {1, 3},                 # can be trusted or depends
    'helpful': {1, 3},               # helpful or depends
    'fair': {2, 3},                  # fair or depends
    'confinan': {1, 2},              # great deal or only some confidence
    'fefam': {1, 2},                 # strongly agree or agree
}

def _dist(d):
    return d if isinstance(d, dict) else json.loads(d)

def cell_stats(y, f):
    y = np.asarray(y, float); f = np.asarray(f, float)
    vy = y.var()
    e = y - f
    ve = e.var()
    sy, sf = y.std(), f.std()
    rho = np.corrcoef(y, f)[0, 1] if sy > 0 and sf > 0 else 0.0
    full = N * vy / ve if ve > 0 else np.inf
    partial = N / (1 - rho**2) if abs(rho) < 1 else np.inf
    n = len(y)
    # adjusted correlation / adjusted-R^2 equivalent used in the diagnostic table
    adj_r2 = max(0.0, 1 - (1 - rho**2) * (n - 1) / (n - 2)) if n > 2 else 0.0
    adjusted = N / (1 - adj_r2) if adj_r2 < 1 else np.inf
    return vy, ve, rho, full, partial, adjusted

rng = np.random.default_rng(SEED)
rows = []
files = sorted(glob.glob(f"{BASE}/llm_runs/*.jsonl"))
if not files:
    raise FileNotFoundError(f"no JSONL model files found under {BASE}/llm_runs")
for fn in files:
    df = pd.DataFrame([json.loads(line) for line in open(fn, encoding='utf-8') if line.strip()])
    model = fn.rsplit('/', 1)[-1].replace('.jsonl', '')
    for q, top in YES.items():
        for style in ['A', 'C']:
            for seed in [0, 1]:
                x = df[(df.question_id == q) & (df.seed == seed) & (df['style'] == style)]
                x = x[x.valid == True]
                if x.empty:
                    continue
                y = x.human_answer.isin(top).astype(float).to_numpy()
                if style == 'A':
                    f = x.pred.isin(top).astype(float).to_numpy()
                else:
                    f = np.array([
                        sum(float(_dist(d).get(str(k), 0.0)) for k in top) /
                        max(sum(float(v) for v in _dist(d).values()), 1e-12)
                        for d in x.dist
                    ])
                vy, ve, rho, full, partial, adjusted = cell_stats(y, f)
                boots = []
                for _ in range(B):
                    ii = rng.integers(0, len(y), len(y))
                    boots.append(cell_stats(y[ii], f[ii])[3])
                rows.append({
                    'model': model, 'question': q, 'style': style, 'seed': seed, 'n': len(y),
                    'full_eq': full, 'partial_eq': partial, 'adjusted_eq': adjusted,
                    'full_interval_lo': float(np.percentile(boots, 2.5)),
                    'full_interval_hi': float(np.percentile(boots, 97.5)),
                })

cells = pd.DataFrame(rows)
summary = []
for style, label in [('A', 'Single answer'), ('C', 'Probability')]:
    g = cells[cells['style'] == style]
    summary.append({
        'analysis': 'Broader recoding',
        'prediction_type': label,
        'results': int(len(g)),
        'fw_improves': int((g.full_eq > N).sum()),
        'fw_interval_above_300': int((g.full_interval_lo > N).sum()),
        'median_fw_equivalent': float(g.full_eq.median()),
        'median_pw_equivalent': float(g.partial_eq.median()),
        'median_pw_equivalent_adjusted_correlation': float(g.adjusted_eq.median()),
    })
S = pd.DataFrame(summary)
S.to_csv(OUT, index=False)
print(S.to_string(index=False))
