# NCR-001 / CA-001 - diameter compensation after setup

**SIMULATED CASE.** Records below are authored process evidence for training, not interviews, shop measurements, approvals or actual supplier/customer correspondence. We chose diameter so the NCR is directly supported by the SPC dataset. Cross-hole inspection remains a separate drawing exercise.

## Detection and nonconformance

- Part: learning shaft QE-001, Rev B learning specification; CTQ D01, diameter 19.700-20.300 mm.
- Event: setup changed from VERIFIED_ZERO to OFFSET_027 at subgroup 41. The simulated setup log is the `Setup_Code` column; its identity is known from the generator.
- Detection: X-bar T1 at subgroup 41 under frozen reference limits; all groups 41-60 trigger T1. The low within-group spread does not excuse the changed mean.
- Affected scope: SPC-041-1 through SPC-060-5, 100 modeled parts. Independent full diameter classification finds 22 above USL. Preserve all 100 in the challenge lot; these are not 100 defective parts.
- Reference: groups 1-40 have 0/200 diameter failures. No claim about unmodeled inventory or customers.

## Containment and disposition

Teaching response: hold the challenge lot, block shipment, preserve the setup record and verify the gage against a reference before adjusting the process. Evaluate all 100 measurements independently of the control chart. Segregate 22 nonconforming pieces for engineering disposition; the other 78 remain held until setup and verification review. No assumed rework feasibility, scrap cost, actual release or customer escape is asserted. Stop at the first signal in a live process; the remaining challenge data are retrospective training evidence.

## Fishbone and evidence discipline

| Branch | Hypothesis | How it would be tested | Evidence in this simulation |
|---|---|---|---|
| Method | Wrong diameter compensation entered after setup | Compare controlled recipe and controller audit trail | Generator and Setup_Code explicitly switch +0.270 mm |
| Machine | Tool damage or spindle shift | Inspect tool/holder and independent test cut | Not modeled; no evidence to rule out in a shop |
| Measurement | Micrometer zero bias | Traceable check before/after, independent gage | Noise is authored as unchanged; no physical verification |
| Material | Stock/material change | Lot trace and hardness/material check | Not modeled |
| People | Missing independent first-piece review | Review sign-off history and training | Hypothetical process-design gap |
| Environment | Thermal shift | Compare part temperature and stabilization | No changing thermal term in Phase 2 |

## Five Whys - proposed causal chain

1. Why are diameters near/above the upper limit? The measured distribution shifted upward.
2. Why did the mean shift? The authored setup introduced +0.270 mm diameter compensation.
3. Why could that setting reach production? A hypothetical setup workflow allowed manual entry without comparison to the approved recipe.
4. Why was it not intercepted at setup? An independent first-piece verification gate was absent in the proposed workflow.
5. Why was that gate absent? The hypothetical control plan did not assign a required owner, acceptance evidence and release record after setup changes.

Only items 1-2 are demonstrated by generated data/code. Items 3-5 are a proposed system-level explanation for designing a preventive control; they are not a discovered factory root cause. A real RCA would gather those records before accepting the chain.

## Actions and ownership

| Action | Proposed role | Evidence / status |
|---|---|---|
| Restore approved zero compensation | Setup technician | Generator returns mean to 20.000 at group 61; simulated implementation complete |
| Require controlled recipe comparison after every setup | Manufacturing engineer | Added to CP-D01; proposed, not deployed |
| Independent first-piece diameter + length check | Quality technician | IP-D01/L01 acceptance record required before release |
| Freeze revised chart limits after rebaseline | Quality engineer | Groups 61-100 only; preserved in results.json |
| Verify effectiveness on later production | Quality engineer | 101-140: 0/200 rejects, but one T3 trend alert; review pending |

## Effectiveness and closure decision

The point comparison is 22/100 diameter failures in the challenge lot versus 0/200 in verification. Reference and rebaseline are both 0/200. This is a programmed intervention example, not proof that a real-world action caused a 22 percentage-point reduction. Verification Cpk/Ppk are provisional because the selected T3 rule triggers. No data are excluded to clean the chart.

**CA-001 status: implementation demonstrated in simulation; effectiveness review open.** Preserve and examine the flagged six-point trend, check for a physical mechanism in a real process, and define an additional confirmation run before closure. A false signal is possible under the unchanged generator, but cannot be used as a blanket reason to ignore an alarm in practice. This is an RCA/corrective-action case, not a completed 8D or AS9102 submission.
