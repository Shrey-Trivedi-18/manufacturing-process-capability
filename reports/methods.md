# Methods and interpretation

## Question and scope

Would an ideal correction to a modeled machine-center offset address the simulated line's inspection losses? The audience is a hypothetical manufacturing-quality team deciding what to investigate next. There is no actual sponsor or production implementation.

All 20,000 part records and 90 Gage R&R readings are generated. True and observed dimensions are separate. Machine offset, operator bias, supplier spread, shift effects and temperature coupling are authored assumptions, not discovered mechanisms.

## Inspection definitions

Diameter: 19.70–20.30 mm. Length: 49.50–50.50 mm. Values exactly on either boundary are accepted. Independently recorded `Diameter_Fail` and `Length_Fail` flags describe dimensional violations. `Inspection_Result` is Fail if either dimension fails or a categorical defect is assigned. Missing/nonfinite measurements are rejected by validation, never counted as passing.

`Defect_Type` is one primary label, with legacy priority: diameter oversize/undersize, surface finish, burr, taper, tool mark, then length if no earlier label exists. This priority preserves the earlier simulation draws. The category Pareto is not a census of multiple physical defects per part. Characteristic counts may overlap; primary-label counts sum to failed parts.

Pass rate = passing parts / inspected parts. PPM defective = failed parts / inspected parts × 1,000,000. No opportunity-based DPMO is reported. No rework history exists, so the principal label is inspection pass rate rather than an operational first-pass-yield claim.

## Measurement simulation

Ten true diameter quantiles (5th through 95th percentile) come from the entire mixed-machine distribution. Three modeled operators take three readings per part. The generator adds operator offsets of −0.004, +0.006 and +0.001 mm and repeatability noise with SD 0.008 mm.

A balanced crossed ANOVA estimates repeatability, operator, part×operator and part variance. Negative estimates are truncated at zero. No significance-driven interaction pooling is used. Percent study variation is 100×sqrt(GRR variance / total variance), not percent variance contribution. ndc is floor(1.41×part SD / GRR SD). Percent tolerance is 100×6×GRR SD / 0.60 mm.

The results apply to the sampled simulated spread. They are not proof of accuracy, per-machine adequacy or physical gage approval. Bias/linearity/stability and repeated categorical appraiser decisions are absent. An attribute-agreement study cannot be reconstructed from one generated primary defect label per part.

## Variation and control

Machine distributions and empirical specification failures are primary. A machine×temperature regression with centered temperature and HC3 standard errors checks authored relationships. Residual supplier SD is descriptive after accounting for machine centers, shifts and thermal effects. It is not a causal supplier-quality estimate.

Pooled Ppk and the pooled I-MR chart were removed. Synthetic dates do not establish production order; machine/shift labels alone do not establish rational subgroups. No stable capability, normal-tail defect prediction or operational control limits are claimed. A real monitoring design would require actual sequence, independent setup history and a verified measurement baseline.

## Paired scenarios and sensitivity

The baseline M3 offset is +0.220 mm. Ideal centering changes it to zero without changing random draws, other machines, thermal slope or measurement noise. Five formerly oversize parts receive another primary label in seed 42, explaining why 80 removed diameter failures produce 75 net fewer failed parts.

Sensitivity uses seeds 0–29 and residual offsets 0, 0.05, 0.10, 0.15 and 0.22 mm, 20,000 parts per condition. The repeated draws within each seed support paired comparisons. Mean/min/max across seeds describe Monte Carlo sampling variability under this generator, not parameter uncertainty or confidence in a real factory benefit. Residual offsets are illustrative choices, not a measured distribution of adjustment errors. No wear, drift, downtime, cost or payback is modeled.

## Data and refresh

`generate_data.py` rebuilds the two synthetic input CSVs. `scripts/rebuild.py` runs shared calculations, rebuilds the PNG companion, executes a fresh notebook kernel and exports the HTML report. `scripts/build_dashboard.mjs` regenerates Excel using the prepared row-level JSON and analysis metrics. The workbook is a rebuilt snapshot with formula-driven baseline summaries, not a live CSV connection. Editing a diameter cell in Excel does not reclassify the source simulation: rerun the rebuild. Scenario/GR&R values are external analysis outputs, labeled as such.

The CSV SHA-256 is stored in `dashboard/metrics.json`; raw measurements are reproducible. The previous full release is retained separately, not mixed into current results. Test coverage includes specification boundaries, missed length failures, invalid identifiers, consistency, deterministic regeneration, pairing and incomplete GR&R designs.

## Interpretation references

- [NIST: assessing process stability](https://www.itl.nist.gov/div898/handbook/ppc/section4/ppc45.htm)
- [NIST: process capability](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm)
- [Minitab: interpreting GR&R output](https://blog.minitab.com/en/blog/quality-data-analysis-and-statistics/how-to-interpret-gage-output-part-2)

These references support interpretation, not provenance of the generated data. No software certification, factory engagement or professional approval is implied.
