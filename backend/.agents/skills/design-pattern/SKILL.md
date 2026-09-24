---

name: design-pattern
description: Identify and explain recurring software design patterns evidenced by an existing repository. Use when analyzing how responsibilities, object creation, behavior, communication, state, data access, and structural relationships are organized through recurring implementation patterns.
compatibility: opencode
-----------------------

# Design Pattern Reverse-Engineering Skill

## Objective

Identify the software design patterns that are actually evidenced by the repository and explain their role in the implementation.

This phase follows Technology Architecture. Technology Architecture explains the major structural organization of the system and its components. The Design Pattern phase examines recurring implementation-level and structural solutions used within that architecture.

The goal is not to search the repository for familiar pattern names and force the code into them. A design pattern should be identified only when the implementation demonstrates the defining structure and intent of that pattern.

## Scope

Examine recurring approaches to problems involving:

* object or resource creation
* separation of responsibilities
* abstraction boundaries
* component composition
* dependency management
* communication between components
* behavior selection
* state management
* data access
* integration boundaries
* extensibility
* error handling
* cross-cutting concerns

Consider creational, structural, behavioral, architectural-adjacent, and repository-specific patterns where supported by evidence.

The phase may identify familiar patterns such as Factory, Strategy, Adapter, Facade, Repository, Observer, Command, Dependency Injection, Template Method, State, or similar patterns, but only where the repository genuinely demonstrates them.

Framework conventions and common language constructs are not automatically design patterns.

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.


## Investigation Workflow

### Step 1: Identify recurring structures

Inspect the repository for repeated relationships between components rather than isolated code fragments.

Look for:

* common abstractions or interfaces
* interchangeable implementations
* central creation mechanisms
* wrappers around external systems
* layers that simplify complex subsystems
* repeated delegation structures
* event or callback relationships
* command-like operations
* centralized state transitions
* common data-access abstractions
* reusable composition mechanisms

Prioritize patterns that recur across the repository or play an important role in the system's design.

### Step 2: Establish the problem being solved

Before naming a pattern, determine the design problem the structure appears intended to address.

Ask:

* What responsibility is being separated?
* What dependency is being isolated?
* What variation is being accommodated?
* What complexity is being hidden?
* What communication problem is being addressed?
* What behavior is being made interchangeable?
* What lifecycle or state problem is being controlled?

A pattern should explain a meaningful design decision, not merely provide a label for a code structure.

### Step 3: Verify the pattern structure

Compare the observed implementation with the defining characteristics of the candidate pattern.

Identify:

* the participating components
* their responsibilities
* their relationships
* the flow of control or data
* the variation or abstraction being managed

Do not require a textbook-perfect implementation. Adaptations and partial implementations may still represent a recognizable pattern, but their limitations must be stated.

### Step 4: Distinguish patterns from conventions

Do not identify a design pattern solely because:

* a framework encourages a particular structure
* a file or class has a familiar name
* a language feature resembles a pattern
* a dependency provides a pattern internally
* a common application layer exists
* a single isolated implementation happens to resemble a pattern

For example, a service directory does not automatically establish a Service Layer pattern, and a wrapper around one library does not automatically establish an Adapter pattern.

Trace how the structure is actually used.

### Step 5: Identify pattern variants and deviations

Where relevant, determine whether the repository uses:

* a modified version of a known pattern
* a partial implementation
* a framework-specific adaptation
* a combination of multiple patterns
* an informal recurring pattern without a standard name

Describe what the repository actually does rather than forcing it to conform to a canonical textbook implementation.

### Step 6: Evaluate architectural significance

Determine whether each identified pattern is:

* central to the system
* significant within a major subsystem
* localized to a specific feature
* incidental or low-impact

Focus the final analysis on patterns that materially improve understanding of the implementation.

Do not produce a catalog of every possible pattern.

## Pattern Evidence Standard

For every important identified pattern, establish:

1. The pattern or recurring design approach.
2. The problem or concern it addresses.
3. The repository components participating in it.
4. How the implementation demonstrates the pattern.
5. The role the pattern plays in the broader system.
6. Whether the pattern is explicit, strongly evidenced, or an interpretation.

Use source structures as evidence, but explain the pattern in terms of responsibilities and relationships rather than producing a code walkthrough.

## Pattern Classification

Where useful, classify patterns into broad categories:

### Creational

Patterns concerned with creating objects, resources, clients, or other application elements.

### Structural

Patterns concerned with composition, wrapping, adaptation, abstraction, or relationships between components.

### Behavioral

Patterns concerned with communication, delegation, state, commands, events, or changing behavior.

### Data and integration patterns

Recurring approaches to data access, external integrations, abstraction boundaries, or communication with external systems.

### Repository-specific patterns

Recurring solutions that may not correspond precisely to a named textbook pattern but are clearly intentional and important to the repository's design.

Do not classify patterns merely to fill every category.

## Confidence and Evidence

Use calibrated confidence.

**Verified pattern:** The implementation clearly demonstrates the defining structure and purpose of the pattern.

**Strongly evidenced pattern:** The implementation substantially resembles the pattern, although the pattern may not be explicitly named.

**Possible pattern:** The structure has some characteristics of a pattern but insufficient evidence exists to establish intent or complete structure.

Do not present possible patterns as definitive.

When the pattern name itself is uncertain, describe the observed recurring structure rather than forcing a classification.

## Anti-patterns and Rationalizations

| Rationalization                                                        | Required response                                                                   |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| "The file is called Factory, so it is a Factory pattern."              | Verify its responsibilities and creation behavior.                                  |
| "The framework uses this pattern."                                     | Identify whether the repository itself relies on or implements the pattern.         |
| "There is an interface and multiple implementations."                  | Verify whether interchangeable behavior is actually selected or used.               |
| "A wrapper means Adapter."                                             | Determine whether incompatible interfaces are actually being adapted.               |
| "A service layer is automatically a design pattern."                   | Examine whether it establishes a meaningful responsibility boundary.                |
| "Every event listener proves Observer."                                | Verify the relationship between publishers, subscribers, and notification behavior. |
| "The code resembles a pattern."                                        | Establish the design problem and the functional role of the structure.              |
| "We should identify many patterns to make the analysis comprehensive." | Prefer a smaller number of well-supported patterns.                                 |

## Red Flags

Investigate further when:

* pattern names appear without concrete participating components
* the analysis could apply equally to almost any repository
* framework conventions are being presented as deliberate application design
* a pattern is identified from a file name alone
* isolated utility code is being elevated into a repository-level pattern
* the claimed pattern does not explain a meaningful design problem
* multiple incompatible pattern labels could describe the same structure
* the analysis contains more pattern terminology than evidence
* the output becomes a code walkthrough rather than a design analysis

## Verification Gate

Before completing this phase, verify that:

* every major pattern is supported by concrete repository evidence
* the defining structure and role of each pattern have been examined
* framework conventions have not automatically been classified as application patterns
* pattern names are not based solely on file, class, or directory names
* the design problem addressed by each pattern is explained
* important participating components are identified
* uncertain classifications are appropriately qualified
* incidental patterns have not overwhelmed important ones
* the result complements rather than duplicates the Technology Architecture analysis

## Output Expectations

### Output boundary
Confidence and repository-support assessments are internal reasoning controls. Do not reproduce them as confidence labels, evidence annotations, or investigation notes in the final Design Pattern document. Present the resulting pattern analysis directly, with natural-language qualifications only where materially necessary.


Return a professional, sufficiently detailed Design Pattern analysis. Cover all materially significant recurring structures and design approaches without artificially constraining the document length.

Begin with a concise overview of the repository's overall pattern orientation.

For each significant pattern, explain what it is, where it occurs, what problem it addresses, and how the repository implements or adapts it.

Where appropriate, distinguish between deliberate patterns, strongly evidenced recurring structures, and possible interpretations.

Do not attempt to prove that the repository follows a particular design methodology. The purpose of this phase is to reconstruct the recurring design solutions that are actually visible in the implementation.

The final analysis should allow a reader to answer:

"What recurring design patterns or significant design approaches does this repository use, where do they occur, what problems do they solve, and how do they contribute to the implementation?"
