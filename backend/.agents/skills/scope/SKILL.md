---

name: scope
description: Reconstruct the current system boundary and scope of an existing software repository from implementation evidence.

---

# Scope Reverse-Engineering Skill

## Objective

Determine what the existing software is responsible for, where its boundary lies, who and what interacts with it, what major capabilities are inside the boundary, which areas are explicitly or strongly unsupported, and which constraints materially shape the current implementation scope.

Scope is not a product-roadmap exercise. The objective is to document the system as it exists and to distinguish implemented scope from inferred intent and unknowns.

## Core Principle

Do not begin with assumptions about what the product should contain.

Start from observable boundaries:

**actors and entry points → externally visible capabilities → system boundary → external interfaces and dependencies → constraints → supported and unsupported areas**

The repository may not contain a formal scope statement. Reconstruct the strongest defensible scope from documentation, user-facing surfaces, APIs, commands, workflows, integrations, configuration, validation, tests, and implementation relationships.

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.


## Scope Dimensions

Analyze the following dimensions where evidence permits.

### System Boundary

Identify what belongs to the application or system being analyzed.

Consider:

* web applications and pages
* backend services and APIs
* command-line interfaces
* workers and background processes
* libraries or packages that are part of the delivered system
* persistence components
* configuration and runtime support
* generated or embedded assets when they materially affect behavior

Distinguish application code from examples, demos, test fixtures, generated artifacts, vendored code, and unrelated repository material when possible.

### Included Capabilities

Identify the major capabilities implemented within the boundary.

Use externally meaningful behavior rather than merely listing files or functions.

For each major capability, establish:

* who or what invokes it
* what the system does
* what outcome it produces
* which major implementation boundary supports it

Do not turn every helper function into a separate scope item.

### Actors and Interacting Systems

Identify actors and systems that materially interact with the software.

Possible actors include:

* end users
* administrators
* operators
* developers
* researchers
* consuming applications
* scheduled processes
* external services

Possible external systems include:

* APIs
* databases
* identity providers
* model providers
* cloud services
* payment services
* source-control platforms
* messaging systems
* storage systems

Only identify an actor or dependency when repository evidence supports the interaction.

### Interfaces and Boundaries

Identify how the system crosses its boundary.

Examples include:

* HTTP routes
* API endpoints
* CLI commands
* web forms
* webhooks
* SDK interfaces
* environment configuration
* file imports/exports
* external API clients
* database connections
* queues or event interfaces

Explain the role of the interface rather than merely listing its path.

### Exclusions and Unsupported Areas

Identify areas outside current implementation scope only when evidence supports the conclusion.

Strong evidence includes:

* explicit documentation stating a capability is unsupported
* validation or guard logic that rejects a category of operation
* deliberately absent implementation accompanied by explicit limitation language
* clear configuration or provider restrictions
* a documented boundary around the application

Do not say "the system does not support X" merely because X was not found. Prefer wording such as "no repository evidence was found for X" when absence is the only evidence.

### Constraints

Document material constraints that shape current scope.

Examples include:

* supported providers or platforms
* authentication requirements
* repository or payload size limits
* required runtime versions
* environment variables
* external service dependencies
* execution-mode restrictions
* persistence or retention behavior
* concurrency or batch limitations
* known implementation boundaries

State these as current implementation constraints. Do not automatically convert them into desired requirements.

### Unknowns

Scope reconstruction is often incomplete.

Explicitly identify important unknowns such as:

* organizational ownership
* contractual boundaries
* undocumented user roles
* historical exclusions
* intended but unimplemented capabilities
* infrastructure managed outside the repository
* production-only integrations not represented in source

Unknowns are preferable to invented scope.

## Investigation Workflow

### Step 1: Establish repository context

Review deterministic intelligence and identify:

* repository topology
* applications and packages
* documentation
* entry points
* routes and pages
* commands
* integrations
* configuration
* tests

Determine whether the repository contains one coherent system or multiple related artifacts.

### Step 2: Identify externally visible entry points

Inspect the strongest boundaries first:

* application entry points
* API routes
* pages
* CLI commands
* public exports
* webhooks
* scheduled jobs

Determine which are actual runtime surfaces and which are examples or tests.

### Step 3: Trace representative capabilities

For each major boundary, trace at least one meaningful workflow from trigger to outcome.

Prefer workflows that demonstrate why the boundary exists rather than isolated implementation utilities.

### Step 4: Identify external dependencies

Inspect integration candidates and verify material dependencies in source.

Distinguish:

* required runtime dependency
* optional integration
* development-only dependency
* example/demo dependency
* stale or apparently unused dependency

### Step 5: Identify current constraints

Inspect configuration, validation, guards, provider selection, runtime assumptions, and documented limitations.

Verify that a constraint actually affects current behavior before treating it as a scope boundary.

### Step 6: Cross-check documentation against implementation

Look for mismatches between stated scope and implemented scope.

Important mismatches include:

* documented capability without corresponding implementation
* implemented capability missing from documentation
* deprecated or abandoned functionality still described as active
* demo/example behavior mistaken for product scope
* provider or platform claims not supported by current integration code

Report material contradictions explicitly.

### Step 7: Form the scope statement

Construct a concise system-boundary statement that explains:

* what the software is
* what it currently does
* who/what interacts with it
* what major capabilities are included
* what important boundaries or constraints apply

Then support it with concrete evidence.

## Evidence Requirements

Prefer multiple evidence types for major scope conclusions, such as:

* documentation + entry point
* page/route + implementation
* API boundary + integration client
* configuration + runtime usage
* validation + observed behavior
* tests + implementation

Do not treat the following as sufficient by themselves:

* repository name
* directory name
* dependency presence
* isolated symbol name
* generic framework conventions

## Internal Scope Classification

Use calibrated language.

**Verified scope:** Directly implemented and externally observable or strongly established by connected source evidence.

**Strongly inferred scope:** Not explicitly stated, but supported by multiple connected implementation artifacts.

**Partial scope:** The boundary can be reconstructed only in part.

**Mixed scope:** Multiple applications, modes, or purposes create more than one legitimate boundary.

**Unverified boundary:** A plausible boundary exists but source evidence is insufficient.

**Unknown:** The repository does not provide enough evidence to establish the boundary.

## Output Expectations

### Output boundary
The evidence and classification mechanisms used during investigation are internal reasoning controls. Do not create Scope Evidence, certainty, confidence, verified/inferred/unverified, or similar metadata sections in the final document. Present the resulting scope directly, and describe material limitations or open questions naturally where they affect the reader's understanding.


The final document should normally cover the following areas, with depth proportional to the system's actual scope and complexity. Do not artificially constrain the document to a fixed page or word count:


1. Scope Summary
2. System Boundary
3. Included Capabilities
4. Actors and Interacting Systems
5. External Interfaces and Dependencies
6. Constraints and Current Limitations
7. Exclusions / Unsupported Areas
8. Scope Evidence
9. Scope Uncertainties and Unknowns
10. Recommendations

The Recommendations section is a cross-cutting output contract and must be the final section. Recommendations must be grounded in the current implementation and actionable, not generic engineering advice.
