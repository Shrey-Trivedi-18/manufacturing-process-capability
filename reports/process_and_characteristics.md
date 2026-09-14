# Process and characteristic mapping

Proposed context for the simulation; not a record of an operating factory.

```text
Incoming stock → Setup and gage verification → Turning → Finishing/deburring
                                                          ↓
                Disposition and feedback ← Final inspection
```

| ID | Step / characteristic | Study specification or definition | Evidence available | Evidence missing |
|---|---|---|---|---|
| D01 | Turning / diameter | 19.70–20.30 mm, inclusive | True and observed simulated diameter; machine, shift, temperature | Actual run order, tool history, physical stability |
| L01 | Turning / length | 49.50–50.50 mm, inclusive | True and observed simulated length; independent failure flag | Actual caliper assessment, length-specific GR&R |
| S01 | Finishing / surface acceptance | Assigned surface-finish category | Simulated primary label | Quantitative Ra, repeat appraiser ratings, acceptance reference |
| B01 | Deburring / burr | Assigned burr category | Simulated primary label | Size/location standard and repeat inspection evidence |
| T01 | Geometry / taper | Assigned taper category | Simulated primary label | Diameter-by-position measurements |
| M01 | Tool marks | Assigned tool-mark category | Simulated primary label | Surface-location and tool-life records |
| G01 | Diameter measurement | Crossed simulated GR&R, 10×3×3 | Variance components under authored noise model | Physical bias, linearity, stability and traceable standards |
| C01 | Final disposition | Fail if either dimension violates limits or another label exists | Reproducible pass/fail logic and reconciliation tests | Rework routes, costs and actual containment history |

The drawing's cross-hole, position, cylindricity and Ra 3.2 requirements are not measured characteristics in the analysis. Visual surface-category acceptance must not be presented as verification of Ra 3.2. IDs above link to the proposed control plan and qualitative risk review.
