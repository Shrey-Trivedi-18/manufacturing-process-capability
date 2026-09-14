"""Build and execute the concise analysis notebook, then export readable HTML."""
from pathlib import Path
import sys
import nbformat as nbf
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client import KernelManager
ROOT=Path(__file__).resolve().parents[1]
md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
cells=[
md('''# Machine centering and inspection yield

**A simulated machining-quality case study.** The decision is whether correcting a diameter offset is sufficient to address the modeled inspection losses. No factory observations, physical Gage R&R or realized savings are claimed.

The generator deliberately assigns machine offsets, thermal response and categorical failure probabilities. The contribution is checking inspection consistency, separating dimensional from total-yield effects, and testing how the modeled decision changes under imperfect centering. This is not independent discovery of a physical root cause.'''),
code('''from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Image
from analysis import summary, validate, gage_analysis, machine_summary
from generate_data import generate_production_data
ROOT=Path.cwd()
d=pd.read_csv(ROOT/'data/manufacturing.csv',keep_default_na=False)
g=pd.read_csv(ROOT/'data/gage_rr.csv')
validate(d)
m=json.loads((ROOT/'dashboard/metrics.json').read_text())
display(Image(filename=str(ROOT/'dashboard/quality_dashboard_preview.png')))
'''),
md('''## 1. Inspection definition and reconciliation

Diameter limits are 19.70–20.30 mm and length limits are 49.50–50.50 mm, inclusive. A part fails if either dimension is outside its interval or it has an assigned categorical defect. Each failed part has one primary label; individual characteristic flags may overlap.

The original inspection logic omitted length even though length was measured. Two previously passing parts violate length limits. The repair preserves the generated measurements and random draws; it changes classification, not the manufacturing distribution.'''),
code('''display(pd.Series(summary(d),name='Baseline'))
display(d.loc[d.Length_Fail,['Part_ID','Length_mm','Inspection_Result']])
display(machine_summary(d).round(5))
display(d.loc[d.Inspection_Result.eq('Fail'),'Defect_Type'].value_counts().to_frame('Primary failures'))'''),
md('''## 2. What the measurement simulation establishes

Ten true diameters are sampled as quantiles of the mixed-machine distribution. Three modeled operators measure each part three times, using operator bias and random repeatability noise. A balanced crossed ANOVA estimates part, operator, interaction and repeatability components. Negative component estimates are truncated at zero; the interaction term is retained rather than selected by a significance test.

This demonstrates a variance-component calculation, not validation of a physical gage. No physical bias, linearity, stability or attribute-agreement study was conducted.'''),
code('''rr=gage_analysis(g)
display(pd.Series(rr,name='Simulated GR&R'))
spread=d.groupby('Machine').Diameter_mm.std()
display((100*rr['grr_sd']/spread).rename('Gage SD / observed machine SD (%)').to_frame())'''),
md('''The 9.13% study-variation result depends on the broad selected part range. The gage SD is approximately 28–30% of individual-machine observed SD; that diagnostic is not a new machine-specific GR&R study. The 9.76% tolerance comparison uses six estimated gage SDs divided by the 0.60 mm diameter tolerance. Neither figure is blanket approval of a measurement system.

## 3. Authored variation, measured transparently

Machine means and distributions are the primary evidence. The regression below checks whether the analysis recovers the authored machine/temperature relationships, using a centered temperature variable and HC3 standard errors. Effect sizes matter more than tiny p-values in a large synthetic sample. These intervals are conditional on the simulated model, not uncertainty about a real factory.'''),
code('''from statsmodels.formula.api import ols
model_data=d.assign(Temperature_centered=d.Temperature_C-22)
model=ols('Diameter_mm ~ C(Machine)*Temperature_centered + C(Shift) + C(Supplier)',data=model_data).fit(cov_type='HC3')
ci=model.conf_int()
display(pd.DataFrame({'Coefficient_mm':model.params,'Lower_95':ci[0],'Upper_95':ci[1]}).round(6))
print(f'Descriptive fit R-squared: {model.rsquared:.4f}')
fig,axes=plt.subplots(1,2,figsize=(11,3.5))
axes[0].scatter(model.fittedvalues,model.resid,s=3,alpha=.15)
axes[0].axhline(0,color='gray');axes[0].set(xlabel='Fitted diameter (mm)',ylabel='Residual (mm)',title='Residuals retain unequal spread')
from scipy import stats
stats.probplot(model.resid,plot=axes[1]);axes[1].set_title('Residual normal-probability plot')
plt.tight_layout();plt.show()
display(model_data.assign(Residual=model.resid).groupby('Supplier').Residual.agg(['count','std']).rename(columns={'std':'Conditional_residual_SD_mm'}))'''),
md('''Supplier spread is examined in residuals after accounting for the large machine-center differences, rather than treating pooled machine mixtures as a clean supplier comparison. This remains a descriptive check of the generator.

No pooled Ppk, normal-tail defect prediction or operational SPC claim is used. Day-level dates were randomly assigned, and part IDs do not recover real within-day sequence. A deployment-ready control chart would require a real sampling and ordering design plus a stable baseline.

## 4. Ideal centering: dimensional and total outcomes differ'''),
code('''centered=generate_production_data(process_centered=True)
comparison=pd.DataFrame({'Baseline':summary(d),'Ideal centering':summary(centered)}).T
display(comparison)
print('Net failures avoided:',summary(d)['failures']-summary(centered)['failures'])
display(pd.crosstab(d.Defect_Type,centered.Defect_Type))'''),
md('''The +0.220 mm M3 offset becomes zero; thermal sensitivity and all random draws remain paired. Diameter failures fall from 80 to zero in seed 42, while total failures fall by 75. Five formerly oversize parts receive other primary labels under the sequential classification model. Two length failures remain.

This is an idealized parameter change, not a controlled production experiment. There is no modeled offset-adjustment cost, downtime, wear, drift or achieved savings.

## 5. Sensitivity to remaining offset and random seed

Thirty paired seeds (0–29), each with 20,000 parts, compare the original +0.220 mm offset with residual offsets of 0, 0.05, 0.10, 0.15 and 0.22 mm. These are analyst-selected scenarios, not empirically calibrated adjustment-error probabilities. The range is simulation variability, not a confidence interval for real-world improvement.'''),
code('''s=pd.read_csv(ROOT/'results/sensitivity.csv')
display(s.groupby('residual_offset_mm').avoided_failures.agg(['count','mean','min','max']).round(2))
ideal=s.loc[s.residual_offset_mm.eq(0),'avoided_failures']
print(f'Ideal centering across 30 seeds: mean {ideal.mean():.1f}, range {ideal.min()}–{ideal.max()} net failures avoided per 20,000 parts.')'''),
md('''## 6. Decision and next evidence

Within this model, centering addresses the diameter offset but leaves most inspection losses. A next engineering investigation would separately assess surface-acceptance criteria, actual adjustment reliability and cost, then run independent confirmation trials. The synthetic category called surface finish is not a measured Ra result.

The proposed process/CTQ mapping, control plan and qualitative risk review describe evidence needed before deployment. They do not claim factory implementation or invented priority ratings. The drawing remains an optional specification exercise; its hole, geometric controls and roughness are not measured in this dataset.

### Interpretation references

- [NIST: process stability](https://www.itl.nist.gov/div898/handbook/ppc/section4/ppc45.htm)
- [Minitab: Gage R&R interpretation](https://blog.minitab.com/en/blog/quality-data-analysis-and-statistics/how-to-interpret-gage-output-part-2)

All numerical production and measurement results above are generated simulation outputs. See `reports/methods.md` for definitions, assumptions and reproducibility.''')]
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}})
km=KernelManager(kernel_name='python3');km.kernel_spec.argv[0]=sys.executable
client=NotebookClient(nb,timeout=180,km=km,resources={'metadata':{'path':str(ROOT)}})
client.execute()
nbf.write(nb,ROOT/'quality_analysis.ipynb')
exporter=HTMLExporter();exporter.exclude_input=True
body,_=exporter.from_notebook_node(nb)
(ROOT/'reports/analysis.html').write_text(body)
print('Notebook executed and HTML report exported.')
