"""Rebuild analysis, previews and executed notebook from committed source CSVs."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for args in [['analysis.py'],['scripts/build_dashboard_preview.py'],['scripts/build_notebook.py']]:
 subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
print('Python outputs rebuilt. Run node scripts/build_dashboard.mjs to rebuild Excel.')
