"""Export actual diagnostic records as a six-trial judge suite; no agent reruns."""
import argparse,csv,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'runtime'))
from integration.d4_harness import read,write,sha,load_contract,code_check,export_results,REVIEW_FIELDS
from integration.output_contract import REVISION

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('preflight',type=Path)
    a=p.parse_args();pre=read(a.preflight)
    if pre.get('contract_revision')!=REVISION:raise ValueError('Wrong revision')
    target=Path(tempfile.mkdtemp(prefix='judge-input-',dir=a.preflight.parent))
    labels,expected=load_contract();labels={l['case_id']:l for l in labels}
    rubric=read(ROOT/'runtime/integration/rubric_clarifications.json')
    rows=[];reviews=[]
    for record in pre['records']:
        cid=record['case_id'];label=labels[cid]
        failures=code_check(record,expected[cid])
        name=cid+'-trial-1.json';write(target/name,record)
        row=dict(case_id=cid,trial=1,negative=label['expected_decision']!='approve_in_principle',record=record,failures=failures,code_passed=not failures,judgement='pending' if record['status']=='completed' else 'not_reviewable')
        rows.append(row)
        if row['judgement']=='pending':
            for i,c in enumerate(label['must_record'],1):
                reviews.append(dict(review_id=f'{cid}/1/{i}',case_id=cid,trial=1,criterion=rubric['replacements'].get(c,c),verdict='',graded_by='',comments='',record_path=name))
    metadata=dict(contract_revision=REVISION,backend='live',model=pre['assignment']['model'],prompt_version=pre['assignment']['version'],scope='six-case diagnostic; not formal battery',source_preflight_sha256=sha(a.preflight),package_sha256=pre['package_sha256'])
    write(target/'metadata.json',metadata);write(target/'review_template.json',reviews)
    write(target/'grading_contract.json',dict(labels=list(labels.values()),audit=expected,clarifications=rubric))
    with (target/'human_review.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=REVIEW_FIELDS);w.writeheader();w.writerows(reviews)
    export_results(target,rows,metadata)
    print(target)
