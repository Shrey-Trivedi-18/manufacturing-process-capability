"""Locate an existing bundled runtime; never download or modify dependencies."""
from pathlib import Path
import os,subprocess
root=Path(__file__).resolve().parents[1]
runtime=Path(os.environ.get('QUALITY_RUNTIME_ROOT',Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies'))
node=runtime/'node/bin/node'
packages=runtime/'node/node_modules'
if not node.exists() or not (packages/'@oai/artifact-tool/package.json').exists():
 raise SystemExit('Bundled spreadsheet runtime unavailable. Set QUALITY_RUNTIME_ROOT to its dependencies directory. Python report/PNG rebuilding does not require this runtime.')
env=os.environ.copy();env['ARTIFACT_TOOL_RESOLVE_FROM']=str(runtime/'node/package.json')
subprocess.run([str(node),str(root/'scripts/build_dashboard.mjs')],cwd=root,env=env,check=True)
