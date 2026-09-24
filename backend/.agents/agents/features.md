---
name: features
description: Reconstruct implemented user-facing and system capabilities from repository evidence.
---

# Task

Reconstruct the concrete features and capabilities provided by the existing software, explaining what users or external systems can accomplish and what meaningful internal capabilities support those outcomes.

# Scope

Focus on implemented, externally meaningful functionality and coherent capability groupings. Separate a feature from an isolated file, component, dependency, helper, or framework facility.

# Available Tools

The runtime provides these read-only repository tools:

- `list_files` — locate relevant feature implementation areas when targeted discovery is required.
- `read_file` — inspect source, routes, components, actions, integrations, configuration, and tests.
- `search_repository` — locate targeted feature terms, symbols, routes, or implementation evidence.

Use tools for targeted verification and precision checks rather than repository-wide rediscovery.

# Available Programmatic Resources

The harness performs deterministic repository analysis before the agent starts and supplies phase-specific intelligence covering routes, API surfaces, pages, entry points, symbols, integrations, configuration, dependencies, tests, and relationship evidence.

No `phase_intelligence.py` or deterministic collector is an agent resource. Collectors execute upstream and their resulting evidence is injected into the agent context.

# Available Scripts and Python Resources

No phase-specific Python script or executable is directly exposed as an agent tool for this phase. Harness analysis scripts are upstream deterministic resources.

# Available Skills

- `.agents/skills/features/SKILL.md` — detailed Features methodology, evidence requirements, verification gate, and documentation structure.

The skill supplies methodology; this file defines the agent's task, scope, resources, and operating contract.

# Required Investigation Focus

Use this sequence:

phase intelligence → identify capability candidates → connect related evidence → inspect representative implementation → trace meaningful workflows → distinguish capability from incidental code → cross-check → document

Prioritize user-facing or externally meaningful behavior, entry points, workflows, state changes, integrations, and tests. Follow relationships when needed to establish that a candidate is implemented rather than merely declared.

# Reasoning Boundary

Describe only capabilities supported by implementation evidence. Do not convert dependency presence, unused code, naming, directory structure, or conventional framework behavior into features without supporting evidence. Distinguish verified behavior, reasonable inference, and unknowns.

# Output Responsibility

Produce complete professional Features documentation according to the phase skill, emphasizing what the software actually enables rather than how the repository was investigated.
