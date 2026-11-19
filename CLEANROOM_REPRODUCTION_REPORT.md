# Clean-room reproduction and final release report

Audit completed: November 18, 2026

Documentation update: November 19, 2026. The public documentation was synchronized to the final concise Online Supplement and the final seven-item GitHub package. No analysis script or result file was changed; the checksum manifest was regenerated after the documentation update.

## Overall result

**Status: release-grade reconciliation passed, with one explicitly documented environment limitation.**

No substantive numerical mismatch was found between the public source records, the frozen result files, the final manuscript, and the final online supplement. The principal GSS and Twin out-of-sample analyses were independently reconstructed from the exact pinned public-source commits. The Monte Carlo simulation and median-uncertainty calculation were rerun from the release package and matched their frozen outputs byte for byte. All Python scripts compile, and all release-package checksums pass.

The one remaining limitation is narrower: the restricted audit container could not install `pyarrow`, so the Parquet-dependent same-seven-fact regression scripts were not freshly executed source-to-output in that container. That benchmark was nevertheless checked through source-file integrity, two separately written implementations, frozen output reconciliation, and manuscript/supplement reconciliation. A public user on a normal networked Python environment can close this final execution gap with the commands in `README.md`.

## 1. Release-package integrity

- The two earlier copies of the replication archive were byte-for-byte identical before the final documentation cleanup.
- Every file listed in `SHA256SUMS.txt` passed checksum verification.
- All Python scripts compile successfully.
- A scan found no machine-local working paths, user-directory paths, temporary file IDs, placeholders, or hidden review-system identifiers in the release files.

## 2. Pinned public-source versions

### GSS benchmark

Repository: `ZihanChen1995/when-synthetic-users-fail-a-cross-domain-benchmark-of-llm-simulated-human-survey-responses`

Pinned commit: `14acf31963170a2384011eeeb70be3fdbe0d2d9c` (October 4, 2026).

The regression audit records SHA-256 checksums for `pilot_sample.parquet` and all four GSS LLM JSONL files. On November 18, all four JSONL files were independently fetched from the pinned public Git commit and their SHA-256 hashes matched the audit exactly. The exact public `pilot_sample.parquet` checksum had also been independently matched during the earlier source-integrity audit.

### Twin-2K-500 mega-study

Repository: `TianyiPeng/Twin-2K-500-Mega-Study`

Pinned commit: `afe2bb933fce377ed196f441a4c12962cb55a53a` (committed June 9, 2026, representing the June 2026 mega-study state).

## 3. Appendix B simulation

Command rerun from a fresh working directory:

```text
python scripts/appendixB_sim.py
```

Result: **PASS, byte-for-byte identical** to the frozen 24-condition release CSV.

SHA-256 of the regenerated and frozen output:

```text
ca471accb5aa26061c5223ea3da3b23e9f9aab51804227605a2304c48b4c0905
```

The complete 24-condition simulation output was reconciled to the frozen CSV, and every selected verification value retained in concise Appendix B agrees with that output after the stated rounding. Mismatches: **0**.

## 4. Median-uncertainty and run-stability calculation

Command rerun:

```text
python scripts/median_uncertainty.py results/out_of_sample_llm_alone_results.csv
```

Result: **PASS, byte-for-byte identical** to `results/median_uncertainty.txt`.

SHA-256:

```text
b3d4f347470bd875e5866bd37e3db55ff03e4c6db59f7070065ce9023d27f396
```

This independently confirms the tie-aware wider/narrower counts, whole-question resampling ranges, and run-to-run stability summaries reported in Appendix D.

## 5. Complete GSS source-level reconstruction

An independent implementation was run directly against all four LLM JSONL files at the exact pinned GSS commit. This final audit closes the file-size gap recorded in the November 15 report: **all 160 model-question-format-run cells were reconstructed**, including all 40 Llama 3.1 8B cells.

Fresh source-level results:

- GSS single answers: median out-of-sample equivalent `305.384900...`, corresponding to `-0.8856%` in margin of error; 17 of 80 results were tie-aware wider results.
- GSS stated probabilities excluding Llama 3.1 8B: median out-of-sample equivalent `313.856987...`, corresponding to `-2.2325%`; 16 of 60 were tie-aware wider results.
- Full-weight single answers: 8 of 80 improved; median equivalent `218.117...`, about 17.3% wider in margin of error.
- Full-weight clean probability results: 48 of 60 improved; median equivalent `317.456...`.
- Llama 3.1 8B probability outputs: 1,139 unusable of 1,986, or `57.35%`.
- Run stability across 80 model-question-format pairs: median absolute difference `0.4296` percentage point in margin-of-error change; 43 of 80 differences were below 0.5 point; maximum `6.9280` points.
- Identical single-answer model-question summaries across the two public runs: 17 of 40.

The two manuscript illustrations also reproduce from the pinned public records:

- Claude Sonnet 4.6, gun permits: human yes 68.0%, synthetic yes 68.0%, agreement 66.0%, correlation 0.21875, out-of-sample equivalent `308.007880...`.
- Llama 3.3 70B, abortion: human yes 54.545%, synthetic yes 78.788%, agreement 71.717%, correlation 0.46915, out-of-sample equivalent `379.884819...`.

Aggregate checks across all 160 reconstructed out-of-sample rows match the frozen result file to displayed floating-point precision. No substantive discrepancy was found.

## 6. Complete Twin-2K-500 source-level reconstruction

The pinned Twin repository contains 19 default-persona individual-level files under `mega_study_evaluation`; applying the article's rule of retaining outcomes with exactly two human values yields the same **13 outcomes** in the release code.

All 13 were independently reconstructed from the public individual-level records, including the two quantitative-intuition outcomes that were not fully source-recomputed in the November 15 audit.

Fresh source-level median out-of-sample equivalent:

```text
301.834006...
```

This corresponds to the reported `301.8` equivalent interviews and approximately `-0.3%` change in margin of error.

The previously outstanding quantitative-intuition outcomes now reproduce directly:

- `scenario_close_QI`: n=1,323, correlation `0.0332743`, in-sample equivalent `300.332521`, out-of-sample equivalent `299.999908`.
- `scenario_open_QI`: n=1,323, correlation `-0.0346998`, in-sample equivalent `300.361658`, out-of-sample equivalent `300.360280`.

The two high-agreement examples also reproduce: Netflix and TikTok algorithm knowledge both have out-of-sample equivalents essentially equal to 300.

Excluding the five Twin outcomes that pool randomized assignments leaves eight outcomes with median out-of-sample equivalent approximately `301.1`, corresponding to about a `0.2%` reduction in margin of error, as reported in Appendix D.

Aggregate checks across all 13 reconstructed rows match the frozen result file to displayed floating-point precision. No substantive discrepancy was found.

## 7. Same-information regression benchmark

The exact GSS `pilot_sample.parquet` at the pinned commit previously matched the SHA-256 checksum recorded in `REGRESSION_BENCHMARK_AUDIT.md`.

The release package contains two separately written implementations of the same-information regression benchmark. Their frozen outputs independently support the range reported in article Table 3 and the conventional-regression benchmark in Supplement Appendix D5:

```text
+1.0% wider to -1.8% narrower in margin of error
294 to 311 precision-equivalent interviews
```

The frozen outputs also support the statement that adding the LLM prediction changes the median by no more than about 2.5 precision-equivalent interviews in either implementation, using the displayed/rounded medians.

**Environment limitation:** a fresh source-to-output run of the Parquet-dependent regression scripts was not completed in this restricted audit container because `pyarrow` is not installed and outbound package resolution is disabled. An attempted `pip install` failed at DNS resolution. This is an execution-environment restriction, not a detected data or numerical mismatch.

Public users can close this gap by installing `requirements.txt` on a normal networked machine and running the three regression commands in the README.

## 8. Broader-recoding diagnostic

The final supplement reports a post hoc broader GSS recoding diagnostic. The original release candidate included only its frozen summary. The final public package includes the authoritative frozen summary `results/gss_broad_sensitivity_summary.csv`. A reconstructed convenience helper, `scripts/gss_broad_sensitivity.py`, implements the documented broader recoding because the original later helper was not recoverable as a standalone file during final archive assembly; the principal article results do not depend on this post-hoc diagnostic helper.

As an independent source-level check, the non-bootstrap quantities were reconstructed directly from all four public files and matched the frozen summary:

- single answers: 6 of 80 full-weight results improve; median full-weight equivalent `205.97` (reported 206); median fitted partial-weight equivalent `309.65` (reported 310); adjusted-correlation median `306.49` (reported 306);
- probabilities: 54 of 80 full-weight results improve; median full-weight equivalent `311.63` (reported 312); median fitted partial-weight equivalent `318.16` (reported 318); adjusted-correlation median `314.30` (reported 314);
- among the three models retained in the headline probability analysis, probability outputs exceed single answers in 51 of 60 matched comparisons under fitted partial weighting.

The cell-level bootstrap interval counts in the frozen diagnostic summary are generated by the new script with seed `20261030` and can be rerun on a normal machine against the pinned source files.

## 9. Manuscript and supplement reconciliation

The current final manuscript and supplement were checked against the frozen outputs and the independent source reconstructions.

Confirmed article Table 3 values:

- GSS single answers: `-0.9% (305)`;
- GSS clean probabilities: `-2.2% (314)`;
- same-information ridge benchmark: `+1.0% to -1.8% (294 to 311)`;
- Twin-2K-500: `-0.3% (302)`.

Confirmed concise Supplement Appendix D2 headline values:

- `305.4`, `-0.9%`, 17/80 wider, resampling range `300.0-311.9`;
- `313.9`, `-2.2%`, 16/60 wider, resampling range `297.9-328.4`;
- `301.8`, `-0.3%`, 1/13 wider, resampling range `300.0-309.0`.

Confirmed the conventional-regression benchmark in Supplement Appendix D5: all 16 displayed cells agree with the frozen Implementation A and B outputs. Confirmed the selected simulation values retained in Appendix B against the complete frozen simulation CSV: 0 mismatches after the stated rounding.

## 10. Dependency note

The release requirements specify compatible minimum versions rather than a fully locked historical environment. The frozen outputs and SHA-256 manifest therefore serve as the immutable release reference, while `scripts/verify_results.py` checks the numerical claims that matter for the article. On future library versions, insignificant text serialization or floating-point last-digit differences should not be mistaken for a substantive replication failure.

## Release decision

**The package is suitable for public release.**

The evidence supports the claim that the article's principal reported numerical findings have been independently reconciled to the pinned public source records and the frozen outputs. It does **not** claim that every source-to-output script was freshly executed inside this restricted container, because the Parquet-dependent regression rerun was blocked by the absence of `pyarrow` and outbound package installation.

For the strongest possible external certification, a reproducer should follow the README on a normal networked Python 3.11+ machine, run every documented script into a separate `reproduced/` folder, and finish with:

```text
python scripts/verify_results.py reproduced
```

No substantive numerical inconsistency was found in the final manuscript, supplement, public source reconstructions, or frozen principal results during this audit.
