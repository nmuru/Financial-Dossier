---

name: business-requirements
description: Reconstruct the business requirements that the software exists to satisfy. Use when identifying the business capabilities, rules, outcomes, stakeholder needs, scope, and constraints implied by repository evidence. The resulting requirements must be technology agnostic. 
-----------------------

# Business Requirements Reverse-Engineering Skill

## Objective

Determine the business requirements that can be defensibly reconstructed from the repository.

This phase answers what the business needs the solution to accomplish and why those needs exist. It must remain distinct from Software Requirements, which describe system behaviour, functionality, and technical constraints.

The Business Requirements analysis must be **technology agnostic**. Requirements must not depend on, prescribe, or describe the frameworks, programming languages, APIs, databases, infrastructure, architecture, or implementation mechanisms used by the repository.

## Core distinction

Business requirements describe required business capabilities, outcomes, rules, and needs.

They answer questions such as:

* What must the business be able to accomplish?
* What must users or business roles be able to achieve?
* What business problem or operational need must be addressed?
* What business rules or constraints govern the activity?
* What outcomes determine whether the need has been satisfied?

Do not convert implementation details into business requirements.

For example:

Incorrect: "The system must use a GraphQL API to retrieve products."

Business requirement: "Customers must be able to access current product information."

Incorrect: "Cart state must be stored in browser cookies."

Business requirement: "Customers must be able to retain their selected items while continuing their shopping activity."

The requirements should remain valid even if the entire software implementation were replaced with a different technology.

## Investigation approach

Examine repository evidence that reveals business intent, including:

* user-facing workflows and capabilities
* domain concepts and business entities
* business rules and validation logic
* user roles and responsibilities
* API and interface behaviour
* documentation and product descriptions
* tests and realistic scenarios
* configuration that reveals business rules or operating constraints
* integrations that reveal external business processes

Use implementation evidence to infer business needs, but do not describe the implementation itself in the final requirements.

Distinguish clearly between:

1. Verified business needs explicitly supported by evidence.
2. Business requirements strongly inferred from recurring implementation behaviour.
3. Unknown or uncertain requirements that cannot be established from the repository.

Do not invent requirements merely because they are common in similar products or industries.

## Required analysis

Determine, where repository evidence permits:

* the business objectives being addressed
* the stakeholders, users, customers, operators, or consuming organisations involved
* the business capabilities required
* the principal business workflows
* important business rules
* required business outcomes
* scope boundaries and exclusions
* important business constraints
* dependencies on external organisations, processes, or services
* requirements that remain uncertain or cannot be established

Avoid repeating the Business Purpose analysis. Business Purpose explains why the software exists. This phase converts that purpose into the specific business needs the solution appears required to satisfy.

## Business Requirements

This is the most important chapter of the output.

State each business requirement as a concise bullet point. Each requirement should normally require only one or a few sentences.

Every requirement must be written in clear, technology-agnostic business language.

Requirements should express a capability, need, rule, or outcome. Where supported by evidence, identify the relevant stakeholder or business role.

Prefer formulations such as:

* "Customers must be able to..."
* "The business must be able to..."
* "Operators must be able to..."
* "The organisation requires..."
* "The process must ensure..."
* "Product information must..."
* "Orders must..."
* "The business must prevent..."

Do not use technical jargon in this chapter unless a technical term is itself an unavoidable domain concept.

Do not mention:

* programming languages
* frameworks
* databases
* APIs
* protocols
* servers
* infrastructure
* source-code structures
* algorithms
* implementation patterns
* deployment mechanisms

Each requirement should stand independently and express what is required, rather than how the repository currently accomplishes it.

Where useful, group requirements by business capability or workflow, using concise but sufficiently detailed bullet points. Do not omit important actors, outcomes, rules, constraints, or acceptance-relevant context merely to keep bullets short.

Do not inflate the number of requirements by splitting one business need into trivial technical sub-requirements.

## Evidence and traceability

Every major requirement must be grounded in repository evidence.

Use technical artifacts during the investigation to establish the requirement, but translate the final requirement into technology-agnostic business language.

When the business intent cannot be established cleanly, resolve the ambiguity during investigation and describe the resulting limitation or open question naturally rather than exposing internal support classifications.

Do not present an unsupported interpretation as an established business requirement.

## Red flags

Investigate further when:

* a supposed business requirement can only be expressed using technology terminology
* a requirement merely describes a software component or implementation mechanism
* multiple technical implementations appear to support the same underlying business need
* documentation and implemented behaviour imply different business needs
* a requirement is inferred solely from a framework, dependency, or project name
* common industry behaviour is being substituted for repository evidence
* the analysis begins to resemble a Software Requirements Specification

When this happens, move the technical detail to the Software Requirements or later implementation-oriented phases and restate the underlying business need.

## Verification gate

Before completing the phase, verify that:

* the requirements are explicitly technology agnostic
* each major requirement describes what is needed rather than how it is implemented
* business requirements are distinguishable from software requirements
* requirements are supported by repository evidence
* unsupported assumptions have not been introduced
* business rules and outcomes have been considered
* scope boundaries and exclusions are identified where evidence permits
* important unknowns are disclosed
* the Business Requirements chapter uses concise bullet points

## Output expectations

Produce a professional, sufficiently detailed Business Requirements analysis. The depth should follow the complexity of the implemented system and should not be artificially constrained by page or word targets.

The document should explain the business context coherently, while the Business Requirements chapter presents requirements clearly and directly. Use enough detail to preserve important business rules, actors, triggers, outcomes, constraints, and acceptance-relevant context; do not artificially compress substantive requirements into minimal bullets.

The final result should enable a business stakeholder to understand what needs the solution is intended to satisfy without requiring knowledge of the technology used to implement it.

The defining quality of this phase is that its requirements remain **technology agnostic**: the requirements should continue to make sense even if the software were redesigned, rewritten, or implemented using an entirely different technology stack.


## Output boundary and depth

Repository evidence and internal support classifications remain investigation mechanisms. They must not become evidence annotations, certainty/confidence labels, or source-trace sections in the normal Business Requirements document.

Produce enough detail for a stakeholder to understand the business need and for downstream specification work to rely on the requirements. Do not artificially shorten the document to meet a fixed page or word count.
