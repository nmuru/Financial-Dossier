---
name: requirements
description: Reconstruct the functional and non-functional requirements evidenced by an existing software repository. Use when translating implemented behavior, interfaces, constraints, configuration, security, performance, reliability, and operational characteristics into evidence-backed software requirements.
---

# Requirements Reverse-Engineering Skill

## Objective

Reconstruct the requirements that the repository reveals the system was designed to satisfy.

The goal is not to invent a conventional requirements specification from the application's technology stack. The goal is to infer requirements from concrete evidence such as user workflows, APIs, validation rules, domain models, configuration, authentication, persistence, tests, deployment artifacts, error handling, and documented behavior.

Requirements should explain what the system must do, what constraints it operates under, and what qualities or operational conditions it appears to require.

Clearly distinguish requirements that are directly evidenced from those inferred from implementation behavior.

## When to Use

Use this skill for the Requirements phase of the nine-phase reverse-engineering workflow.

This phase follows Business Purpose and Features. Use those results as supporting context, but verify requirements against repository evidence.

Do not turn implementation details into requirements merely because they exist. A requirement should express a behavior, constraint, rule, or quality attribute that the system appears to need to satisfy.

Do not propose missing requirements unless they are explicitly requested as a separate gap analysis. Unknown or unverified requirements should be identified as such.

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.


## Requirement Model

Reconstruct requirements across these categories where evidence exists:

### Functional requirements

What the system must enable or perform.

Examples include:

- accepting a particular input
- creating, updating, retrieving, or deleting domain information
- executing a business workflow
- authenticating a user
- generating a result
- integrating with another system
- processing asynchronous work
- exporting or importing information

### Business and domain rules

Rules governing how the system behaves within the domain.

Examples include:

- validation rules
- eligibility conditions
- state transitions
- required fields
- uniqueness constraints
- calculation rules
- workflow sequencing
- authorization rules
- business-specific invariants

### Interface requirements

Requirements imposed by the system's interfaces.

Consider:

- HTTP APIs
- request and response schemas
- status codes
- CLI interfaces
- file formats
- events
- messages
- public library APIs
- UI interaction requirements

### Data requirements

Requirements concerning information the system must store, retrieve, validate, transform, or preserve.

Consider:

- required entities
- relationships
- identifiers
- persistence
- data validation
- retention behavior
- serialization formats
- transactional behavior
- consistency constraints

Only infer data retention, durability, or consistency requirements when repository evidence supports them.

### Security requirements

Identify evidenced security requirements such as:

- authentication
- authorization
- role or permission boundaries
- credential handling
- secret management
- input validation
- access restrictions
- session behavior
- transport security
- protection of sensitive information

Do not claim that a system is secure merely because it contains a security library or middleware. Describe the actual evidenced controls and the requirement they imply.

### Non-functional requirements

Reconstruct quality attributes that are supported by repository evidence.

Consider:

- performance
- scalability
- availability
- reliability
- concurrency
- observability
- maintainability
- portability
- compatibility
- configurability
- resource constraints

Use stronger language only when the repository provides strong evidence. For example, repeated timeout handling may support a reliability or responsiveness requirement, but it does not automatically establish a numerical performance target.

### Operational and deployment requirements

Where supported, identify requirements associated with:

- environment configuration
- deployment
- startup and shutdown
- health checks
- logging
- monitoring
- background workers
- scheduled jobs
- external services
- secrets
- infrastructure dependencies
- supported runtime versions

These should be expressed as operational requirements rather than as a technology inventory.

## Bounded Investigation Protocol

This phase must balance evidence quality with completion. The objective is a representative, evidence-backed requirement set, not an exhaustive repository audit.

### Investigation budget

- Complete runtime setup, prior-phase context, and required template/resource reads first.
- Perform at least **two repository evidence passes** before final synthesis, including concrete implementation evidence.
- Normally use **3–5 repository investigation passes**. Batch related files and questions into each pass.
- After the fifth repository investigation pass, stop broad exploration. A sixth pass is permitted only to resolve one material contradiction, blocker, or missing fact that would otherwise materially weaken the requirements.
- After the investigation cutoff, do not continue repository exploration for completeness. Synthesize from the deterministic phase intelligence, prior-phase outputs, and evidence already collected.
- Preserve the final turns for consolidation, quality checking, and document production.

### Investigation passes are portfolios, not checklist items

The workflow below defines coverage objectives, not a requirement to perform one repository read for every numbered step or every bullet. Combine related objectives into efficient evidence passes.

Prioritize, in roughly this order:

1. major user/business workflows and their entry points;
2. externally visible interfaces and important control paths;
3. data, validation, domain rules, and state constraints;
4. security, integrations, configuration, and operational behavior where materially relevant;
5. targeted verification of contradictions, gaps, or high-impact uncertainty.

Use deterministic phase intelligence as the primary index for structural facts already established. Inspect source when behavioral detail is needed, the intelligence is incomplete, or an important claim requires verification. Do not reread source merely to reconstruct information already available in intelligence or previously collected evidence.

### Materiality rule

Not every requirement category deserves equal repository investigation.

**Tier 1 — must establish where applicable:** major functional workflows, significant external interfaces, important data/state constraints, material validation/domain rules, and consequential integrations or security boundaries.

**Tier 2 — investigate when evidence or system context makes them material:** detailed error behavior, configuration branches, non-functional characteristics, operational behavior, tests, and deployment constraints.

**Tier 3 — normally summarize from intelligence or omit:** repetitive UI/boilerplate behavior, framework internals, generated code, and low-impact implementation details that do not materially change a requirement.

### Synthesis protection

As the investigation cutoff approaches, stop broad discovery and transition to synthesis. Complete only a material verification already in progress, then consolidate the requirement set, check for contradictions and unsupported claims, and produce the final document.

If some category cannot be fully established within the evidence budget, state the supported requirement and its material limitation or open question rather than continuing open-ended exploration.

Richness should come from requirement decomposition, cross-linking related behaviors and constraints, and precise synthesis of the collected evidence—not from exhaustive source inspection.

## Investigation Workflow

### Step 1: Establish the feature baseline

Review the major capabilities established during the Features phase.

For each meaningful feature, ask:

"What must be true for this feature to work as implemented?"

Use the answer to identify candidate requirements.

Do not simply convert every feature description into a requirement. Decompose each feature into the behaviors, rules, inputs, outputs, and constraints that make it possible.

### Step 2: Extract explicit requirements

Search for explicit requirement evidence in:

- README files
- product documentation
- API documentation
- specifications
- comments
- configuration descriptions
- test descriptions
- acceptance tests
- issue or planning artifacts present in the repository

Treat explicit documentation as evidence of intended requirements. Verify implementation where possible.

### Step 3: Derive functional requirements from behavior

Trace important workflows and identify the conditions and behaviors they depend upon.

For example, if the repository demonstrates a workflow where a user submits an input and receives a generated result, investigate:

- required input
- validation
- accepted formats
- processing behavior
- error conditions
- output contract
- persistence or side effects
- external dependencies

Translate those observations into requirement statements.

Do not include implementation mechanisms unless they express a genuine system constraint.

### Step 4: Extract domain rules

Inspect:

- validation schemas
- conditional logic
- state machines
- database constraints
- authorization checks
- calculations
- defaults
- enumerations
- workflow transitions
- business service logic

Identify rules that constrain valid system behavior.

Distinguish technical validation from domain rules. For example, a string length restriction may be an interface constraint, while a rule requiring a particular business state before an operation may be a domain requirement.

### Step 5: Reconstruct interface requirements

For each significant external interface, inspect the contract.

Determine:

- inputs
- required and optional fields
- accepted values
- validation
- authentication requirements
- output structure
- error behavior
- side effects
- protocol or format constraints

Do not infer requirements from a route name alone. Trace the route to its handler and downstream behavior.

### Step 6: Reconstruct data requirements

Inspect models, schemas, migrations, database definitions, persistence code, serializers, and consumers.

Determine:

- what information must exist
- relationships between entities
- required versus optional information
- uniqueness or integrity constraints
- lifecycle and state
- persistence behavior
- transformations
- external data dependencies

Do not infer durability or retention requirements solely because a database exists.

### Step 7: Reconstruct security requirements

Trace actual authentication and authorization behavior.

Inspect:

- authentication entry points
- authorization checks
- roles and permissions
- session or token handling
- secret/configuration handling
- input validation
- sensitive-data flows
- protected routes

Express what the repository requires and enforces. Do not convert the presence of a security framework into a claim of comprehensive security.

### Step 8: Reconstruct non-functional and operational requirements

Look for evidence in:

- timeout and retry behavior
- concurrency controls
- caching
- queues
- asynchronous processing
- logging
- metrics
- tracing
- health endpoints
- resource limits
- deployment configuration
- environment variables
- runtime constraints
- test performance assumptions
- graceful shutdown behavior

Infer quality requirements conservatively.

For example, retry logic can indicate a requirement for resilience against transient failures. It does not prove a specific availability percentage.

### Step 9: Compare stated and implemented requirements

Identify discrepancies between:

- documentation and implementation
- tests and implementation
- configuration and runtime behavior
- API contracts and actual handlers
- UI assumptions and backend validation
- intended workflows and reachable workflows

Classify material discrepancies rather than silently reconciling them.

### Step 10: Formulate the requirement set

Write requirements in behavior-oriented language.

Prefer:

"The system must reject requests that omit the repository URL."

over:

"`AnalyzeRequest` contains a required `repo_url` field."

The second is evidence supporting the first.

When a requirement is inferred rather than explicitly stated, label or qualify it appropriately.

## Requirement Quality Standard

A strong reconstructed requirement should identify, where applicable:

- actor or triggering condition
- required behavior
- input or precondition
- business or technical constraint
- resulting outcome
- evidence
- certainty level

Avoid requirements that merely restate implementation.

Weak:

"The system must use FastAPI."

Better:

"The system exposes an HTTP interface through which clients can submit repository-analysis requests."

The framework is an architectural implementation detail unless the repository explicitly establishes it as a constraint.

## Internal Reasoning: Support and Certainty

Use repository analysis to determine whether a requirement is directly established, strongly implied, or insufficiently supported.

Use these distinctions internally to:
- establish whether behavior actually exists
- distinguish implemented behavior from assumptions
- resolve contradictions
- determine how strongly a requirement can be stated
- avoid inventing conventional requirements

Do not expose these internal classifications in the normal Requirements document.

Do not add:
- Evidence
- Evidence Supporting...
- Implementation Evidence
- Source Evidence
- Provenance
- Certainty
- Confidence
- Verified
- Inferred
- Uncertain

as requirement metadata or standalone sections unless the user explicitly requests a traceability, audit, evidence, provenance, or gap-analysis report.

Where documentation and implementation disagree, resolve the difference during analysis and state the resulting requirement and material limitation directly, without exposing the internal classification scheme.

## Anti-patterns and Rationalizations

| Rationalization | Required response |
|---|---|
| "Every feature becomes one requirement." | Decompose features into behaviors, rules, interfaces, and constraints where appropriate. |
| "Every implementation detail is a requirement." | Separate how the system is built from what it must accomplish. |
| "The framework is a requirement because the code uses it." | Treat framework choice as architecture unless repository evidence establishes it as a constraint. |
| "A database means data must be durable forever." | Do not infer retention or durability without evidence. |
| "There is authentication, so the security requirements are complete." | Trace actual controls and identify only evidenced requirements. |
| "Tests prove the complete requirements." | Tests provide strong behavioral evidence but may cover only part of the system. |
| "The README is the requirements specification." | Treat documentation as stated intent and compare it with implementation. |
| "A timeout proves a precise performance target." | Infer resilience or responsiveness only at the level supported by evidence. |
| "A dependency implies a requirement." | Verify actual usage and its role in system behavior. |
| "We should add standard requirements that any system like this should have." | Do not substitute generic best practices for repository evidence. |

## Red Flags

Investigate further when:

- requirements are mostly technology names
- requirements simply duplicate the feature list
- numerical performance targets appear without evidence
- security requirements are inferred solely from security libraries
- data-retention claims are made without persistence or lifecycle evidence
- documentation describes requirements that implementation does not satisfy
- tests cover only a small subset of the claimed behavior
- configuration materially changes behavior but is ignored
- requirements contain words such as "should probably", "normally", or "typically"
- an apparently important requirement has no identifiable implementation evidence

## Verification Gate

Treat this gate as a final coverage and quality check, not as a mandate to reopen repository exploration. Use the collected evidence and deterministic intelligence to determine whether each item is adequately covered. Reopen investigation only for a material contradiction, blocker, or unsupported high-impact claim that falls within the bounded investigation protocol.

Before completing this phase, verify:

- [ ] Major functional requirements have been reconstructed from the feature workflows.
- [ ] Important business/domain rules have been identified.
- [ ] Significant interface contracts and constraints have been examined.
- [ ] Important data requirements have been examined.
- [ ] Evidenced security requirements have been considered.
- [ ] Relevant non-functional requirements have been considered conservatively.
- [ ] Operational and deployment constraints have been considered where supported.
- [ ] Documentation has been compared with implementation.
- [ ] Requirements are distinguished from implementation details.
- [ ] Verified, inferred, and uncertain requirements are distinguishable.
- [ ] Unsupported numerical targets and generic best-practice requirements have been excluded.
- [ ] Important contradictions or gaps are explicitly identified.
- [ ] The result is grounded in repository evidence.

## Output Expectations

### Output boundary
The evidence and certainty model is an internal reasoning mechanism. It must continue to guide investigation, contradiction resolution, and requirement formulation, but must not appear as requirement metadata or a separate evidence/certainty section in the normal Requirements document. Present the resulting requirements directly and comprehensively.


Return a professional, sufficiently detailed Requirements analysis. Requirements should contain enough behavioral and constraint detail to support specification-driven development; do not artificially constrain the document to a fixed page or word count.

Organize the result around meaningful functional, domain, interface, data, security, non-functional, and operational requirements as applicable to the repository.

For each important requirement, provide enough context to explain what the system must do or satisfy, including relevant actors, triggers, inputs, preconditions, rules, constraints, outcomes, interfaces, and quality characteristics. State requirements directly rather than attaching evidence or certainty metadata.

Do not turn the output into a code walkthrough. Source symbols and implementation details should inform the requirement formulation internally rather than becoming the requirement itself.

Do not propose new requirements or redesign the system. If the repository does not establish an important requirement, do not invent one; describe the resulting limitation or open question only when it materially affects understanding of the requirements.

The final analysis should allow a reader to answer:

"What behaviors, rules, interfaces, data constraints, quality attributes, and operational conditions does the repository indicate this system is required to satisfy?"
