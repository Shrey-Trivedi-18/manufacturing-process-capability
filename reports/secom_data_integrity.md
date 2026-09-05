# SECOM Data Integrity and Process-Monitoring Companion

This report documents the Part 2 companion analysis using the UCI SECOM semiconductor process dataset. The sensors are anonymized, so the results identify statistical monitoring and failure-prediction signals rather than a confirmed physical root cause.

## Dataset and source

The raw files are preserved under `secom/`:

- `secom.data`
- `secom_labels.data`
- `secom.names`

Source: [UCI SECOM dataset](https://archive.ics.uci.edu/dataset/179/secom).

The raw sensor file contains 1,567 production runs and 590 numeric sensor fields. The labels file contains 1,463 passing runs and 104 failing runs. Labels were interpreted using `secom.names`: `-1` is pass and `1` is fail. Timestamps run from July 19, 2008 through October 17, 2008. The timestamps are in chronological order, with 33 duplicate timestamp values.

## Data-integrity audit

| Check | Result | Interpretation |
|---|---:|---|
| Production runs | 1,567 | All rows were read successfully |
| Sensor fields | 590 | Numeric sensor values are stored separately from labels and timestamps |
| Failed runs | 104 | Failure rate is approximately 6.6% |
| Missing sensor values | 41,951 of 924,530 (4.54%) | Missingness is material and must be handled explicitly |
| Sensors with any missing values | 538 | Missingness is widespread across sensors |
| Rows with any missing values | 1,567 (100%) | Every run has at least one missing sensor value |
| Sensors missing more than 50% | 28 | These sensors require review before use |
| Constant sensors | 116 | These provide no variation for modeling and are removed |
| Additional near-constant sensors | 6 | These are flagged for review at the 99% mode-share threshold |
| Numeric parsing errors | 0 | All sensor tokens were read as numeric values or missing values |
| All-missing sensors | 0 | No sensor is entirely missing |
| Rows missing more than 50% of sensors | 0 | No complete production run is dominated by missingness |

The most heavily missing sensors include Sensors 158, 159, 293, and 294, each with approximately 91.2% missing values. The 50-run block-median screening method flagged 54 nonconstant sensors as possible persistent step-change candidates. These are review flags only; without engineering context they cannot be called recalibration events.

Because sensor units and engineering limits are anonymized, magnitude alone cannot be used to label a value as physically impossible. The analysis therefore treats missingness, constant behavior, and abrupt statistical changes as data-quality issues rather than assigning unsupported physical explanations.

## Sensor disposition rules

The initial analytical disposition is:

- Drop the 116 constant sensors.
- Review the 6 additional near-constant sensors.
- Review the 28 sensors with more than 50% missing values before using them for monitoring or modeling.
- Retain the remaining 440 sensors for candidate analysis.
- For later predictive modeling, fit imputation values on the training data only and apply them to the test data to avoid leakage.

## Control limits versus specification limits

Six candidate sensors were selected from nonconstant sensors with no more than 20% missingness, using the standardized difference between failing and passing runs:

`Sensor_060`, `Sensor_104`, `Sensor_511`, `Sensor_349`, `Sensor_432`, and `Sensor_435`.

An initial I-MR individuals-chart baseline used the first 80% of chronological observations. Limits were estimated from the average moving range using `d2 = 1.128`.

| Sensor | Baseline mean | Estimated sigma | LCL | UCL | Signal count |
|---|---:|---:|---:|---:|---:|
| Sensor_060 | 3.858609 | 5.912855 | -13.879956 | 21.597174 | 110 |
| Sensor_104 | -0.009508 | 0.002089 | -0.015773 | -0.003242 | 44 |
| Sensor_511 | 58.544509 | 25.848480 | -19.000931 | 136.089949 | 52 |
| Sensor_349 | 0.024902 | 0.008014 | 0.000861 | 0.048943 | 44 |
| Sensor_432 | 24.298243 | 17.824500 | -29.175258 | 77.771744 | 52 |
| Sensor_435 | 15.766540 | 11.673015 | -19.252504 | 50.785584 | 33 |

The limits are statistical monitoring limits, not engineering specifications. SECOM does not provide specification limits, so Cp and Cpk cannot be calculated for these sensors. The high signal counts also indicate that the initial baseline is not perfectly stable and should be treated as an exploratory reference.

## Control-chart signals versus failure outcomes

| Sensor | Total signals | Pass signal rate | Fail signal rate | Failed runs with signal |
|---|---:|---:|---:|---:|
| Sensor_060 | 110 | 6.43% | 15.38% | 16 of 104 |
| Sensor_104 | 44 | 2.60% | 5.77% | 6 of 104 |
| Sensor_511 | 52 | 2.94% | 8.65% | 9 of 104 |
| Sensor_349 | 44 | 2.53% | 6.73% | 7 of 104 |
| Sensor_432 | 52 | 2.87% | 9.62% | 10 of 104 |
| Sensor_435 | 33 | 1.78% | 6.73% | 7 of 104 |

Each selected sensor signals more often on failed runs than on passing runs. Sensor 060 has the largest fail-versus-pass signal-rate difference among the selected sensors, while Sensor 432 has the highest failed-run signal rate after Sensor 060.

## Failure-signal model

A class-weighted logistic regression was evaluated using:

- A stratified 75/25 train/test split
- Median imputation fit within the training pipeline
- Standardization within the training pipeline
- The six exploratory candidate sensors above
- Class weighting to address the imbalance between passing and failing runs

The model results were:

| Metric | Result |
|---|---:|
| Balanced accuracy | 0.7575 |
| Precision | 0.1939 |
| Recall | 0.7308 |
| F1 score | 0.3065 |
| ROC-AUC | 0.7708 |
| Average precision (PR summary) | 0.1978 |
| Escape rate | 26.92% |
| False-reject rate | 21.58% |

The confusion matrix was:

```text
[[287, 79],
 [  7, 19]]
```

The model captured 19 of 26 failing runs in the test set and missed 7, producing the 26.92% escape rate. It incorrectly classified 79 of 366 passing runs as failures, producing the 21.58% false-reject rate.

The standardized logistic coefficients were:

| Sensor | Coefficient | Odds ratio | Association in this model |
|---|---:|---:|---|
| Sensor_060 | 0.3252 | 1.3843 | Higher values associated with failure |
| Sensor_104 | 0.3279 | 1.3881 | Higher values associated with failure |
| Sensor_511 | 0.1229 | 1.1307 | Higher values associated with failure |
| Sensor_349 | 0.1939 | 1.2140 | Higher values associated with failure |
| Sensor_432 | 0.2351 | 1.2650 | Higher values associated with failure |
| Sensor_435 | -0.1147 | 0.8916 | Higher values associated with passing |

The model and control-chart results both indicate that these sensors carry statistical failure signal. The selection step was exploratory and used the full dataset, so these results should be treated as a transparent baseline rather than an unbiased final predictive-performance estimate.

## Limitations

- Sensor names and units are anonymized.
- Engineering specification limits are unavailable; capability indices are therefore not applicable.
- Control limits identify unusual statistical behavior but do not define product acceptability.
- Missingness may itself carry process information, but it was not treated as a confirmed physical mechanism.
- Sensor selection was exploratory and should be repeated within training folds for a production-grade model.
- Correlation, control-chart signals, and model coefficients do not establish physical causation.
- The dataset represents one line and one historical time window.

## Conclusion

The SECOM companion demonstrates how a quality engineer can audit messy process data before modeling it. The primary findings are widespread missingness, a large set of constant sensors, several persistent step-change candidates, and a small group of sensors with measurable statistical association with failure outcomes. The results support targeted monitoring and further engineering investigation, but they do not identify a confirmed physical root cause.
