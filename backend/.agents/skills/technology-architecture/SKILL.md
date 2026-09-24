---
name: technology-architecture
description: Reconstruct the actual technology architecture of a software repository and produce an evidence-backed architecture diagram. Use when identifying technologies, runtime components, boundaries, data stores, external systems, deployment relationships, and communication flows.
---

# Technology Architecture Reverse-Engineering Skill

## Objective

Produce a rigorous reconstruction of the repository's actual technology architecture.

The analysis must explain what technologies and runtime components exist, how they are connected, where they execute, how they communicate, what data stores and external systems are involved, and which architectural claims are verified versus inferred.

This phase must produce an architecture diagram. The diagram is a first-class deliverable, not an optional illustration.

The architecture must be reconstructed from repository evidence. Do not produce a generic architecture diagram based on the frameworks that appear in a dependency file.

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.


## Architecture scope

Cover the architectural dimensions that the repository supports:

- Client and presentation layer
- API and interface layer
- Application and service components
- Domain or business-logic components
- Persistence and data stores
- Messaging and asynchronous components
- External services and integrations
- Authentication and authorization boundaries
- Configuration and environment boundaries
- Build and runtime boundaries
- Deployment and infrastructure components
- Major libraries or frameworks only when they materially affect architecture
- Important communication and data flows

Do not force layers that do not exist.

A small repository may have a simple architecture. A monorepo may contain several applications or services. An incomplete repository may support only a partial architecture.

## Diagram requirement

Every completed Technology Architecture analysis MUST contain a diagram representing the architecture evidenced by the repository.

The preferred format is Mermaid flowchart syntax when the output channel supports Markdown code blocks. Use a clear directed graph with meaningful component names and labeled relationships.

The diagram should show, where applicable:

- users or external clients
- frontend/application entry points
- backend services
- major internal components
- databases and other stores
- external APIs/services
- queues or asynchronous infrastructure
- important authentication boundaries
- major runtime or deployment boundaries
- principal request/data flows

Do not create decorative diagrams.

Every significant node and relationship must be supported by repository evidence.

If the repository does not support a particular relationship, do not draw it merely because it is conventional.

When a visual image-generation capability is actually available to the agent, it may be used to produce a polished architecture image, but image generation must never be assumed. The default deliverable is a precise Mermaid diagram that can be rendered by the consuming application.

Do not represent the diagram as an invented screenshot or artistic illustration.

## Diagram discipline

Use the diagram to communicate the major architecture at a glance, not implementation trivia. When in doubt, omit or group a detail rather than adding another node.

## Diagram size and abstraction

The primary architecture diagram MUST be a high-level conceptual diagram intended for human comprehension.

Prefer approximately 5 to 10 major nodes. Include only the components necessary to explain the main runtime architecture and primary data or request flows.

Group implementation details into their parent architectural component. For example, middleware, individual libraries, helper modules, individual API routes, development tooling, static asset providers, and internal utility functions should normally not appear as separate diagram nodes.

Do not attempt to represent every technology, dependency, source module, external URL, configuration artifact, or dormant component in the primary diagram.

If additional architectural detail is important, explain it in the accompanying narrative rather than adding more nodes to the primary diagram.

The diagram should allow a reader to understand the system at a glance. Prefer abstraction and grouping over completeness of implementation detail.

Prefer:

User → Next.js Frontend → FastAPI API → Analysis Service → Repository Workspace

over a diagram containing every Python function.

Show technologies when they materially identify a runtime component, for example:

Next.js / React

FastAPI

PostgreSQL

Redis

OpenCode Agent

Do not show every dependency package.

Use arrows to represent actual communication, invocation, data movement, or dependency relationships.

Label important relationships where the direction alone is ambiguous.

Examples:

`HTTP/JSON`

`SQL`

`REST API`

`message`

`filesystem`

`subprocess`

Do not label a relationship with a protocol unless repository evidence supports it.

If a relationship is inferred rather than verified, make that status clear in the surrounding explanation and, where useful, in the diagram label.

## Investigation workflow

### Step 1: Establish system boundaries

Identify the major executable or deployable units in the repository.

Determine whether the repository contains:

- frontend applications
- backend services
- APIs
- workers
- command-line programs
- libraries
- databases or persistence layers
- infrastructure definitions
- external integration clients
- scheduled or event-driven processes

Determine which components appear to form the active system.

Do not assume that every package or directory is deployed.

### Step 2: Identify entry points

Find the actual runtime entry points.

Inspect:

- application startup files
- server initialization
- frontend entry points
- route registration
- CLI entry points
- worker startup
- scheduled jobs
- event consumers
- container entrypoints
- deployment commands

Trace entry points into the application rather than relying only on directory structure.

### Step 3: Identify technology evidence

For each significant architectural component, establish the technology from concrete evidence.

Use:

- dependency manifests
- imports
- framework initialization
- configuration
- deployment files
- build scripts
- runtime commands
- infrastructure definitions

Distinguish:

- declared dependency
- imported dependency
- initialized component
- actively used component
- deployed component

These are not equivalent.

### Step 4: Reconstruct component boundaries

Group implementation artifacts into meaningful architectural components.

A component should represent a meaningful runtime, service, subsystem, or architectural responsibility.

Examples:

- Web frontend
- API server
- Authentication service
- Analysis engine
- Repository workspace manager
- Persistence layer
- Background worker
- External model provider

Do not create a component for every module or directory.

For each component, identify:

- responsibility
- implementation location
- runtime technology
- inputs
- outputs
- dependencies
- state or persistence
- external interactions

### Step 5: Trace communication flows

Trace important calls and data flows across component boundaries.

Inspect:

- HTTP clients and routes
- function/service boundaries
- database access
- ORM configuration
- message producers and consumers
- SDK clients
- subprocess execution
- filesystem interactions
- environment/configuration dependencies

Determine the actual direction of communication.

Do not infer bidirectional communication merely because two components reference one another.

### Step 6: Identify data stores

Find actual persistence and storage mechanisms.

Inspect:

- database configuration
- schemas
- migrations
- models
- repositories
- ORM initialization
- cache configuration
- object/file storage
- filesystem workspaces

Determine what component accesses each store and what information appears to be stored there.

Do not call a temporary directory a database or persistent store.

Do not infer persistence merely because domain models exist.

### Step 7: Identify external systems

Identify external dependencies that materially participate in runtime behavior.

Examples:

- payment providers
- authentication providers
- cloud services
- model providers
- Git repositories
- email services
- storage services
- third-party APIs

For each, determine how the repository connects to it and what role it plays.

A package capable of accessing a service does not establish that the service is actually used.

### Step 8: Identify runtime and deployment boundaries

Inspect deployment and infrastructure artifacts where present:

- Dockerfiles
- compose files
- Kubernetes manifests
- cloud configuration
- process managers
- CI/CD workflows
- environment files
- startup scripts
- package scripts

Determine where major components execute and which components communicate across process, container, host, or network boundaries.

If deployment evidence is absent, do not invent a deployment topology.

### Step 9: Identify configuration boundaries

Determine which architectural behavior depends on:

- environment variables
- configuration files
- feature flags
- provider selection
- runtime options
- secrets
- external endpoints

Configuration can change the actual architecture. For example, a configurable model provider may mean that the conceptual architecture should show a provider boundary rather than a single hard-coded provider.

### Step 10: Separate architecture from implementation detail

Do not allow the architecture diagram to become a call graph.

Include a component when it has meaningful architectural responsibility or represents an important runtime boundary.

Keep detailed class, function, algorithm, and line-level relationships for the Low-Level Design and Implementation Detail phases.

### Step 11: Reconcile documentation and implementation

Compare architecture claims in:

- README files
- architecture documentation
- diagrams
- deployment documentation
- configuration
- comments

against actual implementation.

Identify material differences between intended architecture and implemented architecture.

If a documented component cannot be found, mark it as unverified rather than placing it in the verified architecture.

## Internal Architecture Classification

Classify architectural elements according to evidence:

**Verified:** The repository directly establishes the component, technology, or relationship.

**Strongly inferred:** Multiple artifacts support the architectural interpretation, but no single artifact proves it completely.

**Unverified:** Documentation or configuration claims the component or relationship, but implementation evidence is insufficient.

**Apparently unused/legacy:** The artifact exists but no credible active path to it was found.

Use these classifications only during internal reasoning. Do not reproduce the labels in the final document; describe material limitations or open questions in natural language.

## Technology selection rules

Do not produce technology inventories merely for completeness.

A technology belongs in the architecture when it materially affects:

- runtime behavior
- component boundaries
- communication
- persistence
- deployment
- build/runtime execution
- security
- external integration

For example, an HTTP framework used to expose the backend is architecturally relevant. A small formatting library usually is not.

Do not infer production use from development-only dependencies.

Do not infer deployment from development tooling.

## Architecture quality criteria

A good architecture reconstruction should allow a reader to answer:

- What are the major runtime components?
- What technology implements each component?
- Where does each component run?
- How do components communicate?
- Where does state live?
- Which external systems are involved?
- What are the major trust or security boundaries?
- What configuration changes the architecture?
- Which relationships are verified versus inferred?
- What architectural behavior cannot be established from the repository?

## Anti-patterns and rationalizations

| Rationalization | Required response |
|---|---|
| "The dependency file gives us the architecture." | Dependencies are evidence, not architecture. Trace actual initialization and usage. |
| "React means there is a standard frontend/backend architecture." | Reconstruct the actual runtime boundaries from the repository. |
| "There is a database library, so the application uses a database." | Verify configuration, initialization, access code, and actual consumers. |
| "Every package should be a diagram node." | Group code into meaningful architectural components. |
| "The README architecture diagram is probably correct." | Compare it with implementation and deployment evidence. |
| "A cloud SDK means the system uses that cloud service." | Verify actual runtime calls and configuration. |
| "The API and frontend communicate because both exist." | Identify the actual client calls, routes, or other communication evidence. |
| "A temporary filesystem workspace is persistent storage." | Distinguish temporary execution state from durable persistence. |
| "We need a visually impressive diagram." | Accuracy and evidence matter more than decoration. |
| "A missing deployment configuration can be filled in from common practice." | Do not invent deployment topology. |
| "The model/provider is obvious from one configuration default." | Check how provider selection is actually wired and whether it is configurable. |

## Red flags

Investigate further when:

- the architecture diagram looks like a generic framework template
- every dependency appears as a component
- the diagram contains relationships not traceable in source
- frontend/backend communication is assumed rather than verified
- a database is shown without persistence evidence
- external services appear only in documentation
- deployment boundaries are inferred without deployment artifacts
- development tools are presented as production components
- the diagram has no distinction between runtime components and source-code modules
- the architecture cannot explain the main user workflows identified in earlier phases
- multiple competing architectures appear to exist in the repository

## Verification gate

Before completing this phase, verify:

- [ ] Major executable/runtime components have been identified.
- [ ] Actual technology choices are supported by repository evidence.
- [ ] Major component responsibilities are clear.
- [ ] Important communication paths have been traced.
- [ ] Data stores and persistence mechanisms have been verified where applicable.
- [ ] External systems have been verified where applicable.
- [ ] Runtime/deployment boundaries have been examined where evidence exists.
- [ ] Configuration that materially affects architecture has been considered.
- [ ] Documentation has been reconciled with implementation.
- [ ] The architecture diagram contains only evidence-backed or explicitly qualified relationships.
- [ ] The diagram is readable and communicates meaningful component boundaries.
- [ ] Implementation details have not overwhelmed the architecture.
- [ ] Important unknowns and ambiguities are stated.
- [ ] The architecture explains the major workflows identified in earlier phases.

## Required Output

### Output boundary
Repository support and architecture classifications are internal reasoning mechanisms. Do not reproduce evidence trails, certainty/confidence labels, or source-by-source investigation notes in the final architecture document. Present the resulting architecture directly and use natural-language qualifications for material limitations or open questions.


Return a professional, sufficiently detailed Technology Architecture analysis. Cover all materially significant runtime components, boundaries, flows, state ownership, and deployment context without artificially constraining the document length.

The output MUST include a rendered or renderable architecture diagram. Prefer Mermaid flowchart syntax when the response format supports it.

The analysis should explain the diagram and the major components and relationships it represents. Do not reproduce the investigation trail or attach evidence/certainty metadata to architecture elements.

For each significant architectural component, describe:

- name
- responsibility
- technology
- runtime/deployment context where known
- principal inputs and outputs
- important dependencies
- evidence and certainty

Then explain the major communication and data flows.

Present the architecture directly. Where the implementation does not establish an architectural detail, describe the limitation or open question in natural language rather than using verification-status labels.

Do not provide detailed class-level or function-level design except where necessary to prove an architectural relationship.

Do not recommend architectural improvements in this phase. Future improvements belong to the Future Directions phase.

The final analysis should allow a reader to answer:

"What is the actual technology architecture of this system, what are its major runtime components and boundaries, how do they communicate, where does state live, and what constraints or implementation details establish that architecture?"
