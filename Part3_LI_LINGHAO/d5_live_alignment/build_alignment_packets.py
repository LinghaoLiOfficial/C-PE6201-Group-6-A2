"""Wrap byte-preserved released member files with workflow alignment guides."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'd5_live_v1_1'
OUT = ROOT / 'packets'
OUT.mkdir(exist_ok=True)
release = json.loads((SOURCE / 'release_manifest.json').read_text())
hashes = {}
for source in sorted((SOURCE / 'packets').glob('D5_*.zip')):
    assert hashlib.sha256(source.read_bytes()).hexdigest() == release['packets/' + source.name]
    target = OUT / (source.stem + '_v1.1_alignment.zip')
    with ZipFile(source) as original, ZipFile(target, 'w', ZIP_DEFLATED) as result:
        for item in original.infolist():
            result.writestr(item, original.read(item.filename))
        for name in ('RUN_ALIGNMENT_EN.md', 'RUN_ALIGNMENT_ZH.md'):
            result.write(ROOT / name, name)
    with ZipFile(source) as original, ZipFile(target) as result:
        for name in original.namelist():
            assert original.read(name) == result.read(name), name
        assert len(result.namelist()) == len(original.namelist()) + 2
    hashes[target.name] = hashlib.sha256(target.read_bytes()).hexdigest()
(ROOT / 'packet_sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
print('Verified six alignment packets: every original member file is byte-identical.')
