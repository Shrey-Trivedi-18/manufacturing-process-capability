# Minitab run record — October 17, 2026

## Scope

Executed in Minitab Statistical Software web app, Safari on macOS. Original Python artifacts were preserved, not replaced or retrospectively relabeled. Native project: `outputs/shaft_quality.mpx`. The web About dialog showed the product name and 2026 copyright but no numeric version. Native execution timestamps are UTC.

## Crossed Gage R&R

Imported `inputs/gage_rr.csv`: 90 rows, 10 parts × 3 operators × 3 repeats. Parts=`Part_ID`, operators=`Operator`, measurement=`Diameter_mm`. ANOVA, 6 SD, tolerance width 0.6 mm. To reproduce the original full model, alpha to remove interaction was set to **0.999999**, not the default 0.05. The output rounds that setting to 1.00000; the exact value is preserved in `01_commands.txt` and the native project. Interaction p=0.9713081, with its negative variance estimate truncated to zero. Retaining the interaction is an explicit comparability choice, not a claim of a significant interaction.

GR&R SD=0.009757538505343721 mm; study variation=9.133712278190318%; tolerance=9.757538505343723%; ndc=15. Saved variance components, SD and percentages match the reference to substantially tighter precision than the predeclared tolerances. The broad simulated part spread makes %study variation and ndc study-dependent; this does not validate the newer Phase 2 gage model or a real production gage.

## X-bar/R — initial runs, superseded by calibrated configuration below

Imported `phase2_spc_capability/spc_data.csv` unchanged (temporary upload filename `shaft_spc.csv`), 700 rows. Response=`Diameter_mm`, subgroup ID=`Subgroup`, n=5. Staged historical means: 19.999044996679437, 19.999044996679437, 19.999089231622072, 19.999089231622072. Historical SDs: 0.04712155855739895, 0.04712155855739895, 0.045838205914180134, 0.045838205914180134. Stage order follows the data: reference, setup_shift, rebaseline, verification. These supplied values come from the pre-existing reference, so using them is not itself independent estimation verification.

Selected Tests 1/2/3 with K=3/9/6. Actual generated command history confirms `Test 1 2 3` and the K settings. Two identical staged runs are retained as an audit checkpoint. Minitab reports X-bar Test 1 at 41–60 and Test 2 at 49–60, with no displayed R alarms. Reference rows 1–200 and rebaseline rows 301–500 were additionally charted independently with Minitab-estimated Rbar limits; no test-result alarms were displayed.

### Initial differences and their disposition

1. **Test 2 boundary convention, resolved:** the reference carries its same-side run through the reference/shift boundary and reports T2 beginning at 43. The initial Minitab `Phase` stages restarted that run and reported T2 beginning at 49. The final derived `Control_Stream` column uses boundaries at 61 and 101, matching the reference, and reports T2 at 43–60. The original `Phase` data were not changed.
2. **Verification Test 3, resolved by empirical calibration:** the initial K=6 runs did not display the six-point trend at 122. Diagnostic positive and negative controls identified an effective off-by-one count in this web session. The calibrated K=5 setting reproduces the original six-point rule and flags 122. Exact results and limitations are below. This is not a universal claim that every Minitab release behaves this way.
3. **Control-limit precision, quantified:** the reference uses rounded d2=2.326 and D4=2.114. Full-precision native stored statistics are now exported. Reference R UCL: Minitab 0.23175796145285524 versus reference 0.23170443136233404; new R UCL: Minitab 0.22544604814771213 versus reference 0.22539397594579363. Both methods have no R Test 1 alarms. The X-bar limits match at stored precision. This expected constant-precision difference is preserved in `comparison.csv`, not falsely marked identical.

## Resolution — calibrated rule and matched streams

The raw 90 and 700 measurement values were compared to the native worksheet values and match exactly. No production observations were edited, rounded, deleted or replaced. Diagnostics are explicitly labeled non-production columns C12–C17; C11 is an offset diagnostic and C18 is the derived stream identifier. None is treated as another production lot.

Minitab's documented Test 3 is six monotonic points, and the dialog/generated output calls K the point count. The following **observed application results** differ from that wording in this session:

| Diagnostic input | Native setting | Expected under six-point definition | Observed Minitab alarm points |
|---|---:|---|---|
| 1,2,3,4,5,6,7,8 | K=6 | 6,7,8 | 7,8 |
| 0,1,2,3,4,5 | K=5 | 6 | 6 |
| 5,4,3,2,1,0 | K=5 | 6 | 6 |
| 0,1,2,2,3,4 (tie) | K=5 | none | none |
| 0,1,2,3,2,4 (reversal) | K=5 | none | none |
| 0,1,2,3,4,* (five valid points) | K=5 | none | none |

These checks were performed **inside Minitab**, not calculated by the extraction script. Raw native tables: `11_table_1.csv`, `12_table_1.csv`, `12_table_2.csv`; command 14 in the native project contains the negative controls and displays no test-result alarms. Six-point verification with calibrated K=5 reports chart sample 22 (original subgroup 122), saved in `13_table_1.csv`. The Minitab output still labels K=5 as “5 points”; screenshots and native tables are not relabeled to hide that discrepancy. K=5 is an explicit, benchmark-tested workaround for the predefined six-point rule, **not** a silent switch to a more sensitive five-point rule or a post-hoc deletion of the trend.

The final full-study chart, command 15, uses `Control_Stream = IF(Subgroup <= 60, 1, IF(Subgroup <= 100, 2, 3))`, original `Diameter_mm` measurements, original frozen means/SDs, and Tests 1/2/3 with K=3/9/5. It stores all 140 plotted means, ranges, center lines and limits in the native worksheet. These are exported as `control_chart_statistics.csv`. Supplied historical mean/SD values are not misrepresented as independent parameter estimates.

Final X-bar alarm lists match exactly:

- Test 1: 41–60.
- Test 2: 43–60.
- Calibrated six-point trend: 122.

`alarm_comparison.csv` is extracted from the final native Minitab table and checked against the existing alarm log; extraction fails on any differing alarm list. Reference and rebaseline remain free of the selected alarms. Verification remains provisional because **both implementations now confirm its trend**. Software reconciliation does not close the process corrective action or justify real release.

For another release/session, first run the diagnostic controls and use the setting that implements the declared six-point definition. If K=6 correctly flags the sixth point there, use K=6 instead. Do not apply this workaround without verifying behavior.

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
