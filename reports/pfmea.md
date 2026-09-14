# Qualitative process-risk review

This replaces the earlier numerically scored illustrative PFMEA. No production-validated severity, occurrence or detection ratings are available, so no RPN, Action Priority or standards-compliance claim is made. This is an unscored planning exercise linked to the process/CTQ map, not a completed standards-based PFMEA.

| IDs | Potential failure / effect | Evidence versus assumption | Proposed action / confirmation |
|---|---|---|---|
| D01 | High diameter may fail fit requirements | M3 offset and thermal sensitivity are programmed; actual fit consequences are not measured | Verify setup/measurement, compare independent confirmation runs, assess adjustment drift and costs |
| L01 / C01 | Length violation escapes final classification | Two generated parts were demonstrably mislabeled under the original logic | Independent length flag, boundary tests, final-disposition reconciliation |
| S01 / B01 / T01 / M01 | Surface or geometry defect is accepted or unnecessarily rejected | Labels are generated, not repeat inspection outcomes; causal mechanisms are unobserved | Define acceptance references, collect repeat judgments and objective measurements before choosing controls |
| G01 | Measurement noise masks within-machine change | Global GR&R part range makes the headline ratio look favorable; physical measurement system unknown | Evaluate range appropriate to purpose and verify physical measurement behavior |
| C01 | Dashboard reports stale or inconsistent results | Earlier workbook had hardcoded statistical inputs without a rebuild path | Rebuild from preserved inputs, record source hash and test totals; no live-source claim |

The order of rows is process-oriented, not a risk ranking. A real PFMEA would need cross-functional review, agreed rating criteria, owners, actions and closure evidence.
