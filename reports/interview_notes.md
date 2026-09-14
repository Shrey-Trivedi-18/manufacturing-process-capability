# Explaining the project

## Short explanation

I built a simulated machining-quality study to examine whether correcting one machine's diameter offset would meaningfully reduce inspection losses. I checked the measurement analysis, found two length failures missing from the inspection logic, and compared paired centering scenarios. Ideal centering removes the seed-42 diameter failures but avoids only 75 of 1,067 total failures because most assigned defects have other causes. The project demonstrates analysis and model interpretation, not a real production improvement.

## Questions to prepare for

**How did you do GR&R without a shop?** I did not conduct a physical study. I generated ten true part diameters and 90 readings across three operators and three trials, then estimated crossed-ANOVA variance components. The 9.13% figure describes that selected simulated part range, not gage approval.

**Did you discover the M3 problem?** No. The generator deliberately makes M3 high and temperature-sensitive. The analysis checks those relationships and explores the consequences and limitations of an adjustment.

**Why not use pooled capability or an I-MR chart?** The baseline mixes machine centers and the dates do not establish real production order. I use distributions and observed conformance rather than imply stable qualified capability.

**What changed in the repair?** Length is now included in final classification, conclusions match the evidence, the dashboard has a documented rebuild, and automatic checks catch boundary/classification errors.

**What would you do in a factory?** Establish measurement adequacy, document actual run order and setup history, define defect acceptance criteria, assess costs and repeat independent confirmation trials before recommending implementation.

**Did you use assistance?** Explain the tools and assistance you actually used, and which decisions you reviewed yourself. Do not claim to have independently authored or physically performed work you did not do. Be able to explain the generator, denominators, GR&R limitations and paired scenarios without reading a script.
