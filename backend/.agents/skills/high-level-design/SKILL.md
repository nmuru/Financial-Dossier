---
name: high-level-design
description: Reconstruct the high-level software design of an existing repository, explaining major components, responsibilities, interactions, workflows, state boundaries, and design patterns from evidence. Use when moving from technology architecture to logical system design without descending into function-level implementation detail.
---

# High-Level Design Reverse-Engineering Skill

## Objective

Reconstruct how the software is logically designed.

The Technology Architecture phase establishes the major runtime and technology boundaries. This phase goes one level deeper: it explains the major logical components inside those boundaries, their responsibilities, how they collaborate, how important workflows move through them, where state changes occur, and what design patterns or structural principles are actually evidenced.

The result should allow an engineer to understand the system's logical organization before examining individual classes, functions, algorithms, or implementation details.

Do not turn this phase into a code walkthrough. Do not repeat the Technology Architecture phase at a different level of vocabulary.

## Design scope

Cover the logical design dimensions supported by the repository:

- Major application components and subsystems
- Responsibilities and boundaries
- Component collaboration
- Request and data flows
- Domain/service boundaries
- State transitions
- Persistence boundaries
- External integration boundaries
- Interface contracts between major components
- Error and failure propagation where architecturally significant
- Synchronous and asynchronous workflows
- Important design patterns
- Separation of concerns
- Dependency direction
- Major lifecycle behavior

Do not invent layers or patterns simply because the framework commonly uses them.

## Relationship to other phases

Use the Business Purpose and Features phases to understand what the system is trying to accomplish.

Use the Requirements phase to understand the behaviors and constraints the design must satisfy.

Use the Technology Architecture phase as the outer boundary for the logical design.

This phase should answer:

"How is the system logically organized to deliver the capabilities and satisfy the requirements?"

It should not primarily answer:

"What technologies are used?" That belongs to Technology Architecture.

It should not primarily answer:

"What does each function or class do?" That belongs to Low-Level Design and Implementation Detail.

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.


## Investigation workflow

### Step 1: Establish the logical component map

Starting from the architectural components identified earlier, identify the major logical subsystems within them.

Look for boundaries expressed through:

- directories and modules
- services
- controllers or handlers
- domain packages
- repositories
- use-case/application services
- state managers
- adapters
- clients
- event handlers
- workers
- serializers
- validators
- persistence abstractions

Group related implementation artifacts into meaningful design components.

Do not create a logical component merely because a directory exists.

### Step 2: Determine component responsibilities

For every major logical component, determine:

- what responsibility it owns
- what responsibility it explicitly does not own
- what inputs it accepts
- what outputs it produces
- which components it depends on
- which components depend on it
- what state it owns or changes

Use actual call relationships, imports, interfaces, types, schemas, and workflows as evidence.

Avoid vague responsibilities such as "handles business logic" when the repository permits a more precise description.

### Step 3: Trace representative use cases

Select the most important workflows identified during the Features phase.

For each representative workflow, trace the logical design:

actor or trigger → entry component → validation → application/service logic → domain behavior → persistence/integration → result.

Do not trace every possible path.

Choose workflows that reveal the design structure and expose important component boundaries.

Identify where responsibility changes from one component to another and why the transition occurs.

### Step 4: Identify interfaces between components

Inspect how major components communicate.

Look for:

- function or method interfaces
- typed contracts
- schemas
- service interfaces
- HTTP contracts
- events
- queues
- callbacks
- dependency injection
- adapters
- repository interfaces
- shared domain objects

Determine what information crosses each boundary.

Do not infer an abstract interface when components are directly coupled unless the repository actually demonstrates such an abstraction.

### Step 5: Analyze dependency direction

Determine which components depend on which others.

Look for:

- imports
- constructor dependencies
- service calls
- repository access
- callbacks
- event publication/subscription
- shared state
- configuration dependencies

Identify whether the design has a clear dependency direction or contains cycles and cross-layer coupling.

Do not label something "clean architecture", "hexagonal architecture", "MVC", "DDD", or another pattern solely because its directory structure resembles that pattern.

Name a pattern only when the implementation demonstrates the characteristic structure and relationships.

### Step 6: Identify state ownership and lifecycle

Determine where important state lives and which component owns changes to it.

Consider:

- request state
- session state
- domain state
- database state
- cache state
- filesystem state
- job state
- UI/client state
- external-system state

Trace important state transitions.

Identify whether state is:

- transient
- persistent
- derived
- cached
- externally owned

Do not infer persistence or lifecycle guarantees without evidence.

### Step 7: Analyze synchronous and asynchronous design

Determine whether major workflows are:

- synchronous request/response
- asynchronous
- event-driven
- queued
- scheduled
- polling-based
- callback-based

Identify the boundary where asynchronous work begins and where results are consumed.

Inspect job definitions, queues, workers, events, schedulers, futures/promises, callbacks, and polling logic where relevant.

Do not infer asynchronous behavior merely because a framework supports it.

### Step 8: Analyze failure and boundary behavior

At the high-level design level, identify how important failures move through the system.

Inspect:

- validation boundaries
- service errors
- integration failures
- persistence failures
- retries
- timeouts
- exception translation
- API error responses
- job failure handling
- fallback behavior

Focus on architectural consequences rather than individual exception statements.

For example, identify that an external integration is isolated behind an adapter and its failures are translated into application-level errors if the repository supports that conclusion.

### Step 9: Identify design patterns and principles

Look for patterns that are actually implemented.

Possible examples include:

- MVC
- layered architecture
- repository pattern
- service layer
- adapter
- facade
- dependency injection
- event-driven design
- command/query separation
- state machine
- strategy
- factory
- middleware pipeline

Only identify a named pattern when its defining structure is evidenced.

If the design resembles a pattern but does not fully establish it, describe the observed structure without assigning an unjustified label.

### Step 10: Identify coupling and cohesion

Assess important structural relationships.

Look for:

- excessive shared state
- circular dependencies
- direct database access from presentation components
- business rules duplicated across components
- tight coupling to external providers
- large components with multiple unrelated responsibilities
- well-isolated adapters
- reusable domain services
- clear boundaries

This is descriptive analysis, not a refactoring exercise.

Do not recommend changes unless the repository's design characteristics are necessary to explain the current system.

### Step 11: Reconcile intended and implemented design

Compare documentation, comments, naming, architecture diagrams, and declared abstractions with actual relationships.

Identify:

- abstractions that are not used
- components that bypass intended boundaries
- duplicated implementations
- legacy paths
- partially implemented design
- configuration-dependent designs
- architectural intent that differs from runtime behavior

Report material differences explicitly.

## High-Level Design Diagram

Produce a logical component diagram or workflow diagram when it materially improves understanding.

The diagram should show logical components and their relationships rather than merely repeating the technology architecture diagram.

Prefer Mermaid when the response supports it.

A useful logical diagram may look conceptually like:

```text
Client
  |
  v
API / Controller
  |
  v
Application Service
  |
  +----> Domain Logic
  |
  +----> Repository ---> Database
  |
  +----> External Adapter ---> External Service
```

Do not use this example as an assumption about the target repository. Build the actual diagram from evidence.

The diagram should emphasize responsibility and interaction boundaries.

Do not place every class or function in the diagram.

## Evidence discipline

For each major logical component, identify concrete supporting artifacts.

Useful evidence includes:

- module/package paths
- classes or services
- interfaces
- schemas
- call sites
- imports
- route handlers
- data-access code
- tests
- event definitions
- configuration

For important relationships, prefer evidence from both sides of the boundary when possible.

For example, if component A is said to call component B, identify the caller and the implementation or interface of B.

## Internal Reasoning Classification

Use:

**Verified:** Directly established by implementation relationships.

**Strongly inferred:** Supported by multiple connected artifacts but not explicitly stated.

**Unverified:** Suggested by documentation or naming without sufficient implementation evidence.

**Apparently legacy/unused:** Present in the repository but without a credible active path.

Do not hide uncertainty.

## Anti-patterns and rationalizations

| Rationalization | Required response |
|---|---|
| "The folder structure is the design." | Use structure as evidence, then verify actual dependencies and workflows. |
| "This is clearly MVC." | Verify controller, model, view responsibilities and actual relationships before naming the pattern. |
| "Every service class is a component." | Group artifacts according to meaningful logical responsibility. |
| "The architecture diagram already explains this." | Go one level deeper into logical responsibilities and interactions. |
| "A repository class means the repository pattern is used." | Verify how the abstraction is consumed and whether it isolates persistence. |
| "Dependency injection is present, so components are decoupled." | Inspect actual dependency direction and coupling. |
| "Async syntax means the workflow is asynchronous." | Determine whether work actually crosses an asynchronous boundary. |
| "A queue library means there is a queue architecture." | Verify configuration, producers, consumers, and runtime usage. |
| "The cleanest design is probably the intended design." | Describe the design that exists, including coupling and irregularities. |
| "We can omit awkward legacy paths." | Include them when they materially affect the actual design. |

## Red Flags

Investigate further when:

- the logical design is identical to the technology architecture
- components are defined solely by folders
- the diagram contains classes instead of meaningful subsystems
- a named design pattern is asserted without structural evidence
- important workflows cross component boundaries that the design description ignores
- dependency direction is unclear
- multiple components directly manipulate the same state without explanation
- external integrations are embedded throughout the application
- documented abstractions are bypassed by actual code
- asynchronous behavior is claimed without a real asynchronous boundary
- error handling changes architectural flow but is omitted
- legacy or alternate paths materially affect behavior

## Verification Gate

Before completing this phase, verify:

- [ ] Major logical components have been identified.
- [ ] Each major component has a concrete responsibility.
- [ ] Important component boundaries are evidence-backed.
- [ ] Representative workflows have been traced through the logical design.
- [ ] Important interfaces and data crossing boundaries have been identified.
- [ ] Dependency direction and significant coupling have been examined.
- [ ] Important state ownership and lifecycle behavior have been examined.
- [ ] Synchronous/asynchronous boundaries have been verified where relevant.
- [ ] Important failure propagation paths have been considered.
- [ ] Named design patterns are supported by structural evidence.
- [ ] The logical design is clearly distinguished from the technology architecture.
- [ ] Documentation and intended design have been compared with implementation.
- [ ] A logical component/workflow diagram is included when appropriate.
- [ ] Facts, inferences, and unknowns are distinguishable.
- [ ] No redesign has been substituted for reconstruction.

## Output Expectations

### Output boundary
Repository support and internal classification of relationships are reasoning mechanisms. Do not reproduce them as evidence annotations or certainty labels in the final High-Level Design document. Present the established design directly and describe material limitations or open questions in natural language when needed.


Return a professional, sufficiently detailed High-Level Design analysis. Cover all materially important components, boundaries, interactions, state ownership, and workflows without artificially constraining the document length.

Explain the major logical components, their responsibilities, interfaces, dependencies, state ownership, important workflows, and architectural interactions.

Include a logical component or workflow diagram when it improves understanding, preferably in Mermaid syntax.

Use implementation artifacts to establish the design, but avoid descending into individual function behavior unless needed to establish a component relationship. Do not reproduce the investigation trail or internal confidence classifications in the final document.

Explicitly identify important design patterns only when the repository analysis establishes them. Do not expose the internal support assessment as a label.

Discuss meaningful coupling, boundary violations, or legacy paths when they are part of the actual design.

Do not recommend architectural improvements in this phase. Describe the existing design. Improvements belong to Future Directions.

The final analysis should allow a reader to answer:

"How is the system logically organized, what responsibilities belong to each major component, how do those components collaborate, where does state and control flow cross boundaries, and what design principles are actually present?"
