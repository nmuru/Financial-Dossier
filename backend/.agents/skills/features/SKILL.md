---
name: features
description: Reconstruct the implemented functional capabilities of a software repository and the workflows they support. Use when identifying user-facing and system-level features from repository evidence, distinguishing implemented behavior from intended, partial, unused, or speculative functionality.
---

# Features Reverse-Engineering Skill

## Overview

Determine what the software can actually do, expressed as coherent functional capabilities rather than as a list of files, functions, endpoints, or technologies.

A feature is a meaningful capability or workflow provided by the system. The analysis should connect externally visible behavior to the underlying implementation and distinguish implemented features from documented intentions, incomplete prototypes, unused code, and inferred capabilities.

The objective is to produce a feature inventory that is useful to an engineer or product reader who needs to understand the system without inspecting the repository personally.

## When to Use

Use this skill for the Features phase of the nine-phase reverse-engineering workflow.

Use it after the Business Purpose phase so that feature interpretation can be consistent with the repository's apparent purpose.

Do not use this skill to reconstruct detailed technical architecture, low-level implementation, test strategy, or future improvements. Those belong to later phases.

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.


## Core Process

### Step 1: Establish the feature surface

Identify the repository's externally reachable surfaces.

Depending on the system, inspect:

- Web pages and UI navigation.
- HTTP routes and API endpoints.
- CLI commands.
- Public library APIs.
- Event consumers and producers.
- Background jobs.
- Scheduled tasks.
- Authentication and account workflows.
- File import/export behavior.
- Integrations with external systems.
- Administrative or operational interfaces.

Do not assume that every source-code capability is a feature. Start with what a user, operator, administrator, client application, or external system can actually invoke or observe.

### Step 2: Map major workflows

Group related operations into coherent workflows.

For each significant workflow, trace:

external trigger → entry point → validation → business/service logic → data or external interaction → resulting outcome.

A collection of CRUD endpoints should not automatically become several unrelated features if they collectively implement one meaningful workflow.

Conversely, do not collapse genuinely distinct user capabilities merely because they share an implementation layer.

The feature should be described at the level of the meaningful capability, not at the level of individual functions.

### Step 3: Identify feature evidence

For every candidate feature, find concrete implementation evidence.

Useful evidence includes:

- routes and handlers
- UI components and pages
- service methods
- domain models
- database operations
- schemas and validation
- event handlers
- background jobs
- integration clients
- tests
- configuration
- documentation

Prefer multiple evidence sources for important features.

A route alone establishes an exposed interface, but not necessarily a complete or working feature. Trace the route far enough to determine what it actually does.

### Step 4: Classify feature status

Classify each significant capability according to the strongest available evidence.

Use categories such as:

- Implemented: the capability is exposed and its behavior can be traced through working application logic.
- Partially implemented: the capability exists but important portions are missing, placeholder, disconnected, or incomplete.
- Documented but not verified: documentation claims the capability, but repository evidence does not establish its implementation.
- Internal/system capability: meaningful system behavior not necessarily exposed directly to an end user, such as scheduled processing or synchronization.
- Apparently unused or legacy: implementation exists but no credible active path to it was found.
- Inferred capability: a reasonable capability can be inferred from connected evidence but is not directly exposed or documented.

Do not force every feature into a status when the evidence is ambiguous. Explain the ambiguity.

### Step 5: Identify actors and feature boundaries

For each important feature, determine who or what initiates it where evidence permits.

Possible actors include:

- end users
- administrators
- internal services
- scheduled processes
- external systems
- API consumers
- developers or operators

Do not invent personas. Use routes, permissions, UI flows, authentication logic, API clients, event definitions, documentation, and tests as evidence.

Identify meaningful boundaries between features based on distinct user outcomes or workflows, not arbitrary code boundaries.

### Step 6: Trace feature dependencies

Determine which features depend on other capabilities.

Examples include:

authentication required before another workflow, configuration required before an integration can operate, data creation required before reporting can work, or one API operation triggering asynchronous processing.

Only describe dependencies that can be supported by repository evidence.

This produces a feature model rather than an isolated feature list.

### Step 7: Compare documentation and implementation

Compare README files, product documentation, API documentation, UI text, comments, and examples with actual repository behavior.

Look specifically for:

- documented features absent from code
- implemented features absent from documentation
- UI features whose backend behavior is incomplete
- backend capabilities with no visible consumer
- placeholder endpoints
- dead or unreachable feature code
- configuration-gated features
- experimental or prototype features
- deprecated workflows still present in the repository

Material discrepancies should be reported because they affect the reliability of the feature inventory.

### Step 8: Check completeness from multiple surfaces

After identifying the main features, revisit the repository through a different evidence surface.

For example, if the initial feature inventory came primarily from API routes, cross-check it against UI pages, domain models, tests, and documentation.

If the system is a library or service without a UI, cross-check public APIs against tests, consumers, examples, and package documentation.

The purpose is to reduce the risk of producing a feature inventory based on only one layer of the repository.

## Feature description standard

Describe each major feature in terms of:

- Capability: what the system enables.
- Actor or trigger: who or what initiates it.
- Workflow: the meaningful sequence of operations.
- Outcome: what the actor or system obtains.
- Evidence: the repository artifacts supporting the conclusion.
- Status: implemented, partial, documented-but-unverified, internal, inferred, or apparently unused where applicable.

Do not turn this into a dump of endpoint names or function names.

For example, prefer:

"Users can submit a repository URL for analysis, after which the backend creates an analysis workspace and invokes the reverse-engineering pipeline."

over:

"`POST /api/analyze` calls `analyze_repository()`."

The second statement is useful evidence for the first, but is not itself the feature description.

## Distinguishing features from implementation details

A feature represents meaningful system capability.

The following are usually implementation details rather than independent features:

- database connection pooling
- logging
- dependency injection
- a helper function
- an internal utility class
- a framework middleware
- a model class with no independently meaningful behavior
- a configuration loader

The following may be features when they provide a meaningful user or operational outcome:

- authentication
- repository analysis
- report generation
- search
- data import/export
- notifications
- synchronization
- scheduled processing
- administration

When uncertain, determine whether the behavior produces an independently meaningful outcome or merely supports another capability.

## Anti-patterns and rationalizations

| Rationalization | Reality |
|---|---|
| "Every endpoint is a feature." | Endpoints are implementation surfaces. Group them into meaningful capabilities and workflows. |
| "The README lists the features, so we can copy it." | Documentation is evidence of intent. Verify what is actually implemented. |
| "This function exists, so the feature exists." | A definition does not establish reachability or active usage. Trace the execution path. |
| "The UI shows a button, so the feature works." | Verify the backend path and resulting behavior. |
| "The backend endpoint exists, so users can use the feature." | The endpoint may be internal, unused, protected, incomplete, or disconnected from any consumer. |
| "CRUD operations should be listed separately." | CRUD operations may collectively implement one meaningful domain workflow. |
| "The model names make the feature obvious." | Domain models are clues. Verify their relationships and actual usage. |
| "A dependency implies a feature." | Dependencies show possible implementation capability, not necessarily active functionality. |
| "We should include planned features because they are in the roadmap." | Planned behavior is not implemented behavior. Report it separately if supported by repository evidence. |
| "The feature list looks too short." | Do not invent features to make the dossier appear complete. |

## Red Flags

Investigate further when:

- the feature inventory is almost identical to the list of API endpoints
- every file or module has been described as a feature
- documentation claims substantially more functionality than implementation exposes
- UI elements have no traceable backend behavior
- API endpoints have no identifiable consumers
- important workflows terminate in placeholder responses
- large portions of the repository appear unused or experimental
- the same feature appears under several different names
- a feature's status is asserted without evidence
- feature descriptions contain mainly technology names rather than user or system outcomes

## Verification

Before completing this phase, confirm:

- [ ] Major externally visible and meaningful system capabilities have been identified.
- [ ] Important internal or operational capabilities have been considered where relevant.
- [ ] Features are expressed as meaningful capabilities rather than raw code artifacts.
- [ ] Major features have been traced through enough implementation to establish what they actually do.
- [ ] Feature actors or triggers are evidence-based.
- [ ] Feature outcomes are explicit.
- [ ] Important feature dependencies are identified where supported.
- [ ] Documentation has been compared with implementation.
- [ ] Partial, unverified, inferred, and apparently unused capabilities are distinguished from implemented features.
- [ ] The inventory has been cross-checked using more than one repository surface where possible.
- [ ] No feature has been added solely because it would be typical for the technology or domain.
- [ ] The result contributes information distinct from the Business Purpose phase.

## Output Expectations

Return a professional, sufficiently detailed Features analysis. Cover the meaningful capabilities and workflows needed to understand the system without artificially constraining the document length.

Organize the result around coherent functional capabilities and workflows.

For each major feature, explain what it does, who or what triggers it, the meaningful workflow, the resulting outcome, and its implementation status. Use repository analysis internally to establish these details; do not reproduce the investigation trail or confidence classifications in the final document.

Include secondary or internal features when they materially contribute to understanding how the system operates.

Separate documented intent from implemented behavior where they differ, without exposing internal verification labels.

Do not provide detailed architecture or low-level code analysis unless required to establish a feature's behavior. Those topics belong to later phases.

Do not recommend new features or improvements. The purpose of this phase is to reconstruct what exists.

The final analysis should allow a reader to answer:

"What meaningful things can this system actually do, for whom or what, through which workflows, and what implementation behavior and constraints shape those capabilities?"


## Output boundary and depth

Repository support and internal implementation-status classifications are reasoning mechanisms. Do not reproduce evidence trails, certainty/confidence labels, or source-by-source investigation notes in the final Features document.

Cover the meaningful capabilities and workflows needed for comprehensive understanding. Do not artificially constrain the document to a fixed page or word count, and do not add unsupported features merely to make the inventory longer.
