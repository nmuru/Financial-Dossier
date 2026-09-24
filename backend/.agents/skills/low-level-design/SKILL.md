---
name: low-level-design
description: Reconstruct the concrete internal design of an existing software repository at class, function, module, schema, state, and interaction level. Use when translating the high-level design into evidence-backed implementation structure without turning the analysis into a line-by-line code walkthrough.
---

# Low-Level Design Reverse-Engineering Skill

## Objective

Reconstruct the concrete internal design that implements the system's high-level design.

This phase moves from logical components to the actual modules, classes, functions, interfaces, schemas, data structures, state transitions, algorithms, and internal interactions that make those components work.

The objective is to explain how the implementation is organized internally, not merely to summarize source files.

The analysis must remain evidence-driven. Every important relationship should be traceable to concrete repository artifacts.

Do not redesign the system. Do not silently "clean up" poor design. Describe the implementation that exists, including duplication, coupling, legacy paths, incomplete abstractions, and unusual structures when they materially affect understanding.

## Relationship to other phases

Business Purpose explains why the system exists.

Features explains what meaningful capabilities it provides.

Requirements reconstructs what behaviors and constraints the system appears to satisfy.

Technology Architecture explains the major runtime technologies and boundaries.

High-Level Design explains the major logical components and their responsibilities.

Low-Level Design explains how those logical components are concretely implemented.

Implementation Detail later explains implementation mechanics, configuration, build, deployment, and operational execution in greater depth.

This phase should therefore answer:

"What concrete modules, classes, functions, data structures, interfaces, and interactions implement the high-level design?"

## Scope

Cover the implementation dimensions that materially explain the system:

- module/package organization
- classes and important objects
- functions and methods
- interfaces and abstractions
- schemas and data structures
- validation
- domain logic
- service logic
- persistence access
- external integration adapters
- state management
- important algorithms
- control flow
- dependency relationships
- error propagation
- serialization/deserialization
- configuration-dependent implementation
- significant concurrency or asynchronous mechanisms

Do not attempt to describe every function. Focus on implementation elements that are architecturally or behaviorally significant.

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.


## Bounded Investigation Protocol

Low-Level Design requires real repository inspection, but exhaustive inspection is neither necessary nor compatible with a finite turn budget.

Use a **minimum-to-rich evidence portfolio**:

- **Minimum evidence pass:** Before final synthesis, perform at least 2 repository evidence turns. At least one must use `read_file` or `search_repository` to inspect concrete implementation content. Do not produce the final document directly from deterministic intelligence alone when repository tools are available.
- **Normal investigation budget:** Target 3–5 repository investigation turns. Batch related reads/searches in each turn.
- **Hard cutoff:** After the 5th repository investigation turn, stop exploratory inspection. A 6th turn is allowed only for one material contradiction or one missing fact that blocks a major design conclusion. After that, repository exploration is closed.
- **Synthesis protection:** Once the cutoff is reached, spend the remaining budget on reasoning, verification against already collected evidence, and document production. Do not trade synthesis turns for additional repository discovery.
- **Checklist semantics:** The verification gate is a completeness check over the evidence already collected. It does not mean that every checklist item requires a separate source read or tool call.
- **Unknowns are acceptable:** If a material detail cannot be established within the evidence budget, qualify it naturally or omit it. Do not continue exploring solely to eliminate every uncertainty.

### Investigation turns should be portfolio-oriented

Prefer a small number of broad, high-value investigation turns:

1. **Component and entry-point pass:** Map the most important high-level components to concrete modules and identify the entry points that drive representative workflows.
2. **Execution-flow pass:** Trace the most important end-to-end workflows through validation, calls, transformations, state, persistence, and external boundaries.
3. **Contract/data pass:** Verify important interfaces, schemas, types, state representations, configuration-dependent paths, and error behavior.
4. **Cross-check pass:** Check tests, alternate implementations, legacy paths, or configuration only where they can materially change the design already reconstructed.
5. **Targeted-gap pass:** Only if needed, resolve the highest-impact remaining ambiguity or contradiction.

Do not spend an investigation turn on a long list of unrelated files merely because they exist. Do not repeat reads that reconfirm facts already established by deterministic intelligence or earlier source inspection.

### Materiality rule

Prioritize evidence using these tiers:

- **Tier 1 — must trace:** primary entry points, representative business/runtime flows, major component boundaries, important external calls, persistence/state transitions, and contracts that materially affect behavior.
- **Tier 2 — trace when relevant:** validation details, significant error paths, configuration-controlled branches, important algorithms, and tests that clarify active behavior.
- **Tier 3 — normally summarize from intelligence or omit:** trivial helpers, boilerplate, repetitive wrappers, generated code, framework internals, and low-impact alternate files.

A comprehensive final LLD does not require every implementation element to be inspected. It requires the important relationships to be covered with enough concrete evidence to explain how the system works.

### Tool-use guardrail

When repository tools are available, do not stop after reading only runtime resources and previous-phase artifacts. Perform the minimum repository evidence pass above.

Conversely, once the hard investigation cutoff is reached, do not let red flags or checklist items restart broad exploration. Red flags should cause a targeted read only when the missing evidence could materially change a major conclusion.

## Investigation workflow

The workflow below defines what to cover, not a requirement to execute one tool call per step. Combine related steps within the bounded investigation protocol above.

### Step 1: Start from high-level components

Use the High-Level Design results to identify the logical components that require concrete implementation mapping.

For each major component, locate:

- primary modules
- entry classes/functions
- public interfaces
- service objects
- repositories or persistence adapters
- domain objects
- external clients
- validators
- serializers
- configuration dependencies

Do not blindly search the entire repository without a component-level hypothesis.

### Step 2: Map logical components to source artifacts

Create an evidence-backed mapping:

logical component → package/module → classes/functions → important collaborators.

Use:

- imports
- call sites
- type references
- inheritance
- composition
- dependency injection
- route registration
- object construction
- interface implementation
- event registration

Do not map components based solely on filenames.

### Step 3: Identify important entry points

For each major workflow, identify the concrete implementation entry point.

Examples:

- HTTP route handler
- UI event handler
- CLI command
- worker entry point
- event consumer
- scheduled task
- library public API

Trace the entry point into the internal implementation far enough to explain the main control flow.

### Step 4: Reconstruct control flow

For important workflows, follow the actual sequence of calls.

Identify:

- validation
- branching
- service invocation
- domain logic
- persistence
- external calls
- transformation
- result construction
- error propagation

Do not produce a raw call graph containing every helper function.

Focus on the calls that explain meaningful behavior or component boundaries.

### Step 5: Analyze classes and objects

For important classes or objects, determine:

- responsibility
- public methods
- important internal state
- collaborators
- construction/lifecycle
- inheritance or composition
- invariants
- side effects

Only include classes that materially contribute to the system's design.

Do not describe trivial data classes individually unless they represent important domain or interface concepts.

### Step 6: Analyze functions and methods

For important functions and methods, determine:

- purpose
- inputs
- outputs
- important validation
- side effects
- dependencies
- error behavior
- state changes
- external interactions

Use signatures, implementations, call sites, and tests together.

Do not infer a function's behavior from its name alone.

### Step 7: Analyze interfaces and contracts

Inspect:

- Python/TypeScript interfaces
- abstract classes
- protocols
- request/response schemas
- DTOs
- domain types
- event payloads
- serialized structures
- configuration contracts

Determine what each important boundary expects and produces.

Identify where static types and runtime validation differ.

Do not assume an interface is meaningful merely because it exists. Determine whether it has implementations and consumers.

### Step 8: Analyze data structures and schemas

For important data structures, reconstruct:

- fields
- types
- required/optional status
- defaults
- validation
- relationships
- transformations
- lifecycle
- serialization

Trace important data structures through their consumers.

Distinguish transport schemas from domain models and persistence models when the repository does so.

### Step 9: Analyze persistence implementation

Where persistence exists, trace:

model/schema → repository/access layer → database/storage operation → consumer.

Identify:

- queries
- repositories
- ORM usage
- transactions
- migrations
- serialization
- caching
- connection boundaries

Do not duplicate the full database architecture from the Technology Architecture phase. Focus here on the concrete implementation structure.

### Step 10: Analyze external integrations

For important external services, trace:

application component → client/adapter → request construction → external call → response handling → error handling.

Identify provider-specific abstractions and whether the design isolates or couples the application to the provider.

Do not claim an integration is active solely because an SDK is installed.

### Step 11: Analyze state transitions

For important stateful behavior, identify:

- state representation
- initial state
- valid transitions
- transition triggers
- validation
- persistence
- consumers of the resulting state

State may exist in objects, databases, caches, files, UI stores, job records, or external systems.

Do not invent state machines where the repository only contains loosely related status values.

### Step 12: Analyze important algorithms

Identify algorithms or processing logic that materially determines system behavior.

Explain:

- inputs
- major processing stages
- decisions
- transformations
- outputs
- complexity considerations where evidence permits

Do not reproduce large blocks of source code.

Explain the algorithm in precise prose or concise pseudocode when necessary.

### Step 13: Analyze error and exception flow

Trace important errors through the implementation.

Identify:

- validation failures
- domain errors
- integration failures
- persistence errors
- retries
- exception translation
- fallback behavior
- API response conversion
- worker/job failure handling

Focus on errors that materially affect control flow or external behavior.

### Step 14: Analyze configuration-dependent implementation

Identify implementation behavior controlled by:

- environment variables
- configuration files
- feature flags
- provider settings
- runtime modes
- optional dependencies

Determine how configuration changes actual code paths.

Do not describe configuration values without explaining their implementation effect.

### Step 15: Identify dead, legacy, or incomplete implementation

Look for:

- unused functions
- unreachable modules
- deprecated classes
- placeholder implementations
- commented-out logic
- duplicate implementations
- abandoned abstractions
- unused dependencies
- alternate execution paths

Do not label something dead solely because it is not obvious. Use lack of references, configuration, consumers, or execution paths as evidence.

## Low-Level Design Artifacts

Where useful, produce one or more precise diagrams.

Possible diagrams include:

- class relationship diagram
- module dependency diagram
- sequence diagram for a representative workflow
- data transformation diagram
- state transition diagram

Prefer Mermaid when the response format supports it.

Do not create diagrams merely for decoration.

A diagram should be limited to the most important implementation relationships and should remain readable.

For a sequence diagram, show actual participants and meaningful calls.

For a class diagram, include only important classes, attributes, methods, inheritance, and composition relationships.

For a module diagram, show actual dependency direction.

Do not fabricate relationships to make the diagram symmetrical or complete.

## Evidence requirements

For each major low-level design claim, ensure that concrete repository evidence exists in the collected evidence portfolio. Evidence may be represented by:

- file path
- module
- class
- function/method
- type/interface
- schema
- route
- call site
- test
- configuration key

Do not reopen a source file solely to attach another citation or reconfirm a relationship already established by strong collected evidence.

Prefer evidence from implementation and call sites rather than names or comments alone.

When saying "A calls B", establish the call relationship from source.

When saying "A implements interface B", establish the inheritance, protocol, registration, or equivalent mechanism.

When saying "A owns state B", identify where B is created, changed, and consumed.

## Internal Reasoning Classification

Use:

**Verified:** Directly established by source relationships or multiple strong artifacts.

**Strongly inferred:** Supported by connected implementation evidence but not explicit in one place.

**Unverified:** Suggested by names, documentation, or intended abstractions without enough implementation evidence.

**Apparently unused/legacy:** Present but lacking a credible active path.

Do not convert inferred implementation behavior into verified fact without evidence.

## Distinguishing design from incidental code

Include an implementation element when it materially explains:

- a feature
- a requirement
- a component boundary
- data flow
- state
- integration
- algorithm
- error behavior
- configuration-dependent behavior

Usually exclude:

- trivial getters/setters
- boilerplate
- generated code
- framework internals
- dependency source
- repetitive wrappers with no meaningful behavior

Mention them only when they have architectural or behavioral significance.

## Anti-patterns and rationalizations

| Rationalization | Required response |
|---|---|
| "Low-level design means documenting every function." | Focus on functions and classes that materially explain behavior and structure. |
| "The class name tells us its responsibility." | Verify behavior, collaborators, and call sites. |
| "A method exists, so it is part of the active flow." | Establish reachability and usage. |
| "The interface defines the architecture." | Check implementations and consumers. |
| "Every schema is a domain model." | Distinguish transport, domain, persistence, and configuration structures. |
| "The ORM model proves the database behavior." | Trace actual access code and operations. |
| "An SDK import proves the integration." | Verify actual client creation and calls. |
| "A status enum is a state machine." | Establish actual transitions and transition logic. |
| "The code is messy, so we should describe the cleaner intended design." | Describe the implementation that exists. |
| "We can ignore legacy code." | Include legacy or alternate paths when they affect actual behavior or understanding. |
| "Copying source code is the safest way to be accurate." | Explain behavior and relationships rather than reproducing code. |

## Red Flags

Investigate further when:

- the low-level design is only a list of filenames
- every function has been documented regardless of relevance
- class relationships are inferred from names
- call relationships are claimed without call-site evidence
- interfaces have no identified consumers or implementations
- schemas are described without tracing their use
- important state transitions are missing
- persistence behavior is assumed from model definitions
- external integrations are assumed from dependency declarations
- the diagram contains more elements than can be understood
- implementation detail is being repeated without explaining design significance
- a legacy or duplicate implementation may change which path is actually active

## Verification Gate

The gate is a final coverage check against the evidence already collected. It is not a mandate for additional repository-wide discovery. If a checkbox cannot be fully established within the investigation budget, preserve the uncertainty rather than reopening broad exploration.

Before completing this phase, verify:

- [ ] Major high-level components have been mapped to concrete source artifacts.
- [ ] Important entry points have been identified.
- [ ] Representative workflows have been traced through concrete calls.
- [ ] Important classes and functions have been analyzed at the appropriate level.
- [ ] Important interfaces and contracts have been verified.
- [ ] Significant data structures and schemas have been traced.
- [ ] Persistence implementation has been examined where relevant.
- [ ] External integrations have been traced where relevant.
- [ ] Important state transitions have been examined.
- [ ] Significant algorithms have been identified where relevant.
- [ ] Important error paths have been examined.
- [ ] Configuration-dependent code paths have been considered.
- [ ] Legacy, duplicate, or incomplete paths have been considered.
- [ ] Any low-level diagrams contain evidence-backed relationships.
- [ ] The result is deeper than High-Level Design without becoming a source-code dump.
- [ ] Facts, inferences, and unknowns are distinguishable.

## Output Expectations

### Output boundary
The support and classification mechanisms used during investigation are internal. Do not reproduce evidence annotations, certainty labels, or source-by-source investigation notes in the final Low-Level Design document. Present the resulting design and relationships directly, with natural-language qualifications only where materially necessary.


Return a professional, sufficiently detailed Low-Level Design analysis. Cover the concrete structures and interactions needed for implementation understanding without artificially constraining the document length. Richness should come from synthesis and cross-linking of the collected evidence, not from exhaustive repository inspection.

Organize the result around the major logical components and concrete implementation structures that realize them.

For each significant component, explain the relevant modules, classes, functions, interfaces, data structures, collaborators, state, and important control flows.

Include a precise Mermaid diagram when a class, module, sequence, or state diagram materially improves understanding.

Use source artifacts to establish the design internally and identify important paths precisely. Do not expose the investigation trail or internal confidence classifications in the final document.

Do not reproduce large sections of source code.

Do not recommend refactoring or redesign. Describe the existing low-level design, including important weaknesses or irregularities only when they are necessary to understand how the system works.

The final analysis should allow a reader to answer:

"Which concrete modules, classes, functions, contracts, data structures, state transitions, and internal interactions implement the system's high-level design?"
