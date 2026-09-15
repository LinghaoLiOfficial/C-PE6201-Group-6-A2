#!/usr/bin/env python3
"""Create a clean local archive, excluding credentials and unrelated legacy code."""
import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIRECTORIES=['claim_agent','A2_reference_data','tests','scripts','docs','results','output']
FILES=['README.md','CONTRIBUTIONS.md','IMPROVEMENTS.md','IMPROVEMENTS_ZH.md','run_eval.py','.gitignore','requirements-authoring.txt']

def members():
    paths=[]
    for d in DIRECTORIES:
        for p in (ROOT/d).rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts or p.name.startswith('.'):continue
            if p.name in ['EDITORIAL_BRIEF.md','INTEGRATION_CONTRACT.md','TEAM_COORDINATION.md']:continue
            if p.suffix in ['.pyc','.zip']:continue
            if d=='A2_reference_data' and p.suffix=='.pdf':continue
            paths.append(p)
    paths += [ROOT/f for f in FILES if (ROOT/f).exists()]
    return sorted(set(paths))

def main():
    target=ROOT/'PE6201_A2_Group-6.zip'
    paths=members();manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.name!='package_manifest.json'}
    (ROOT/'results/package_manifest.json').write_text(json.dumps(manifest,indent=2));paths=members()
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for p in paths:z.write(p,'PE6201_A2_Group-6/'+str(p.relative_to(ROOT)))
    with zipfile.ZipFile(target) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('Archive integrity failure: '+bad)
    print(json.dumps({'archive':str(target),'files':len(paths),'bytes':target.stat().st_size},indent=2))
if __name__=='__main__':main()
