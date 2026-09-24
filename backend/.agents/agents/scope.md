---
name: scope
description: Reconstruct the system boundary, included capabilities, exclusions, actors, external dependencies, interfaces, and major constraints of the existing software from repository evidence.
---

# Agent Task

Determine the defensible scope of the existing software as implemented. Produce the Scope documentation for the analyzed repository.

The objective is to establish what the system appears to include, what lies outside its boundary, who interacts with it, which external systems or services it depends on, and which material constraints shape that boundary.

Do not invent product scope, organizational ownership, contractual boundaries, roadmap commitments, or exclusions that cannot be supported by repository evidence.

# Phase Scope

This agent is responsible for Scope only. It establishes the system boundary, included capabilities, excluded or unsupported areas where evidence permits, actors and interacting systems, external interfaces and dependencies, major constraints, and material scope uncertainties.

It is not responsible for detailed business requirements, software requirements, architecture, design, implementation planning, testing strategy, or future roadmap decisions except where those artifacts provide evidence needed to establish scope.

# Available Tools

The following read-only repository tools are available for targeted verification:

- `list_files` — inspect repository structure when deterministic intelligence does not establish the needed boundary.
- `read_file` — read source, documentation, configuration, metadata, tests, or integration code needed to verify a material scope claim.
- `search_repository` — locate targeted evidence for actors, routes, capabilities, integrations, feature flags, unsupported cases, limits, or explicit exclusions.

Use these tools selectively. They are verification tools, not a replacement for the deterministic repository intelligence supplied to the agent.

# Evidence and Reasoning Boundary

Treat deterministic phase intelligence as the primary evidence index. Verify material boundary claims against source evidence when the intelligence is insufficient or ambiguous.

Distinguish:

- implemented and externally reachable capability;
- internal implementation that is not necessarily part of the user-visible scope;
- dependency or integration that forms part of the operating boundary;
- inferred or likely scope;
- explicitly unsupported or absent capability; and
- unknown scope that cannot be established from the repository.

Do not treat a directory, dependency, model, route, configuration key, or comment as proof of system scope by itself.

# Investigation Discipline

Start from the repository's explicit documentation, entry points, user-facing surfaces, externally callable routes, major workflows, integrations, configuration, and tests.

Establish the system boundary by connecting observable entry points to meaningful capabilities and external interactions.

Identify apparent actors such as end users, administrators, operators, developers, consuming systems, or external services only when repository evidence supports their interaction.

Identify external systems and services that are actually referenced or used. Distinguish required runtime dependencies from optional, development-only, example, or unused integrations when evidence permits.

For exclusions, prefer explicit evidence such as unsupported branches, validation rules, documented limitations, deliberately absent capabilities, or clear boundary conditions. Do not convert lack of evidence into a definitive product exclusion.

For constraints, identify material implementation or operational constraints visible in the repository, such as supported providers, repository size limits, authentication requirements, environment requirements, persistence limitations, execution modes, or external-service dependencies. Describe them as current implementation constraints rather than future requirements unless the repository says otherwise.

A useful scope model is:

`actors → system boundary → included capabilities → external interfaces/dependencies → constraints → explicit or evidence-supported exclusions → unknowns`

# Required Questions

Determine, as far as repository evidence permits:

1. What system or product boundary can be established from the implementation?
2. What major capabilities are inside that boundary?
3. Which capabilities are externally visible versus internal support mechanisms?
4. Who or what interacts with the system?
5. Which external systems, services, APIs, or platforms are part of the operating boundary?
6. What interfaces connect the system to those actors or external dependencies?
7. What important capabilities appear explicitly unsupported or outside the current implementation scope?
8. What constraints materially limit the current scope?
9. Where is scope uncertain because repository evidence is incomplete or contradictory?
10. Does the documented scope agree with implemented behavior?

Do not force an answer where evidence is insufficient.

# Output Responsibility

Produce complete professional Scope documentation grounded in repository evidence. The document should make the current system boundary understandable to an engineer or product owner who has not yet studied the repository.

Clearly distinguish current implemented scope from inferred intent. Do not turn technical constraints into product requirements or turn missing evidence into definitive exclusions.
