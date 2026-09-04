"""
A2 Problem A — the tool layer (deliverable D2(a)), owned by person 1.
8 tools = 8 small "open-the-drawer" functions. All complete.
"""
import json
import os

# ---- data location (A2_DATA_DIR makes the shared code portable; legacy path stays as fallback) ----
DATA_DIR = os.environ.get(
    "A2_DATA_DIR",
    r"C:\Users\86178\Desktop\NTU-school materials\6201\Assignments\A2\A2_reference_data_extracted\A2_reference_data\data_A",
)

# D2(b): v1 is retained only for the measured descriptor comparison. The submitted
# final interface defaults to v2, which computes service-date validity in code.
PREAUTH_VERSION = os.environ.get("PREAUTH_VERSION", "v2")

def set_preauth_version(version: str):
    """Select the D2(b) pre-authorisation interface for a controlled v1/v2 run."""
    global PREAUTH_VERSION
    if version not in {"v1", "v2"}:
        raise ValueError("PREAUTH_VERSION must be 'v1' or 'v2'")
    PREAUTH_VERSION = version

def _load(path: str):
    """Read one JSON file and return its Python data."""
    with open(os.path.join(DATA_DIR, path), encoding="utf-8") as f:
        return json.load(f)

# ---- load the 8 "drawers" into key-indexed dicts (copied to hand for fast lookup) ----
CLAIMS     = {c["claim_id"]: c for c in _load("claims.json")}
MEMBERS    = {m["member_id"]: m for m in _load("members.json")}
POLICIES   = {p["policy_id"]: p for p in _load("policies.json")}
HOSPITALS  = {h["hospital_id"]: h for h in _load("hospitals.json")}
PROCEDURES = {p["code"]: p for p in _load("procedures.json")}

# pre-authorisation: looked up by the (member_id, procedure_code) pair
PREAUTHS = {(p["member_id"], p["procedure_code"]): p
            for p in _load("preauthorisations.json")}

# required documents: one procedure may require several documents
REQUIRED_DOCS = {}
for r in _load("required_documents.json"):
    REQUIRED_DOCS.setdefault(r["procedure_code"], []).append(r["document"])

# decided claims: duplicate detection needs a full scan, keep as a list
DECIDED_CLAIMS = _load("decided_claims.json")


# ==================== tool 1: read the claim (entry point) ====================
def get_claim(claim_id: str) -> str:
    """WHAT    fetch one claim by id; return its identity + structure
    INPUT    claim_id, e.g. "CLM-8842"
    RETURNS  member_id / hospital_id / date_of_service / narrative / documents / lines
    FAILS    unknown id -> "ERROR: no claim ..."
    WHY      the entry point: every later query needs the member_id / hospital_id / codes it returns
    """
    c = CLAIMS.get(claim_id)
    if not c:
        return f"ERROR: no claim {claim_id}"
    return (f"claim_id={c['claim_id']} "
            f"member_id={c['member_id']} "
            f"hospital_id={c['hospital_id']} "
            f"date_of_service={c['date_of_service']} "
            f"narrative={c['narrative']!r} "      # !r keeps free text from breaking the format
            f"documents={c['documents']} "
            f"lines={c['lines']}")


# ==================== tool 2: look up a member ====================
def lookup_member(member_id: str) -> str:
    """WHAT    look up a member; return only the decision-relevant field: their policy_id
    INPUT    member_id, e.g. "M-2214"
    RETURNS  member_id / policy_id
    FAILS    unknown member -> "ERROR: no member ..."
    WHY      the member row's name / join_date do not affect the decision, so they are
             deliberately not returned (fewer tokens + no misleading information)
    """
    m = MEMBERS.get(member_id)
    if not m:
        return f"ERROR: no member {member_id}"
    return f"member_id={m['member_id']} policy_id={m['policy_id']}"


# ==================== tool 3: look up a policy ====================
def lookup_policy(policy_id: str, date_of_service: str = None, claim_total: int = None) -> str:
    """Return policy facts, or the safe D2(b) policy decision contract.

    Supplying both date_of_service and claim_total selects the poka-yoke contract:
    code computes coverage dates and annual-limit status instead of asking a model
    to perform the comparison and arithmetic.
    """
    p = POLICIES.get(policy_id)
    if not p:
        return f"ERROR: no policy {policy_id}"
    if date_of_service is not None or claim_total is not None:
        if date_of_service is None or claim_total is None:
            return "ERROR: date_of_service and claim_total must be supplied together"
        if not isinstance(claim_total, (int, float)) or isinstance(claim_total, bool) or claim_total < 0:
            return "ERROR: claim_total must be a non-negative number"
        remaining = p["annual_limit"] - p["used_to_date"]
        covered = p["start_date"] <= date_of_service <= p["end_date"]
        limit_status = "within_limit" if claim_total <= remaining else "exceeded"
        return (f"policy_id={p['policy_id']} "
                f"policy_status={p['status']} "
                f"service_date_covered={covered} "
                f"remaining_annual_limit={remaining} "
                f"annual_limit_status={limit_status} "
                f"exclusions={p['exclusions']}")
    return (f"policy_id={p['policy_id']} "
            f"status={p['status']} "
            f"start_date={p['start_date']} "
            f"end_date={p['end_date']} "
            f"annual_limit={p['annual_limit']} "
            f"used_to_date={p['used_to_date']} "
            f"exclusions={p['exclusions']}")


# ==================== tool 4: hospital network status ====================
def get_hospital_status(hospital_id: str) -> str:
    """WHAT    check whether a hospital is in the claims network
    INPUT    hospital_id, e.g. "H-114"
    RETURNS  hospital_id / panel (true = in-network, false = out-of-network)
    FAILS    unknown hospital -> "ERROR: no hospital ..."
    WHY      panel=false changes the outcome, so it must be checked.
    """
    h = HOSPITALS.get(hospital_id)
    if not h:
        return f"ERROR: no hospital {hospital_id}"
    return f"hospital_id={h['hospital_id']} panel={h['panel']}"


# ==================== tool 5: check a procedure ====================
def check_procedure(code: str) -> str:
    """WHAT    check what a procedure is and whether it needs pre-authorisation
    INPUT    code, e.g. "62480"
    RETURNS  code / description / requires_preauth
    FAILS    unknown code -> "ERROR: no procedure ..."
    WHY      requires_preauth is the "branch switch": true -> go check the pre-auth, false -> skip.
             This is exactly why different claims need a different number of steps.
    """
    p = PROCEDURES.get(code)
    if not p:
        return f"ERROR: no procedure {code}"
    return (f"code={p['code']} "
            f"description={p['description']} "
            f"requires_preauth={p['requires_preauth']}")


# ==================== tool 6: check a pre-authorisation ====================
def get_preauthorisation(member_id: str, procedure_code: str, date_of_service: str = None) -> str:
    """Return the D2(b) v1 or v2 pre-authorisation contract.

    v1 returns raw dates for the model to interpret. v2 requires date_of_service
    and returns a compact, deterministic status so an expired authorisation cannot
    be mistaken for a valid one.
    """
    pa = PREAUTHS.get((member_id, procedure_code))
    if PREAUTH_VERSION == "v1":
        if not pa:
            return f"ERROR: no preauthorisation for {member_id} / {procedure_code}"
        return (f"preauth_id={pa['preauth_id']} "
                f"member_id={pa['member_id']} "
                f"procedure_code={pa['procedure_code']} "
                f"valid_from={pa['valid_from']} "
                f"valid_to={pa['valid_to']}")

    if not date_of_service:
        return "ERROR: date_of_service is required for v2 preauthorisation lookup"
    if not pa:
        return "status=not_found valid_on_service_date=False"
    if pa["valid_from"] <= date_of_service <= pa["valid_to"]:
        return (f"status=valid valid_on_service_date=True "
                f"preauth_id={pa['preauth_id']}")
    return "status=expired_before_service valid_on_service_date=False"


# ==================== tool 7: check required documents ====================
def check_documents(procedure_code: str) -> str:
    """WHAT    check which documents a procedure requires
    INPUT    procedure_code, e.g. "45378"
    RETURNS  the list of documents required for that procedure
    FAILS    no special requirement -> "no documents required ..."
    WHY      a missing document is an "ask" to the customer, not a refuse. The tool only
             reports what is needed; the model compares it against what the claim attached.
    """
    docs = REQUIRED_DOCS.get(procedure_code)
    if not docs:
        return f"no documents required for procedure {procedure_code}"
    return f"procedure_code={procedure_code} required_documents={docs}"


# ==================== tool 8: duplicate check ====================
def check_duplicate(claim_id: str) -> str:
    """WHAT    check whether this claim re-submits a visit that was already decided
    INPUT    claim_id, e.g. "CLM-8933"
    RETURNS  if duplicate -> the earlier claim id + its decision; else -> "no duplicate"
    WHY      a duplicate is not the same claim_id (a resubmission gets a new id) — it is
             four matching facts: same member + same hospital + same service date + same lines.
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


# ==================== tool registry ====================
# The model says "call get_claim"; the code looks the name up here to find the function.
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
    # self-test: run the 8 tools with a few representative inputs and check the outputs
    print("--- tools 1-4 ---")
    print(get_claim("CLM-8842"))
    print(lookup_member("M-2214"))
    print(lookup_policy("POL-3310"))
    print(get_hospital_status("H-114"))

    print("\n--- tool 5 check_procedure ---")
    print(check_procedure("62480"))   # lumbar: needs pre-auth
    print(check_procedure("47120"))   # appendix: does not

    print("\n--- tool 6 get_preauthorisation ---")
    print(get_preauthorisation("M-2214", "62480", "2026-09-02"))  # valid on CLM-8842 service date
    print(get_preauthorisation("M-6118", "29881", "2026-09-14"))  # expired on CLM-8894 service date

    print("\n--- tool 7 check_documents ---")
    print(check_documents("45378"))   # colonoscopy: needs itemised_bill
    print(check_documents("47120"))   # appendix: no special requirement

    print("\n--- tool 8 check_duplicate ---")
    print(check_duplicate("CLM-8933"))   # should be a duplicate (vs CLM-8710)
    print(check_duplicate("CLM-8842"))   # should not be a duplicate
