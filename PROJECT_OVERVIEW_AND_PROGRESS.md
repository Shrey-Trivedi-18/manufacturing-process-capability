# Manufacturing Process Capability & Defect Reduction Study

## Original project description

This project demonstrates an end-to-end quality-engineering workflow applied to a **simulated precision-machining line**. All data is synthetically generated; the process characteristics and root cause were defined by the author. The purpose is to demonstrate command of the methodology, not to report a real process improvement.

The project has two required parts:

1. A complete quality-engineering workflow on a controlled synthetic manufacturing dataset.
2. A companion analysis using messy, real semiconductor process data where the root cause is unknown.

An optional GD&T and tolerance-stack-up module can be added later.

---

## Part 1 — Simulated manufacturing quality study

### Simulated production line

- Automotive precision machining
- 4 CNC machines: M1–M4
- 3 shifts: A, B, C
- 3 raw-material suppliers
- 3 operators for the Gage R&R study
- 6 defect categories: oversize, undersize, surface finish, burr, taper, and tool mark
- 20,000 simulated parts

### Critical characteristics

**Outer diameter**

- Target: 20.00 mm
- LSL: 19.70 mm
- USL: 20.30 mm

**Length**

- Target: 50.00 mm
- LSL: 49.50 mm
- USL: 50.50 mm

### Production data fields

`Part_ID`, `Date`, `Shift`, `Machine`, `Operator`, `Supplier`, `Diameter_mm`, `Length_mm`, `Temperature_C`, `Cycle_Time_sec`, `Defect_Type`, and `Inspection_Result`.

The simulation also retains true dimensions as audit fields so that measurement error can be separated from actual process variation.

### Deliberately embedded process behavior

The data generator is designed to embed effects that the analysis should recover:

1. M3 is centered at approximately 20.22 mm instead of 20.00 mm.
2. Diameter is correlated with temperature, with the strongest relationship on M3.
3. Each operator contributes measurement bias and repeatability noise.
4. Shift C has a higher surface-finish defect rate.
5. Supplier B has slightly higher incoming-stock variation.

The effects should remain modest enough that the analysis is meaningful rather than trivial.

### Intended technical stack

- Python 3 and Jupyter for analytical work
- pandas and numpy for data handling
- scipy.stats and statsmodels for statistics
- matplotlib for plots
- Excel for the final one-sheet dashboard only
- Git and a public GitHub repository for version control

### Intended repository structure

```text
manufacturing-quality-study/
├── README.md
├── generate_data.py
├── quality_analysis.ipynb
├── data/
│   └── manufacturing.csv
├── dashboard/
│   └── quality_dashboard.xlsx
└── reports/
    ├── control_plan.md
    └── pfmea.md
```

### Part 1 analytical workflow

#### 1. Measurement Systems Analysis

Perform a crossed Gage R&R study using:

- 10 parts
- 3 operators
- 3 trials per operator and part
- 90 total measurements

Calculate:

- Repeatability
- Reproducibility
- Total Gage R&R
- `%GRR`
- Number of distinct categories, or `ndc`

Reference criteria:

- Less than 10% GRR: generally good
- 10–30%: marginal
- Greater than 30%: unacceptable
- `ndc >= 5`: generally acceptable

MSA must be performed before capability analysis so that process capability is not interpreted through an unreliable measurement system.

#### 2. Process performance baseline

- Calculate mean and standard deviation overall and by machine.
- Calculate Cp and Cpk against the engineering specifications.
- Calculate PPM defective, defect rate, and first-pass yield.
- Build an I-MR or Xbar-R chart.
- Apply Western Electric rules and identify signaling points.

#### 3. Problem identification

- Create a Pareto chart of defect types.
- Stratify defects by machine, shift, and supplier.
- Examine defect trends over time.

Expected finding: M3 should produce a disproportionate share of dimensional defects relative to its production volume.

#### 4. Root-cause analysis

Test, rather than simply assert, the suspected causes:

- ANOVA: test whether machine affects diameter.
- Regression: model diameter using machine, temperature, shift, and supplier.
- Correlation: compare temperature and dimensional deviation by machine.
- Review residuals, normality, and model assumptions.

Then create qualitative quality-engineering outputs:

- 6M fishbone diagram
- 5-Why analysis
- PFMEA with 8–12 rows, including severity, occurrence, detection, RPN, and recommended actions

#### 5. Improvement simulation

Clearly label this as a simulation. Re-run the generator with M3 centered at 20.00 mm and compare:

- Cpk
- Defect rate
- PPM
- First-pass yield
- Before/after distributions against specification limits

The project must describe this as modeled process centering, not as a real production improvement.

#### 6. Control plan

Create an operational control plan defining:

- CTQ
- Specification
- Measurement method
- Sample size
- Frequency
- Reaction plan

Example controls include diameter checks, length checks, and 100% visual inspection for surface finish.

### Dashboard

Create one Excel dashboard sheet with:

1. Cpk by machine with a 1.33 reference line
2. Defect percentage over time
3. Pareto of defect types
4. FPY and PPM summary tiles
5. Machine × shift defect-rate heatmap

Excel is intended for this presentation layer, not as the primary analytical engine.

### Part 1 resume and interview principles

Resume language should state that the line and improvement are simulated. Use wording such as:

> Demonstrated capability improvement through modeled process centering.

Do not claim that a real manufacturing line was improved.

The interview story should emphasize that measurement-system variation was checked before trusting capability results.

---

## Part 2 — Real-data process monitoring companion

### Dataset

UCI Machine Learning Repository — SECOM:

`https://archive.ics.uci.edu/dataset/179/secom`

The dataset contains approximately:

- 1,567 semiconductor production runs
- Approximately 590 anonymized sensor signals
- Timestamps
- Pass/fail labels
- Approximately 6.6% failed runs
- Heavy missingness, constant columns, and dead sensors

### Part 2 analytical workflow

#### 1. Data integrity assessment

- Quantify missingness by sensor.
- Identify constant and near-constant sensors.
- Flag impossible values, stuck readings, and step changes.
- Document whether each category is dropped, imputed, or investigated.

#### 2. Control limits versus specification limits

- Select 4–6 surviving high-signal sensors.
- Establish a stable baseline period.
- Build I-MR charts and apply Western Electric rules.
- Explicitly state that Cp and Cpk cannot be computed without engineering specification limits.

#### 3. Failure signal analysis

- Address severe class imbalance.
- Use stratified splits and appropriate weighting or resampling.
- Do not rely on raw accuracy.
- Report escape rate and false-reject rate separately.
- Identify sensors carrying failure signal.
- Compare model signals with control-chart findings.

#### 4. Honest limitations

State that:

- Sensors are anonymized, so statistical signal is not the same as physical root cause.
- There are no specification limits for capability analysis.
- Correlation is not causation without process knowledge.
- The dataset represents one line and one time window.

---

## Optional GD&T module

If time allows, add a separate module covering:

- Worst-case tolerance stack-up
- RSS tolerance stack-up
- Monte Carlo simulation across 100,000 virtual assemblies
- Assembly-level Cpk
- One engineering drawing with properly used GD&T feature-control frames

This is optional and should come after both required parts are complete.

---

## Progress to date

### Working location

The active project folder is:

the repository root (run notebooks from this directory).

### Files created

- `generate_data.py`
- `README.md`
- `quality_analysis.ipynb`
- `data/manufacturing.csv`
- `data/gage_rr.csv`
- `data/gage_rr_progress.xlsx`
- `dashboard/quality_dashboard.xlsx`
- `reports/control_plan.md`
- `reports/pfmea.md`
- `secom_analysis.ipynb`
- `secom/secom.data`
- `secom/secom_labels.data`
- `secom/secom.names`
- `reports/secom_data_integrity.md`

### Completed work

#### Synthetic data layer

- Generated 20,000 production records.
- Generated 90 Gage R&R measurements.
- Kept true and observed dimensions separate.
- Embedded the M3 mean shift, temperature effect, operator measurement error, Shift C surface-finish effect, and Supplier B variation effect.

#### Gage R&R learning and spreadsheet work

Built and understood:

- Part–Operator cell means
- Within-cell standard deviations
- Cell variances
- Pooled repeatability variance
- Repeatability standard deviation
- Operator means across all parts
- Operator spread by part
- Part means
- Grand mean
- Part Sum of Squares
- Part degrees of freedom
- Part Mean Square
- Operator Sum of Squares
- Operator degrees of freedom
- Operator Mean Square
- Part–Operator interaction effects
- Interaction Sum of Squares
- Interaction degrees of freedom
- Interaction Mean Square
- Repeatability, interaction, operator, Gage R&R, and part-to-part variance components

Current spreadsheet results are approximately:

- Pooled repeatability variance: `0.000082`
- Repeatability standard deviation: `0.009028`
- Part Mean Square: `0.101893`
- Operator Mean Square: `0.000447`
- Interaction Mean Square: `0.000036`
- Interaction variance component: `0`
- Operator variance component: `0.000014`
- Gage R&R variance: `0.000095`
- Part-to-part variance: `0.011317`

The final Gage R&R checks are:

- `%GRR`: 9.13%
- `ndc`: 15

These results are reproduced and documented in the Python notebook.

### Important alignment note

The Excel workbook is a learning scratchpad and a validation check. It is not the final analytical architecture of the project.

The original project requires:

- Python/Jupyter for the complete analysis
- Excel later for the final dashboard only

### Current position — September 5, 2026

- Part 1 analysis, Gage R&R, modeled centering experiment, dashboard, control plan and preliminary PFMEA are complete.
- Part 2 exploratory SECOM audit and monitoring/modeling notebook are complete. Full-data sensor selection remains an explicitly documented limitation.
- The Onshape drawing and its PDF/PNG exports are complete as an instructional drawing. This is not a production-approved design.
- README navigation and previews, Pp/Ppk terminology, dependency setup and repository packaging have been reviewed.
- See [release verification](reports/release_verification.md) for fresh-kernel execution and data checks.

### Optional work not included

The drawing completes only the drawing portion of the optional GD&T module. Worst-case/RSS tolerance stacks, a 100,000-assembly Monte Carlo model and assembly-level capability have not been performed. They are not required to present the two completed studies.

## Future analytical work

1. Repeat SECOM feature selection inside training folds and evaluate on a chronological holdout.
2. Establish stable, machine-specific control-chart baselines with defensible sampling order.
3. Expand the drawing module only if an assembly-level functional requirement is defined.
