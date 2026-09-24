---
name: future-directions
description: Identify evidence-based future opportunities, limitations, risks, and evolution paths.
---

# Task

Identify realistic future directions that follow from the current implementation, including limitations, technical debt, scalability or maintainability concerns, missing capabilities, risks, and evidence-based evolution opportunities.

# Scope

Start from the current repository as implemented. Separate observed constraints and gaps from proposed improvements. Future directions may be technical, operational, or capability-oriented, but must remain grounded in the current implementation and repository analysis. The resulting document should explain the rationale for each direction without exposing the investigation trail or internal confidence classifications.

# Available Tools

The runtime provides these read-only repository tools:

- `list_files` — locate implementation areas relevant to an identified limitation or opportunity.
- `read_file` — inspect concrete mechanisms, configuration, tests, and constraints.
- `search_repository` — locate targeted markers, TODOs, configuration, dependencies, or implementation evidence.

Use tools for targeted verification when a recommendation depends on source-level detail.

# Available Programmatic Resources

The harness performs deterministic repository analysis before the agent starts and supplies phase-specific intelligence covering architecture, dependencies, topology, integrations, configuration, tests, symbols, markers, and relationships relevant to identifying constraints and opportunities.

No `phase_intelligence.py` or deterministic collector is an agent resource. Collectors execute upstream and their resulting evidence is injected into the agent context.

# Available Scripts and Python Resources

No phase-specific Python script or executable is directly exposed as an agent tool for this phase. Harness analysis scripts are upstream deterministic resources.

# Available Skills

- `.agents/skills/future-directions/SKILL.md` — detailed Future Directions methodology, evidence requirements, verification gate, and documentation structure.

The skill supplies methodology; this file defines the agent's task, scope, resources, and operating contract.

# Required Investigation Focus

Use this sequence:

phase intelligence → identify current constraints/gaps → inspect material mechanisms → assess impact → formulate evidence-based direction → distinguish observation from recommendation → document

Prioritize limitations that materially affect maintainability, scalability, reliability, security, operability, extensibility, or future capability. Check important recommendations against concrete implementation evidence.

# Reasoning Boundary

Separate observed limitations from proposed improvements. Do not present speculative product plans, developer intent, market assumptions, or generic technology roadmaps as established facts. Recommendations must follow from evidence in the current implementation and should be qualified when evidence is incomplete.

# Output Responsibility

Produce complete professional Future Directions documentation according to the phase skill, clearly distinguishing current-state evidence, limitations, and proposed evolution.
