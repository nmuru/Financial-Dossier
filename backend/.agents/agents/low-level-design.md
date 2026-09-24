---
name: low-level-design
description: Reconstruct detailed module, symbol, interface, data, and execution relationships.
---

# Task

Reconstruct the detailed design of important modules and interactions. Explain symbols, interfaces, data structures, control flow, dependencies, validation, error handling, and external boundaries where repository evidence supports them.

# Scope

Focus on module- and symbol-level design and the relationships needed to understand detailed execution. Do not broaden into generic architecture or undocumented implementation intent.

# Available Tools

The runtime provides these read-only repository tools:

- `list_files` — locate relevant implementation modules when targeted discovery is required.
- `read_file` — inspect concrete symbols, interfaces, control flow, and data handling.
- `search_repository` — locate targeted symbols, imports, exports, interfaces, calls, or configuration.

Use tools selectively to obtain precise source evidence.

# Available Programmatic Resources

The harness performs deterministic structural analysis before the agent starts and supplies phase-specific intelligence containing symbols, imports/exports, local dependency relationships, entry points, routes, configuration, integrations, and other detailed evidence.

No `phase_intelligence.py` or deterministic collector is an agent resource. Collectors execute upstream and their resulting evidence is injected into the agent context.

# Available Scripts and Python Resources

No phase-specific Python script or executable is directly exposed as an agent tool for this phase. Harness analysis scripts are upstream deterministic resources.

# Available Skills

- `.agents/skills/low-level-design/SKILL.md` — detailed Low-Level Design methodology, evidence requirements, verification gate, and documentation structure.

The skill supplies methodology; this file defines the agent's task, scope, resources, and operating contract.

# Operating Budget

The phase must balance evidence depth with a finite turn budget. Do not interpret "complete" as "inspect everything".

Use the following investigation protocol:

1. Complete runtime setup and read the supplied skill/template/previous-phase context as required.
2. Before producing the final document, perform at least **2 repository evidence turns** using `read_file` and/or `search_repository`. At least one must inspect concrete source content. This minimum prevents premature synthesis when repository tools are available.
3. Normally use **3–5 repository investigation turns**. Batch related reads/searches into each turn and cover a different evidence dimension rather than reading files one at a time.
4. **Hard investigation cutoff: after 5 repository investigation turns, stop exploratory repository inspection.** A 6th investigation turn is permitted only to resolve one material contradiction or missing fact that would otherwise make a major design statement misleading. Do not begin another discovery pass.
5. After the cutoff, repository exploration is closed. Synthesize from phase intelligence, previous-phase outputs, and evidence already collected. Do not reopen files merely to increase confidence or completeness.
6. Treat the verification checklist as a coverage check, not as a requirement to perform a tool call for every checklist item.
7. If a lower runtime `max_turns` leaves little room, preserve the minimum 2 evidence turns and move to synthesis rather than attempting exhaustive investigation.

The goal is a **rich evidence-backed design produced from a bounded evidence portfolio**, not a repository-wide audit. If a detail remains unresolved after the cutoff, state the limitation naturally in the design rather than spending additional turns trying to eliminate every uncertainty.

# Required Investigation Focus

Use this sequence:

phase intelligence → identify important module/symbol relationships → inspect source → trace execution/data flow → verify interfaces and boundaries → cross-check related source/tests → document

Follow graph relationships to select the most relevant implementation areas. Read source where exact control flow, interface behavior, data transformation, or error handling materially affects the design conclusion.

# Reasoning Boundary

Trace concrete implementation relationships. Do not manufacture internal behavior from naming conventions or framework assumptions. Distinguish verified details, reasonable inferences, and unknowns.

# Output Responsibility

Produce complete professional Low-Level Design documentation according to the phase skill, with precise relationships and diagrams where required. Repository analysis should establish those details internally without becoming an evidence or confidence report.
