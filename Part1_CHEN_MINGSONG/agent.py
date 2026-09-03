"""
A2 问题 A —— 理赔版 ReAct Agent（交付物 D1），person 1 负责
= 提示词(SYSTEM) + 循环(run_agent) + 真模型(call_model) + 8 个工具(来自 tools.py)

把老师的循环骨架(parse_action / run_agent 的 6 阶段)抄过来，
内容(提示词/工具/任务)换成保险理赔版，再让真模型跑一次。
"""
import json
import os
import re
import urllib.request

# ---- 从 tools.py 拿我们写好的 8 个工具 ----
from tools import TOOLS


# ---- 本地读 .env（.env 不进 git，key 只存在你自己电脑上）----
def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_env()

# ---- OpenRouter 配置（key 从环境变量读，不再硬编码在代码里）----
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "deepseek/deepseek-v3.2"
API_URL = "https://openrouter.ai/api/v1/chat/completions"


# ==================== 8 个工具的"说明书"，贴进提示词 ====================
TOOL_SPEC = """
get_claim(claim_id: str) -> claim header: member_id, hospital_id, date_of_service, narrative, documents, lines
lookup_member(member_id: str) -> member_id, policy_id
lookup_policy(policy_id: str) -> status, start_date, end_date, annual_limit, used_to_date, exclusions
get_hospital_status(hospital_id: str) -> hospital_id, panel (true=in-network)
check_procedure(code: str) -> code, description, requires_preauth
get_preauthorisation(member_id: str, procedure_code: str) -> preauth_id, valid_from, valid_to
check_documents(procedure_code: str) -> required_documents (list)
check_duplicate(claim_id: str) -> duplicate of an earlier decided claim, or "no duplicate found"
""".strip()


# ==================== 提示词：角色 + 规则 + 工具 + 输出格式 ====================
SYSTEM = f"""You are a health-insurance claims assistant. Your job is the FIRST RESPONSE to a claim: for each procedure line on the claim, decide one of three outcomes:
  - approve
  - refuse  (always cite the rule id)
  - ask     (a required document is missing — request it, do not refuse)

Available tools:
{TOOL_SPEC}

Rules. Use ONLY the tools to get facts — never invent member, policy, hospital, procedure, or preauthorisation data.

1. Read the claim: call get_claim(claim_id). Then call check_duplicate(claim_id). If it is a duplicate of an already-decided claim, report that earlier decision and stop.

2. Member and policy: lookup_member(member_id) to get policy_id, then lookup_policy(policy_id). A line can only be approved if ALL of these hold:
   - status is active
   - date_of_service is between start_date and end_date
   - the total approved amount stays within headroom, where headroom = annual_limit - used_to_date
   - the line's code is NOT in exclusions. If it is excluded, refuse that line and cite its rule id.

3. Hospital: get_hospital_status(hospital_id). If panel is false, say the hospital is out-of-network in the decision.

4. Each line's procedure: check_procedure(code) for each code. If requires_preauth is true, call get_preauthorisation(member_id, procedure_code) and confirm date_of_service is between valid_from and valid_to. A missing or expired preauthorisation means that line cannot be approved.

5. Documents: call check_documents(procedure_code) for each code. If a required document is not in the claim's documents list, that line is an "ask" (request the missing document).

Reply in exactly this form, one step at a time:
Thought: <your reasoning>
Action: <tool_name>(arg="value", ...)

STRICT RULES (follow them or the run fails):
- You MAY output several Actions in one reply, but ONLY for tool calls that do not depend on each other's output. If one call needs another's result, wait for the next turn.
- NEVER write the Observation yourself — the system supplies it after your Action(s).
- NEVER predict or invent what a tool returns; use only the Observation you actually receive.

Dependency rule (which calls may go together):
- get_claim must run FIRST and alone — every later call needs the member_id / hospital_id / codes it returns.
- After get_claim, these are independent of each other and MAY go in one turn: lookup_member, get_hospital_status, check_procedure(each code), check_documents(each code), check_duplicate.
- lookup_policy needs lookup_member's policy_id, so it waits for the next turn.
- get_preauthorisation needs check_procedure to say requires_preauth=true first, so it waits.

When finished, reply:
Thought: <why you are done>
Final: <one decision per line: approve / refuse (rule id) / ask (missing document)>
"""

TASK = ("Process claim CLM-8842. For each procedure line give a decision "
        "(approve / refuse with rule id / ask with the missing document). "
        "Cite preauthorisation ids and rule ids where relevant.")


# ==================== 真模型调用（OpenRouter） ====================
def call_model(prompt: str) -> str:
    """把整段 transcript 发给真模型，拿回它下一步的文本(Thought/Action 或 Thought/Final)。"""
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,       # 0 = 尽量确定，格式更稳
        "max_tokens": 2000,
    }).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "choices" not in data:
        raise RuntimeError(f"API error: {data}")
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return content, usage


# ==================== 解析 Action（抄老师的，一行不改） ====================
def parse_action(step: str):
    """从 'Action: 工具名(参数="值")' 里抽出工具名和参数。"""
    m = re.search(r"^Action:\s*(\w+)\((.*)\)\s*$", step, flags=re.M | re.S)
    if not m:
        return None, {}
    name, argstr = m.group(1), m.group(2)
    kwargs = {}
    for k, v in re.findall(r'(\w+)\s*=\s*"([^"]*)"', argstr):
        kwargs[k] = v
    for k, v in re.findall(r'(\w+)\s*=\s*(True|False)', argstr):
        kwargs[k] = (v == "True")
    return name, kwargs


def parse_actions(step: str):
    """一轮里解析出所有的 Action，返回 [(工具名, 参数字典), ...]。

    D2(c) 需要：允许模型一轮发多个互不依赖的工具调用。用 finditer 把每个
    "Action: name(...)" 都找出来（参数里没有括号，用 [^()]* 安全地停在一对括号内）。
    """
    actions = []
    for m in re.finditer(r"Action:\s*(\w+)\(([^()]*)\)", step):
        name, argstr = m.group(1), m.group(2)
        kwargs = {}
        for k, v in re.findall(r'(\w+)\s*=\s*"([^"]*)"', argstr):
            kwargs[k] = v
        for k, v in re.findall(r'(\w+)\s*=\s*(True|False)', argstr):
            kwargs[k] = (v == "True")
        actions.append((name, kwargs))
    return actions


# ==================== ReAct 循环（D2(c) 版：一轮可执行多个 Action） ====================
def run_agent(task: str, max_turns: int = 25, parallel: bool = True):
    header = SYSTEM
    if not parallel:
        # 串行基线：强制一次一个工具，用来和并行版对比 turns / tokens / cost
        header += ("\n\nMODE: strictly SEQUENTIAL — output EXACTLY ONE Action per "
                   "reply. Never more than one.")

    transcript = header + "\n\nTask: " + task + "\n"
    final = ""
    total_prompt = 0
    total_completion = 0

    for turn in range(1, max_turns + 1):
        # ① ASK —— 唯一碰模型的一步，同时累计 token 用量
        step, usage = call_model(transcript)
        total_prompt += usage.get("prompt_tokens", 0)
        total_completion += usage.get("completion_tokens", 0)

        print(f"\n── turn {turn} " + "─" * 46)
        print("   " + step.strip().replace("\n", "\n   "))

        # ② PARSE —— 一轮里可能有好几个 Action
        actions = parse_actions(step)

        # ③ STOP? —— 没有 Action 且出现 Final 才算结束
        if not actions:
            if "Final:" in step:
                final = step.split("Final:", 1)[1].strip()
                transcript += step + "\n"
                break
            obs = ('ERROR: could not parse an Action. Reply with exactly:\n'
                   'Thought: <reasoning>\n'
                   'Action: <tool_name>(arg="value", ...)')
            print(f"   Observation: {obs}")
            transcript += step + "\nObservation: " + obs + "\n"
            continue

        # ④ ACT —— 把所有 Action 一起执行，每个结果单独标号喂回去
        obs_lines = []
        for i, (name, kwargs) in enumerate(actions, 1):
            if name in TOOLS:
                try:
                    o = TOOLS[name](**kwargs)
                except Exception as e:
                    o = f"ERROR: {type(e).__name__}: {e}"
            else:
                o = f"ERROR: no tool named {name}"
            obs_lines.append(f"[{i}] {name} -> {o}")
        obs = "\n".join(obs_lines)

        print(f"   Observation:\n   " + obs.replace("\n", "\n   "))

        # ⑤ APPEND —— 模型这步 + 所有观察结果粘回 transcript，下一轮重发
        transcript += step + "\nObservation:\n" + obs + "\n"
    else:
        print(f"\n   ⛔ STEP CAP: {max_turns} turns without a Final")

    return final, turn, transcript, total_prompt, total_completion


if __name__ == "__main__":
    final, turns, _, ptok, ctok = run_agent(TASK, parallel=True)
    print("\n" + "=" * 60)
    print(f"FINAL ANSWER ({turns} turns):")
    print(final)
    print(f"\nTOKENS  prompt={ptok}  completion={ctok}  total={ptok + ctok}")
