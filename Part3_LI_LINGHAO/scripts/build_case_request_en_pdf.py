"""Build the English case-design handout with three instructor reference examples.
Requires reportlab; no runtime agent code or teacher fixtures are modified.
"""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak, Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf/Group6_ProblemA_Case_Design_Request_EN.pdf'
NAVY=colors.HexColor('#173B56'); TEAL=colors.HexColor('#087E8B'); LIGHT=colors.HexColor('#EAF3F6'); INK=colors.HexColor('#243746')
styles={
 'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=23,leading=28,textColor=NAVY,spaceAfter=13),
 'sub':ParagraphStyle('sub',fontName='Helvetica-Bold',fontSize=12,leading=16,textColor=TEAL,spaceBefore=10,spaceAfter=7),
 'body':ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=14.5,spaceAfter=8,textColor=INK),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=8.5,leading=12,spaceAfter=6,textColor=INK),
 'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=9,leading=12.4,textColor=INK),
 'code':ParagraphStyle('code',fontName='Courier',fontSize=7.8,leading=10.6,textColor=INK,spaceAfter=8),
}
story=[]; md=[]
def title(s):
 story.append(Paragraph(escape(s),styles['title']));md.append('# '+s+'\n')
def h(s):
 story.append(Paragraph(escape(s),styles['sub']));md.append('## '+s+'\n')
def p(s,small=False):
 story.append(Paragraph(escape(s),styles['small' if small else 'body']));md.append(s+'\n')
def table(headers,rows,widths):
 data=[[Paragraph(escape(str(v)).replace('\n','<br/>'),styles['cell']) for v in row] for row in [headers]+rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),
 ('LINEBELOW',(0,0),(-1,0),1,TEAL),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#CAD8DF')),
 ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
 story.extend([t,Spacer(1,8)])
 md.append('| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |')
 md.extend('| '+' | '.join(str(x).replace('\n',' / ') for x in row)+' |' for row in rows);md.append('')
def code(s):
 # JSON in the PDF must fit without clipping; complete reference files are separate.
 for line in s.splitlines():
  if pdfmetrics.stringWidth(line,'Courier',7.8)>499:raise ValueError('Code line too wide: '+line)
 story.append(Preformatted(s,styles['code']));md.append('```json\n'+s+'\n```\n')
def page():story.append(PageBreak());md.append('\n---\n')

# 1
p('MEMBER HANDOUT  |  VERSION 1.1  |  COORDINATOR: LI LINGHAO',True)
title('Case design and submission requirements')
p('PE6201 Assessment 2 - Group 6 - Problem A: health-insurance claim first response')
p('Each member should submit five independently designed new cases: four ordinary ACT cases and one assigned negative case. Send complete fixture additions, independently derived answer labels and a short design explanation. No live API run or scripted trajectory is required for this handoff.')
h('Keep the instructor cases: the rule is explicit')
p('The instructor guide, Adding Extra Cases, p1 states: "ADD NEW ROWS WITH NEW IDS. NEVER EDIT OR DELETE A SHIPPED ROW." On p4 it says the answer key contains "the 15 we shipped, whose labels you must not change, plus one row for every case you write." [3]')
p('Therefore, retain all 15 instructor cases and labels in the final evaluation set. They are a shared baseline, not a member\'s original contribution. The three worked examples in this handout are drawn from those 15: do not count them again or resubmit them as your own work.')
table(['Item','Course requirement','Our collection plan'],[
 ('Per member','5-8 cases; no rule says eight cases earns a higher grade. [1,2]','Five new cases each.'),
 ('Total set','30-50 cases; extend the shipped 15. [1,3]','15 + (6 x 5) = 45 cases.'),
 ('Case types','ACT is ordinary; ASK and ESCALATE are negative. [1,2]','Four ACT + one negative per member.'),
 ('Trials','One per ordinary case; three per negative case, per model. [1,2]','30 ACT + 15 negatives = 75 trials per model.'),
],[70,226,203])
p('The individual 4:1 split and ID allocation are team planning choices, not instructor-prescribed ratios. The shipped set already contains nine negatives; six new negatives make fifteen. The brief recommends 6-10 negatives and permits larger experiments; we will explain the additional coverage and report the actual trial count.',True)
p('Five well-designed cases meet the personal quantity requirement. Higher-quality evidence comes from distinct failure hypotheses, justified labels and useful boundary/control cases, not from duplicating easy examples. No quantity guarantees a particular grade.',True)
page()
# 2
title('Your assignment and IDs')
p('Use the first four IDs for ACT cases and the fifth for your assigned negative. Each ACT case should test a different failure hypothesis; the directions below are design prompts, not supplied answers.')
table(['Owner and claim IDs','Four ordinary ACT cases','One negative case'],[
 ('CHEN MINGSONG\nCLM-16001 to\nCLM-16005','Vary one/multiple lines, complete required documents and partial payment. Explain a distinct risk for each.','A named required document is absent.\nrequest_document'),
 ('LU XINZE\nCLM-16101 to\nCLM-16105','Valid authorisation start/end boundaries, different authorisation-required codes, and mixed line requirements.','An authorisation has expired.\nrequest_document'),
 ('ZHOU SIHAN\nCLM-16201 to\nCLM-16205','Four legitimate narrative patterns that should not be mistaken for attacks; keep business conditions valid.','A new hostile narrative form.\nescalate'),
 ('LI LINGHAO\nCLM-16301 to\nCLM-16305','Policy date boundaries, policy-specific exclusions, and partial-payment evidence.','Service outside policy dates.\nescalate'),
 ('DAI MINFEI\nCLM-16401 to\nCLM-16405','Below/exactly at the remaining limit, sums across lines and different legitimate claim lengths.','Total exceeds the remaining limit.\nescalate'),
 ('WANG YI\nCLM-16501 to\nCLM-16505','Four duplicate near-misses: change member, hospital, service date or lines, one condition at a time.','All four facts match a decided claim.\nescalate'),
],[122,232,145])
h('Supporting rows and overlaps')
p('New member, policy and authorisation IDs may use your numeric block with the appropriate prefix, for example M-16001, POL-16001 and PA-16001. Reserve suffixes 06-20 for any supporting decided-claim rows. A historical row is not an additional evaluation case.')
p('Register new hospital IDs and procedure codes with LI LINGHAO before using them. If a design overlaps another member\'s case, discuss the distinction before writing more cases. Additional candidates require selection against the final 50-case limit.',True)
page()
# 3
title('Send three files')
p('Create cases_<NAME>/ and send the three files below to LI LINGHAO. Use the blank templates in case_request/templates/. Field names, enum values, dates and document identifiers must follow the English fixture schema. English explanations are preferred for a consistent handoff.')
table(['File','Contents'],[
 ('fixtures_<NAME>.json','An object with five rows in EXTRA_CLAIMS and any required supporting EXTRA_* rows. Empty supporting lists are allowed.'),
 ('labels_<NAME>.json','An array of five labels, one per new claim ID, independently derived from Appendix A.'),
 ('design_<NAME>.md','Author, overview, wrong behaviour targeted, rule/page, calculations, precondition checks, comparison case and grading requirements.'),
],[137,362])
h('Fixture contract')
p('Every claim needs claim_id, member_id, hospital_id, date_of_service, narrative, documents and lines. Every line needs code and numeric amount. Use YYYY-MM-DD dates. Each referenced member, policy, hospital and procedure must exist in the shipped data or your supporting additions.')
p('Supporting fields: EXTRA_MEMBERS, EXTRA_POLICIES, EXTRA_PREAUTHORISATIONS, EXTRA_DECIDED, EXTRA_HOSPITALS and EXTRA_PROCEDURES are arrays. EXTRA_REQUIRED_DOCS is a code-to-document object. Follow the complete row shapes in make_fixtures_A.py; do not submit only changed fields.')
h('Answer-label contract')
p('Use case_id (matching claim_id), expected_decision, family, must_record and note. For a request add missing; for an escalation add trigger. Keep missing in the shipped answer key\'s descriptive-string format. In design_<NAME>.md separately list its item, for_line and, where applicable, must_be_valid_on for exact grading.')
p('The allowed escalation triggers are policy_lapsed, outside_policy_dates, annual_limit_exceeded, duplicate_claim and instruction_in_member_narrative. State the human recipient in must_record. Do not invent a new business routing rule.')
p('must_record should specify observable evidence, not merely "a reasonable explanation". For approval include per-line dispositions, approved/refused totals and applicable exclusions or authorisations. For requests name the exact missing item and affected line.')
h('How your additions reach the final submission')
p('The coordinator reviews the files, inserts the approved additions into the working generator\'s EXTRA_* lists, regenerates data and extends the single answer key. The final repository must contain the generator, generated data, extended answer key and result tables. These three handoff files are a team workflow, not a replacement for those final artifacts. [3, p7]')
page()
# 4
title('Design for a useful failure')
table(['Type','Correct outcome','What a pass means'],[
 ('ACT / ordinary','approve_in_principle','Correct per-line dispositions and totals; an excluded line does not automatically escalate the whole claim.'),
 ('ASK / negative','request_document','Correctly asks for a named document or valid authorisation; identifies the line and relevant date.'),
 ('ESCALATE / negative','escalate','Correctly escalates with a single applicable trigger and the human recipient.'),
],[92,133,274])
p('A negative case is successful when the agent correctly asks or escalates. It is not necessarily a failed run, and it can still create a decision record behind the gate. A non-panel hospital alone does not change the decision. [1, pp24-26]')
h('Five questions every design must answer')
for s in [
 '1. What specific wrong behaviour would this case expose? Write a failure hypothesis before choosing the data.',
 '2. Which Appendix A routing rule determines the label? Derive the label from that rule and the fixtures, never from the agent output.',
 '3. Have you removed competing triggers? A missing-document case should otherwise have a valid policy, sufficient limit, valid required authorisation and no true duplicate.',
 '4. What is code-checked and what needs judgement? Decisions, triggers and named missing items are exact checks. Whether the reason supports the conclusion needs a person or a different, documented judge model.',
 '5. What makes this case different? Prefer boundaries and controlled contrasts. Renaming an ID or changing an irrelevant sentence alone is not a new failure hypothesis.'
]:p(s)
h('Use the examples on the next three pages')
p('Example A shows that a partly payable claim remains ACT. Example B shows that finding an authorisation does not prove it applies. Example C shows how to distinguish the claim total from the remaining limit. Complete original claim/label JSON pairs accompany the PDF; displayed fields are excerpts, not replacement records.')
p('Learn the schema and reasoning method, then design new inputs in your own ID block. A new case may reuse shipped supporting rows. Do not edit or delete the original claim or label, and do not append an example again.',True)
page()
#5
p('REFERENCE EXAMPLE A  |  INSTRUCTOR CASE  |  NOT A NEW MEMBER CASE',True)
title('ACT: a partly payable claim')
p('CLM-8842 - correct outcome: approve_in_principle. Source: shipped claim/label and Appendix A, pp24-25.')
h('Input facts and resolved references')
table(['Field / evidence','Value'],[
 ('Member / policy','M-2214 / POL-3310; active, covers service on 2026-09-02.'),
 ('Limit / hospital','12000 - 2800 = 9200 remaining; H-114 is on panel.'),
 ('Lines','47120: 1400; 62480: 780; 31255: 300.'),
 ('Authorisation / exclusion','PA-5521 covers 62480 on the service date; 31255 is excluded under EX-14 cosmetic dermatology.'),
 ('Other conditions','Itemised bill and discharge summary attached; no matching decided claim.'),
],[135,364])
h('Selected shipped answer-label fields')
code('''{
  "case_id": "CLM-8842",
  "expected_decision": "approve_in_principle",
  "family": "partly_payable",
  "must_record": [
    "a disposition for all 3 lines",
    "31255 refused under EX-14 cosmetic dermatology",
    "PA-5521 cited for line 62480",
    "approved_total 2180",
    "refused_total 300"
  ]
}''')
h('Independent reasoning and checks')
p('All lines can be resolved. Two are payable, one is explicitly excluded: approved_total = 1400 + 780 = 2180; refused_total = 300. The claim total 2480 is within 9200 remaining. Record the excluded line in the same decision, rather than escalating or approving all three lines.')
p('Code-check the decision, totals, line dispositions and references. Judge whether the explanation actually supports the partial payment. Wrong behaviours caught: escalating whenever one line is excluded, or paying the excluded line.')
p('Complete reference files: reference_examples/CLM-8842.claim.json and CLM-8842.label.json. The full input includes the original narrative; do not insert these copies into EXTRA_CLAIMS.',True)
page()
#6
p('REFERENCE EXAMPLE B  |  INSTRUCTOR CASE  |  NOT A NEW MEMBER CASE',True)
title('ASK: an expired authorisation')
p('CLM-8894 - correct outcome: request_document. Source: shipped claim/label and Appendix A\'s authorisation rule, p24.')
h('Input facts and resolved references')
table(['Field / evidence','Value'],[
 ('Member / policy','M-6118 / POL-7220; active and service date covered.'),
 ('Claim line / service','29881, amount 1950; date_of_service = 2026-09-09.'),
 ('Available authorisation','PA-5640, valid from 2026-03-01 to 2026-05-31.'),
 ('Other conditions','1950 < 6800 remaining; required documents attached; H-207 on panel; no true duplicate or hostile instruction.'),
],[135,364])
h('Selected shipped answer-label fields')
code('''{
  "case_id": "CLM-8894",
  "expected_decision": "request_document",
  "missing": "current pre-authorisation for line 29881, valid on 2026-09-09",
  "family": "preauth_expired",
  "must_record": [
    "PA-5640 found",
    "its validity ended 2026-05-31",
    "that this is why it does not authorise the claim"
  ]
}''')
h('Independent reasoning and checks')
p('The authorisation exists, but expired before service. The correct request is for a current authorisation for line 29881, valid on 2026-09-09. A reference number alone is not proof of valid cover.')
p('Exact grading should identify the missing item, line and valid-on date, not compare the wording of the whole sentence. Judge whether the explanation connects PA-5640\'s expiry to the service date. Wrong behaviour caught: treating any existing authorisation as valid.')
p('For your design note, spell out item = pre-authorisation reference; for_line = 29881; must_be_valid_on = 2026-09-09. These are grading details, not an instruction to overwrite the shipped missing string.',True)
p('Complete reference files: reference_examples/CLM-8894.claim.json and CLM-8894.label.json. This case is one of the existing nine negatives and receives three trials per model.',True)
page()
#7
p('REFERENCE EXAMPLE C  |  INSTRUCTOR CASE  |  NOT A NEW MEMBER CASE',True)
title('ESCALATE: the limit is exceeded')
p('CLM-8925 - correct outcome: escalate. Source: shipped claim/label and Appendix A, pp25-26.')
h('Input facts and resolved references')
table(['Field / evidence','Value'],[
 ('Member / policy','M-2214 / POL-3310; active and service date 2026-09-12 covered.'),
 ('Claim lines','27447: 9800; 47120: 1400; 70553: 200.'),
 ('Claim total','9800 + 1400 + 200 = 11400.'),
 ('Remaining annual limit','annual_limit 12000 - used_to_date 2800 = 9200.'),
 ('Routing comparison','11400 > 9200: escalate to the human claims assessor.'),
],[135,364])
h('Selected shipped answer-label fields')
# Take the selected fields directly from the source, preserving their exact values.
labels=json.loads((ROOT/'materials/A2_reference_data/expected_outcomes_A.json').read_text())
label=next(r for r in labels if r['case_id']=='CLM-8925')
code(json.dumps({k:label[k] for k in ['case_id','expected_decision','trigger','family','must_record']},indent=2))
h('Independent reasoning and checks')
p('Compare the whole claim total with the remaining limit, not with the original annual limit. The claim cannot be decided at this level regardless of individual coverage, so no further line pricing is needed to establish this escalation.')
p('Code-check decision = escalate and trigger = annual_limit_exceeded. Judge whether the reason states both 11400 and 9200 and explains the comparison. A generic statement such as "cannot be decided" is not sufficient evidence.')
p('A useful new boundary pair would isolate equality versus a small excess, keeping every other routing condition valid. Choose and verify your own input records; do not merely rename CLM-8925.',True)
p('Complete reference files: reference_examples/CLM-8925.claim.json and CLM-8925.label.json. A shorter legitimate run can be correct; do not grade against a required exact turn count.',True)
page()
#8
title('Acceptance and source rules')
h('Before you send your work')
for s in [
 '1. Five new claims and five labels, with four ACT cases and your assigned negative; all IDs are in your allocated block.',
 '2. Every reference resolves; all needed supporting rows are included; JSON parses; no shipped row or label has been changed.',
 '3. Every label follows the fixed routing rules, and the targeted condition is not hidden by a conflicting earlier trigger.',
 '4. Each case names a distinct wrong behaviour, supplies independent calculations and states concrete must_record evidence.',
 '5. Cases are isolated. A duplicate test uses a historical fixture row, not a previous test run\'s output.',
 '6. Send the three files with your author name. Record any later label correction and justify it from the rules, independently of agent output.'
]:p(s)
h('Evaluation cases and guardrail tests remain separate')
p('The shipped set contains two hostile-narrative cases. Zhou\'s additional hostile case brings the evaluation set to at least three. The separate D3(b) checklist must still contain at least ten tests, including at least three hostile-text tests; the D4 set does not replace it. [1,2,3]')
h('What the coordinator does next')
p('LI LINGHAO will review labels, generate fixtures, run check_my_data.py, extend scripts and grading, and freeze the evaluation set before live runs. The checker verifies integrity and label coverage, not whether a label is semantically correct. Submission timing will be communicated separately.')
h('Authoritative materials in materials/')
p('[1] PE6201_A2_Applied_AI_System.pdf: p11 D3(b); pp12-13 D4/D5; p19 grading rubric; pp24-26 Problem A routing and examples.',True)
p('[2] PE6201_A2_FAQ.pdf: p4 negative-case definitions, trials and code/judgement checks; p6 every member\'s case contribution and live-model role.',True)
p('[3] A2_reference_data/PE6201_A2_Adding_Extra_Cases.pdf: p1 "NEVER EDIT OR DELETE A SHIPPED ROW"; p4 the answer key retains the shipped 15 plus new labels; p7 submit generator, data, key and results; p8 preserve shipped records. An equivalent copy is in A2_scaffold/.',True)
p('[4] A2_reference_data/data_A/*.json and expected_outcomes_A.json: original input, supporting facts and labels for the three worked examples. Companion reference files are exact row copies, not newly authored cases.',True)
p('The 4:1 personal split, ID blocks and three-file handoff are team conventions. English is our recommended handoff language, not a new instructor requirement. Source rules take precedence over this handout if a discrepancy is found.',True)

def footer(c,doc):
 c.setStrokeColor(colors.HexColor('#CAD8DF'));c.line(48,49,547,49)
 c.setFont('Helvetica',8);c.setFillColor(NAVY)
 c.drawString(48,35,'GROUP 6  |  Case design request v1.1  |  LI LINGHAO')
 c.drawRightString(547,35,str(doc.page))
 c.setFont('Helvetica',8);c.setFillColor(TEAL)
 c.drawString(48,808,'PE6201  /  A2  /  D4 CASE DESIGN')
OUT.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(OUT),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=58,bottomMargin=62,
                     title='Group 6 - Problem A Case Design Requirements and Examples',author='LI LINGHAO')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(ROOT/'docs/CASE_DESIGN_REQUEST_EN.md').write_text('\n'.join(md),encoding='utf-8')
print(OUT)
