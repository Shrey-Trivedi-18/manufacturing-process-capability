# Quality planning traceability

All ownership and controls below are proposed teaching assignments. No numeric severity/occurrence/detection ranking is asserted without agreed criteria and a team review. This is a PFMEA-style qualitative worksheet, not a validated standards submission.

| CTQ / drawing | Failure mode / effect | Cause or hypothesis | Prevention / detection control | Inspection / reaction | Evidence / owner |
|---|---|---|---|---|---|
| D01 | Oversize OD / may prevent fit | Demonstrated programmed setup offset | CP-D01: controlled recipe check, independent first piece, frozen X-bar/R limits | IP-D01; hold, NCR-001 and CA-001 | Ordered CSV, alarm log, CA report / manufacturing + quality engineer |
| L01 | Incorrect length / seating or stack mismatch | Stop/setup error hypothesis; Phase 1 classification escape demonstrated | CP-L01: independent length flag and setup length check | IP-L01; segregate and reconcile software | Phase 1 length exceptions, boundary tests / quality technician |
| H01 | Wrong hole size / pin fit | Drill wear or wrong tool hypothesis | CP-H01: tool identity and first-piece bore check | IP-H01; hold, tool review | FAI-style size example only / machining technician |
| H02 | Hole axis outside position zone / cross-pin assembly interference | Fixture seating or setup hypothesis | CP-H02: datum seating review, first-piece axis evaluation | IP-H02; hold and initiate a new NCR if found | Endpoint/bonus challenge records / quality engineer |
| E01 | End face not square / poor seating | Facing alignment hypothesis | CP-E01: datum alignment and face evaluation | IP-E01; hold and facing review | Invented first-piece reading / quality technician |
| F01 | Cylindricity outside limit / poor functional fit | Tool/process/form hypothesis | CP-F01: form measurement after change | IP-F01; hold and investigate | Invented first-piece form result / quality engineer |
| S01 | Ra exceeds requirement / surface function affected | Finishing/tool hypothesis | CP-S01: agreed profilometer procedure | IP-S01; hold and investigate finishing | Invented Ra record; Phase 1 labels excluded / quality technician |
| G01 | Misleading measurement result / false acceptance or adjustment | Gage/operator variation | CP-G01: bias/linearity/stability, purpose-specific GR&R | Stop measurement release if adequacy unknown | Simulated 10x3x3 GR&R; physical validation open / metrology |

## Control and release gates

1. Verify drawing revision and characteristic IDs before setup.
2. Confirm instruments and methods are adequate; no simulated GR&R substitutes for physical acceptance.
3. Record first-piece characteristics and independent reviewer; only actual personnel may sign.
4. For D01 use five consecutive observations per 15-minute teaching interval; review R and X-bar with the selected tests.
5. On a signal or nonconformance, hold traceable material, preserve data and initiate NCR review. Do not delete signals or reset limits to accommodate them.
6. Implement a supported correction, establish a justified new baseline, and evaluate later observations with fixed limits. CA-001 remains open for effectiveness review because its verification trend alarm is retained.

The original Phase 1 control plan and risk review remain at `reports/`. This linked worksheet extends them for Rev B and Phase 2; it does not retroactively claim the original records measured hole position or surface roughness.
