# Release verification

Verified September 5, 2026. This record describes reproducibility and presentation checks, not production qualification.

## Executed analyses

| Notebook | Code cells | Execution errors | Fresh-kernel run |
|---|---:|---:|---:|
| `quality_analysis.ipynb` | 24 | 0 | 4.6 seconds |
| `secom_analysis.ipynb` | 11 | 0 | 2.6 seconds |

Both notebooks were run sequentially from the repository root with a separate fresh Python kernel. Outputs include five machining figures and one multi-panel SECOM figure. The machining notebook no longer installs packages during execution. Runtime is machine-dependent; these timings are from the final run with cached imports.

Test environment: Python 3.12.14, NumPy 2.3.5, pandas 2.2.3, Matplotlib 3.11.1, SciPy 1.18.1, statsmodels 0.15.0, scikit-learn 1.9.0, nbclient 0.11.0 and ipykernel 7.3.0.

## Numerical reconciliation

- Baseline: 20,000 parts; 1,065 inspection failures; 18,935 passes; FPY 94.675%; 53,250 defective parts per million.
- Diameter Ppk: overall 0.791243; M1 2.929119; M2 2.947525; M3 0.729650; M4 2.989022.
- Assigned defects: surface finish 407, burr 211, taper 206, tool mark 161, oversize 80, undersize 0. Sum = 1,065.
- Centered scenario: 990 failures; FPY 95.050%; 49,500 defective parts per million; overall Ppk 2.874321; M3 Ppk 2.804253.
- SECOM confusion matrix reproduced as `[[287, 79], [7, 19]]`. Balanced accuracy 0.757461, ROC-AUC 0.770807 and average precision 0.197778.

## File and presentation checks

- The baseline generator reproduces the committed production observations within CSV precision.
- The two source CSVs, three raw SECOM files and original drawing exports are unchanged.
- Dashboard source numeric cells and existing formulas are preserved. Three native, range-backed charts are present; chart positions, date-label spacing and percentage-axis formatting were reviewed.
- The PNG companion recomputes its summary directly from the production CSV. It is not an Excel screenshot and does not automatically refresh the workbook.
- The README links to both notebooks, the dashboard, drawing and reports. Local Markdown links resolve.
- `pfema.md` was renamed to `pfmea.md`; the progress record was updated.
- OS metadata, the virtual environment, notebook checkpoints and learning-scratchpad previews are excluded from version control.

## Interpretation corrections and remaining limitations

The machining indices are now labeled Pp/Ppk because they use overall sample standard deviation. No numerical capability formula was changed. The mixed-machine process and synthetic daily ordering do not establish stable, normal, machine-specific capability.

The SECOM label-guided feature selection precedes the train/test split. The scores therefore remain exploratory and potentially optimistic despite train-only imputation and scaling. No new unbiased validation experiment is claimed.

The drawing is an instructional extension, not a manufacturing release. Its remaining template angular-tolerance field is unspecified; checked/approved fields are not signed. The depicted material, roughness and GD&T have not been validated against a real assembly or measured production parts. Worst-case/RSS stacks and Monte Carlo assembly analysis remain optional future work.
