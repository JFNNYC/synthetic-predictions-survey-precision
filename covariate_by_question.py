"""Regression on the seven profile facts, fitted only on each GSS question's own respondents (about 100),
evaluated out of sample by leave-one-out. One result per question (10 questions). Reports the median
precision-equivalent and margin-of-error change across penalty settings and two codings of the facts."""
import sys, runpy, numpy as np, pandas as pd
sys.argv = ['x', sys.argv[1], sys.argv[2]]
g = runpy.run_path(__import__('os').path.join(__import__('os').path.dirname(__file__), 'covariate_benchmark.py'), run_name='lib')
L, facts, loo_r2 = g['L'], g['facts'], g['loo_r2']
P = L.drop_duplicates(['respondent_id', 'question_id'])
def small(d):
    return np.column_stack([(d.age.values - 48) / 17.0, (d.sex.values == 2).astype(float), d.degree.values.astype(float),
                            d.polviews.values.astype(float), np.where(d.partyid.values <= 6, d.partyid.values, 3).astype(float)])
moe = lambda e: 100 * (np.sqrt(300 / e) - 1)
rows = []
for name, fx in [('all seven facts', facts), ('five numeric facts', small)]:
    for lam in [1, 10, 50, 200]:
        eqs = []
        for q, gg in P.groupby('question_id'):
            eqs.append(300 / (1 - loo_r2(gg.y.values.astype(float), fx(gg), lam)))
        m = float(np.median(eqs)); rows.append(dict(coding=name, penalty=lam, median_eq=round(m, 1), moe_change=round(moe(m), 1), n_questions=len(eqs)))
R = pd.DataFrame(rows); print(R.to_string(index=False)); R.to_csv(sys.argv[2] + '/covariate_by_question.csv', index=False)
print('respondents per question:', P.groupby('question_id').size().to_dict())
