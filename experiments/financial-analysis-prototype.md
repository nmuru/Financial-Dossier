# Financial Analysis Prototype

This experiment keeps the ReverseEngineer-SDLC application flow and adds a financial-analysis phase without replacing the agent runner.

The prototype uses:
- the existing deterministic repository intelligence collector;
- a second deterministic SEC Company Facts collector;
- the existing semantic research stage;
- bounded generic JSON navigation tools;
- bounded financial fact/statement retrieval;
- a financial phase agent and skill.

The intended evidence flow is:

RAW companyfacts.json
-> deterministic source intelligence
-> deterministic annual fact extraction
-> semantic research brief
-> targeted verification tools
-> financial analysis

The generic JSON tools use standard JSON Pointer paths. They inspect structure before reading large values and allow coherent blocks up to about 50k-token scale when the selected block itself is appropriate.

Financial retrieval is deliberately bounded and evidence-oriented. It selects 10-K annual observations and preserves filing metadata. It does not perform analyst interpretation.

This is a working prototype, not a mock UI. It is intentionally narrow: the first supported financial phase is Revenue & Earnings Engine.
