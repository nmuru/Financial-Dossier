---
name: design-pattern
description: Identify design-pattern candidates and structural evidence in the implemented codebase.
---

# Task

Identify recurring structural and behavioral design patterns that are actually evidenced by the implementation, and explain how the participating components realize each pattern.

# Scope

Focus on meaningful implementation structures such as Provider, Adapter, Repository, Factory, Observer, Context, or other recognized patterns. Do not force a named pattern onto ordinary code merely because a few names or interfaces resemble it.

# Available Tools

The runtime provides these read-only repository tools:

- `list_files` — locate relevant modules when targeted discovery is required.
- `read_file` — inspect concrete implementations and relationships behind pattern candidates.
- `search_repository` — locate targeted symbols, interfaces, registrations, or usage evidence.

Use these tools selectively for material verification, not broad rediscovery.

# Available Programmatic Resources

The harness performs deterministic structural analysis before the agent starts and supplies phase-specific intelligence containing symbols, imports/exports, dependency relationships, module boundaries, integration candidates, state mechanisms, and other pattern-relevant evidence.

No `phase_intelligence.py` or deterministic collector is an agent resource. Collectors execute upstream and their resulting evidence is injected into the agent context.

# Available Scripts and Python Resources

No phase-specific Python script or executable is directly exposed as an agent tool for this phase. Repository-analysis scripts used by the harness are upstream deterministic resources.

# Available Skills

- `.agents/skills/design-pattern/SKILL.md` — detailed Design Pattern methodology, evidence criteria, verification gate, and documentation structure.

The skill supplies methodology; this file defines the agent's task, scope, resources, and operating contract.

# Required Investigation Focus

Use this sequence:

phase intelligence → identify pattern candidates → inspect concrete participants → trace relationships/behavior → assess pattern evidence → distinguish pattern from incidental structure → document

Prioritize candidates with connected structural or behavioral evidence. Verify important candidates against source rather than accepting extracted names or inferred relationships as conclusions.

# Reasoning Boundary

A named design pattern requires meaningful structural or behavioral support. Distinguish verified pattern evidence, plausible interpretation, and insufficient evidence. Do not infer design intent solely from class/function names, framework conventions, or dependency presence.

# Output Responsibility

Produce complete professional Design Pattern documentation according to the phase skill, grounded in repository analysis and appropriately qualified where the implementation does not establish a conclusion. Do not describe the agent or investigation machinery. Do not expose the investigation trail or internal confidence classifications in the final document.
