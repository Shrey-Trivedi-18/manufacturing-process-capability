# Minitab run record — October 17, 2026

## Scope

Executed in Minitab Statistical Software web app, Safari on macOS. Original Python artifacts were preserved, not replaced or retrospectively relabeled. Native project: `outputs/shaft_quality.mpx`. The web About dialog showed the product name and 2026 copyright but no numeric version. Native execution timestamps are UTC.

## Crossed Gage R&R

Imported `inputs/gage_rr.csv`: 90 rows, 10 parts × 3 operators × 3 repeats. Parts=`Part_ID`, operators=`Operator`, measurement=`Diameter_mm`. ANOVA, 6 SD, tolerance width 0.6 mm. To reproduce the original full model, alpha to remove interaction was set to **0.999999**, not the default 0.05. The output rounds that setting to 1.00000; the exact value is preserved in `01_commands.txt` and the native project. Interaction p=0.9713081, with its negative variance estimate truncated to zero. Retaining the interaction is an explicit comparability choice, not a claim of a significant interaction.

GR&R SD=0.009757538505343721 mm; study variation=9.133712278190318%; tolerance=9.757538505343723%; ndc=15. Saved variance components, SD and percentages match the reference to substantially tighter precision than the predeclared tolerances. The broad simulated part spread makes %study variation and ndc study-dependent; this does not validate the newer Phase 2 gage model or a real production gage.

## X-bar/R

Imported `phase2_spc_capability/spc_data.csv` unchanged (temporary upload filename `shaft_spc.csv`), 700 rows. Response=`Diameter_mm`, subgroup ID=`Subgroup`, n=5. Staged historical means: 19.999044996679437, 19.999044996679437, 19.999089231622072, 19.999089231622072. Historical SDs: 0.04712155855739895, 0.04712155855739895, 0.045838205914180134, 0.045838205914180134. Stage order follows the data: reference, setup_shift, rebaseline, verification. These supplied values come from the pre-existing reference, so using them is not itself independent estimation verification.

Selected Tests 1/2/3 with K=3/9/6. Actual generated command history confirms `Test 1 2 3` and the K settings. Two identical staged runs are retained as an audit checkpoint. Minitab reports X-bar Test 1 at 41–60 and Test 2 at 49–60, with no displayed R alarms. Reference rows 1–200 and rebaseline rows 301–500 were additionally charted independently with Minitab-estimated Rbar limits; no test-result alarms were displayed.

### Differences that must not be hidden

1. **Test 2 boundary convention:** the original Python reference carries the same-side run through the reference/shift boundary and reports T2 beginning at 43. The Minitab staged chart starts a fresh run at that boundary and reports T2 beginning at 49. Both identify the first Test 1 shift at 41. These are not identical run-state conventions; do not claim matching complete alarm lists.
2. **Verification Test 3:** the earlier reference reports six increasing subgroup means at 117–122 and flags 122. Minitab did not display that alarm in either the full staged chart or the verification-only check (rows 501–700, chart samples 1–40). Tests 1/2/3 and K=6 were verified in the dialog and saved generated commands. A traditional-chart command run without `IGraph` also did not report it. The reason is **unresolved**; no assertion of a Minitab bug or equivalence is made. Preserve the reference flag and keep verification provisional until the differing behavior is explained.
3. **Control-limit precision:** the Python reference uses rounded d2=2.326 and D4=2.114. Minitab's displayed R UCL for the frozen new limits is 0.225446 versus Python 0.2253939759. Do not treat this as numerical identity. Exact native limits have not been transcribed into the comparison table; constants/precision remain a reconciliation item. This difference does not change the observed shift detection.

The chart package is executed evidence, not a completed validation sign-off. No observations were removed to eliminate the verification complication.

## Normal capability

Normal capability for one response split by `Phase`; subgroup size 5; LSL=19.7, USL=20.3 mm; Rbar estimator with unbiasing constants; ordinary sample overall SD (no overall unbiasing adjustment); tolerance multiplier 6; within and overall outputs; no transformation. All four phases were computed for transparent numerical comparison. Only reference/rebaseline support conditional capability interpretation; setup-shift indices are descriptive and verification is provisional.

Full-precision mean, within SD, overall SD, Cp/Cpk/Pp/Ppk for reference, rebaseline and verification match the pre-existing reference within 1e-5 mm / 0.002 index units. The native project also contains all four capability histograms and normal probability plots. No pooled-across-phase capability claim is made.

## Files and reproducibility

Native project download is unchanged. Cropped screenshots are direct Minitab captures. CSV tables and command text are mechanically extracted from the native archive, not recalculated analyses. Re-extract with:

```sh
ruby minitab/extract_native_results.rb minitab/outputs/shaft_quality.mpx
```

The optional one-way machine ANOVA was not requested in this run and remains not run in Minitab. Existing Python results and corrective-action documents remain historical evidence; this log adds the software comparison and its limitations.

Official references: [GR&R options](https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/measurement-system-analysis/how-to/gage-study/crossed-gage-r-r-study/perform-the-analysis/specify-the-options/), [historical chart parameters](https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/control-charts/how-to/variables-charts-for-subgroups/xbar-r-chart/perform-the-analysis/xbar-r-options/enter-historical-parameters/), [special-cause tests](https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/control-charts/how-to/variables-charts-for-subgroups/xbar-r-chart/perform-the-analysis/xbar-r-options/select-tests-for-special-causes/).
