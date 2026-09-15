from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from nbconvert import HTMLExporter
ROOT=Path(__file__).resolve().parents[1]
nb=nbformat.v4.new_notebook(cells=[
nbformat.v4.new_markdown_cell('# Phase 2: ordered SPC and capability\nSynthetic production. Fixed seed20260914; no seed searching or alarm removal. See README.md for sampling, formulas and references.'),
nbformat.v4.new_code_cell("from pathlib import Path\nimport json\nimport pandas as pd\nfrom IPython.display import display, Image\nroot=Path.cwd()\nm=json.loads((root/'results.json').read_text())\nd=pd.read_csv(root/'spc_data.csv')\ng=pd.read_csv(root/'subgroup_results.csv',keep_default_na=False)\ndisplay(d.groupby('Phase',sort=False).agg(Parts=('Part_ID','size'),Failures=('Diameter_Fail','sum')))"),
nbformat.v4.new_markdown_cell('## Frozen-limit monitoring\nEstimate groups1-40; evaluate41-60 with the same limits. Re-estimate only from61-100, then hold fixed for101-140. The selected-rule alert in verification is retained.'),
nbformat.v4.new_code_cell("display(Image(filename='charts/01_xbar_r.png'))\ndisplay(g[(g.X_Rules!='')|(g.R_Rules!='')][['Subgroup','Phase','Mean','Range','X_Rules','R_Rules']])"),
nbformat.v4.new_markdown_cell('## Capability: conditional interpretation\nReference and rebaseline have no selected-rule signals. Verification is provisional because of T3. Shifted and pooled results are descriptive and cannot establish stable capability.'),
nbformat.v4.new_code_cell("display(pd.DataFrame(m['capability']).T[['n','mean','within_sd','overall_sd','Cp','Cpk','Pp','Ppk','failures','interpretation']])\ndisplay(Image(filename='charts/04_capability.png'))"),
nbformat.v4.new_code_cell("display(Image(filename='charts/03_normality.png'))\ndisplay(pd.DataFrame(m['capability']).T[['shapiro_p','lag1','zero_failure_upper95']])"),
nbformat.v4.new_markdown_cell('## Corrective-action decision\nThe programmed shift produces22/100 rejects. Verification produces0/200 but a trend alarm, so effectiveness review remains open. Consult ../quality_documents/corrective_action.md and ../drawing_and_inspection/inspection_plan.md for linked actions and separate simulated inspection examples. Minitab runs remain pending authenticated access.')])
nb.metadata.kernelspec={'display_name':'Python 3','language':'python','name':'python3'}
km=KernelManager();km.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
NotebookClient(nb,timeout=180,resources={'metadata':{'path':str(ROOT/'phase2_spc_capability')}},km=km).execute()
nbformat.write(nb,ROOT/'phase2_spc_capability/spc_analysis.ipynb')
html,_=HTMLExporter(exclude_input=True).from_notebook_node(nb)
(ROOT/'phase2_spc_capability/analysis.html').write_text(html)
print('Executed and exported SPC notebook.')
