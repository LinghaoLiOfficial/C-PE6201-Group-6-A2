"""Offline integration check of the distributed commands. No paid API calls."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parent

def main():
    for path in sorted((ROOT/'packets').glob('*.zip')):
        with tempfile.TemporaryDirectory() as td:
            with ZipFile(path) as z: z.extractall(td)
            folder=next(Path(td).iterdir())
            subprocess.run([sys.executable,str(folder/'run_member.py'),'verify'],check=True)
    with tempfile.TemporaryDirectory() as td:
        with ZipFile(ROOT/'packets/D5_LI_LINGHAO.zip') as z:z.extractall(td)
        folder=Path(td)/'D5_LI_LINGHAO'
        spec=importlib.util.spec_from_file_location('dispatch',folder/'run_member.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        original=m.run_case
        def offline(cid,**kw):
            kw['backend']='scripted'
            return original(cid,**kw)
        def invoke(*args):
            with patch.object(sys,'argv',['run_member.py',*map(str,args)]):m.main()
        with patch.object(m,'authenticate',lambda:None),patch.object(m,'run_case',offline):
            invoke('preflight')
            pre=next((folder/'output').glob('preflight-*/preflight.json'))
            invoke('release','--preflight',pre,'--note','OFFLINE TEST ONLY')
            rel=pre.parent/'release.json'
            invoke('full','--preflight',pre,'--release',rel)
            suite=next((folder/'output/full').glob('suite-*'))
            summary=m.read(suite/'summary.json')
            assert summary['trials']==75 and summary['code_passed']==75
            assert summary['judgement_pending']==75 and summary['overall_passed']==0
            invoke('pack','--suite',suite)
            try:invoke('full','--preflight',pre,'--release',rel)
            except ValueError as e:assert 'already started' in str(e)
            else:raise AssertionError('Repeat full run was allowed')
            (folder/'assignment.json').write_text('{}')
            try:invoke('verify')
            except ValueError as e:assert 'Package changed' in str(e)
            else:raise AssertionError('Tampering not detected')
    print('PASS: six extracted manifests; mocked preflight/release/full/pack; pending judgement; rerun and tamper rejection. No live API used.')

if __name__=='__main__':main()
