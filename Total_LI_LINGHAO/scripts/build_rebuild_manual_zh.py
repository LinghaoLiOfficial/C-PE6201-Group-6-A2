#!/usr/bin/env python3
"""Render a source-grounded, step-by-step Chinese reconstruction manual."""
import ast, hashlib, json, re, textwrap
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.platypus.tableofcontents import TableOfContents
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf/PE6201_A2_Group-6_Rebuild_Manual_ZH.pdf'
pdfmetrics.registerFont(TTFont('ManualCN','/System/Library/Fonts/Supplemental/Songti.ttc',subfontIndex=0))
BLUE=colors.HexColor('#173D55');TEAL=colors.HexColor('#108782')
styles={
 'h1':ParagraphStyle('h1',fontName='ManualCN',fontSize=18,leading=25,textColor=BLUE,spaceAfter=13,keepWithNext=True,wordWrap='CJK'),
 'h2':ParagraphStyle('h2',fontName='ManualCN',fontSize=11.3,leading=17,textColor=TEAL,spaceBefore=9,spaceAfter=5,keepWithNext=True,wordWrap='CJK'),
 'p':ParagraphStyle('p',fontName='ManualCN',fontSize=10,leading=16,textColor=BLUE,spaceAfter=7,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='ManualCN',fontSize=8.8,leading=13,textColor=BLUE,spaceAfter=5,wordWrap='CJK'),
 'code':ParagraphStyle('code',fontName='Courier',fontSize=7.4,leading=9.3,textColor=BLUE),
 'codecn':ParagraphStyle('codecn',fontName='ManualCN',fontSize=8,leading=9.3,textColor=BLUE),
 'toc':ParagraphStyle('toc',fontName='ManualCN',fontSize=10,leading=17,textColor=BLUE,leftIndent=0,firstLineIndent=0,spaceAfter=4)}
SOURCE_FILES=['claim_agent/__init__.py','claim_agent/tools.py','claim_agent/agent.py','claim_agent/backends.py','claim_agent/harness.py','run_eval.py','tests/test_tools.py','tests/test_loop.py','tests/test_guardrails.py','tests/test_d7.py','scripts/check_guardrail_variants.py','scripts/reproduce.py','scripts/run_live.py','scripts/run_judgement.py','scripts/replay_judgements.py','scripts/build_analysis.py','scripts/reconcile_spend.py','scripts/verify_package.py','scripts/build_report.py','scripts/package_submission.py']
DOC_FILES=['docs/PREBUILD.md','docs/DESIGN.md','docs/TOOL_CONTRACTS.md','docs/DATA_DESIGN.md','docs/EXPERIMENT_PROTOCOL.md','docs/GUARDRAIL_CHECKLIST.md','CONTRIBUTIONS.md','docs/SELF_APPRAISAL.md','docs/DEMO_EN.md','docs/DEMO_ZH.md']
TEACHER=[
 ('T1','PE6201_A2_Applied_AI_System.pdf','教师作业brief；本地PDF原件，29页。p.4–18 D0–D7，p.18–21交付/评分/参与，p.24–26 Problem A。'),
 ('T2','PE6201_A2_FAQ.pdf','教师FAQ原件，7页；p.1只是问题目录，应引用正文p.2–7。'),
 ('T3','A2_reference_data/PE6201_A2_Adding_Extra_Cases.pdf','教师扩案指引原件，8页。可与scaffold内副本对照。'),
 ('T4','../course_ipynb/PE6201_Class4_C2_Agent_Build.ipynb','教师课堂notebook；按从1开始的物理cell编号定位，不按execution_count。带_PRERUN是另一个运行副本，不能混用cell号。'),
 ('T5','../course_ipynb/PE6201_Class5_C2_Cost_to_Serve.ipynb','教师成本notebook；模型公式来源。团队需要另存工作副本才算产出。'),
 ('T6','../TEAM_DECLARATION.docx','教师模板的已填写团队副本：字段与说明源自教师，填入的团队ID/成员/分工属于团队内容。不是空白原件。'),
 ('T7','A2_scaffold/','教师脚手架输入：agent/backends/tools/guardrails/prompt/config/harness/run_eval/demo_loop_failure与Tour notebook。只读参考，最终运行模块为N类claim_agent，不是这些原文件。'),
 ('T8','../Part3_LI_LINGHAO/A2_reference_data/','留存的教师reference-data基线：make_fixtures_A.py的EXTRA为空；checker、原15案/标签作保护基线。当前工作目录A2_reference_data已被扩充，不再整体属于原件。')]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 story=[];md=[];source_index=[];step_pages={};anchors=0
 def para(text,style='p'):story.append(Paragraph(escape(str(text)),styles[style]));md.extend([str(text),''])
 def heading(text,level=1,key=None):
  nonlocal anchors
  anchors+=1;p=Paragraph(escape(text),styles['h1' if level==1 else 'h2']);p.anchor=key or 'a'+str(anchors);p.toc_entry=level==1
  story.append(p);md.extend(['#'*level+' '+text,''])
 def page():story.append(PageBreak());md.extend(['','---',''])
 def code(content,numbered=False,start=1):
  md.extend(['```text',content,'```',''])
  for i,line in enumerate(content.splitlines(),start):
   for j,part in enumerate(textwrap.wrap(line.expandtabs(4),width=96 if numbered else 100,replace_whitespace=False,drop_whitespace=False,break_on_hyphens=False) or ['']):
    prefix=(f'{i:>4} | ' if j==0 else '     | ') if numbered else ''
    st='codecn' if any(ord(c)>255 for c in part) else 'code'
    story.append(Preformatted(prefix+part,styles[st]))
  story.append(Spacer(1,8))
 def markdown(content):
  block=[];fence=False
  for line in content.splitlines()+['']:
   if line.startswith('```'):
    if fence:code('\n'.join(block));block=[]
    fence=not fence;continue
   if fence:block.append(line);continue
   if not line.strip():continue
   if line.startswith('# '):heading(line[2:],2)
   elif line.startswith('## '):heading(line[3:],2)
   elif line.startswith('### '):heading(line[4:],2)
   elif line.startswith('|'):
    if set(line.replace('|','').replace('-','').replace(':','').strip()):para(line,'small')
   else:para(line)
 heading('从零重建整个 A2\nProblem A 中文逐步实施手册',key='cover')
 para('40 个连续步骤 · 教师依据逐项定位 · 成员成果前后对照 · 完整代码与标签附录','h2')
 para('目标：一支团队拿到教师原始文件，从建立工作目录开始，依照步骤完成实现、评测、成本、六节报告、演示和提交准备。每一步回答：先读哪里、改哪个文件的哪段、为什么、写什么分析、怎样确认完成。')
 para('本手册依据当前已完成实现整理，不伪造重新开发历史。参考基线：47e1212；评测引擎保持原冻结版本。生成本手册不重新发送模型请求，不改变正式实验。')
 para('正文约束：官方代码/报告/演示仍为英文，本手册为中文学习附件，不计入正式2000词报告。显示的源码行号属于参考版本，编辑时优先用函数名/section定位。')
 para('本手册替代上一份概念式33页导读，上一版仅保留为历史辅助材料。这里的T/M/N/G/P分类始终优先于文件所在目录；路径以Total_LI_LINGHAO为相对根，../指父仓库。')
 page();heading('目录：按顺序执行，按附录查完整代码')
 toc=TableOfContents();toc.levelStyles=[styles['toc']];toc.dotsMinLevel=0;story.append(toc)
 page();heading('使用约定与文件来源总表',key='inventory')
 para('T=教师原始输入或明确标注的已填写模板；M=成员已有成果；N=团队新增实现/人工撰写；G=脚本生成产物；P=本手册提出但当前尚未执行的补齐方案。修改教师工作副本记作T→N，不能仍称原件。')
 for ident,path,note in TEACHER:heading(ident+' | '+path,2);para(note)
 heading('M | 成员原成果（全部保留原目录）',2)
 for text in [
  '陈明松：../Part1_CHEN_MINGSONG/agent.py、tools.py、D2a_tool_scoring.md、D2c_parallel_comparison.md、D4_evaluation_cases_draft.md。原工具/循环/评分/单例实验和案例草稿。',
  '陆鑫泽：../Part2_LU_XINZE/D2b_integrated_tools.py、D2b_integrated_agent.py、D2b_tool_descriptors.md、D2b_v1_v2_preauthorisation.md、D2b_smoke_test_results.md。已有接口防错和授权两版。',
  '周思涵：../Part2_ZHOU_SIHAN/guardrails.py、gated_action.py、run_agent_guarded.py、run_guardrail_checklist.py、D7_*、D4_eval_cases_zhou.md。原防护、gate、故障演示、案例。',
  '王毅：../Part8_WANG_YI/Problem_A_D0_Why_an_Agent.md、D4_eval_cases_wang_yi.md。D0与6案例；原分析中的目标不是最终测量。',
  '李凌昊：../Part3_LI_LINGHAO与当前Total集成任务。发起与整合指令为真人贡献，代码/评测执行中的AI辅助另列。',
  '戴敏飞：../Part4_DAI_MINFEI/init.md是任务说明；没有据此推断已经完成成本代码。']:para(text)
 heading('N、G、P | 团队输出及生成方向',2)
 for text in [
  'N：claim_agent/*.py、run_eval.py、tests/*.py、scripts/*.py；这些都是当前集成版本新增文件，非在教师scaffold原件上静默覆写。代码附录C逐文件给出完整内容。',
  'T→N：A2_reference_data/make_fixtures_A.py仅EXTRA块追加；expected_outcomes_A.json只增加25条，保留教师15条；G：data_A由generator生成。N：expected_details_A.json/case_provenance_A.json为独立新增标签/来源。',
  'N：PREBUILD/DESIGN/TOOL_CONTRACTS/DATA_DESIGN/EXPERIMENT_PROTOCOL/GUARDRAIL_CHECKLIST/贡献/改进/演示/自评草稿。G：REPORT.md和报告PDF由build_report.py的sections生成；RESULTS/FAILURE_EXPERIMENTS由build_analysis生成。',
  'G：results中的offline/live/judge/cost/manifest，须由实际运行产生；历史文件可回放，不是新团队自动拥有的测量。N→G：本手册steps_zh.json和supplements_zh.md→中文MD/PDF。',
  'P：个人模型runner参数扩展、analysis/Cost_to_Serve_A2.ipynb、真人录像/自评/发布/上传；本手册给出具体操作，但不将其标为当前已完成。']:para(text)
 heading('从零工作区骨架',2)
 code('reference_original/          # T: read-only originals\nmember_original/             # M: preserved source/history\nTotal_LI_LINGHAO/\n  A2_reference_data/         # T copy + explicit N additions\n  claim_agent/              # N: one runtime agent\n  tests/                    # N: executable checks\n  scripts/                  # N: eval/cost/report builders\n  docs/                     # N and G: identified separately\n  results/                  # G: actual runs, not invented\n  output/pdf/               # G: final report and handbook\n  analysis/                 # P: Class 5 working copy to add')
 para('依赖顺序：1–4定义目标/规则/接口；5–16实现；17–21数据与评分/验证；22–24受控离线实验；25–31 live与成本；32–38分析/报告/演示；39–40验收/提交。数据设计应在实现阶段并行思考，但答案键绝不来自agent输出。')
 steps=json.loads((ROOT/'docs/rebuild_manual/steps_zh.json').read_text())
 for step in steps:
  page();heading(f"步骤 {step['number']:02d} | {step['title']}",key=f"step-{step['number']}")
  for title,key in [('1. 先完成什么','prerequisites'),('2. 教师依据：打开哪个文件哪一段','teacher'),('3. 成员已有内容与保留方式','member'),('4. 修改或新增的准确产出位置','targets')]:heading(title,2);para(step[key])
  heading('5. 按顺序操作：改成什么',2)
  for i,action in enumerate(step['actions'],1):para(f'{i}) {action}')
  heading('6. 为什么这样改',2);para(step['reason'])
  heading('7. 此时应写的分析文段',2);para(step['writing'])
  heading('8. 命令、证据与通过条件',2);para(step['verification'])
 page();heading('补充操作 | 空目录缺少的输入与课程合规收尾',key='supplement')
 markdown((ROOT/'docs/rebuild_manual/supplements_zh.md').read_text())
 page();heading('附录 A | 教师原文定位与短引文',key='appendix-a')
 para('以下页码是PDF物理页码，与印刷Page一致。短引文只用于定位；完整题意以T1/T2/T3原文为准。代码/Notebook使用函数名或从1开始cell编号。')
 extracts=json.loads((ROOT/'docs/rebuild_manual/reference_extracts.json').read_text())
 for ref in extracts['quotes']:
  heading(f"{ref['source'].upper()} p.{ref['page']} | {ref['section']}",2);para(ref['quote'],'small')
 heading('Notebook逐段定位',2)
 for entry in extracts['notebooks']:
  para(f"{entry['id']} cell {entry['cell']} ({entry['type']}): {entry['heading']}",'small')
 page();heading('附录 B | 成员原始代码：改进前到底是什么',key='appendix-b')
 for ref in extracts['originals']:
  heading(ref['path']+f" 原第{ref['start']}–{ref['end']}行",2);para(ref['note'])
  code(ref['code'],True,ref['start'])
 para('旧D7文件的案例构想保留，但两项正式消融必须用C附录的最终run_case开关；旧单例D2c结果保留历史，不在本手册重新计算为正式数据。原贡献不是通过对代码行数打分判断的。')
 page();heading('附录 C | 完整新增代码：按文件原样建立',key='appendix-c')
 para('下列为全部运行、测试、评测、分析、报告、打包Python源码。每个文件完整列出，无省略号替代实现；原始长行仅视觉折行，续行左侧只有竖线。拷贝时不要把显示行号/竖线写入代码。读者也可从同名随附文件直接复制。')
 for rel in SOURCE_FILES:
  page();heading('C | '+rel,key='code-'+rel.replace('/','-'))
  path=ROOT/rel;data=path.read_text();para('分类N：团队新增/整合产出。SHA-256 '+sha(path),'small')
  tree=ast.parse(data)
  funcs=[f'{n.name}: {n.lineno}–{n.end_lineno}' for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
  if funcs:para('定位：'+'；'.join(funcs),'small')
  code(data,True);source_index.append({'path':rel,'sha256':sha(path),'lines':len(data.splitlines()),'classification':'N'})
 page();heading('附录 D | 教师生成器的精确追加与完整答案键',key='appendix-d')
 para('本附录第一块仅替换教师generator的EXTRA_*赋值。上方SHIPPED常量、下方生成器流程、teacher checker保持不改。现有最终行号不同于教师原件，定位用变量名。')
 rel='A2_reference_data/make_fixtures_A.py';data=(ROOT/rel).read_text();tree=ast.parse(data);nodes=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id.startswith('EXTRA_') for t in n.targets)]
 lines=data.splitlines()
 for n in nodes:heading(n.targets[0].id,2);code('\n'.join(lines[n.lineno-1:n.end_lineno]),True,n.lineno)
 for rel in ['A2_reference_data/expected_outcomes_A.json','A2_reference_data/expected_details_A.json','A2_reference_data/case_provenance_A.json']:
  page();heading('D | '+rel)
  para('expected_outcomes：原15对象保留，追加其余；details/provenance：N类新增。此处紧凑JSON仅改变排版，内容与磁盘一致。模型runtime不得读取答案键。','small')
  val=json.loads((ROOT/rel).read_text());code(json.dumps(val,ensure_ascii=False,indent=None) if not isinstance(val,list) else '[\n'+',\n'.join(json.dumps(v,ensure_ascii=False,separators=(',',':')) for v in val)+'\n]')
  source_index.append({'path':rel,'sha256':sha(ROOT/rel),'classification':'T→N' if 'outcomes' in rel else 'N'})
 page();heading('附录 E | 当前六节英文报告全文与编辑入口',key='appendix-e')
 para('此处为当前版本参考文字。真正编辑源是C附录build_report.py中的sections；REPORT.md是生成输出。重建团队必须用自己的测量、时间和贡献替换相应段落。1552词是当前参考报告，不是本中文手册字数。')
 markdown((ROOT/'docs/REPORT.md').read_text())
 page();heading('附录 F | 当前配套分析与演示文本范本',key='appendix-f')
 para('这些文件展示步骤中要求写出的完整配套内容。表格在手册中按行展开便于长内容换行；可编辑原Markdown随提交包保留。涉及未来参与和日期时，以步骤39/40的真实性核验为准。')
 for rel in DOC_FILES:
  page();heading('F | '+rel)
  markdown((ROOT/rel).read_text())
 page();heading('附录 G | 最后验收矩阵与证据索引',key='appendix-g')
 for row in [('D0','2、29、33','PREBUILD先于agent；最终P/T/s和架构比较'),('D1','5–15、20','单手写loop、scripted默认、多工具单turn'),('D2(a/b/c)','4、7–10、14、22','三问/六字段/poka-yoke/同模型v1v2/全量串分组'),('D3','11–16、21','默认拒绝、资源cap、16独立checks、已批准攻击'),('D4','17–20、28','40cases/64trials、teacher未改、独立labels、强grader+judge'),('D5','25–29','5家族+1v1=384；真实usage/raw；个人执行要求单独核验'),('D6','30–31、36','Class5工作副本、三层/四杠杆/敏感性/门槛/预算对账'),('D7','23–24、37','同engine两项删除与恢复、完整trace、层归因'),('Submission','32、38–40','真实贡献、≤2000词、5分钟六人、自评、公仓+代码副本+回执')]:para(' | '.join(row))
 para('没有旧results也能重建：先跑offline；然后在余额和执行条件具备时采集live/judge；再分析与报告。没有API条件时仍能完成离线系统，但必须保留live待完成。没有真人材料时不得声称整个课程提交完成。')
 for rel in ['results/live/manifest.json','results/spend_reconciliation.json','results/cost_model.json','results/d7_failures.json','results/guardrail_checklist.json','IMPROVEMENTS.md','IMPROVEMENTS_ZH.md']:
  path=ROOT/rel
  if path.exists():para(rel+' | SHA-256 '+sha(path),'small')
 class Doc(SimpleDocTemplate):
  def afterFlowable(self,f):
   if isinstance(f,Paragraph) and hasattr(f,'anchor'):
    self.canv.bookmarkPage(f.anchor)
    if f.toc_entry:
     self.canv.addOutlineEntry(f.getPlainText(),f.anchor,0,False)
     if f.anchor not in ['cover','a2']:self.notify('TOCEntry',(0,f.getPlainText(),self.page,f.anchor))
     if f.anchor.startswith('step-'):step_pages[f.anchor]=self.page
 def footer(c,d):
  c.setStrokeColor(TEAL);c.line(43,38,552,38);c.setFillColor(BLUE);c.setFont('ManualCN',8)
  c.drawString(43,24,'A2 Problem A · 从零重建 · T教师 / M成员 / N新增 / G生成 / P待补齐');c.drawRightString(552,24,str(d.page))
 OUT.parent.mkdir(parents=True,exist_ok=True)
 doc=Doc(str(OUT),pagesize=(595.28,841.89),leftMargin=43,rightMargin=43,topMargin=38,bottomMargin=52,title='A2 Problem A 从零重建完整中文实施手册',author='Group-6 · AI辅助整理')
 doc.multiBuild(story,onFirstPage=footer,onLaterPages=footer)
 (ROOT/'docs/REBUILD_A2_STEP_BY_STEP_ZH.md').write_text('\n'.join(md))
 (ROOT/'docs/rebuild_manual/source_index.json').write_text(json.dumps({'reference_commit':'47e1212','steps':step_pages,'sources':source_index},ensure_ascii=False,indent=2))
 print(json.dumps({'pdf':str(OUT),'steps':len(steps),'source_files':len(SOURCE_FILES),'pages':doc.page,'text_chars':len('\n'.join(md))},ensure_ascii=False))
if __name__=='__main__':main()
