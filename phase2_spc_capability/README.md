# Phase 2 - ordered SPC and capability

This is a new synthetic experiment; Phase 1 is unchanged. Run `python phase2_spc_capability/study.py` from the repository root. Seed 20260914 and the four windows were set before inspecting results. No alarm points were deleted and no seed was selected to obtain a clean chart.

## Sampling design

One hypothetical turning operation, one shaft diameter, one gage. Five consecutive parts are sampled at minutes 0-4 of every 15-minute interval. The remaining interval represents no modeled production: **700 is the entire simulated population, not a sample from an invented larger lot**. Timestamps have no timezone and represent a teaching schedule. True part SD is 0.045 mm; independent gage SD is 0.006 mm. This new gage model is not validated by the Phase 1 mixed-part GR&R.

| Window | Subgroups | Parts | Authored mean | Purpose |
|---|---|---|---|---|
| Reference | 1-40 | 200 | 20.000 mm | Establish initial limits |
| Setup shift | 41-60 | 100 | 20.270 mm | Wrong diameter compensation after setup |
| Rebaseline | 61-100 | 200 | 20.000 mm | Establish limits after restoring setup |
| Verification | 101-140 | 200 | 20.000 mm | Independent later run against frozen new limits |

All 100 shifted parts are a quarantined challenge lot in this retrospective exercise. The signal at subgroup 41 does not authorize continued production until subgroup 60. In a live implementation, stop/hold at the first alarm; this full challenge window exists to evaluate the failure mode.

## Methods fixed for this release

- n=5; d2=2.326; A2=3/(d2*sqrt(5)); D3=0; D4=2.114. X-bar limits = grand mean +/- A2*Rbar. R limits = D3*Rbar, D4*Rbar. Small differences from rounded A2=0.577 are expected.
- X-bar tests: T1 one point beyond 3 sigma; T2 nine consecutive points strictly on one side; T3 six strictly increasing/decreasing points. Report the final point in the triggering window. R chart: T1 only. These are a selected Nelson-style subset, not every Western Electric or Nelson test. Rule state restarts at the rebaseline and verification boundaries. Equality is not beyond a limit; ties break trends.
- Reference limits are fixed for groups 1-60. Rebaseline limits use groups 61-100 only and are held fixed for 101-140. R stability is reviewed alongside X-bar.
- Within SD=Rbar/d2; overall SD=sample SD with ddof=1. Cp=(USL-LSL)/(6*within SD); Cpk=min(USL-mean,mean-LSL)/(3*within SD). Pp/Ppk use overall SD. Specs: 19.700-20.300 mm inclusive. No measurement-error subtraction.
- Normal probability plots, Shapiro-Wilk and lag-1 correlation are supporting diagnostics. A large normality p-value and no chart alarm do not prove stability, normality or independence. Finite subgroup counts limit assurance.
- Reference and rebaseline have zero selected-rule signals. Verification has one T3 alert; its indices are **provisional**, despite zero observed rejects. The result is not a clean effectiveness closure. Retain the six-point sequence and investigate before real release.
- The shifted and pooled indices are descriptive counterexamples only. The pooled distribution mixes distinct means; it cannot establish stable capability. Do not compare its Ppk against the corrected window as a realized capability gain.
- 0/200 rejects has an exact one-sided 95% binomial upper bound of 1.487% under independent identical Bernoulli trials. That bound describes finite sampling uncertainty; it is not evidence of zero risk and is conditional on those assumptions.

## Evidence

[X-bar/R chart](charts/01_xbar_r.png) · [Distribution comparison](charts/02_diameter_distributions.png) · [Normality diagnostics](charts/03_normality.png) · [Indices](charts/04_capability.png)

[Part records](spc_data.csv) · [Subgroup calculations](subgroup_results.csv) · [Every alarm](alarm_log.csv) · [Capability table](capability_summary.csv) · [Executed notebook](spc_analysis.ipynb)

## Sources

Formulas and small-subgroup chart context: [NIST X-bar/R](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc311.htm). Capability requires a stable process: [NIST capability](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm). Test definitions: [Minitab X-bar/R tests](https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/control-charts/how-to/variables-charts-for-subgroups/xbar-r-chart/perform-the-analysis/xbar-r-options/select-tests-for-special-causes/). Within-SD indices: [Minitab capability formulas](https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/capability-analysis/how-to/capability-analysis/normal-capability-analysis/methods-and-formulas/potential-capability/). Accessed 2026-09-14.
