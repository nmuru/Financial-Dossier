---
name: software-requirements
description: Reconstruct software requirements from implemented behavior and repository evidence.
---

# Task

Reconstruct functional and non-functional software requirements represented by the existing implementation. Capture externally observable behavior, interfaces, data, security, operational constraints, and other demonstrable requirements where evidence permits.

# Scope

Focus on what the software demonstrably must do or constrain in its current implementation. Separate implemented requirements from inferred intent and from generic expectations for the detected product or technology.

# Available Tools

The runtime provides these read-only repository tools:

- `list_files` — locate relevant requirements-bearing implementation areas when targeted discovery is required.
- `read_file` — inspect source, routes, APIs, configuration, integrations, tests, and other concrete evidence.
- `search_repository` — locate targeted requirements signals, symbols, configuration keys, validation, and interface evidence.

Use tools only for material ambiguity, missing passages, or important verification.

# Available Programmatic Resources

The harness performs deterministic repository analysis before the agent starts and supplies phase-specific software-requirements intelligence covering entry points, routes and APIs, page/component structure, actions, configuration, environment variables, integrations, symbols, tests, dependencies, and relationships.

No `phase_intelligence.py` or deterministic collector is an agent resource. Collectors execute upstream and their resulting evidence is injected into the agent context.

# Available Scripts and Python Resources

No phase-specific Python script or executable is directly exposed as an agent tool for this phase. Harness analysis scripts are upstream deterministic resources.

# Available Skills

- `.agents/skills/software-requirements/SKILL.md` — detailed Software Requirements methodology, evidence requirements, verification gate, and documentation structure.

The skill supplies methodology; this file defines the agent's task, scope, resources, and operating contract.

# Required Investigation Focus

Use this sequence:

phase intelligence → identify requirement candidates → connect behavior/evidence → inspect representative implementation → trace interfaces and constraints → cross-check tests/configuration → distinguish fact from inferred intent → document

Prioritize functional behavior, externally visible interfaces, data requirements, validation, security controls, operational constraints, integrations, and non-functional characteristics that are actually evidenced.

# Reasoning Boundary

Requirements describe what the implemented system does or demonstrably constrains. Separate verified implementation facts from inferred requirements and unknown intended behavior. Do not invent requirements simply because they are conventional for the detected stack or product category.

# Output Responsibility

Produce complete professional Software Requirements documentation according to the phase skill. State the resulting requirements directly and with sufficient detail for specification-driven development. Use repository analysis internally to prevent invention and resolve contradictions, but do not expose evidence trails or certainty/uncertainty classifications in the normal requirements document.
