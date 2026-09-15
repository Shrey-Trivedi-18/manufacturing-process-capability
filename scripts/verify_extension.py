"""Reconcile saved evidence rather than trusting formatted headlines."""
from pathlib import Path
import json,re,sys
import numpy as np
import pandas as pd
import nbformat
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'phase2_spc_capability'))
from study import generate
d=pd.read_csv(ROOT/'phase2_spc_capability/spc_data.csv')
g=pd.read_csv(ROOT/'phase2_spc_capability/subgroup_results.csv',keep_default_na=False)
m=json.loads((ROOT/'phase2_spc_capability/results.json').read_text())
np.testing.assert_allclose(d.Diameter_mm,generate().Diameter_mm,atol=1e-12)
assert len(d)==700 and len(g)==140
means=d.groupby('Subgroup').Diameter_mm.mean();np.testing.assert_allclose(means,g.Mean,atol=1e-12)
for ph in d.Phase.unique():
    q=d[d.Phase==ph];assert int(q.Diameter_Fail.sum())==m['capability'][ph]['failures']
verify=g[g.Phase=='verification'];assert verify.X_LCL.nunique()==1
assert verify.X_LCL.iloc[0]==m['new_limits']['x_lcl']
assert verify[verify.X_Rules!=''].Subgroup.tolist()==[122]
assert verify[verify.X_Rules!=''].X_Rules.tolist()==['T3']
h=pd.read_csv(ROOT/'drawing_and_inspection/hole_position_examples.csv')
np.testing.assert_allclose(h.Position_Diameter_mm,2*h[['Endpoint1_Radial_mm','Endpoint2_Radial_mm']].abs().max(axis=1))
assert h.Result.tolist()==['Pass','Pass','Fail']
nb=nbformat.read(ROOT/'phase2_spc_capability/spc_analysis.ipynb',as_version=4)
for cell in nb.cells:
    if cell.cell_type=='code':assert cell.execution_count is not None and not any(x.output_type=='error' for x in cell.outputs)
for path,n in [('quality_documents/quality_engineering_case_study.pdf',15),('drawing_and_inspection/gdandt_learning_drawing.pdf',1)]:
    assert len(PdfReader(ROOT/path).pages)==n
comparison=pd.read_csv(ROOT/'minitab/comparison.csv',keep_default_na=False)
assert comparison.Status.str.startswith('NOT RUN').all() and comparison.Minitab.eq('').all()
print('Verified 700 parts, 140 subgroups, retained T3 alert, hole challenge decisions, executed notebook, 16 PDF pages and honest Minitab status.')
