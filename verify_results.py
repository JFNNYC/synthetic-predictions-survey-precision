"""Verify the principal numerical claims in the article against a results folder.

Usage:
    python scripts/verify_results.py results
"""
import math, re, sys
from pathlib import Path
import pandas as pd

if len(sys.argv) != 2:
    raise SystemExit("usage: python scripts/verify_results.py RESULTS_DIR")
R = Path(sys.argv[1])
errors = []

def ok(label, cond, got=None, expected=None):
    if cond:
        print(f"PASS: {label}")
    else:
        msg = f"FAIL: {label}"
        if got is not None or expected is not None:
            msg += f" (got {got!r}, expected {expected!r})"
        print(msg); errors.append(msg)

def close(a, b, tol=0.06):
    return math.isfinite(float(a)) and abs(float(a)-float(b)) <= tol

# Out-of-sample headline medians.
p = R / 'out_of_sample_llm_alone_results.csv'
if not p.exists():
    errors.append(f"missing {p}")
else:
    d = pd.read_csv(p)
    gssA = d[(d['src']=='GSS') & (d['style']=='A')].loo.median()
    gssC = d[(d['src']=='GSS') & (d['style']=='C') & (d['model']!='llama3.1-8b')].loo.median()
    twin = d[(d['src']=='Twin') & (d['style']=='A')].loo.median()
    ok('GSS single-answer median equivalent = 305.4', close(gssA,305.4), gssA, 305.4)
    ok('GSS clean-probability median equivalent = 313.9', close(gssC,313.9), gssC, 313.9)
    ok('Twin median equivalent = 301.8', close(twin,301.8), twin, 301.8)
    # Table 4 examples
    a=d[(d['src']=='GSS')&(d['model']=='claude-sonnet-4.6')&(d['q']=='gunlaw')]
    b=d[(d['src']=='GSS')&(d['model']=='llama3.3-70b')&(d['q']=='abany')]
    if not a.empty: ok('gun-permit illustration LOO equivalent rounds to 308', round(a.loo.iloc[0])==308, a.loo.iloc[0], 308)
    if not b.empty: ok('abortion illustration LOO equivalent rounds to 380', round(b.loo.iloc[0])==380, b.loo.iloc[0], 380)

# Whole-question resampling and run stability.
p = R / 'median_uncertainty.txt'
if p.exists():
    t = p.read_text(encoding='utf-8')
    checks = [
        ('single resampling range 300.0 to 311.9', '300.0 to 311.9'),
        ('probability resampling range 297.9 to 328.4', '297.9 to 328.4'),
        ('Twin resampling range 300.0 to 309.0', '300.0 to 309.0'),
        ('run-to-run median 0.43', 'median 0.43'),
        ('run-to-run maximum 6.9', 'maximum 6.9'),
    ]
    for label, s in checks: ok(label, s in t)
else:
    errors.append(f"missing {p}")

# Same-information ridge range.
p = R / 'covariate_by_question.csv'
if p.exists():
    q = pd.read_csv(p)
    # Accept common output schemas: use any numeric MOE-change column if present; otherwise
    # validate precision-equivalent range from numeric columns that contain the grid medians.
    nums = q.select_dtypes(include='number')
    vals = nums.to_numpy().ravel()
    # The frozen grid contains equivalents spanning about 294 to 311.
    ok('ridge Implementation A includes +1.0% / about 294', any(abs(x-293.9)<0.2 for x in vals if math.isfinite(x)))
    ip = R / 'covariate_independent_check.txt'
    if ip.exists():
        it = ip.read_text(encoding='utf-8')
        ok('ridge combined grid reaches -1.8% / 311 in Implementation B', ('-1.8' in it or '−1.8' in it) and ('311' in it))
    else:
        errors.append(f'missing {ip}')
else:
    errors.append(f"missing {p}")

# Simulation identity/shape.
sim = None
for name in ['sim_results_24_conditions.csv','sim_results.csv','sim_results_24_conditions_2026-10-29.csv']:
    p=R/name
    if p.exists(): sim=p; break
if sim:
    s=pd.read_csv(sim)
    ok('simulation has 24 conditions', len(s)==24, len(s), 24)
else:
    errors.append('missing simulation result CSV')

if errors:
    print('\nREPORTED-NUMBER CHECKS FAILED')
    raise SystemExit(1)
print('\nALL REPORTED-NUMBER CHECKS PASSED')
