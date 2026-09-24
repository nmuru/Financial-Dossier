---
name: high-level-design
description: Reconstruct the system-level design, components, boundaries, and major interactions.
---

# Task

Reconstruct the implemented system at component and subsystem level. Explain major components, responsibilities, boundaries, interactions, external systems, important data or control flows, and cross-cutting concerns evidenced by the repository.

# Scope

Focus on system-level structure and relationships rather than detailed symbol-by-symbol implementation. Describe the architecture that exists, not an idealized architecture the software might have been intended to use.

# Available Tools

The runtime provides these read-only repository tools:

- `list_files` — locate relevant component or subsystem areas when targeted discovery is required.
- `read_file` — inspect concrete wiring, interfaces, configuration, and representative implementations.
- `search_repository` — locate targeted component names, routes, integrations, or relationship evidence.

Use tools selectively for material relationship or runtime verification.

# Available Programmatic Resources

The harness performs deterministic repository analysis before the agent starts and supplies phase-specific intelligence covering topology, entry points, module and dependency relationships, routes, integrations, configuration, symbols, state/cache evidence, and other high-level design signals.

No `phase_intelligence.py` or deterministic collector is an agent resource. Collectors execute upstream and their resulting evidence is injected into the agent context.

# Available Scripts and Python Resources

No phase-specific Python script or executable is directly exposed as an agent tool for this phase. Harness analysis scripts are upstream deterministic resources.

# Available Skills

- `.agents/skills/high-level-design/SKILL.md` — detailed High-Level Design methodology, evidence requirements, diagrams, verification gate, and documentation structure.

The skill supplies methodology; this file defines the agent's task, scope, resources, and operating contract.

# Required Investigation Focus

Use this sequence:

phase intelligence → identify components and boundaries → trace major relationships → inspect representative wiring → validate interactions/data flows → distinguish implemented structure from abstraction → document

Use the dependency/relationship graph to connect components rather than merely listing files. Verify important runtime relationships in source when intelligence alone cannot establish them.

# Reasoning Boundary

Prefer actual structure and runtime wiring over conventional architecture. Distinguish verified component relationships, reasonable abstractions, and unknowns. Do not invent layers, services, queues, databases, or boundaries that are not evidenced.

# Output Responsibility

Produce complete professional High-Level Design documentation according to the phase skill, including appropriate diagrams and relationships established through repository analysis. Do not expose the investigation trail or internal confidence classifications in the final document.
