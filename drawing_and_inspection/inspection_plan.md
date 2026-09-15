# QE-001 Rev B - drawing interpretation and inspection plan

Learning specification only. The original Onshape export is retained under `reports/`. The separate Rev B inspection drawing is an authored schematic/addendum, not a new native Onshape export. Datum letters change intentionally: **Rev B A = outside cylindrical datum feature / derived shaft axis; Rev B B = left end face.** Do not apply these labels to the older sheet, which used the opposite labels.

## Functional assumptions

The shaft locates in a cylindrical mating feature and seats at the left end. Its cross-hole has no required clocking angle around the shaft. Primary datum A constrains two transverse translations and two tilts; secondary end plane B constrains axial translation. Rotation about A remains free by design. If an assembly needs angular clocking, add a functional feature and tertiary datum before use. This drawing is not a manufacturing release or a claim of full Y14.5 compliance.

| ID | Learning requirement | Method and setup | Defined teaching sample plan | Acceptance / reaction |
|---|---|---|---|---|
| D01 | OD 20.00 +/-0.30 mm | Micrometer at three axial stations, two orientations; establish cylindrical datum separately for geometry | First piece and after every setup; Phase 2 five consecutive parts/15 min | All local sizes 19.70-20.30; check relevant form/envelope separately; hold since last accepted check and NCR-001 |
| L01 | Length 50.00 +/-0.50 mm | Calibrated height gage on suitable seating fixture, or validated caliper | First piece; five/15 min in a real teaching plan, not collected by Phase 2 | 49.50-50.50; hold, review end stop and independent recheck |
| H01 | Cross-hole 5.00 +/-0.05 THRU | Bore/pin method with adequate access; size at multiple sections | First piece; after drilling tool/fixture change; five/lot assumed | Local size 4.95-5.05; hold and assess drill/reamer |
| H02 | Position diameter 0.10 at MMC relative A then B; axial basic 25, axis perpendicular to A | CMM/validated functional method; establish A before B; evaluate entire derived axis across hole length, allow unconstrained clocking | First piece and after fixture change; five/lot assumed | Allowed zone 0.10 + actual mating size - 4.95, only while H01 passes; hold/NCR and fixture review |
| E01 | B end-face perpendicularity 0.05 to A | CMM or suitably constrained sweep excluding runout/setup artifacts | First piece and after facing/setup change | Face fits between planes 0.05 apart perpendicular to A; hold and inspect seating/facing |
| F01 | OD cylindricity 0.10 | Form tester or validated dense CMM sampling along OD | First piece and after process change | Surface fits coaxial cylinders 0.10 radial separation; no datum references; hold |
| S01 | OD Ra <=3.2 micrometres | Profilometer; procedure must specify filter, cutoff, evaluation length and lay direction before physical use | First piece; after finishing/tool change; five/lot assumed | <=3.2 under agreed procedure; hold and investigate finishing |

Frequencies other than the explicit Phase 2 subgroup schedule are assumed teaching controls, not statistically justified sampling or an AQL plan. Lots with signals remain held; passing a sample alone does not release them. No formal FAI, PPAP or AS9102 approval is claimed.

## GD&T reading guide

- A datum feature is the imperfect physical surface; the datum is the theoretically exact reference established from it. The gage/fixture must simulate the datum precedence.
- The basic 25 mm dimension locates the ideal cross-hole axis from B. It is not a +/- dimension; position provides the permitted variation.
- A position zone here is cylindrical. Its 0.10 value is a diameter, not a radius. It controls location and orientation of the derived axis. A center coordinate alone cannot certify a tilted or bowed hole.
- Internal-hole MMC is the smallest allowed hole, 4.95 mm; LMC is 5.05. For the ideal cylindrical-hole example at 5.02, bonus =0.07 and allowed zone=0.17. Virtual condition is 4.95-0.10=4.85 mm for the applicable ideal functional-boundary exercise.
- Without a material modifier the tolerance is RFS; there is no size-dependent bonus. LMC applies at least material and is a different design choice, often related to wall thickness; it is not used here.
- Datum A has no material-boundary modifier in this learning callout: do not add arbitrary datum shift to the bonus calculation.
- End-face perpendicularity is two parallel planes 0.05 apart, not a cylindrical zone and not a +/- angle. It does not control location of the plane.
- Surface Ra, cylindricity and perpendicularity cannot be inferred from one diameter measurement. Phase 1 surface-finish labels are not profilometer measurements.

## First-piece records

`first_piece_records.csv` contains one complete invented learning record plus deliberate boundary/failure challenge records for H02. For the hole geometry check, a perfectly straight cylindrical axis is represented by two endpoints across 20 mm, after datum alignment and the allowed clocking alignment. The maximum endpoint radial deviation controls this simplified straight-line example; form error and real datum-establishment uncertainty are excluded. The boundary case tests 0.17 exactly and the failing case exceeds it by 0.01. These are calculated examples, not CMM exports.

Physical use still requires instrument calibration, method validation, environmental controls, a measurement-uncertainty decision rule and drawing approval. No signature or traceability certificate has been invented.

References: [ASME Y14.5 scope](https://www.asme.org/products/codes-standards/y145-2018-dimensioning-and-tolerancing); [position and feature-control-frame interpretation](https://www.tec-ease.com/Position-Symbol.php). Accessed 2026-09-14.
