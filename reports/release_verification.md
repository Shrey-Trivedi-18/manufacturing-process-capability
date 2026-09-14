# Repair verification

September 14, 2026. This verifies a simulated analytical project, not production qualification.

## Changes from the original release

- Preserved the original release separately and removed the unrelated real-data companion from the active machining project.
- Added independent diameter/length flags and included missed length failures in final disposition. Generated measurements and random draws are unchanged.
- Removed pooled capability headlines and the pseudo-chronological pooled control chart.
- Replaced blanket measurement approval with purpose-specific interpretation of the simulated GR&R calculation.
- Added paired sensitivity across 30 seeds and five residual-offset assumptions.
- Rebuilt the dashboard from prepared observations with native charts and tested formula dependencies.
- Replaced invented numeric PFMEA priorities with an unscored process-risk review and linked proposed controls.
- Shortened the README, added a readable HTML report, and added executable tests and a CI workflow definition.

## Verified results

| Measure | Corrected baseline | Ideal centering, paired seed 42 |
|---|---:|---:|
| Parts | 20,000 | 20,000 |
| Failed parts | 1,067 | 992 |
| Passing parts | 18,933 | 19,008 |
| Inspection pass rate | 94.665% | 95.040% |
| PPM defective | 53,350 | 49,600 |
| Diameter violations | 80 | 0 |
| Length violations | 2 | 2 |

The baseline has 407 surface-finish, 211 burr, 206 taper, 161 tool-mark, 80 oversize and two primary length labels. The primary labels sum to 1,067 failures. The two repaired records are P16351 and P16539.

GR&R arithmetic reproduces 9.1337% study variation, 9.7575% tolerance and ndc 15. These are conditional simulation outputs, not measurement-system approval.

## Checks performed

- Eighteen Python tests passed: boundary behavior, nonfinite inputs, classification, expected counts, unique identifiers, deterministic regeneration, paired scenarios and GR&R structure.
- A fresh notebook kernel executed the repaired analytical notebook successfully; HTML was exported from those results.
- Workbook totals were reconciled to the CSV-derived summary. A reversible in-memory row-flag change altered the dashboard failure total correctly, then restored it. No spreadsheet-engine formula error was reported.
- Both native charts and the dashboard/detail/data views were rendered for visual inspection. The static PNG is a separately generated presentation companion, not an Excel screenshot.
- Saved-file and local-link checks are provided in `scripts/verify_release.py`. The CSV fingerprint is recorded in `dashboard/metrics.json`.

Test environment: Python 3.12, NumPy 2.3.5, pandas 2.2.3, Matplotlib 3.11.1, SciPy 1.18.1, statsmodels 0.15.0, nbformat 5.11.1, nbclient 0.11.0. Excel creation/verification used bundled artifact-tool 2.8.59.

## Remaining boundaries

The CI workflow has been authored but has not run on the remote service; no passing-badge claim is made. Excel was checked in the generating engine and saved package, not manually recalculated in the Microsoft Excel application. Its builder requires the bundled spreadsheet runtime rather than a publicly installable npm dependency. Python analysis, HTML and PNG rebuilding do not require that runtime.

This repair does not turn simulated data into factory evidence. There are no real savings, physical MSA results, validated risk ratings or deployed controls. The optional drawing is unchanged and remains an instructional specification exercise. No new code license was selected or granted as part of this repair.
