# Uncertainty in the out-of-sample medians of article Table 3 (supplement Appendix D).
# Usage: python median_uncertainty.py results/out_of_sample_llm_alone_results.csv > results/median_uncertainty.txt
# Resamples whole questions (or Twin outcomes) with replacement, because results for the same question are not independent.
import sys, numpy as np, pandas as pd
o = pd.read_csv(sys.argv[1])
moe = lambda e: 100 * (np.sqrt(300 / e) - 1)
rng = np.random.default_rng(20261114); B = 4000
gs = o[o.src == 'GSS']
sets = [('GSS, single answers', gs[gs['style'] == 'A']),
        ('GSS, stated probabilities without Llama 3.1 8B', gs[(gs['style'] == 'C') & (gs.model != 'llama3.1-8b')]),
        ('Twin-2K-500', o[o.src == 'Twin'])]
for name, d in sets:
    groups = {q: g.loo.values for q, g in d.groupby('q')}; keys = list(groups)
    meds = [np.median(np.concatenate([groups[k] for k in rng.choice(keys, len(keys))])) for _ in range(B)]
    lo, hi = np.percentile(meds, [2.5, 97.5])
    nar = int((d.loo > 300.5).sum()); wid = int((d.loo < 299.5).sum())
    print(f"{name}: {len(d)} results; narrower {nar}, wider {wid}, within half an interview of 300 {len(d) - nar - wid}")
    print(f"  median equivalent {d.loo.median():.1f} (margin of error {moe(d.loo.median()):+.1f}%); "
          f"95% range of the median {lo:.1f} to {hi:.1f} (margin of error {moe(lo):+.1f}% to {moe(hi):+.1f}%)")
p = gs.pivot_table(index=['model', 'style', 'q'], columns='seed', values='loo')
diff = (p.iloc[:, 0].map(moe) - p.iloc[:, 1].map(moe)).abs()
print(f"Run-to-run difference, out of sample (points of margin of error): median {diff.median():.2f}, maximum {diff.max():.1f}; {(diff < 0.5).sum()} of {len(diff)} pairs differ by less than 0.5")
print("Largest differences:")
print(diff.sort_values().tail(8).round(1).to_string())
