"""Independent saved-output reconciliation. Never alters source artifacts."""
from pathlib import Path
import hashlib,json,re,sys,zipfile,xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from analysis import summary,gage_analysis
d=pd.read_csv(ROOT/'data/manufacturing.csv',keep_default_na=False)
m=json.loads((ROOT/'dashboard/metrics.json').read_text())
assert summary(d)==m['baseline']
assert hashlib.sha256((ROOT/'data/manufacturing.csv').read_bytes()).hexdigest()==m['source_sha256']
assert sum(m['primary_defects'].values())==m['baseline']['failures']
nb=json.loads((ROOT/'quality_analysis.ipynb').read_text())
codes=[c for c in nb['cells'] if c['cell_type']=='code']
assert all(c['execution_count'] is not None for c in codes)
assert not any(o.get('output_type')=='error' for c in codes for o in c.get('outputs',[]))
for p in ROOT.rglob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not target.startswith(('http:','https:','#')):
   assert (p.parent/target.split('#')[0]).exists(),(p,target)
if '--skip-excel' not in sys.argv:
 z=zipfile.ZipFile(ROOT/'dashboard/quality_dashboard.xlsx');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 sheet=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
 cells={c.get('r'):c for c in sheet.findall('.//s:c',ns)}
 def number(a):return float(cells[a].find('s:v',ns).text)
 for a,v in {'A6':len(d),'D6':m['baseline']['failures'],'G6':m['baseline']['pass_rate'],'J6':m['baseline']['ppm'],'C42':m['baseline']['failures']-m['centered']['failures']}.items():
  assert abs(number(a)-v)<1e-8,(a,number(a),v)
 assert len([p for p in z.namelist() if re.fullmatch(r'xl/(?:drawings/)?charts/chart\d+.xml',p)])==2
 data=ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
 rows=data.findall('.//s:sheetData/s:row',ns)
 assert sum(int(r.get('r'))>=6 for r in rows)==len(d)
 for name in z.namelist():
  if name.startswith('xl/worksheets/') and name.endswith('.xml'):
   assert not ET.fromstring(z.read(name)).findall('.//s:c[@t="e"]',ns),name
print(f'Verified {len(d):,} observations, {len(codes)} executed notebook cells, source hash, links and'+(' Python outputs.' if '--skip-excel' in sys.argv else ' saved Excel totals/charts.'))
