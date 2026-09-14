# Proposed control plan

These are planning requirements for a hypothetical line, not deployed controls. The analysis does not establish production sampling intervals, control limits or restart authority. Those choices require a process owner and actual operating evidence.

| ID | Proposed measurement / check | Timing basis to establish | Proposed reaction | Evidence before use |
|---|---|---|---|---|
| D01 | Diameter with a traceable micrometer, recorded by machine and actual sequence | Start-up and after an adjustment; routine interval determined from production risk | Identify material since last verified acceptable check, verify gage, investigate offset/temperature, independently recheck before release | Measurement adequacy, stable per-machine baseline, traceability and approved restart criteria |
| L01 | Length measured independently of diameter disposition | Include in the inspection plan; routine sampling not inferred from this simulation | Segregate detected failures; investigate setup and verify length after correction | Length-specific measurement assessment and agreed containment scope |
| S01 / B01 / T01 / M01 | Written defect references; objective dimensional/roughness methods where specified | Establish coverage from defect risk and inspection performance | Record category/location and review tooling, finishing or handling; do not assume Shift C is the physical cause | Reference samples, repeat appraiser agreement and objective measurements |
| G01 | Repeatability/reproducibility plus purpose-specific measurement assessment | Before adoption and after relevant equipment/process changes | Investigate gage or operator effects before adjusting production | Bias, linearity and stability where applicable; adequate part range for intended use |
| C01 | Reconcile dimension flags, primary categories and final disposition | Every software rebuild; actual inspection logic tested before deployment | Block release of inconsistent records and correct the logic | Boundary tests, missing-value policy, reconciliation and versioned data |

For SPC, select rational subgroups or individual-observation charts only after the real sampling structure is known. Specification limits are acceptance requirements, not control limits. A successful centering recheck alone does not prove long-term stability or eliminate other failure modes.
