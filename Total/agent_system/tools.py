"""Run-local adaptation of Chen's tools as extended by Lu for D2(b).
Source fingerprints and integration changes are documented in docs/STEP1_INTEGRATION_EN.md.
"""
import json
from pathlib import Path


class ClaimTools:
    def __init__(self, data_dir, version="v2"):
        if version not in {"v1", "v2"}:
            raise ValueError("version must be v1 or v2")
        self.DATA_DIR = Path(data_dir)
        self.PREAUTH_VERSION = version
        def load(name):
            return json.loads((self.DATA_DIR / (name + ".json")).read_text(encoding="utf-8"))
        self.CLAIMS = {r["claim_id"]: r for r in load("claims")}
        self.MEMBERS = {r["member_id"]: r for r in load("members")}
        self.POLICIES = {r["policy_id"]: r for r in load("policies")}
        self.HOSPITALS = {r["hospital_id"]: r for r in load("hospitals")}
        self.PROCEDURES = {r["code"]: r for r in load("procedures")}
        self.PREAUTHS = {(r["member_id"], r["procedure_code"]): r for r in load("preauthorisations")}
        self.REQUIRED_DOCS = {}
        for r in load("required_documents"):
            self.REQUIRED_DOCS.setdefault(r["procedure_code"], []).append(r["document"])
        self.DECIDED_CLAIMS = load("decided_claims")

    def registry(self):
        names = ("get_claim", "lookup_member", "lookup_policy", "get_hospital_status",
                 "check_procedure", "get_preauthorisation", "check_documents", "check_duplicate")
        return {name: getattr(self, name) for name in names}

    def get_claim(self, claim_id: str) -> str:
        """WHAT    fetch one claim by id; return its identity + structure
        INPUT    claim_id, e.g. "CLM-8842"
        RETURNS  member_id / hospital_id / date_of_service / narrative / documents / lines
        FAILS    unknown id -> "ERROR: no claim ..."
        WHY      the entry point: every later query needs the member_id / hospital_id / codes it returns
        """
        c = self.CLAIMS.get(claim_id)
        if not c:
            return f'ERROR: no claim {claim_id}'
        return f"claim_id={c['claim_id']} member_id={c['member_id']} hospital_id={c['hospital_id']} date_of_service={c['date_of_service']} narrative={c['narrative']!r} documents={c['documents']} lines={c['lines']}"

    def lookup_member(self, member_id: str) -> str:
        """WHAT    look up a member; return only the decision-relevant field: their policy_id
        INPUT    member_id, e.g. "M-2214"
        RETURNS  member_id / policy_id
        FAILS    unknown member -> "ERROR: no member ..."
        WHY      the member row's name / join_date do not affect the decision, so they are
                 deliberately not returned (fewer tokens + no misleading information)
        """
        m = self.MEMBERS.get(member_id)
        if not m:
            return f'ERROR: no member {member_id}'
        return f"member_id={m['member_id']} policy_id={m['policy_id']}"

    def lookup_policy(self, policy_id: str, date_of_service: str=None, claim_total: int=None) -> str:
        """Return policy facts, or the safe D2(b) policy decision contract.

        Supplying both date_of_service and claim_total selects the poka-yoke contract:
        code computes coverage dates and annual-limit status instead of asking a model
        to perform the comparison and arithmetic.
        """
        p = self.POLICIES.get(policy_id)
        if not p:
            return f'ERROR: no policy {policy_id}'
        if date_of_service is not None or claim_total is not None:
            if date_of_service is None or claim_total is None:
                return 'ERROR: date_of_service and claim_total must be supplied together'
            if not isinstance(claim_total, (int, float)) or isinstance(claim_total, bool) or claim_total < 0:
                return 'ERROR: claim_total must be a non-negative number'
            remaining = p['annual_limit'] - p['used_to_date']
            covered = p['start_date'] <= date_of_service <= p['end_date']
            limit_status = 'within_limit' if claim_total <= remaining else 'exceeded'
            return f"policy_id={p['policy_id']} policy_status={p['status']} start_date={p['start_date']} end_date={p['end_date']} service_date_covered={covered} remaining_annual_limit={remaining} annual_limit_status={limit_status} exclusions={p['exclusions']}"
        return f"policy_id={p['policy_id']} status={p['status']} start_date={p['start_date']} end_date={p['end_date']} annual_limit={p['annual_limit']} used_to_date={p['used_to_date']} exclusions={p['exclusions']}"

    def get_hospital_status(self, hospital_id: str) -> str:
        """WHAT    check whether a hospital is in the claims network
        INPUT    hospital_id, e.g. "H-114"
        RETURNS  hospital_id / panel (true = in-network, false = out-of-network)
        FAILS    unknown hospital -> "ERROR: no hospital ..."
        WHY      panel=false must be recorded; it does not change the decision.
        """
        h = self.HOSPITALS.get(hospital_id)
        if not h:
            return f'ERROR: no hospital {hospital_id}'
        return f"hospital_id={h['hospital_id']} panel={h['panel']}"

    def check_procedure(self, code: str) -> str:
        """WHAT    check what a procedure is and whether it needs pre-authorisation
        INPUT    code, e.g. "62480"
        RETURNS  code / description / requires_preauth
        FAILS    unknown code -> "ERROR: no procedure ..."
        WHY      requires_preauth is the "branch switch": true -> go check the pre-auth, false -> skip.
                 This is exactly why different claims need a different number of steps.
        """
        p = self.PROCEDURES.get(code)
        if not p:
            return f'ERROR: no procedure {code}'
        return f"code={p['code']} description={p['description']} requires_preauth={p['requires_preauth']}"

    def get_preauthorisation(self, member_id: str, procedure_code: str, date_of_service: str=None) -> str:
        """Return the D2(b) v1 or v2 pre-authorisation contract.

        v1 returns raw dates for the model to interpret. v2 requires date_of_service
        and returns a compact, deterministic status so an expired authorisation cannot
        be mistaken for a valid one.
        """
        pa = self.PREAUTHS.get((member_id, procedure_code))
        if self.PREAUTH_VERSION == 'v1':
            if not pa:
                return f'ERROR: no preauthorisation for {member_id} / {procedure_code}'
            return f"preauth_id={pa['preauth_id']} member_id={pa['member_id']} procedure_code={pa['procedure_code']} valid_from={pa['valid_from']} valid_to={pa['valid_to']}"
        if not date_of_service:
            return 'ERROR: date_of_service is required for v2 preauthorisation lookup'
        if not pa:
            return 'status=not_found valid_on_service_date=False'
        if pa['valid_from'] <= date_of_service <= pa['valid_to']:
            return f"status=valid valid_on_service_date=True preauth_id={pa['preauth_id']} valid_from={pa['valid_from']} valid_to={pa['valid_to']}"
        return (f"status=expired_before_service valid_on_service_date=False "
                f"preauth_id={pa['preauth_id']} valid_to={pa['valid_to']}")

    def check_documents(self, procedure_code: str) -> str:
        """WHAT    check which documents a procedure requires
        INPUT    procedure_code, e.g. "45378"
        RETURNS  the list of documents required for that procedure
        FAILS    no special requirement -> "no documents required ..."
        WHY      a missing document is an "ask" to the customer, not a refuse. The tool only
                 reports what is needed; the model compares it against what the claim attached.
        """
        docs = self.REQUIRED_DOCS.get(procedure_code)
        if not docs:
            return f'no documents required for procedure {procedure_code}'
        return f'procedure_code={procedure_code} required_documents={docs}'

    def check_duplicate(self, claim_id: str) -> str:
        """WHAT    check whether this claim re-submits a visit that was already decided
        INPUT    claim_id, e.g. "CLM-8933"
        RETURNS  if duplicate -> the earlier claim id + its decision; else -> "no duplicate"
        WHY      a duplicate is not the same claim_id (a resubmission gets a new id) — it is
                 four matching facts: same member + same hospital + same service date + same lines.
        """
        c = self.CLAIMS.get(claim_id)
        if not c:
            return f'ERROR: no claim {claim_id}'
        for d in self.DECIDED_CLAIMS:
            if d['member_id'] == c['member_id'] and d['hospital_id'] == c['hospital_id'] and (d['date_of_service'] == c['date_of_service']) and (d['lines'] == c['lines']):
                return f"DUPLICATE of {d['claim_id']}: already decided {d['decision']} on {d['decided_on']}"
        # Near matches make the four-fact comparison auditable without exposing
        # unrelated history. A near match never changes the duplicate decision.
        fields = ('member_id', 'hospital_id', 'date_of_service', 'lines')
        near = [d for d in self.DECIDED_CLAIMS
                if sum(d[k] == c[k] for k in fields) >= 2]
        details = '; '.join(
            f"prior {d['claim_id']}: " + ', '.join(f'{k}={d[k]!r}' for k in fields)
            for d in near)
        return f'no duplicate found for {claim_id}' + (f'; comparison evidence: {details}' if details else '')
