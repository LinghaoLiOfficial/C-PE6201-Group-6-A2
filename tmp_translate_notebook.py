import html
import json
import re
import subprocess
from pathlib import Path


ROOT = Path("/Users/llh/PycharmProjects/C-PE6201-Group-6-A2")
SOURCE = ROOT / "Part3_LI_LINGHAO" / "PE6201_Class4_C2_Agent_Build.ipynb"
OUT_NB = ROOT / "Part3_LI_LINGHAO" / "PE6201_Class4_C2_Agent_Build_中文.ipynb"
OUT_MD = ROOT / "tmp" / "PE6201_Class4_C2_Agent_Build_中文.md"
OUT_HTML = ROOT / "tmp" / "PE6201_Class4_C2_Agent_Build_中文.html"
OUT_PDF = ROOT / "Part3_LI_LINGHAO" / "PE6201_Class4_C2_Agent_Build_中文.pdf"

MARKDOWN = {
0: r"""# PE6201 · 第 4 课 · Capsule 2 - B 部分
## 使用一个工具构建 ReAct 智能体，然后故意让它失效

**企业人工智能硕士 · 新兴人工智能技术 · 第 4 周**

---

### 如何使用本 Notebook

你不需要在课堂上完成它，也不应该这样做。课堂上我们会基于一份预先运行过的副本，
一起追踪智能体的运行轨迹。**这个 Notebook 是留给你课后运行的**，学习恰恰发生在
这里：阅读别人产生的轨迹，并不等同于亲眼看到自己的智能体做出一些不理智的事情。

**请从上到下运行。** 不需要 API 密钥，也不会产生费用：

```python
BACKEND = "scripted"   # 默认值 - 确定性的模型替身
BACKEND = "live"       # 使用真实模型运行相同循环（需要密钥）
```

脚本后端不是对大语言模型的模拟，而是一个小型策略，用来重放真实模型在这个任务中
可能做出的决策，包括我们想观察的两个错误。它周围的一切，包括循环、工具、令牌
统计、护栏和评估，都是实际代码，在两个后端之间保持不变。

> **模型任选。** `"live"` 并不绑定某一家供应商。默认路径使用 OpenRouter 密钥，
> 通过一个端点访问 Claude、GPT、Gemini、Llama、Qwen、DeepSeek、Mistral 等模型；
> 只需修改 `MODEL` 字符串即可。直接使用 OpenAI 或 Anthropic 密钥也可以，也可以
> 使用运行在自己电脑上的模型。**让两个或三个不同模型完成相同的八个任务，是本
> Notebook 中最有意思的一小时**，而评估工具让这样的比较真正有意义。

> **为什么还要伪造模型？** 因为无法复现的失败就无法调试；而让三十名同学同时触发
> 速率限制，也不能算是一堂课。先观察脚本应产生什么样的轨迹，再切换到 `"live"`；
> 之后真正有价值的是看真实模型在哪些地方与脚本不同。

### 十个章节

| 章节 | 内容 | 课堂安排 |
|---|---|---|
| 0 | 任务，以及构建前要问的问题 | 讲解 |
| 1 | 单次调用、没有循环 - 基线 | 讲解 |
| 2 | **手写 ReAct 循环** - 完整轨迹与每轮成本 | 讲解 |
| 3 | 通过原生工具调用完成同一任务 | 阅读 |
| 4 | **故意破坏 #1** - 智能体不断重复 | 讲解 |
| 5 | **故意破坏 #2** - 臃肿的观察与自信的错误答案 | 讲解 |
| 6 | 修复方案一 - **代码**层 | 讲解 |
| 7 | 修复方案二 - **工具**层 | 阅读 |
| 8 | **自主性滑杆**：建议 / 确认 / 执行 | 讲解 |
| 9 | 什么才算做好 - 一个小型评估工具 | 阅读 |
| 10 | 课后练习 - 审查智能体、压缩与草稿本 | 自主完成 |""",
1: r"""---
## 第 0 章 · 任务，以及构建前要问的问题

在 Capsule 1 中，我们把下面的任务作为真正具有智能体特征的例子，因为没有人能预先
说出它需要多少步骤：

> **“查明订单 SO-4471 为什么延迟，给客户一个现实的新日期，并告诉客户。”**

现在开始构建。

### 首先，构建前诊断（预读材料 1）

> **什么会告诉这个循环它走错了，以及它能多快知道？**
> 如果诚实答案是*“下周由人工处理”*，就不要构建智能体。

对于这个任务，答案很好：每一步都会访问一个能在一秒内反驳模型的记录系统，例如
订单行、承运商扫描记录和库存数量。这就是**以机器速度到达的事实依据**，也是这里
允许循环无人监督运行的全部理由。

### 其次，写下什么才算做好

在写任何代码之前完成。这是评估的下游依据，正如案例说明中所说，*“这就是 Capsule 2
的全部内容。”*

**这个任务的一次良好运行应该：**

1. 说出可以追溯到记录的**真实**延迟原因，而不是听起来合理的故事。
2. 给出与承运商扫描和库存状态**一致**的新日期。
3. 事实确认之后，最多发送**一封**客户邮件。
4. 当记录不足以支持某个日期时，说**“我不知道”**，而不是编造日期。
5. 成本低于人工处理。（我们会在 Capsule 3 中正式计算。）

第 4 点是团队最容易忘记的，也是我们将观察智能体失败的地方。""",
3: r"""### 智能体所操作的世界

四个记录系统，分别代表 ERP、承运商 API、WMS，以及每个组织都有却无人维护的自由文本
备注字段。

**SO-4471 的真实情况**（智能体不知道，但我们知道）：
订单延迟是因为承运商在 8 月 18 日于吉隆坡把托盘分拣错误。库存充足，现实的新日期
是 **8 月 27 日**。无论说得多么自信，任何其他答案都是错误的。""",
6: r"""### 它实际获得哪些工具？

把一个工具写好是上一个问题。再往上一级，真实系统经常在这里出错：**人们把手头
所有东西都接进来。**

一个工具加入列表前，先问三个问题。

**1 · 没有它，任务真的会失败吗？**
从完成任务所需的最小集合开始，只根据已经观察到的失败添加工具，不要根据想象添加。
大多数团队反过来做：第一次运行前就先写工具列表。

**2 · 模型会把它和另一个工具混淆吗？**
关键是**可区分性，而不是数量**。十个明显不同的工具没问题；三个相互重叠的工具
就很危险，因为模型会选中“差不多”的那个，还会自信地这么做。如果你无法用一句话
说明什么时候使用 A 而不是 B，模型也无法做到。

**3 · 从不调用它时，它仍然要付出什么成本？**
每个定义都位于提示词前缀中，**每一轮都会重新发送并重新计费**，不管是否调用。
工具还会扩大无法穷举测试的失败面：N 个工具、T 轮的轨迹空间是组合式增长的；
如果工具能写入数据，它还会增加一道闸门。

### 本 Notebook 中的五个工具

| 工具 | 没有它会失败吗？ | 会混淆吗？ | 它存在的理由 |
|---|---|---|---|
| `lookup_order` | 会 - 没有其他工具能解析订单 ID | 不会 | 入口；其他工具都需要它的输出 |
| `check_shipment` | 会 - 只有它能提供真实原因 | 不会 | 唯一能反驳合理猜测的工具 |
| `check_inventory` | 对日期来说会 - 库存可能使 8 月 27 日不成立 | 不会 | 成本低，可避免自信地做出错误承诺 |
| `search_notes` | **不会**，但我们仍保留它 | **会**，与前两个工具重叠 | 有意保留：它是第 5 章的陷阱；生产环境中应该删掉它 |
| `send_customer_email` | 会 - 任务要求“告诉客户” | 不会 | 唯一的写入操作；一道闸门即可覆盖整个智能体 |

`search_notes` 是一个诚实的例子。它同时无法通过问题 1 和问题 2，而第 5 章的失败
正是由它造成的。**这不是巧合，而是论证本身。**

### 添加工具前，先尝试不添加

* 扩展现有工具的参数，而不是添加一个同类工具
* 让一次调用返回更多信息，而不是再添加一次查询
* 把该步骤移出循环，放入普通代码，在循环之前或之后执行
* 交给一个拥有精简工具集的**子智能体**，让它返回简短摘要""",
8: r"""### 模型

只有一个函数：输入转录内容，输出下一步。除此之外，上下都是普通代码。

脚本后端根据转录中已有的内容选择下一步，这正是真实模型的做法，只是它的“大脑”
小得多。它接收一个 `policy`，三个策略对应我们关心的三种运行方式：

| 策略 | 行为 | 为什么需要它 |
|---|---|---|
| `"careful"` | 查完记录，然后发送邮件 | 应该发生的运行 |
| `"repeats"` | 重复发出同一个动作 | 第 4 章：预读材料 2 首先指出的失败 |
| `"credulous"` | 相信备注字段 | 第 5 章：自信、错误，并报告成功 |
| `"eager"` | 对真实任务谨慎，对负面案例轻信 | 第 9 章：通过所有 happy-path 测试的智能体 |""",
10: r"""---
## 第 1 章 · 单次调用，没有循环 - 基线

在循环之前，先做一个诚实的比较：一次调用要花多少钱，又能得到什么？

它只会以不到一美分的成本生成一段流畅但没有事实依据的文字。记住这个数字。从现在
开始增加的每一轮，都必须证明自己值得相对于它存在。""",
12: r"""---
## 第 2 章 · 手写 ReAct 循环

这是预读材料 2 中的循环，大约只有二十行。请认真阅读，因为**现代框架把它藏在 API
后面，让你无法调试自己看不见的东西。**

观察轨迹时注意两点：

1. **转录内容每轮都在增长，而且每轮都会重新发送全部内容。** 这就是输入令牌数不断
   增加而输出长度相对稳定的原因，也是成本随轮数呈二次增长而不是线性增长的原因。
   Capsule 3 会计算公式；这里先观察曲线弯曲。
2. **每个 Observation 都是事实依据。** 模型提出建议，记录决定结果。拿掉 Observation，
   剩下的就只是独白。""",
15: r"""**阅读最后两行。** 轮数增加了 *n* 倍，账单增加得超过 *n* 倍。没有东西损坏，
这只是因为不断重新发送增长中的转录而产生的成本。记住这个比例；Capsule 3 会把它
写成公式。""",
16: r"""---
## 第 3 章 · 相同的循环，更好的连接方式

现在每个服务商都有原生工具调用：你传入 JSON Schema，模型返回结构化的 `tool_use`
块，而不是一行文本，SDK 会替你解析。

**循环本身没有改变。** 改变的只是由谁来做字符串解析；上面那个在生产环境中最先
容易出问题的 `parse_action` 正则表达式消失了。阅读此单元格，不要运行它。

先手写循环的意义在于：当框架版本行为异常时，你已经知道它底层做了什么。""",
18: r"""---
## 第 4 章 · 故意破坏 #1 - 智能体重复自己

预读材料 2 首先指出了这个问题，预读材料 3 解释了原因：**循环没有记录动作带来了
什么变化。** 智能体的上下文中已有发货记录，却再次请求发货记录。它不是混淆了数据，
而是没有“我已经做过了，而且这没有让我前进”的表示。

观察成本列，而不是文字。""",
20: r"""---
## 第 5 章 · 故意破坏 #2 - 臃肿的观察与自信的错误答案

`search_notes` 返回整个备注字段：其中有 246 个令牌，大部分是过时文本，还埋着一条
**未经批准的政策草案**。智能体读到它，照此执行，并生成一个与它从未检查过的承运商
记录相矛盾的日期。

然后它说：**“任务完成，无需进一步操作。”**

这是 Devin 的*自信信号*失败，也是本 Notebook 中最危险的失败，因为表面上什么都正常。
没有 traceback，输出格式正确、听起来合理；如果审查者只看最终答案，它很可能直接通过。""",
22: r"""### 两种失败，两种不同的修复方式 - 这正是团队最容易弄错的地方

| | 第 4 章：重复 | 第 5 章：自信但错误 |
|---|---|---|
| **本质** | 循环没有状态 | 观察结果有问题，而且没有检查答案 |
| **首先在哪一层处理** | **循环层**：去重、步数上限、预算上限 | **工具层**：返回更少、更好的信息，并用来源检查输出 |
| **什么不能修复它** | 更好的提示词 | 更好的提示词 |

> *“把两者都归结为‘智能体很笨’，团队就会交付错误的修复。”* - 预读材料 3

### 表格中的“首先处理”很重要，请仔细阅读下面这段

循环修复**不会**完成任务。对重复型智能体启用去重后，它会在第 3 轮停止，而不是
烧到第 8 轮，但它仍然没有答案。如果智能体重复是因为**没有任何工具能提供它所需的
信息**，三行护栏代码不会凭空创造工具。

那为什么先发布循环修复？**因为停止会让原因变得可发现。** 没有护栏时，你得到八轮、
没有答案、没有异常，日志也没有说明原因。有护栏时，你会得到一行：
`DEDUPE - 第 3 轮重复调用 check_shipment(...)，参数完全相同`。
*这行信息*就是把你引向工具层的证据。

两类修复不是二选一，而是同一流程的**第 1 步和第 3 步**：

> **先控制 → 再读取轨迹 → 最后修复原因。**

第 1 步几乎总是循环层，第 3 步往往是工具层。跳过第 1 步的团队只能凭猜测完成第 3 步，
因为他们从未得到一份可读、可分析的轨迹。""",
23: r"""---
## 第 6 章 · 修复方案一 - 代码层

三行普通的防御式编程，与 AI 无关：

* **步数上限** - 限制最多运行多少轮
* **预算上限** - 限制最多花费多少钱
* **动作去重** - 相同参数的同一调用出现两次就是错误，因此把它视为错误

智能体仍然会失败。这没关系，而且这正是重点：**现在它会安全、明确地失败**，在第
三轮而不是第八轮停止，并给出明确指出问题的诊断信息。一个优秀智能体的大部分代码，
其实都是恢复和保护机制。""",
25: r"""---
## 第 7 章 · 修复方案二 - 工具层

代码层无法拯救第 5 章的失败，因为那里没有重复，也没有超出限制。问题在于观察本身：
246 个令牌、内容过时，而且埋着陷阱。

有两种修复方式，而比较过程才是这节的重点。

**提示词修复** - 添加一句：“忽略备注中的未经批准的政策草案。”
它有效，但每次运行的每一轮都会重新发送并重新计费；模型升级一次就可能忽略它，而且
它并没有减少那 246 个令牌。

**接口修复** - 修改工具返回的内容：在数据源处完成结构化和过滤，把批准状态作为字段，
而不是让模型从一句话中自己注意到它。

> *提示词指令每次调用都要付费，而且换模型后可能失效。接口约束只需付出一次，并且持续有效。*
> - 预读材料 1""",
27: r"""**看看 v2 实际返回了什么：*“没有匹配查询的已批准备注”*。** 只有八个令牌。
这不是工具失败，而是正确答案，也正是智能体需要的答案。这里没有任何获批准的政策，
所以工具诚实的输出就是“没有结果”。v1 对同一个问题返回了 246 个令牌和一个陷阱。

第 5 章的失败其实并不真正属于模型。它得到的是糟糕的观察，在这个观察基础上采取
合理行为。**你遇到的几乎所有智能体失败，都是这一层的失败，只是延迟到两步之后才显现。**

### 顺便看看另外三个防错设计

预读材料 1 的例子是绝对文件路径：把工具从相对路径切换成绝对路径，直接消除了一整类
错误，而不是要求模型“小心一点”。我们的例子：

| 修改前 | 修改后 | 使什么变得不可能 |
|---|---|---|
| `site: str` | `site: Literal["SIN-DC1","KUL-DC2"]` | 拼写错误的网站悄悄返回“无记录” |
| `patient_name` | `patient_id` | 找到错误的 Tan |
| `send_email(...)` | `draft_email(...)` **+** `send_email(...)` | 本想起草却直接发送 |
| `dry_run: bool` | `dry_run: bool = True` | 默认执行不可逆操作 |

每一项都是设计决策，而不是提示词。这就是 ACI 的核心思想：
**工具说明和函数签名就是完整手册。** 模型不能向你询问意图，不能悬停查看提示，
也不能先在测试环境中试一次。""",
28: r"""---
## 第 8 章 · 自主性滑杆

自主性是一个**旋钮，而不是开关**（预读材料 5），Google 也是这样设计的：
Spark 默认关闭权限，并在花费你的钱之前询问你（预读材料 4）。

一个参数，三个位置；闸门位于唯一会接触真实世界的工具之前：

* `"suggest"` - 提议邮件，但不执行
* `"confirm"` - 只有人在确认后才执行
* `"act"` - 执行

注意旋钮的位置：**它位于写入工具之前，而不是位于智能体之前。**
读取操作仍然无人监督，因为它们可以撤销。这就是 Capsule 1 中的治理悬崖：
不是从 RAG 到 agentic RAG，而是第一次写入发生的地方。""",
30: r"""---
## 第 9 章 · 什么才算做好 - 一个小型评估工具

你在第 3 周写的评估工具无法直接适用于智能体。三件事发生了变化：

1. 一次调用变成了**轨迹**，出错位置变多了；
2. 输出包含**副作用**，邮件要么发出去了，要么没有；
3. 相同输入会产生**不同运行结果**，因此一次试验说明不了什么。

所以要进行**结果评估，而不是路径评估；多次试验；试验之间相互隔离；至少包含一个负面
案例**，也就是正确行为应当是拒绝的任务。

下面完整写出评估集，因为看到真实例子本身就是重点。八个任务：六个普通任务，一个
诚实答案是“我不知道”的任务，以及一个应该升级处理而不是回答的任务。每个任务运行三次。

> **真正的评估集应有 20-50 个任务**，来源于你实际见过的失败，并结合不同评分器：
> 代码检查和评分标准裁判。八个任务只是教学规模，不是上线规模；这个差距是有意保留的。
> A2 很可能要求类似结构，具体要求会写在任务说明中。""",
32: r"""### 三个智能体是如何构建的，以及为什么值得阅读代码

下表比较 `careful`、`eager` 和 `credulous`。它们**不是三个智能体**，而是同一个智能体
的一个参数；它们的差异只存在于 `_scripted()` 中的几行代码。这是有意设计的，值得花
两分钟阅读，因为**如何构造失败演示，本身就是一堂关于智能体如何失败的课。**

#### 共享骨架

每个策略都使用同一种写法：在运行中的转录上串联一组守卫条件：

```python
def _did(prompt, tool):
    # 这个工具已经在转录中被调用了多少次？
    return len(re.findall(rf"^Action: {tool}\(", prompt, flags=re.M))
```

`_did()` 是策略拥有的唯一状态。每一轮它都会重新读取转录，并询问“我已经做过这个
了吗？”因此每个策略都只是：

```python
if not _did(prompt, "tool_a"):  return "Action: tool_a(...)"
if not _did(prompt, "tool_b"):  return "Action: tool_b(...)"
return "Final: ..."
```

**一个策略就是一组有顺序的守卫条件，加上列表耗尽时要说的话。** 行为被编码在结构中，
所以你可以直接从代码看出差异。

#### `careful` - 按证据顺序执行的完整链条

    lookup_order → check_shipment → check_inventory → send_customer_email → Final

在允许得出结论之前，必须通过四个守卫。行为本身就是顺序：只有所有守卫都满足后，
它才能输出 `Final:`。“先确立事实再回答”在这里不是性格，而是控制流属性。

#### `credulous` - 缺少一个步骤的链条

    lookup_order → search_notes → Final

有两个变化，而且都很重要：

1. **链条中根本没有 `check_shipment`**，不是顺序错误，也不是有条件跳过，而是完全不存在；
   掌握事实依据的工具永远无法被访问。
2. **`search_notes` 占据了本应属于它的位置**，一个没有权威性的自由文本字段成为陷阱所在。

重点是：**轻信型智能体不是犯了一个错误，而是遗漏了一个步骤。** 基于它看到的内容，
它的推理没有问题；它只是从未真正去查找。这正是生产环境中的真实失败方式，也是第 5
章轨迹比答案更重要的原因。

#### `eager` - 没有自己的决策代码

人们通常以为它是第三个质量等级，但并不是。它只有两行代码，也没有新增行为：

```python
base = "careful"   if policy == "eager" else policy   # 用于真实任务
neg  = "credulous" if policy == "eager" else policy   # 用于负面案例
```

`eager` 是一个**路由器**。它所做的每一个动作都已经写在另外两个策略中；唯一新增的
内容是把它们粘合起来的位置，而这个连接点恰好位于任务类型边界：

    _scripted(prompt, policy)
        ├── 任务提到 SO-9999      → 使用 `neg` 决策
        ├── 任务提到 goodwill/5%  → 使用 `neg` 决策
        └── 其他所有任务          → 使用 `base` 决策

这个边界正是 happy-path 评估集不会覆盖的地方。`eager` 不是“稍微粗心”，而是在测试
覆盖范围的边缘之前都表现完美，一越过边缘就变得轻信。把它构造成组合策略本身就说明：
**危险的智能体，往往是一个在未测试区域表现良好的智能体。**

#### `repeats`（第 4 章）- 删除了一个守卫

```python
if not _did(prompt, "lookup_order"):
    return 'Action: lookup_order(order_id="SO-4471")'
# 它从未记录自己已经拥有发货记录。
return 'Action: check_shipment(tracking_id="TRK-88120")'
```

第二次调用没有 `_did` 守卫。删除这一行就会产生八轮、没有答案、成本增加 1.6 倍，
却没有异常。这一行代码证明：除非显式提供机制，否则循环不会记住自己的动作；而这正
是去重护栏所补上的内容。

#### 其他条件全部保持不变

这使得下面的表格是真正的比较，而不是轶事。每个策略都经过完全相同的调用：

```python
run_agent(task, policy=policy, step_cap=6, budget_usd=0.02, dedupe=True, verbose=False)
```

相同的循环、五个工具、工具说明、系统提示、护栏、步数上限、预算、三次试验，以及每次
试验之间的 `OUTBOX.clear()`。**只改变一个变量。** 评估工具只能根据结果区分它们，
这就是从内部看到的结果评估。

> **把这一点带入 A2。** 复现两个失败时，把每个失败构造成工作智能体的一个*删除操作*：
> 删除一个守卫，或让一个工具无法访问，而不是另写一个坏智能体。这样你能用一句话解释
> 失败，指出具体修复位置，并让评估工具真正测出修复前后的差异。""",
34: r"""**在解读这些数字之前先记住：** `careful` 策略得分 100%，是因为它是脚本，永远
不会状态不好。真实模型不会如此；把 `BACKEND` 切换为 `"live"`，比较这两次运行之间
的差距，是你在家里能做的最有价值的实验。**可交付成果是评估工具，而不是分数。**

**然后做两次。** 让相同的八个任务分别运行在两个不同模型上：先把 `MODEL` 设为 Claude，
再设为 GPT、Gemini，或一个能在本地运行的小型开放模型。这样得到的是针对*你自己的任务*
的模型比较，而不是别人的排行榜，而且成本只有几美分。特别留意哪些模型会在 E7 和 E8
上失败；普通任务区分模型的能力远不如负面案例。

**这个评估工具真正的用途。** 不是分数，因为分数只是关于一个玩具的数字。它的用途是：
三周后你修改了工具说明，发现通过率从 92% 降到 71%，并能在一分钟内知道发生了什么。
没有评估工具，你会从客户那里得知。

有两点值得带入 A2：

* **负面案例包含最多信息。** 看 `eager` 列：普通任务六战全胜，两个负面案例全部失败。
  只测试 happy path 的评估工具会给它 100% 分，然后把它上线。
* **评估结果，而不是路径。** 这些检查都不关心调用了哪些工具、顺序如何。如果智能体
  找到了更好的路线，那是更好的智能体，而不是失败。""",
35: r"""---
## 第 10 章 · 课后练习 - 值得你自己花一小时的两件事

课堂没有覆盖这两项内容，但都很简短，而且直接来自预读材料。

### (a) 使用干净上下文的审查智能体

预读材料 5 对其多智能体观点的修正是：第二个智能体可以发现第一个智能体无法发现的
问题，但前提是你给它**产物和要求，而不是轨迹**。如果把轨迹也展示给它，它会继承同样
的视野限制，相当于为同一个观点付了两次钱。

### (b) 压缩与草稿本

预读材料 2 特别把这一点放在这里。上下文就是状态，并且每轮都会增长。你有两种做法，
但它们不能互相替代：

* **压缩** - 总结当前转录并携带摘要。便宜，但会丢失信息，而且只有在信息变得重要时，
  你才会发现它已经丢失。
* **移出上下文窗口** - 把发现写入文件或草稿本，只保留指针，需要时再读回来。连接代码
  更多，但不会静默丢失信息。

经验法则：压缩推理，外部化事实。""",
37: r"""---
## 把这些带入 A2

A2 的任务说明尚未发布，因此请把这里看作工作形态，而不是正式规格。这个 Notebook 中
有六个值得带入 A2 的习惯：

1. **把构建前的问题写下来并回答。** 什么会告诉你的循环走错了，以及它能多快知道？
   如果答案是“下周由人工处理”，就换一个任务。
2. **工具列表中每个工具都用一句话说明理由**：没有它哪个任务会失败，以及为什么不会
   和相邻工具混淆。无法用一句话解释的工具，说明你还没有真正决定是否需要它。评分看重
   能完成任务的*最短*列表，而不是最长列表。
3. **在写第一行智能体代码前，写下“什么才算做好”。**
4. **优先交付代码层。** 步数上限、预算上限、去重，不可妥协。
5. **有意复现两个失败**，并把每个失败的修复放在正确的层。
6. **准备 20-50 个自己的评估任务**，按结果评分，运行多次，包含负面案例，并使用实际
   测量而不是估计的通过率。

*无论 A2 最终要求什么，这六点都不会浪费：它们让没有参与构建的人也能相信你的智能体。*

*Capsule 3 会计算这一切的成本：每一轮要花多少钱，什么时候循环不值得，以及 Anthropic
针对这个问题采取了什么做法。*""",
}


COMMENT_REPLACEMENTS = [
    ("configuration", "配置"),
    ("THE WORLD", "运行世界"),
    ("four stand-in systems of record", "四个模拟记录系统"),
    ("THE TOOLS", "工具"),
    ("four reads and one write", "四次读取和一次写入"),
    ("THE MODEL INTERFACE", "模型接口"),
    ("the ONE place a decision gets made", "唯一做出决策的地方"),
    ("Not run in class", "课堂不运行"),
    ("needs a key", "需要密钥"),
    ("the eval set", "评估集"),
    ("isolation between trials", "试验之间相互隔离"),
    ("WHAT THE COLUMNS ARE, AND WHY THERE ARE FEWER OF THEM WHEN YOU GO LIVE", "列的含义，以及切换到 live 后为什么列数更少"),
    ("SCRIPTED backend", "SCRIPTED 后端"),
    ("LIVE backend", "LIVE 后端"),
    ("review agent with a clean context", "使用干净上下文的审查智能体"),
    ("compaction vs scratchpad", "压缩与草稿本"),
    ("same dispatch", "相同的分发机制"),
    ("same four moves", "相同的四个步骤"),
    ("the agent loop above it does not change at all", "上面的智能体循环完全不变"),
    ("Illustrative prices", "示例价格"),
    ("A rough token estimate", "粗略的令牌估算"),
    ("Deliberately not a real tokeniser", "有意不使用真实分词器"),
    ("The ReAct loop itself", "ReAct 循环本身"),
    ("per turn", "每轮"),
    ("the same tool", "同一个工具"),
    ("with identical arguments", "参数完全相同"),
    ("customer notified", "已通知客户"),
    ("human says", "人工回答"),
    ("all requirements met", "所有要求均已满足"),
]


def translate_code(code: str) -> str:
    lines = []
    for line in code.splitlines():
        if line.lstrip().startswith("#"):
            for old, new in COMMENT_REPLACEMENTS:
                line = line.replace(old, new)
        lines.append(line)
    code = "\n".join(lines)
    doc_replacements = [
        ("A rough token estimate:", "粗略的令牌估算："),
        ("The ReAct loop itself. Read this function once and you have read the agent.", "ReAct 循环本身。读完这个函数，就理解了这个智能体。"),
        ("Pull the tool name and kwargs out of an 'Action:' line.", "从 Action 行中提取工具名称和关键字参数。"),
        ("Group the notes field into whole records. A record starts with a date.", "将备注字段分组为完整记录。每条记录都以日期开头。"),
        ("v2 — filtered at the source, relevance-ranked, and small.", "v2 - 在数据源处过滤、按相关性排序，并保持结果精简。"),
        ("Deliberately does NOT see the trace. Only the output and what was asked for.", "有意不查看轨迹，只查看输出和要求。"),
    ]
    for old, new in doc_replacements:
        code = code.replace(old, new)
    return code


def markdown_to_html(text: str) -> str:
    proc = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html5"],
        input=text,
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout


def main():
    nb = json.loads(SOURCE.read_text(encoding="utf-8"))
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "markdown" and i in MARKDOWN:
            cell["source"] = MARKDOWN[i].splitlines(keepends=True)
        elif cell["cell_type"] == "code":
            cell["source"] = translate_code("".join(cell.get("source", []))).splitlines(keepends=True)
    OUT_NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

    chunks = []
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "markdown":
            chunks.append(markdown_to_html("".join(cell["source"])))
        else:
            code = html.escape("".join(cell.get("source", [])))
            chunks.append(f'<div class="cell code-cell"><pre><code>{code}</code></pre></div>')
    body = "\n<hr class=\"cell-separator\">\n".join(chunks)
    document = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<style>
@page {{ size: A4; margin: 16mm 15mm 17mm 15mm; }}
body {{ font-family: "Arial Unicode MS", "PingFang SC", "Heiti SC", "Songti SC", sans-serif; color: #202124; font-size: 10.5pt; line-height: 1.55; }}
h1 {{ font-size: 22pt; color: #17365d; margin: 0 0 6pt; }}
h2 {{ font-size: 16pt; color: #1f4e79; margin: 18pt 0 6pt; border-bottom: 1px solid #b7c9dc; padding-bottom: 3pt; }}
h3 {{ font-size: 12.5pt; color: #365f91; margin: 14pt 0 5pt; }}
h4 {{ font-size: 11pt; color: #365f91; margin: 10pt 0 4pt; }}
p {{ margin: 5pt 0; }}
blockquote {{ border-left: 3px solid #6b9ac4; background: #f2f6fa; padding: 5pt 9pt; margin: 8pt 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9pt; }}
th, td {{ border: 1px solid #aebdca; padding: 4pt 5pt; vertical-align: top; }}
th {{ background: #dce6f1; color: #17365d; }}
code {{ font-family: "Menlo", "Monaco", monospace; font-size: 8.1pt; background: #f1f3f4; padding: 1pt 2pt; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #f5f6f7; border: 1px solid #d7dbe0; border-radius: 3px; padding: 8pt; font-family: "Menlo", "Monaco", monospace; font-size: 7.2pt; line-height: 1.35; }}
.code-cell {{ page-break-inside: avoid; margin: 7pt 0 10pt; }}
.cell-separator {{ border: 0; border-top: 2px solid #dce6f1; margin: 12pt 0; }}
hr:not(.cell-separator) {{ border: 0; border-top: 1px solid #c9d4df; }}
li {{ margin: 2pt 0; }}
</style></head><body>{body}</body></html>"""
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(document, encoding="utf-8")
    soffice = "/Users/llh/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/soffice"
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(OUT_PDF.parent), str(OUT_HTML)],
        check=True,
        capture_output=True,
        text=True,
    )
    generated = OUT_PDF.parent / (OUT_HTML.stem + ".pdf")
    if generated != OUT_PDF:
        generated.replace(OUT_PDF)
    print(OUT_NB)
    print(OUT_PDF)


if __name__ == "__main__":
    main()
