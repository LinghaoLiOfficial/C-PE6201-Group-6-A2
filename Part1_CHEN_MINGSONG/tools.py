"""
A2 问题 A —— 工具层（交付物 D2a），person 1 负责
8 个工具 = 8 个"开柜子取数据"的小函数。全部完成。
"""
import json
import os

# ---- 数据位置（改成你自己的路径）----
DATA_DIR = r"C:\Users\86178\Desktop\NTU-school materials\6201\Assignments\A2\A2_reference_data_extracted\A2_reference_data\data_A"

def _load(path: str):
    """读一个 JSON 文件，返回 Python 数据。"""
    with open(os.path.join(DATA_DIR, path), encoding="utf-8") as f:
        return json.load(f)

# ---- 把 8 个柜子的文件读进来，转成"按 key 索引的字典"（= 抄到手边，方便查）----
CLAIMS     = {c["claim_id"]: c for c in _load("claims.json")}
MEMBERS    = {m["member_id"]: m for m in _load("members.json")}
POLICIES   = {p["policy_id"]: p for p in _load("policies.json")}
HOSPITALS  = {h["hospital_id"]: h for h in _load("hospitals.json")}
PROCEDURES = {p["code"]: p for p in _load("procedures.json")}

# 预授权：用 (member_id, procedure_code) 两个键一起查
PREAUTHS = {(p["member_id"], p["procedure_code"]): p
            for p in _load("preauthorisations.json")}

# 所需材料：一个项目可能要求多份材料
REQUIRED_DOCS = {}
for r in _load("required_documents.json"):
    REQUIRED_DOCS.setdefault(r["procedure_code"], []).append(r["document"])

# 已决理赔：查重需要遍历比对，保持 list
DECIDED_CLAIMS = _load("decided_claims.json")


# ==================== 工具 1：查理赔单（入口）====================
def get_claim(claim_id: str) -> str:
    """WHAT    按单号取一张理赔单，返回它的身份 + 结构
    INPUT    claim_id，如 "CLM-8842"
    RETURNS  member_id / hospital_id / date_of_service / narrative / documents / lines
    FAILS    单号不存在 -> "ERROR: no claim ..."
    WHY      入口：后面所有查询都要靠它给出的 member_id、hospital_id、code 往下走
    """
    c = CLAIMS.get(claim_id)
    if not c:
        return f"ERROR: no claim {claim_id}"
    return (f"claim_id={c['claim_id']} "
            f"member_id={c['member_id']} "
            f"hospital_id={c['hospital_id']} "
            f"date_of_service={c['date_of_service']} "
            f"narrative={c['narrative']!r} "      # !r 保证自由文本不破坏格式
            f"documents={c['documents']} "
            f"lines={c['lines']}")


# ==================== 工具 2：查会员 ====================
def lookup_member(member_id: str) -> str:
    """WHAT    查一个会员，只返回影响决策的字段：他的保单号
    INPUT    member_id，如 "M-2214"
    RETURNS  member_id / policy_id
    FAILS    会员不存在 -> "ERROR: no member ..."
    WHY      会员行的 name、join_date 不参与决策，故意不返回（省 token + 避免误导）
    """
    m = MEMBERS.get(member_id)
    if not m:
        return f"ERROR: no member {member_id}"
    return f"member_id={m['member_id']} policy_id={m['policy_id']}"


# ==================== 工具 3：查保单 ====================
def lookup_policy(policy_id: str) -> str:
    """WHAT    查一张保单，返回判定赔付所需的所有条款
    INPUT    policy_id，如 "POL-3310"
    RETURNS  status / 起止日 / annual_limit / used_to_date / exclusions
    FAILS    保单不存在 -> "ERROR: no policy ..."
    WHY      赔付要看：保单是否 active、日期是否在保障期内、额度够不够、是否被排除。
             注意：剩余额度 = annual_limit - used_to_date，要模型自己算。
    """
    p = POLICIES.get(policy_id)
    if not p:
        return f"ERROR: no policy {policy_id}"
    return (f"policy_id={p['policy_id']} "
            f"status={p['status']} "
            f"start_date={p['start_date']} "
            f"end_date={p['end_date']} "
            f"annual_limit={p['annual_limit']} "
            f"used_to_date={p['used_to_date']} "
            f"exclusions={p['exclusions']}")


# ==================== 工具 4：查医院 ====================
def get_hospital_status(hospital_id: str) -> str:
    """WHAT    查一家医院在不在理赔网络内
    INPUT    hospital_id，如 "H-114"
    RETURNS  hospital_id / panel（true=网络内，false=网络外）
    FAILS    医院不存在 -> "ERROR: no hospital ..."
    WHY      panel=false 会改变赔付结果，必须查。
    """
    h = HOSPITALS.get(hospital_id)
    if not h:
        return f"ERROR: no hospital {hospital_id}"
    return f"hospital_id={h['hospital_id']} panel={h['panel']}"


# ==================== 工具 5：查治疗项目 ====================
def check_procedure(code: str) -> str:
    """WHAT    查一个治疗项目是什么、要不要预授权
    INPUT    code，如 "62480"
    RETURNS  code / description / requires_preauth
    FAILS    项目码不存在 -> "ERROR: no procedure ..."
    WHY      requires_preauth 是"分支开关"：true 就要去查预授权，false 不用。
             这正是"不同的理赔单，要查的步数不一样"的原因。
    """
    p = PROCEDURES.get(code)
    if not p:
        return f"ERROR: no procedure {code}"
    return (f"code={p['code']} "
            f"description={p['description']} "
            f"requires_preauth={p['requires_preauth']}")


# ==================== 工具 6：查预授权 ====================
def get_preauthorisation(member_id: str, procedure_code: str) -> str:
    """WHAT    查"某会员对某项目"有没有预授权，以及它的有效期
    INPUT    member_id + procedure_code（两个都要对上）
    RETURNS  preauth_id / valid_from / valid_to
    FAILS    没查到 -> "ERROR: no preauthorisation ..."
    WHY      预授权属于"某个人 + 某个项目"的组合，缺一不可。
             关键：只看"有没有"不够，还要看 valid_to 过期没过期（过期 = 没有）。
    """
    pa = PREAUTHS.get((member_id, procedure_code))
    if not pa:
        return f"ERROR: no preauthorisation for {member_id} / {procedure_code}"
    return (f"preauth_id={pa['preauth_id']} "
            f"member_id={pa['member_id']} "
            f"procedure_code={pa['procedure_code']} "
            f"valid_from={pa['valid_from']} "
            f"valid_to={pa['valid_to']}")


# ==================== 工具 7：查所需材料 ====================
def check_documents(procedure_code: str) -> str:
    """WHAT    查某个治疗项目需要附哪些材料
    INPUT    procedure_code，如 "45378"
    RETURNS  该项目要求提交的材料清单
    FAILS    该项目没特殊材料要求 -> "no documents required ..."
    WHY      材料缺失 = 向客户"索取"，不是"拒赔"。工具只负责告诉"需要什么"，
             由模型去对比理赔单实际附了什么、缺不缺。
    """
    docs = REQUIRED_DOCS.get(procedure_code)
    if not docs:
        return f"no documents required for procedure {procedure_code}"
    return f"procedure_code={procedure_code} required_documents={docs}"


# ==================== 工具 8：查重复理赔 ====================
def check_duplicate(claim_id: str) -> str:
    """WHAT    查这张理赔单是不是"已经判过的一次就诊"又重交了一遍
    INPUT    claim_id，如 "CLM-8933"
    RETURNS  是重复 -> 之前的单号 + 当时的决定；不是 -> "no duplicate"
    WHY      重复不是看 claim_id（重交会有新 id），而是看四个事实是否全对上：
             同会员 + 同医院 + 同就诊日期 + 同样的 lines。缺一个都不算重复。
    """
    c = CLAIMS.get(claim_id)
    if not c:
        return f"ERROR: no claim {claim_id}"
    for d in DECIDED_CLAIMS:
        if (d["member_id"] == c["member_id"]
                and d["hospital_id"] == c["hospital_id"]
                and d["date_of_service"] == c["date_of_service"]
                and d["lines"] == c["lines"]):
            return (f"DUPLICATE of {d['claim_id']}: already decided {d['decision']} "
                    f"on {d['decided_on']}")
    return f"no duplicate found for {claim_id}"


# ==================== 工具注册表 ====================
# 模型说"调用 get_claim"，代码就拿这个名字来这里找对应的函数。
TOOLS = {
    "get_claim": get_claim,
    "lookup_member": lookup_member,
    "lookup_policy": lookup_policy,
    "get_hospital_status": get_hospital_status,
    "check_procedure": check_procedure,
    "get_preauthorisation": get_preauthorisation,
    "check_documents": check_documents,
    "check_duplicate": check_duplicate,
}


if __name__ == "__main__":
    # 自测：跑 8 个工具，挑了几个"有代表性"的输入，看输出对不对
    print("--- 工具 1~4 ---")
    print(get_claim("CLM-8842"))
    print(lookup_member("M-2214"))
    print(lookup_policy("POL-3310"))
    print(get_hospital_status("H-114"))

    print("\n--- 工具 5 check_procedure ---")
    print(check_procedure("62480"))   # 腰椎：需要预授权
    print(check_procedure("47120"))   # 阑尾：不需要

    print("\n--- 工具 6 get_preauthorisation ---")
    print(get_preauthorisation("M-2214", "62480"))   # 有效期内
    print(get_preauthorisation("M-6118", "29881"))   # 已过期的那个（CLM-8894）

    print("\n--- 工具 7 check_documents ---")
    print(check_documents("45378"))   # 肠镜：需要 itemised_bill
    print(check_documents("47120"))   # 阑尾：无特殊要求

    print("\n--- 工具 8 check_duplicate ---")
    print(check_duplicate("CLM-8933"))   # 应该是重复（对照 CLM-8710）
    print(check_duplicate("CLM-8842"))   # 应该不是重复
