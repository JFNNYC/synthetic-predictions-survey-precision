# Audit: regression on the same seven facts (article Table 3; supplement Appendix D5)

This file records everything needed to check the regression comparison in the article.

## Data (frozen)

GSS benchmark of Chen, Zhu, and Zheng (2026), repository version of October 4, 2026, folder `experiment/datasets/GSS/build`.

| File | SHA-256 |
|---|---|
| `pilot_sample.parquet` | `eef827ffeda773c2ee75fc5b330a01c8f8f813e74f1534f5c59ec3b93a4a2ba6` |
| `llm_runs/claude-haiku-4.5.jsonl` | `80b761ce73844a1528b6b51582f1a12c4cf2b016f01fe0c5ba9ab9aa1b659b30` |
| `llm_runs/claude-sonnet-4.6.jsonl` | `84fde2cee9f8c8bfc771124e3b166d30fbc325ad4e4380e755ab6ff0217a26ba` |
| `llm_runs/llama3.1-8b.jsonl` | `f3f05e6a9c31df245427c122ae6006ffc795510d4bc2ca6573e14825397d2b46` |
| `llm_runs/llama3.3-70b.jsonl` | `b5b866dfe282fb22670830bceb577389a814a6485486c13bb8a45dd1ad6cc8c0` |

## The ten questions and the "yes" category

| Question | Yes = answer code(s) | Respondents |
|---|---|---|
| abany (abortion for any reason) | 1 yes | 99 |
| cappun (death penalty) | 1 favor | 100 |
| confinan (confidence in banks) | 1 a great deal | 99 |
| fair (people try to be fair) | 2 would try to be fair | 99 |
| fefam (man works, woman tends home) | 1 strongly agree, 2 agree | 100 |
| grass (marijuana legal) | 1 should be legal | 100 |
| gunlaw (gun permits) | 1 favor | 100 |
| happy (very happy) | 1 very happy | 98 |
| helpful (people try to be helpful) | 1 try to be helpful | 99 |
| trust (most people can be trusted) | 1 can be trusted | 99 |

## Method (both implementations)

- Outcome: 1 if the answer is in the yes category, else 0.
- Predictors: the seven facts given to the LLMs (age, sex, race, degree, region, political views, party), in two codings: all seven facts, and five numeric facts (age, sex, degree, political views, party).
- Model: ridge-penalized linear regression with an unpenalized intercept, penalties 1, 10, 50, and 200.
- Fitted only on each question's own respondents (98 to 100 people).
- Out of sample: leave-one-out. For each respondent, the model is fitted on all others and predicts that respondent.
- Baseline: the leave-one-out human mean (the same baseline used for the LLM results).
- Precision equivalent for 300 interviews: 300 / (1 − R²), where R² = 1 − Σ(y − prediction)² / Σ(y − leave-one-out mean)². Margin-of-error change: sqrt(300 / equivalent) − 1. No floor at zero.
- Combined model: the seven-fact coding plus the LLM prediction as one more predictor, penalty 10, one fit per model, format, run, and question.

## Why the two implementations differ

| | Implementation A (`covariate_benchmark.py`, `covariate_by_question.py`) | Implementation B (`covariate_independent_check.py`) |
|---|---|---|
| Age | linear only | linear and squared |
| Party | "other party" (code 7) recoded as independent (3) | codes kept as recorded (0 to 7) |
| Scaling | every fact standardized within each leave-one-out fit | numeric facts standardized over the question's respondents; race and region indicators left as 0 or 1 |
| Written | first | separately, from the supplement's description |

These choices change how much each fact is penalized, which moves the medians by up to about 1 point of margin of error. Neither implementation tuned its penalty; both use the same fixed grid and report every setting.

## Answers to likely reviewer questions

- **The 16 settings.** Two codings (all seven facts; five numeric facts) times four penalties (1, 10, 50, 200) times two implementations.
- **Same respondents and questions?** Yes. Both read the same `pilot_sample.parquet` and use the same ten questions and yes categories. The 16 question-level settings use each question's respondents (98 to 100; Implementation A takes them from the respondents with at least one usable LLM answer, which here is every respondent, the same 98 to 100 used by Implementation B). In the combined comparison, LLM alone, regression alone, and regression plus LLM are all fitted on the same respondents for each result: those with a usable LLM answer for that model, format, and run.
- **Preprocessing.** It differs only in the three coding choices in the table above. Neither implementation drops or reweights respondents.
- **Was the penalty grid prespecified?** The grid was fixed when the check was written, which was after the LLM results were known. It was not tuned: no setting was chosen, and all 16 are reported. The comparison should be read as a sensitivity range, not a preregistered test.
- **Is the combined model evaluated the same way?** Yes: the same leave-one-out procedure, baseline, and precision-equivalent formula as the LLM-alone and regression-alone results.
- **Medians behind "little or no further gain."** See the last table: the regression-plus-LLM medians differ from the regression-alone medians by +1.6 and +2.5 interviews (A) and −1.5 and +0.2 interviews (B).

## Results (median over 10 questions; change in margin of error, equivalent in parentheses)

| Setting | A | B |
|---|---|---|
| Seven facts, penalty 1 | +1.0% (294) | −0.1% (300) |
| Seven facts, penalty 10 | +0.3% (298) | −0.7% (304) |
| Seven facts, penalty 50 | −0.8% (305) | −1.8% (311) |
| Seven facts, penalty 200 | −1.4% (309) | −1.3% (308) |
| Five facts, penalty 1 | −0.4% (303) | −0.1% (300) |
| Five facts, penalty 10 | −0.9% (305) | −0.6% (303) |
| Five facts, penalty 50 | −1.5% (309) | −1.3% (308) |
| Five facts, penalty 200 | −1.2% (308) | −1.1% (307) |

Range across all 16 settings: +1.0% to −1.8% (294 to 311). This is the range in article Table 3.

## LLM and combined results (medians over results)

| | A | B |
|---|---|---|
| LLM alone, single answers (80) | 305.4 | 305.4 |
| Regression alone, same results | 298.3 | 304.5 |
| Regression plus LLM, single answers | 299.9 | 303.0 |
| LLM alone, probabilities without Llama 3.1 8B (60) | 313.9 | 313.9 |
| Regression alone, same results | 298.3 | 304.5 |
| Regression plus LLM, probabilities | 300.8 | 304.7 |

Implementation B reproduces the LLM-alone medians exactly. In both, adding the LLM prediction to the regression changes the median by about 2.5 interviews or less: "little or no further gain."

## Output files

| Article or supplement item | File |
|---|---|
| Article Table 3 regression row; Supplement Appendix D5, Implementation A | `results/covariate_by_question.csv` |
| Supplement Appendix D5, combined results, Implementation A | `results/covariate_benchmark_results.csv` |
| Supplement Appendix D5, Implementation B | `results/covariate_independent_check.txt`, `results/covariate_independent_check_cells.csv` |
| Table 3, LLM and twin rows | `results/out_of_sample_llm_alone_results.csv` |

Rerunning Implementation A on the frozen files reproduces `covariate_benchmark_results.csv` and `covariate_by_question.csv` byte for byte.
