IMPORTANT: This phase is a financial-analysis prototype. Treat companyfacts.json as financial evidence, not as application source code.

Analyze the supplied SEC Company Facts evidence as a financial-analysis phase.

The deterministic evidence package is the primary evidence index. Verify the supplied annual facts first; do not rediscover the entire JSON resource.

Use targeted financial retrieval when the evidence package is insufficient:
- query_financial_facts(concepts, years, form="10-K", annual=true)
- query_financial_statement(statement, years, form="10-K", annual=true)

Use generic JSON tools only for a specific ambiguity that the financial tools cannot resolve.

Do not invent financial facts or values. Do not forecast. Distinguish verified observations, calculations derived from verified observations, analytical interpretation, and unknowns.

Required output:
- Executive Summary
- Revenue trajectory with annual values and YoY growth
- Margin evolution where supported
- Net income vs diluted EPS/share-count discussion
- Data quality / evidence limitations
- Source/provenance notes
