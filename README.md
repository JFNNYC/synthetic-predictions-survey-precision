# Replication package for "When Synthetic Predictions Improve Survey Precision"

## Start here: what this folder is

This folder contains the computer files used to check and reproduce the numerical analyses reported in the article and its Online Supplement.

You do **not** need this folder in order to read or understand the article. The three parts of the submission have different purposes:

- **The article** explains the question, method, main results, and practical implications.
- **The Online Supplement** gives supporting simulation details, a brief technical note on the precision calculations, the paired-data reanalyses and robustness checks, the 28-study inventory, and the AI-use disclosure.
- **This replication package** contains the computer programs, saved numerical outputs, and audit records that allow someone to inspect or rerun the calculations.

## Do I need to know Python?

No, not simply to understand what this package contains.

Some files in this folder are Python programs. **Python** is a free programming language widely used for statistical and data analysis. The Python files are the instructions a computer follows to perform the calculations.

There are three ways to use this package:

1. **Understand what was provided.** Read this README and the audit reports. No programming is required.
2. **Inspect the saved results.** Open the files in the `results` folder. Most are ordinary CSV or text files that can be viewed without rerunning the analyses.
3. **Reproduce the calculations.** Install Python and the listed software packages, obtain the two public source datasets, and run the supplied programs. The technical instructions begin below.

A reader who does not use statistical software can stop after the first two levels. The command-line instructions are provided for researchers or technical reviewers who want to rerun the work themselves.

## What exactly can be reproduced?

The package reproduces three kinds of analysis used in the article:

- the reanalysis of the public General Social Survey (GSS) human-synthetic benchmark;
- the reanalysis of the public Twin-2K-500 human/digital-twin data; and
- the computer simulation reported in Appendix B.

The package starts from human answers and **already-generated** LLM or digital-twin predictions released by the original study teams. It does **not** regenerate those original predictions, recreate the original language-model pipelines, or collect new human survey data. No new model output was generated for this article.

### What is the Monte Carlo simulation?

Appendix B uses what statisticians call a **Monte Carlo simulation**. In plain language, the computer repeatedly creates artificial survey samples under conditions specified in advance and calculates the results each time. Repeating the process thousands of times shows how the statistical method behaves across many possible samples rather than relying on one sample.

The simulation in this article is not an LLM simulation and does not imitate a commercial synthetic-data product. It is a controlled statistical check of the formulas used in the article.

## What is in this folder?

At the top level, the public repository contains exactly **five files and two folders**:

| File or folder | What it is and why it is here |
|---|---|
| `README.md` | This guide. It explains the package and how to rerun the analyses. |
| `results/` | Saved numerical outputs used as the release reference. These allow readers to inspect the reported results without rerunning the code. |
| `scripts/` | Python programs that perform the simulation and reanalyses. |
| `requirements.txt` | The Python software packages needed to run the programs. |
| `CLEANROOM_REPRODUCTION_REPORT.md` | A record of the independent final checks performed on the analyses and package. |
| `REGRESSION_BENCHMARK_AUDIT.md` | Detailed documentation of the same-information conventional-regression benchmark and its independent implementation check. |
| `SHA256SUMS.txt` | Digital fingerprints of the released files. These can be used to confirm that files have not changed accidentally. |

## A note about "frozen" result files

The word **frozen** means that a copy of the final output was saved as the reference version used to check the paper. It does not mean that the result cannot be rerun. It means the package includes a known reference against which a new rerun can be compared.

## A note about the broader-recoding sensitivity check

One post-hoc sensitivity analysis uses `results/gss_broad_sensitivity_summary.csv` as its authoritative released output. During final package assembly, the original later helper script for that sensitivity check was not recoverable as a standalone file. The package therefore includes a reconstructed convenience helper, `scripts/gss_broad_sensitivity.py`, implementing the documented recoding. The helper is included for transparency and rerunning convenience; the article's principal results do not depend on this post-hoc diagnostic.

---

# Technical instructions for reproducing the analyses

The remainder of this README is for readers who want to run the code themselves.

## 1. Software needed

You will need:

- Python 3.11 or later;
- Git, to obtain the exact public source files used in the article; and
- the Python packages listed in `requirements.txt` (`numpy`, `pandas`, and `pyarrow`).

A **repository** is simply a stored collection of files and their revision history. **Git** is the tool used to download an exact historical version of a repository. The long strings below are Git commit identifiers; they ensure that a reproducer uses the same public-source versions used for the article.

## 2. Obtain the exact public source data

### GSS benchmark: Chen, Zhu, and Zheng (2026)

```bash
git clone https://github.com/ZihanChen1995/when-synthetic-users-fail-a-cross-domain-benchmark-of-llm-simulated-human-survey-responses.git gss-source
cd gss-source
git checkout 14acf31963170a2384011eeeb70be3fdbe0d2d9c
cd ..
```

The scripts use:

```text
gss-source/experiment/datasets/GSS/build
```

This directory is called `GSS_BUILD` below.

### Twin-2K-500 mega-study: Toubia et al. (2025); Peng et al. (2026)

```bash
git clone https://github.com/TianyiPeng/Twin-2K-500-Mega-Study.git twin-source
cd twin-source
git checkout afe2bb933fce377ed196f441a4c12962cb55a53a
cd ..
```

The scripts use:

```text
twin-source/mega_study_evaluation
```

This directory is called `TWIN_DIR` below. The pinned commit was made June 9, 2026 and represents the June 2026 mega-study state used for this article.

## 3. Set up Python

A **virtual environment** is an isolated folder that keeps the software used for this reproduction separate from other Python software on the computer.

```bash
python -m venv .venv
```

Activate it.

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

The requirements file specifies compatible minimum versions. The frozen result files are the release reference. Exact last digits or text-file byte formatting can vary across future software/platform versions, so the package also includes a numerical verification script that checks the findings reported in the article.

## 4. Optional: confirm that the released package has not changed

On macOS/Linux:

```bash
sha256sum -c SHA256SUMS.txt
```

Each listed file should report `OK`. `SHA256SUMS.txt` contains digital fingerprints of the release files. This step checks file integrity; it does not rerun the statistical analysis.

## 5. Check the saved results against the article

Before downloading source data or rerunning anything, you can ask the supplied checker to confirm that the frozen result files contain the headline numbers reported in the article:

```bash
python scripts/verify_results.py results
```

The final line should be:

```text
ALL REPORTED-NUMBER CHECKS PASSED
```

This verifies the released numerical outputs. It is not a substitute for rerunning the source analyses, which is the next step.

## 6. Rerun the analyses

Create a separate output folder so the frozen reference files are not overwritten. The path-variable commands below use macOS/Linux shell syntax:

```bash
mkdir -p reproduced
GSS_BUILD=/full/path/to/gss-source/experiment/datasets/GSS/build
TWIN_DIR=/full/path/to/twin-source/mega_study_evaluation
```

On Windows, create a folder named `reproduced` (for example, with File Explorer or `mkdir reproduced`) and replace `$GSS_BUILD` and `$TWIN_DIR` in the commands below with the quoted full paths to the two source directories.

Run the analyses:

```bash
python scripts/gss_recompute.py "$GSS_BUILD" reproduced/gss_160_cells.csv
python scripts/twin_recompute.py "$TWIN_DIR" reproduced/twin_13_binary.csv
python scripts/out_of_sample_llm_alone.py "$GSS_BUILD" "$TWIN_DIR" reproduced/out_of_sample_llm_alone_results.csv
python scripts/covariate_benchmark.py "$GSS_BUILD" reproduced
python scripts/covariate_by_question.py "$GSS_BUILD" reproduced
python scripts/covariate_independent_check.py "$GSS_BUILD" reproduced > reproduced/covariate_independent_check.txt
python scripts/gss_broad_sensitivity.py "$GSS_BUILD" reproduced/gss_broad_sensitivity_summary.csv
python scripts/median_uncertainty.py reproduced/out_of_sample_llm_alone_results.csv > reproduced/median_uncertainty.txt
(cd reproduced && python ../scripts/appendixB_sim.py && mv sim_results.csv sim_results_24_conditions.csv)
```

Finally, run the numerical checker on the newly reproduced output folder:

```bash
python scripts/verify_results.py reproduced
```

## 7. Which program produces which result?

| Script | What it produces | Where it is used |
|---|---|---|
| `scripts/gss_recompute.py` | 160 GSS diagnostic cells, including bootstrap intervals | Appendix D diagnostics |
| `scripts/twin_recompute.py` | 13 Twin-2K-500 two-option outcomes, including bootstrap intervals | Appendix D diagnostics |
| `scripts/out_of_sample_llm_alone.py` | Leave-one-out results for GSS LLMs and Twin digital twins | Article Table 3; Supplement Table D1 and examples in D2 |
| `scripts/covariate_benchmark.py` | Same-seven-fact regression and regression-plus-LLM results | Article Table 3; Supplement Appendix D5 |
| `scripts/covariate_by_question.py` | Question-level ridge sensitivity grid, Implementation A | Article Table 3; Supplement Appendix D5 |
| `scripts/covariate_independent_check.py` | Separately written regression check, Implementation B | Supplement Appendix D5 |
| `scripts/gss_broad_sensitivity.py` | Broader-recoding diagnostic summary | Supplement Appendix D4 |
| `scripts/median_uncertainty.py` | Whole-question resampling ranges and run-to-run stability | Supplement Appendix D2 and D4 |
| `scripts/appendixB_sim.py` | 24-condition statistical simulation | Supplement Appendix B and Article Table 2 examples |
| `scripts/verify_results.py` | Checks reported numerical claims against a results folder | Release/reconciliation check |

## 8. Expected headline results

A correct rerun should recover these values, subject to displayed rounding:

| Result | Expected value |
|---|---:|
| GSS single-answer out-of-sample median equivalent | 305.4 |
| GSS single-answer median margin-of-error change | -0.9% |
| GSS clean probability out-of-sample median equivalent | 313.9 |
| GSS clean probability median margin-of-error change | -2.2% |
| Twin-2K-500 out-of-sample median equivalent | 301.8 |
| Twin-2K-500 median margin-of-error change | -0.3% |
| Same-information ridge benchmark range | +1.0% wider to -1.8% narrower (294 to 311 equivalent interviews) |
| Llama 3.1 8B unusable GSS probability outputs | 1,139 / 1,986 (57%) |
| GSS single-answer model-question pairs identical across the two released runs | 17 / 40 |
| Median run-to-run difference in out-of-sample MOE change | 0.43 percentage point |
| Largest run-to-run difference | 6.9 percentage points |

`REGRESSION_BENCHMARK_AUDIT.md` documents the two independently written regression implementations, coding choices, fixed penalty grid, and source-file checksums.

## 9. Why are there three simulation filenames?

Three names refer to the same 24-condition simulation output at different stages of the workflow:

- `sim_results.csv` is the filename written by `appendixB_sim.py` in the working directory;
- `results/sim_results_24_conditions.csv` is the normalized release filename; and
- `results/sim_results_24_conditions_2026-10-29.csv` is the dated filename referred to in Appendix B.

The dated release file is byte-for-byte identical to the simulation output reproduced in the final clean-room check.

## 10. Random-number seeds

A **random-number seed** is a fixed starting value that allows a computer simulation or resampling procedure to be repeated in the same way.

- `20261029`: Appendix B statistical simulation.
- `20261030`: cell-level bootstrap intervals in the GSS and Twin recomputation scripts, including the broader-recoding diagnostic.
- `20261114`: whole-question resampling in `median_uncertainty.py`.

## 11. Independent checks and known limitation

`CLEANROOM_REPRODUCTION_REPORT.md` records the final independent checks. Among other things, the audit reconstructed all 160 GSS cells and all 13 Twin outcomes from the pinned public source records and reran the simulation and median-uncertainty calculation byte-for-byte.

The audit environment could not install `pyarrow`, so the Parquet-dependent same-seven-fact regression programs were not freshly executed source-to-output inside that restricted environment. That benchmark was instead checked through source-file integrity, two separately written implementations, frozen output reconciliation, and manuscript/Supplement reconciliation. A reproducer with a normal networked Python environment can close that execution gap by installing `requirements.txt` and running the regression commands above.

## 12. AI-use disclosure

ChatGPT and Claude assisted with literature retrieval, coding suggestions, drafting and checking analysis code, robustness and arithmetic checks, source and citation checking, organization of results, and editing. The author reviewed the sources, code, outputs, coding decisions, interpretations, and final text. Appendix F of the Online Supplement gives the full disclosure and distinguishes this research-assistance use from the LLM/digital-twin predictions contained in the public datasets being analyzed.
