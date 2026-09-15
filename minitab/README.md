# Minitab comparison package - execution pending

On 2026-09-14, `https://app.minitab.com` redirected to the Minitab License Portal sign-in form in Safari. No authenticated Minitab analysis session was available. **No Minitab analysis, screenshot, native project or numerical agreement is claimed.** Sign-in/license access is the remaining dependency for Phase 3.

## Prepared inputs and comparison protocol

Import the CSVs in `inputs/` via the application worksheet open/import command. These are synthetic data. Preserve columns and subgroup order. `python_reference.csv` is the Python reference; Minitab result columns are intentionally empty and status is NOT RUN. Never relabel a Python image as Minitab output.

| Analysis | Input | Required options | Compare / save |
|---|---|---|---|
| Crossed Gage R&R | gage_rr.csv | Parts=Part_ID, operators=Operator, measurement=Diameter_mm; ANOVA; 6 sigma; tolerance width 0.6; retain part/operator interaction | Variance components, GR&R SD, study variation %, tolerance %, ndc; native project + exported output |
| X-bar/R | spc_reference.csv and spc_verification.csv | Diameter_mm grouped by Subgroup, n=5; Rbar estimate; constants matching README; verification uses historical center and sigma from new_limits in results.json; select X-bar tests 1,2,3 and R test 1 | Center, limits, alarm subgroup IDs; do not re-estimate verification limits |
| Normal capability | each phase CSV separately | LSL19.7, USL20.3; subgroup5; within SD Rbar/d2, 6 sigma; no transformation | mean, within/overall SD, Cp/Cpk/Pp/Ppk; label verification provisional and shift descriptive |
| One-way ANOVA | anova.csv | Response Diameter_mm, factor Machine; equal-variance model for numerical comparison | F, DF, p; phase1 unequal variances/large n limit causal interpretation |

The Python GR&R retains interaction even when a term is small; Minitab can remove a nonsignificant interaction by default. Match that choice explicitly before comparing. Truncated negative components, ndc rounding, d2 precision and displayed decimal rounding must be logged. Suggested comparison tolerances: means/SD/limits 1e-5 mm, capability indices 0.002, variance components 1e-7 mm^2; compare underlying precision rather than rounded screenshots. A mismatch must be investigated, not overwritten.

Save genuine exports in `outputs/` with version/date/options and update `comparison.csv`. Only after the major analyses have actually run and differences are resolved should Minitab be added to the resume skills line.

Official procedures: [crossed GR&R](https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/measurement-system-analysis/supporting-topics/basics/measurement-system-analyses-in-minitab/) and [X-bar/R overview](https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/control-charts/how-to/variables-charts-for-subgroups/xbar-r-chart/before-you-start/overview/).
