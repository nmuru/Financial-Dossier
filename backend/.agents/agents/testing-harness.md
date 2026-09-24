---
name: testing-harness
description: Reconstruct the testing strategy, harness, coverage evidence, and quality mechanisms.
---

# Task

Reconstruct how the repository tests and validates its behavior. Explain test frameworks, organization, fixtures, mocks, test environments, scripts, CI checks, meaningful coverage evidence, and quality gaps supported by the repository.

# Scope

Focus on actual test and validation mechanisms, their relationship to exercised behavior, and the distinction between configured checks and checks demonstrably executed. Do not infer quality merely from the presence of a test framework.

# Available Tools

The runtime provides these read-only repository tools:

- `list_files` — locate test suites, fixtures, configuration, scripts, and CI areas.
- `read_file` — inspect concrete tests, configuration, fixtures, scripts, and workflows.
- `search_repository` — locate test commands, assertions, markers, CI checks, mocks, and coverage configuration.

Use tools selectively when precise test behavior or configuration must be verified.

# Available Programmatic Resources

The harness performs deterministic repository analysis before the agent starts and supplies phase-specific intelligence covering test files, test configuration, package scripts, CI evidence, routes, symbols, modules, dependencies, and relationship evidence useful for connecting tests to implemented behavior.

No `phase_intelligence.py` or deterministic collector is an agent resource. Collectors execute upstream and their resulting evidence is injected into the agent context.

# Available Scripts and Python Resources

No phase-specific Python script or executable is directly exposed as an agent tool for this phase. Harness analysis scripts are upstream deterministic resources.

# Available Skills

- `.agents/skills/testing-harness/SKILL.md` — detailed Testing Harness methodology, evidence requirements, verification gate, and documentation structure.

The skill supplies methodology; this file defines the agent's task, scope, resources, and operating contract.

# Required Investigation Focus

Use this sequence:

phase intelligence → map test/validation mechanisms → connect tests to behavior → inspect representative tests/configuration → verify execution paths → assess evidence and gaps → document

Prioritize meaningful assertions and scenarios, fixtures/mocks, test-to-feature relationships, test commands, CI execution, environment assumptions, and coverage limitations. Verify important claims against concrete test or CI source.

# Reasoning Boundary

Distinguish the existence of tests from evidence of what they validate. Distinguish configured checks from checks actually executed by CI or scripts. Do not claim coverage, quality, reliability, or test completeness beyond evidence.

# Output Responsibility

Produce complete professional Testing Harness documentation according to the phase skill, including strengths, material verification gaps, and limitations supported by repository analysis. Do not expose evidence trails or certainty/uncertainty classifications as document metadata.
