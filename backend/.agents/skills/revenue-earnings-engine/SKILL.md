---
name: revenue-earnings-engine
description: Historical revenue, profitability and earnings-quality analysis from SEC Company Facts evidence.
---

# Method

Use the deterministic financial evidence as the starting point.

For annual observations:
- prefer form 10-K;
- prefer annual observations (fp=FY or equivalent annual evidence);
- where duplicate frame/end observations exist, prefer the latest filed observation;
- preserve the original fiscal year, end date, frame, accession and filing date when material.

Revenue:
- use the collector's selected revenue concept first;
- if several revenue concepts exist, explain which reported series was used and why;
- calculate YoY growth only from verified comparable annual values;
- calculate multi-year CAGR only when endpoints and periods are comparable.

Margins:
- gross margin = gross profit / revenue;
- operating margin = operating income / revenue;
- net margin = net income / revenue;
- do not calculate a margin if the numerator or denominator is missing or not comparable.

Earnings quality:
- compare net-income growth with diluted EPS growth;
- use diluted weighted-average shares when available to distinguish earnings growth from share-count effects;
- do not infer a buyback effect unless the evidence supports it.

Tool discipline:
- query_financial_facts is for precise fact retrieval;
- query_financial_statement is for a coherent statement block;
- inspect_json_structure/search_json/read_json_value/query_json are fallback primitives for unfamiliar or ambiguous JSON;
- a large raw concept object is not a useful default query when a bounded fact query can answer the question.

Output should distinguish verified observations, calculations derived from verified observations, analytical interpretation, and unknowns.
