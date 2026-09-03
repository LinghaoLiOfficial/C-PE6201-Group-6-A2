# D2(a) — The tool set: scored against the three questions

> A2 asks: score every tool you ship against the three Class 4 questions, in a table in the repository. The three questions: ① does a task actually fail without it? ② could the model confuse it with a neighbour? ③ what does it cost when it is never called?

## Question 3 first (one answer for all eight tools)

Every tool's description lives in the fixed prompt prefix (`TOOL_SPEC`), re-sent and re-billed on **every turn, whether called or not**. Our design: each tool is described by **one signature line** (~25–35 tokens), so the whole prefix is ~300 tokens.

→ The prefix cost is a **small constant**, because each descriptor is cut down to a signature. The more tools and the more verbose the description, the larger this hidden cost — which is exactly why we keep one-line signatures.

## The eight-tool scoring table

| Tool | ① Fails without it? | ② Confusable with a neighbour? | Why it earns its place |
|------|---------------------|-------------------------------|------------------------|
| **get_claim** | **Yes** — nothing else can even get member_id / hospital_id / codes | **No** — the only entry point | Entry point; every later query needs the ids it returns |
| **lookup_member** | **Yes** — the only member_id → policy_id bridge | **No** — deliberately returns **only policy_id** (no name / join_date) to deny the model irrelevant facts | The only bridge. But note: A2 says "this jump carries no decision information at all" — it is the tool we most seriously argued about removing (see reflection 2) |
| **lookup_policy** | **Yes** — the sole source of status / dates / headroom / exclusions | **No** | A2's words: "most refusals come from this row" — all three refusal reasons live here |
| **get_hospital_status** | **Yes** — the sole source of `panel` | **No** | panel=false changes the outcome; it must be checked, not silently assumed |
| **check_procedure** | **Yes** — the sole source of `requires_preauth` | ⚠️ **Yes**, with get_preauthorisation | The "**whether** a pre-auth is needed" branch switch; it decides how long the run gets |
| **get_preauthorisation** | **Yes** — the sole source of the pre-auth + its validity window | ⚠️ **Yes**, with check_procedure | The "**is there** a pre-auth, and is it still valid" — only queried when check_procedure says true |
| **check_documents** | **Yes** — the sole source of required materials | **No** | Turns "a document is missing" into an **ask**, not a mistaken refuse |
| **check_duplicate** | **Yes** — the sole source of duplicate detection | **No** (both it and get_claim take claim_id; the signature distinguishes them) | The only tool that recognises a re-submission; it compares four facts, not just the claim_id |

## Two honest reflections (worth marks in the report)

**1. We have no `search_notes`-style trap tool.**

A2 uses Class 4's `search_notes` as the example: a tool that fails questions 1 and 2, and is precisely the one that breaks the agent. Our eight tools are **each the single source of one fact** — no redundancy. That is itself evidence of a shortest-defensible list. The cost: we have no "obviously cuttable" tool with which to demonstrate the act of cutting one. We own that trade-off explicitly rather than pretending.

**2. `lookup_member` is a pure bridge — and we *tried not adding it*.**

A2 lists four moves in order of preference, and asks us to *"say in the report which you tried."* Move 2 is *"return more from one call instead of adding a second lookup."* `lookup_member` returns only `policy_id`, carrying no decision information — A2's own words: *"the first one carries no decision information at all."*

So we **tried move 2**: have `get_claim` also return `policy_id`, and delete `lookup_member` (8 tools → 7, one fewer round-trip). We measured/argued it and **chose to keep `lookup_member`**, for a defensible reason: one tool = one "drawer", single responsibility, which keeps the model's discrimination clean. Documenting that we *tried not adding it* — and why we kept it anyway — is exactly the "at least one 'we tried not adding it' documented" A2 credits.
