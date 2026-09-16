# Development candidate B (not released)

Retained six-trial preflight after adding explicit exclusion:string syntax.
CLM-8842, CLM-8888 and CLM-16404 used JSON null in nested Action dictionaries, rejected by
Python-only literal_eval. Candidate C uses a restricted AST transformation for
exact JSON constant names null/true/false only. This is a documented transport
syntax extension common to v1/v2; it does not normalize status values, repair
missing evidence, execute variables or forgive fabricated observations. Original
candidate-B results remain unchanged. A new preflight is required.
