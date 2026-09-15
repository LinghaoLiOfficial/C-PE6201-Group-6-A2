#!/usr/bin/env python3
"""Build the detailed Chinese implementation handbook from Markdown and actual source."""
import ast,json,re,textwrap
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Preformatted,KeepTogether,Table,TableStyle

ROOT=Path(__file__).resolve().parents[1]
FONT='/System/Library/Fonts/Supplemental/Songti.ttc'
# Authoring only; no dependency or change to the evaluated runtime.
pdfmetrics.registerFont(TTFont('GuideCN',FONT,subfontIndex=0))
BLUE=colors.HexColor('#173D55');TEAL=colors.HexColor('#138A86');INK=colors.HexColor('#263A48')
styles={
 'h1':ParagraphStyle('h1',fontName='GuideCN',fontSize=19,leading=27,textColor=BLUE,spaceAfter=16,keepWithNext=True,wordWrap='CJK'),
 'h2':ParagraphStyle('h2',fontName='GuideCN',fontSize=12,leading=18,textColor=TEAL,spaceBefore=10,spaceAfter=6,keepWithNext=True,wordWrap='CJK'),
 'p':ParagraphStyle('p',fontName='GuideCN',fontSize=10.5,leading=17,textColor=INK,spaceAfter=8,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='GuideCN',fontSize=9,leading=14,textColor=INK,spaceAfter=5,wordWrap='CJK'),
 'code':ParagraphStyle('code',fontName='Courier',fontSize=7.3,leading=10.3,textColor=INK,backColor=colors.HexColor('#EEF4F6'),borderPadding=7,spaceBefore=5,spaceAfter=10),
 'toc':ParagraphStyle('toc',fontName='GuideCN',fontSize=10.5,leading=19,textColor=BLUE,spaceAfter=3,wordWrap='CJK')}


def source_block(path,start,end):
 lines=(ROOT/path).read_text().splitlines(); out=[]
 for no in range(start,end+1):
  line=lines[no-1].expandtabs(4)
  wrapped=textwrap.wrap(line,width=89,break_long_words=True,break_on_hyphens=False,replace_whitespace=False,drop_whitespace=False) or ['']
  for i,part in enumerate(wrapped):out.append((f'{no:>3} | ' if i==0 else '    | ')+part)
 return '\n'.join(out)


def defline(path,name):
 tree=ast.parse((ROOT/path).read_text())
 for n in ast.walk(tree):
  if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name:return n.lineno,n.end_lineno
 raise ValueError(name)


def main():
 text=(ROOT/'docs/IMPLEMENTATION_WALKTHROUGH_ZH.md').read_text()
 chunks=text.split('---PAGE---');story=[];headings=[]
 for c in chunks:
  title=next(x[2:] for x in c.strip().splitlines() if x.startswith('# '));headings.append(title)
 # Cover first, then a navigable contents page, then numbered chapters.
 def append_markdown(chunk):
  lines=chunk.strip().splitlines();buffer=[];code=[];in_code=False
  def flush():
   if buffer:story.append(Paragraph(escape(' '.join(buffer)),styles['p']));buffer.clear()
  for line in lines:
   if line.startswith('```'):
    flush()
    if in_code:
     rendered=[]
     for raw in code:
      rendered.extend(textwrap.wrap(raw,width=90,replace_whitespace=False,drop_whitespace=False) or [''])
     story.append(Preformatted('\n'.join(rendered),styles['code']));code=[]
    in_code=not in_code;continue
   if in_code:code.append(line);continue
   if line.startswith('# '):flush();story.append(Paragraph(escape(line[2:]),styles['h1']))
   elif line.startswith('## '):flush();story.append(Paragraph(escape(line[3:]),styles['h2']))
   elif not line.strip():flush()
   else:buffer.append(line.strip())
  flush()
 append_markdown(chunks[0]);story.append(Spacer(1,14));story.append(Paragraph('阅读路径：要求拆解 → 代码修改 → 独立验证 → 数值分析 → 报告表达',styles['h2']))
 story.append(PageBreak());story.append(Paragraph('目录与使用建议',styles['h1']))
 for i,title in enumerate(headings[1:],1):story.append(Paragraph('<link href="#section-'+str(i+2)+'">'+escape(title)+' · '+str(i+2)+'</link>',styles['toc']))
 story.append(Spacer(1,8));story.append(Paragraph('附录 A1–A6（第 28–33 页）：当前源码摘录、行号和逐段解释。章节固定另起一页；长代码按显示宽度折行，左侧数字始终为原文件行号。',styles['small']))
 for c in chunks[1:]:story.append(PageBreak());append_markdown(c)
 appendices=[
 ('A1｜保单与授权：让证据足够完整','claim_agent/tools.py',[
  ('_policy_result',None,'先汇总 claim 全部金额，再计算 remaining；失效、日期、超限逐项判断。严格 > 保留等于额度的合法边界。'),
  ('_preauth',None,'返回所有候选及时间状态，valid 只指实际覆盖服务日的候选。ablated 分支仅用于 D7；业务写入校验不会使用这个削弱版本。')]),
 ('A2｜循环：先计费，再检查与执行','claim_agent/agent.py',[
  ('run_case',39,'此处显示 run_case 前半段。observed 来自调用前已有观察，因此同一个 batch 不能用前一个成员刚产出的事实满足后一个成员依赖。token 已消费即计入，即便后续工具被阻止。')]),
 ('A3｜写入：不允许用正确 outcome 掩盖错误事实','claim_agent/tools.py',[
  ('_issue',30,'入口验证字段、案号与 evidence；只有引用实际观察才可能通过。后续函数还重新核验 line、金额和缺失项，最后才调用确认与 ledger。')]),
 ('A4｜独立评分：对照标签而非自我证明','claim_agent/harness.py',[
  ('grade',None,'grader 单独持有详细答案键。pending/unresolved 是明确语义映射，不是模糊关键词匹配。该代码不能从运行结果反写期望标签。')]),
 ('A5｜模型适配：提供案号、真实观察和明确调用格式','claim_agent/backends.py',[
  ('next',27,'这是 LiveBackend.next。模型收到当前案号和已有观察；运行时提示只列已完成动作和契约，不读取答案键。后半段还保存 provider usage 并解析 JSON/fenced JSON，解析失败仍保留 raw。')]),
 ('A6｜D7 测试：同一 engine 的受控删除','tests/test_d7.py',[
  ('RepeatingBackend',None,'固定 backend 故障每次重复同一动作，两组都使用它。token 仍按传入上下文估算，而非随意填写示例数字。'),
  ('D7Tests',None,'第一项证明删除去重后消耗更多轮次；第二项证明删除授权有效性投影产生错误提议，但独立 gate 仍拦截。恢复后正确索取授权。')])]
 index=['# 当前源码定位（自动生成）','', '对应 IMPLEMENTATION_WALKTHROUGH_ZH.md 的详细说明。代码来自构建时实际文件；行号以后可能变化。','']
 for title,path,items in appendices:
  story.append(PageBreak());story.append(Paragraph(title,styles['h1']));story.append(Paragraph('来源：'+escape(path),styles['small']))
  index+=['## '+title,'']
  for name,limit,explanation in items:
   start,end=defline(path,name)
   if limit:end=min(end,start+limit-1)
   label=f'{name} · 原文件第 {start}–{end} 行'
   story.append(Paragraph(escape(label),styles['h2']));story.append(Paragraph(explanation,styles['p']));story.append(Preformatted(source_block(path,start,end),styles['code']))
   index += [f'{path}:{start} · {name}','',explanation,'','```python',source_block(path,start,end),'```','']
 story.append(Spacer(1,5));story.append(Paragraph('读代码时，先用失败案例说明“如果删掉这一条件会怎样”，再用对应测试证明。不要只逐行翻译语法；解释每一块代码保护的业务或实验不变量。',styles['small']))
 (ROOT/'docs/IMPLEMENTATION_SOURCE_INDEX_ZH.md').write_text('\n'.join(index))
 out=ROOT/'output/pdf/PE6201_A2_Group-6_Implementation_Guide_ZH.pdf';out.parent.mkdir(parents=True,exist_ok=True)
 def page(canvas,doc):
  canvas.setStrokeColor(TEAL);canvas.setLineWidth(.7);canvas.line(42,39,553,39)
  canvas.setFont('GuideCN',8);canvas.setFillColor(BLUE);canvas.drawString(42,25,'PE6201 A2 · Group-6 · 要求、实现、验证与写作');canvas.drawRightString(553,25,str(doc.page))
 class Doc(SimpleDocTemplate):
  def afterFlowable(self,flowable):
   if isinstance(flowable,Paragraph) and flowable.style.name=='h1':
    name='section-'+str(self.page);self.canv.bookmarkPage(name);self.canv.addOutlineEntry(flowable.getPlainText(),name,level=0,closed=False)
 doc=Doc(str(out),pagesize=(595.28,841.89),leftMargin=43,rightMargin=43,topMargin=38,bottomMargin=53,title='PE6201 A2 Problem A 完整中文实施与写作说明',author='Group-6 · AI 辅助集成说明')
 doc.build(story,onFirstPage=page,onLaterPages=page)
 print(json.dumps({'pdf':str(out),'chapters':len(chunks)-1,'source_appendices':len(appendices),'main_text_characters':len(text)},ensure_ascii=False))
if __name__=='__main__':main()
