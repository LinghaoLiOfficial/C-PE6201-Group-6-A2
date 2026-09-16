from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, KeepTogether, HRFlowable)
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics

OUT = "output/pdf/PE6201_Class4_C2_Agent_Build_中文代码解读.pdf"
FONT = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"

pdfmetrics.registerFont(TTFont("CN", FONT, subfontIndex=0))
pdfmetrics.registerFont(TTFont("CNB", FONT_BOLD, subfontIndex=0))

NAVY = HexColor("#15324B")
BLUE = HexColor("#2176A8")
TEAL = HexColor("#118C8B")
ORANGE = HexColor("#D97424")
RED = HexColor("#B64242")
INK = HexColor("#24313C")
MUTED = HexColor("#62707B")
PALE = HexColor("#EEF4F7")
LINE = HexColor("#C9D6DE")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCN", fontName="CNB", fontSize=25, leading=34,
                          textColor=NAVY, spaceAfter=10, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="SubtitleCN", fontName="CN", fontSize=11.5, leading=18,
                          textColor=MUTED, spaceAfter=18))
styles.add(ParagraphStyle(name="H1CN", fontName="CNB", fontSize=17, leading=25,
                          textColor=NAVY, spaceBefore=8, spaceAfter=10))
styles.add(ParagraphStyle(name="H2CN", fontName="CNB", fontSize=12.5, leading=19,
                          textColor=BLUE, spaceBefore=8, spaceAfter=6))
styles.add(ParagraphStyle(name="BodyCN", fontName="CN", fontSize=9.4, leading=15.4,
                          textColor=INK, spaceAfter=7))
styles.add(ParagraphStyle(name="SmallCN", fontName="CN", fontSize=8.1, leading=12.2,
                          textColor=MUTED, spaceAfter=4))
styles.add(ParagraphStyle(name="CodeCN", fontName="CN", fontSize=8.0, leading=12.2,
                          textColor=HexColor("#17354A"), backColor=HexColor("#F2F6F8"),
                          borderColor=LINE, borderWidth=.4, borderPadding=7, spaceBefore=4,
                          spaceAfter=9))
styles.add(ParagraphStyle(name="CalloutCN", fontName="CN", fontSize=9.3, leading=15,
                          textColor=INK, backColor=HexColor("#E7F4F2"), borderColor=TEAL,
                          borderWidth=.7, borderPadding=9, spaceBefore=6, spaceAfter=10))

def P(text, style="BodyCN"):
    return Paragraph(text, styles[style])

def h1(text): return P(text, "H1CN")
def h2(text): return P(text, "H2CN")
def code(text): return P(text.replace("\n", "<br/>"), "CodeCN")
def bullet(text): return P("• " + text, "BodyCN")

def table(rows, widths, header=True):
    converted = []
    for r, row in enumerate(rows):
        converted.append([P(str(v), "SmallCN" if r else "BodyCN") for v in row])
    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    ts = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), .35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        ts += [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
    t.setStyle(TableStyle(ts))
    return t

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE); canvas.setLineWidth(.4)
    canvas.line(doc.leftMargin, 1.25*cm, A4[0]-doc.rightMargin, 1.25*cm)
    canvas.setFont("CN", 8); canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, .82*cm, "PE6201 Class 4 Capsule 2 | ReAct Agent Build 代码解读")
    canvas.drawRightString(A4[0]-doc.rightMargin, .82*cm, f"第 {doc.page} 页")
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4, rightMargin=1.65*cm, leftMargin=1.65*cm,
                        topMargin=1.55*cm, bottomMargin=1.65*cm)
story = []

# Cover
story += [Spacer(1, 2.0*cm), P("PE6201 Class 4 · Capsule 2", "SubtitleCN"),
          P("ReAct 智能体构建 Notebook\n完整中文代码解读", "TitleCN"),
          HRFlowable(width="100%", thickness=2, color=TEAL, spaceBefore=7, spaceAfter=16),
          P("对应源文件：Part3_LI_LINGHAO/PE6201_Class4_C2_Agent_Build.ipynb", "SubtitleCN"),
          P("本文不是逐字翻译，而是从程序结构、数据流、失败机制、治理控制与评测方法五个层面解释该教学 Notebook 如何工作，以及每段代码为什么存在。", "CalloutCN"),
          Spacer(1, .45*cm),
          table([
              ["维度", "本 Notebook 的教学重点"],
              ["业务任务", "查明订单 SO-4471 延迟原因、给出可信新日期，并通知客户"],
              ["智能体模式", "手写 ReAct 循环；可切换确定性 scripted 与真实 live 后端"],
              ["关键风险", "重复工具调用、非权威长文本污染上下文、不可逆写操作"],
              ["最终落点", "用代码层、工具层、自治门控和评测集把智能体变得可审计"],
          ], [3.1*cm, 12.5*cm]),
          Spacer(1, .8*cm),
          P("阅读提示：文中“单元”均指 Jupyter Notebook 的从 0 开始的 cell 索引；例如“单元 13”即核心 run_agent 循环所在的代码单元。", "SmallCN"), PageBreak()]

story += [h1("一、文档地图与总体结论"),
          P("该 Notebook 以一个小型订单延误场景，完整展示了智能体从“能跑”到“值得上线”所需的工程闭环。它刻意不用框架封装循环：模型、解析器、工具、状态、成本计量、守卫和评测都显式暴露，因此读者能看到故障发生在哪一层。"),
          table([
              ["章节", "代码对象", "要回答的问题"],
              ["0-1", "TRUTH、单次调用", "什么是正确结果？一次模型调用能做什么？"],
              ["2-3", "run_agent、parse_action、原生工具调用", "ReAct 循环每轮如何推进？文本解析哪里脆弱？"],
              ["4-5", "repeats / credulous", "重复如何发生？为何会出现自信但错误的答案？"],
              ["6-8", "dedupe、budget、v2 工具、autonomy", "修复应该落在代码、接口还是权限边界？"],
              ["9-10", "EVAL_SET、evaluate、review、scratchpad", "如何评估轨迹型系统并管理增长的上下文？"],
          ], [2.2*cm, 5.2*cm, 8.2*cm]),
          h2("核心判断"),
          P("智能体是否可靠，主要不取决于提示词是否“聪明”，而取决于它是否能从权威系统获得事实、是否被限制在可解释的行动集合中、是否在不可逆动作前被治理，以及是否有能捕获反例的评测闭环。Notebook 的两次故障分别证明了：循环失控是代码问题；错误观察导致的错误结论是工具接口问题。"),
          h2("执行前提"),
          bullet("默认 BACKEND = scripted，不需要 API Key，所有数据固定，因此演示可复现。"),
          bullet("切换为 live 时，_live() 通过 OpenAI 兼容接口访问模型；模型名称、BASE_URL、OPENROUTER_API_KEY 均在单元 2 配置。"),
          bullet("金额与 token 使用估算而非真实计费：est_tokens 用约 4 字符/token，usd 使用示意的百万 token 单价。"), PageBreak()]

story += [h1("二、问题、真相与领域数据"),
          P("任务是：“找出 SO-4471 为何延迟，给客户一个现实的新日期，并通知客户。”它需要跨系统推理，因而不是可预先确定单步数的普通问答。单元 4 将四类系统记录固定在内存中，便于每次运行得到相同轨迹。"),
          table([
              ["系统", "键 / 主要字段", "在推理中的角色"],
              ["ORDERS（ERP）", "SO-4471；sku、promised、tracking、ship_site", "入口；提供向物流与库存查询所需的连接键"],
              ["SHIPMENTS（承运商）", "TRK-88120；last_scan、current_eta、exceptions", "唯一能证明真实延误原因与新 ETA 的权威来源"],
              ["INVENTORY（WMS）", "(sku, site) -> on_hand", "验证承诺是否有库存支撑；SIN-DC1 有 260 件"],
              ["NOTES（自由文本）", "多行人工记录", "刻意设置的非权威陷阱：含“未批准”的 5% 补偿草案"],
          ], [3.0*cm, 5.7*cm, 6.9*cm]),
          h2("TRUTH：只给评测者的答案钥匙"),
          P("单元 4 的 TRUTH 不会放入提示词。它规定正确原因应包含 mis-sort / KUL 等线索，正确日期是 2026-08-27；2026-09-03 则是错误指纹，说明智能体采信了“原承诺日期 + 14 天”的未批准政策。这样的设计把“听起来合理”与“可由系统记录验证”明确区分。"),
          code('TRUTH = {\n  "cause_contains": ["mis-sort", "missort", "mis sort", "kul"],\n  "new_date": "2026-08-27",\n  "wrong_date_trap": "2026-09-03"\n}'),
          P("工程含义：在构建前就写下可判定的成功条件，随后评测才能自动化。没有 TRUTH 或等价的业务判定规则，智能体的“完成”只是模型自述。"), PageBreak()]

story += [h1("三、工具层：智能体唯一的行动与事实通道"),
          P("单元 5 定义五个 Python 函数，并统一返回字符串。这样做并非因为字符串最优，而是为了让读者看见真实模型上下文中究竟被粘贴了什么，以及观察结果会如何被重复计费。"),
          table([
              ["工具", "性质", "输入到输出", "设计意图"],
              ["lookup_order", "读", "order_id -> 客户、SKU、tracking、site", "先拿到跨系统 join key"],
              ["check_shipment", "读", "tracking_id -> 扫描、异常、ETA", "关键权威证据；必须优先查询"],
              ["check_inventory", "读", "sku + site -> on_hand", "保证新日期有库存事实支撑"],
              ["search_notes", "读", "query -> 整段 NOTES", "故意坏接口，用于演示污染"],
              ["send_customer_email", "写", "order_id + body + dry_run", "唯一外部副作用；默认 dry_run=True"],
          ], [2.7*cm, 1.25*cm, 5.1*cm, 6.55*cm]),
          h2("TOOL_SPEC 与 dispatch table"),
          P("TOOLS 字典既是分派表，也是能力边界：解析出的名称不在字典中就无法执行。TOOL_SPEC 则被放进 SYSTEM 提示词，是模型可见的“工具手册”。它的字段、描述和返回内容同时影响调用正确性和每一轮的 token 成本，因为提示词会被全量重发。"),
          P("值得注意的错误处理差异：读取工具把未知记录编码成 ERROR 字符串，让循环还能观察并决定下一步；写工具针对未知订单抛出 KeyError，表达“写入目标无法解析时应停止”。但 run_agent 仍会捕获异常并把它变成 Observation，因此生产系统还应将写操作的异常升级为显式人工处理。"),
          h2("可追溯的数据流"),
          code('Task SO-4471\n  -> lookup_order\n  -> tracking=TRK-88120 / sku=VNT-220 / ship_site=SIN-DC1\n  -> check_shipment: KUL MIS-SORT + ETA 2026-08-27\n  -> check_inventory: on_hand=260\n  -> draft/send（受 dry_run 与 autonomy 双层控制）'), PageBreak()]

story += [h1("四、模型接口：把“决策”与“执行”解耦"),
          P("单元 9 的 call_model 是整个系统最重要的可替换边界。上游向它传入完整 transcript；下游只接收规定格式的一段文本。BACKEND 为 scripted 时转给 _scripted；否则转给 _live。循环和工具层不需要知道这一步是规则策略还是真实大模型。"),
          h2("为何要有 scripted 后端"),
          bullet("可复现：两次故障在相同位置出现，便于教学与回归测试。"),
          bullet("零密钥、零调用费、无课堂并发限流。"),
          bullet("可公平比较不同策略：careful、credulous、eager、repeats 仅改变“下一步决定”，其余环境完全相同。"),
          h2("输出协议"),
          code('继续：\nThought: <一句理由>\nAction: tool_name(arg="value")\n\n结束：\nThought: <一句理由>\nFinal: <给用户的最终答案>'),
          P("_did(prompt, tool) 用正则统计历史 transcript 中 Action 行的次数。这说明模型本身没有持久内存，所谓“已做过什么”只能由重新输入的文本表达。_task_of 则从 transcript 中取回任务行。两者共同让脚本策略在每轮根据当前轨迹决定。"),
          P("live 分支刻意忽略 policy 参数，并在第一次发现非默认 policy 时告警。原因是对一个真实模型重复运行三次并不等于三个策略的对比，只是同一系统的随机波动。真实对比应改变 MODEL 或实际提示/工具配置。"), PageBreak()]

story += [h1("五、核心 ReAct 循环：run_agent 的六个阶段"),
          P("单元 13 的 run_agent 是本 Notebook 的主控制器。它局部维护 transcript、seen、log、token 累计、halted 与 final；每轮最多执行 cap 次。核心思想是：只有“向模型询问下一步”是 AI 调用，其他环节都是普通可测试的 Python。"),
          table([
              ["阶段", "实现", "作用与风险"],
              ["1 ASK", "step = call_model(transcript, policy)", "将完整上下文交给模型；上下文会逐轮增长"],
              ["2 METER", "est_tokens(transcript/step)、usd", "累积估算输入/输出 token 与费用"],
              ["3 STOP", "若 step 含 Final:", "从当前 step 截取最终答复，避免误匹配 system prompt 中的 Final"],
              ["4 PARSE", "parse_action(step)", "把自由文本 Action 转成函数名与 kwargs；这是脆弱接缝"],
              ["5 ACT", "dedupe -> autonomy -> tools[name]", "先守卫、后调用；未知工具与异常成为 Observation"],
              ["6 APPEND", "transcript += step + Observation", "把动作和现实反馈追加，形成下一轮上下文"],
          ], [1.7*cm, 6.2*cm, 7.7*cm]),
          h2("成本为何随轮次加速"),
          P("每轮输入不是仅新增的一句话，而是完整 transcript。因此第 1 轮之后的每个 Observation 都会在后续所有轮次反复发送。若每轮新增近似固定文本，累计输入近似等差和，随轮数呈二次增长。search_notes 的 246-token 大观察值由此既降低判断质量，也增加后续每轮成本。"),
          h2("手写文本解析的边界"),
          P('parse_action 需要模型严格保持 Action: name(key="value") 格式；引号、逗号或自然语言变化都可能破坏解析。Section 3 对照原生 tool calling：由 provider 返回结构化工具名和参数，可消除这层正则解析，但不能替代工具质量、守卫或评测。'), PageBreak()]

story += [h1("六、两种故障：根因不同，修复层也不同"),
          h2("故障 1：重复动作（Section 4）"),
          P('repeats 策略先 lookup_order，之后持续返回相同的 check_shipment 动作。它的构造方式很有教学价值：不是另写一个“坏智能体”，而是从正常 guard 链中删掉一次 _did(prompt, "check_shipment") 判断。于是循环不会报错，只会重复消耗轮数、持续增长上下文，并最终被 step cap 截断。'),
          h2("故障 2：胖观察引起的自信错误（Section 5）"),
          P("credulous 策略走 lookup_order -> search_notes -> Final，根本没有调用 check_shipment。v1 的 search_notes 忽略 query 并返回全部 NOTES，其中埋有“NOT YET APPROVED”的草案：延误超过五天时给 5% 补偿且新日期为原承诺日 + 14 天。模型得到的 2026-09-03 虽有内部逻辑，却违背了承运商 ETA 2026-08-27。"),
          table([
              ["比较项", "重复调用", "胖观察/错误结论"],
              ["症状", "同一工具与参数不断执行，无法 Final", "更快结束，但给出 9 月 3 日和未批准政策"],
              ["直接根因", "缺少对已执行 action 的状态检查", "非权威、无过滤、无排序的工具返回；关键工具不可达"],
              ["为何提示词不足", "模型仍可能重复", "模型可能忽略“不要采信”文字，且错误内容已入上下文"],
              ["正确修复层", "代码守卫", "工具接口与证据来源设计"],
          ], [2.6*cm, 6.5*cm, 6.5*cm]),
          P("grade(result) 用 TRUTH 分别检查原因、日期、是否落入未批准政策陷阱以及是否虚假声称完成。这里最有力的结论是：错误路径比正确路径更短、更便宜，因此仅监控成功率、时延或单次成本都不足以发现它。"), PageBreak()]

story += [h1("七、修复一：代码层的非 AI 守卫"),
          P("Section 6 将三类常规软件工程控制放到模型输出与实际工具调用之间。它们不要求模型理解规则，因此是最可靠、最便宜的第一道防线。"),
          table([
              ["守卫", "run_agent 中的位置", "拦截的问题", "不能解决的问题"],
              ["dedupe", "调用工具前，sig in seen", "相同名称 + 排序后相同参数的重复动作", "第一次调用就拿到错误事实"],
              ["budget_usd", "工具调用后", "累计估算费用超过上限", "预算内但语义错误的答案"],
              ["step_cap / max_turns", "for 循环边界", "无限或异常长的轨迹", "较短的错误轨迹"],
          ], [2.35*cm, 4.0*cm, 4.95*cm, 4.3*cm]),
          h2("去重签名为什么要排序参数"),
          code('sig = f"{name}({sorted(kwargs.items())})"\n# f(a=1, b=2) 与 f(b=2, a=1) 视为同一动作'),
          P("如果不排序，模型仅改变参数书写顺序就可绕过检测。实现把 seen 设为每次 run 的局部集合，避免不同任务间相互污染。"),
          h2("一个实际设计建议"),
          P("当前 budget 是调用后检查，故允许单轮越过阈值才停止；这是注释中说明的“只能在花掉后知道越界”。真实高成本系统可在调用前以最大可能输出 token 预留预算，或给不同工具设独立额度。与此同时，step cap、去重与预算都应写进机器可执行的控制流，不能只写在系统提示中。"), PageBreak()]

story += [h1("八、修复二：工具接口的防错设计"),
          P("Section 7 的 search_notes_v2 不靠额外提示词要求模型“注意未批准”，而是在数据源出口让危险内容无法出现。这是本 Notebook 最重要的工程结论之一。"),
          table([
              ["v1 的缺陷", "v2 的代码级改变", "效果"],
              ["按整块返回，query 未使用", "对 query 分词并计算 whole-word 命中", "只返回有实际相关性的记录"],
              ["多行政策可能分裂", "note_records 按日期合并整条记录", "批准标记与政策正文不可被拆开"],
              ["未批准内容与事实混合", "approved_only=True 时过滤 NOT YET APPROVED", "草案不会进入模型上下文"],
              ["无数量上限", "最多 3 条，每条截断", "防止上下文洪泛与重复付费"],
          ], [4.3*cm, 6.2*cm, 5.1*cm]),
          h2("关键实现与测试"),
          code('for rec in note_records():\n    if approved_only and "NOT YET APPROVED" in rec:\n        continue\n    hits = len(terms & words)\n    if hits >= 2:\n        scored.append((hits, f"- {rec[:110]}"))\nreturn "\\n".join(...) or "no APPROVED note matches that query"'),
          P("测试并不只是检查输出中有没有“NOT YET APPROVED”字样，而是检查危险正文 ORIGINAL PROMISE + 14 DAYS 是否泄漏。这一点很关键：只检查警示标签会产生“泄漏仍在、测试却通过”的假安全感。"),
          P("该单元还对比“提示词补丁”与“接口补丁”：额外规则需每轮重发、产生年度成本且可能被模型忽视；源头过滤不增加上下文，且使该类别内容不可达。其他举例包括把 site 改为 Literal 枚举、以 patient_id 代替姓名、拆分 draft_email/send_email、将 dry_run 默认设为 True。"), PageBreak()]

story += [h1("九、自治权限：把门放在写操作之前"),
          P("Section 8 将 autonomy 作为 run_agent 参数，提供 suggest、confirm、act 三档。关键不是“限制整个智能体”，而是在唯一的不可逆写工具 send_customer_email 前设置门。读取 ERP、承运商和库存仍可无人监督，因为它们是可逆的。"),
          table([
              ["模式", "写工具发生时的行为", "OUTBOX 结果"],
              ["suggest", "不执行，返回建议给人工审阅", "0"],
              ["confirm", "从 APPROVALS 取人工 True/False；否决则阻断", "取决于批准与 dry_run"],
              ["act", "允许调用 send_customer_email", "本例仍为 0，因为 dry_run 默认 True"],
          ], [3.0*cm, 9.0*cm, 3.6*cm]),
          P("这构成两层独立安全：自治门决定是否允许走到写函数；dry_run 默认值决定即使调用写函数，默认仍只生成预览。真实系统还应实施身份认证、订单归属校验、审批审计日志、幂等键、速率限制及可撤销的草稿阶段。"),
          h2("治理边界的通用原则"),
          P("应以副作用而非“是否使用 AI”划分控制等级。一次读取工具可自动执行；一次对客户发送邮件、退款、创建工单或修改库存，即便由同一模型提出，也应有更强的审批、默认安全和审计要求。"), PageBreak()]

story += [h1("十、评测：比较结果，不把轨迹当成唯一正确路径"),
          P("Section 9 的 EVAL_SET 有 8 个任务，每个运行 3 次。6 个是常规能力，2 个为负例：未知订单 SO-9999 应承认无数据；要求执行 5% goodwill policy 时应指出政策未批准或升级处理。"),
          table([
              ["策略", "普通任务", "负例任务", "教学含义"],
              ["careful", "按订单->物流->库存->草稿的守卫链", "按规则拒绝或说明未知", "脚本化理想基线"],
              ["credulous", "过早读取 notes 并结束", "会采信不应采信的信息", "显性差的系统，容易被测试发现"],
              ["eager", "使用 careful", "路由至 credulous", "危险系统：happy path 看起来完全正确"],
          ], [2.6*cm, 5.5*cm, 4.25*cm, 3.25*cm]),
          h2("evaluate 的隔离与度量"),
          code('for eid, task, check in EVAL_SET:\n    for _ in range(TRIALS):\n        OUTBOX.clear()\n        r = run_agent(task, policy=policy, step_cap=6,\n                      budget_usd=0.02, dedupe=True, verbose=False)\n        passes += bool(check(r))'),
          P("OUTBOX.clear() 防止一次试验的副作用污染下一次；check 只检查 final 的业务结果，而不要求严格同一工具序列，这为更优的有效路径留下空间。切到 live 后 Notebook 只保留一个列，避免把同一模型的重复采样伪装成 policy 对比。要比较真实模型，应逐次修改 MODEL 并保留相同任务、预算、工具和评分器。"),
          P("最重要的评测结论：只用六个 happy-path 用例时 eager 可能得 100%，而两条负例揭示其行为边界。因此生产评测应从真实故障中抽样，包含拒答、越权、缺失数据、冲突数据、重复副作用等负例，并同时记录通过率、成本、轮数、停止原因和人工复核结果。"), PageBreak()]

story += [h1("十一、课后扩展：复核与上下文管理"),
          h2("独立复核器"),
          P("review(artefact, requirements) 只接收最终产物和需求清单，不接收原始 trace。这样第二个判断器不会继承第一个智能体的注意力偏差。演示要求最终答案包含 mis-sort、2026-08-27 与 260；缺少任何一个即返回 UNMET。真实项目可将其替换为规则校验、检索式事实核验或独立 LLM judge，并保留证据链接。"),
          h2("压缩与外置事实"),
          table([
              ["方案", "compact", "externalise + SCRATCHPAD"],
              ["做法", "从 Observation 抽取并截断为摘要", "把每条 Observation 写成 fact_i，只在需要时读取"],
              ["优点", "上下文短、调用便宜", "事实无损、上下文只保留指针"],
              ["代价", "推理细节与截断外的信息可能永久丢失", "需要额外存储和读取工具"],
              ["适用建议", "可丢失的推理过程", "订单号、金额、日期、授权状态等关键事实"],
          ], [2.7*cm, 6.55*cm, 6.35*cm]),
          P("Notebook 的一句规则值得直接复用：压缩 reasoning，外置 facts。因为后者一旦丢失，智能体往往不会知道自己遗忘了什么。"),
          h1("十二、复现与作业迁移清单"),
          bullet("先运行 scripted 版本，观察 careful、repeats、credulous 的 trace 与 halted 字段。"),
          bullet("把 BACKEND 改为 live 前配置 API Key、模型名与额度，并只以相同 harness 比较不同模型。"),
          bullet("针对自己的 A2 场景，先定义可机读的 TRUTH / 评分规则，再挑选最小的权威工具集合。"),
          bullet("每个失败都应能缩减为一个清楚的删改：缺了哪条 guard？哪个工具返回了不应返回的数据？"),
          bullet("把负例、写操作审批、去重、预算和步骤上限作为交付的一部分，而不是附录。"),
          Spacer(1, .25*cm),
          P("来源说明：本解读基于 Part3_LI_LINGHAO/PE6201_Class4_C2_Agent_Build.ipynb 的 Markdown 与代码单元撰写。由于当前环境未提供 Jupyter 可执行命令，本文未宣称实际运行该 Notebook 的输出数值；所有结果描述均来自固定数据、脚本策略及代码逻辑本身。", "CalloutCN"),
          P("完", "SmallCN")]

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
