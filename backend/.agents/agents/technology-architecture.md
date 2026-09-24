---
name: technology-architecture
description: Reconstruct the actual technology architecture and runtime topology from repository evidence.
---

# Task

Reconstruct the actual technology architecture and runtime topology. Explain technologies and versions where evidenced, runtime structure, major boundaries, integrations, state mechanisms, configuration, deployment evidence, and important data or control flows.

# Scope

Focus on the technology and runtime architecture that exists in the repository. Distinguish detected technologies from demonstrated use and architecture inferred from connected implementation evidence.

# Available Tools

The runtime provides these read-only repository tools:

- `list_files` — locate relevant architectural or deployment areas when targeted discovery is required.
- `read_file` — inspect manifests, configuration, wiring, deployment files, and representative source.
- `search_repository` — locate targeted technologies, versions, environment keys, integrations, or runtime markers.

Use tools only for material ambiguity or precision checks.

# Available Programmatic Resources

The harness performs deterministic repository analysis before the agent starts and supplies phase-specific intelligence covering technology/version evidence, entry points, module relationships, routes, configuration, environment provenance, integrations, symbols, dependencies, and topology.

No `phase_intelligence.py` or deterministic collector is an agent resource. Collectors execute upstream and their resulting evidence is injected into the agent context.

# Available Scripts and Python Resources

No phase-specific Python script or executable is directly exposed as an agent tool for this phase. Harness analysis scripts are upstream deterministic resources.

# Available Skills

- `.agents/skills/technology-architecture/SKILL.md` — detailed Technology Architecture methodology, evidence requirements, verification gate, and documentation structure.

The skill supplies methodology; this file defines the agent's task, scope, resources, and operating contract.

# Required Investigation Focus

Use this sequence:

phase intelligence → identify architectural evidence → trace runtime/topology relationships → inspect representative wiring → verify technology usage and configuration → cross-check integrations/deployment evidence → document

Prioritize actual runtime wiring, component boundaries, technology usage, state/configuration mechanisms, integrations, and deployment evidence. Prefer exact source and manifest evidence over generic framework expectations.

# Reasoning Boundary

Describe actual runtime wiring where established. Distinguish detected dependencies from demonstrated usage and architectural inference from verified structure. Do not introduce technologies, versions, deployment mechanisms, or architectural patterns merely because they are common for the detected stack.

# Output Responsibility

Produce complete professional Technology Architecture documentation according to the phase skill, clearly qualifying inferred or unsupported areas.
