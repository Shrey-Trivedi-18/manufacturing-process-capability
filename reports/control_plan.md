# Control Plan

This is a proposed control plan for the simulated precision-machining line. It is not a validated production control plan.

| CTQ / Process Parameter | Specification / Target | Measurement Method | Sample Size | Frequency | Reaction Plan |
|---|---|---|---:|---|---|
| Outer diameter | Target: 20.00 mm; LSL: 19.70 mm; USL: 20.30 mm | Calibrated micrometer | 5 parts | Start-up and every 25 parts | Stop the process if any result is out of specification; quarantine the previous 25 parts; verify the gage; check the machine offset; remeasure after correction |
| M3 outer diameter | 19.70–20.30 mm; monitor centered process behavior | Calibrated micrometer plus temperature log | 5 parts | M3 start-up, after warm-up, and every 25 parts | Stop M3 if diameter trends upward or signals on the I-MR chart; stabilize temperature; re-center the offset; inspect parts since the last acceptable check |
| Process temperature on M3 | Establish baseline and control limits from stable-process data | Calibrated temperature sensor | Continuous or hourly log | During M3 production | Investigate temperature excursions; pause M3 if the diameter trend is also moving; verify the offset before restarting |
| Length | Target: 50.00 mm; LSL: 49.50 mm; USL: 50.50 mm | Calibrated caliper | 3 parts | Start-up and every 50 parts | Inspect the previous batch; adjust the process if needed; quarantine any nonconforming parts |
| Surface finish | No visible surface-finish defect | Visual inspection under consistent lighting | 100% of parts | Every part | Segregate defective parts; record the defect category; review tooling, coolant, handling, and Shift C conditions |
| Burr | No unacceptable burr | Visual inspection and touch check | 100% of parts | Every part | Segregate affected parts; check tool condition and deburring method; inspect parts produced since the last acceptable check |
| Incoming material variation | Meets incoming-material specification | Supplier documentation plus dimensional sampling | 5 pieces per lot | Every incoming lot | Quarantine the lot if requirements are not met; notify the supplier; increase sampling until variation is acceptable |
| Measurement system | %GRR below 10%; ndc ≥ 5 | Periodic Gage R&R review and calibration records | As defined by MSA plan | At the scheduled MSA interval or after a gage/operator change | Stop using the gage if the system becomes unacceptable; recalibrate, investigate bias, retrain operators, and repeat the MSA |

## General reaction rules

1. Stop the affected machine or process when a CTQ is out of specification or an SPC rule signals.
2. Identify and quarantine parts produced since the last known acceptable check.
3. Verify the measurement system before making process adjustments.
4. Investigate machine offset, temperature, tooling, material, and method conditions.
5. Correct the process and confirm acceptable readings with a defined recheck.
6. Document the event, disposition, corrective action, and restart approval.

## Control-limit note

Specification limits define customer or engineering requirements. Control limits are calculated from stable process data and are used to detect process change. They should not be treated as interchangeable.
