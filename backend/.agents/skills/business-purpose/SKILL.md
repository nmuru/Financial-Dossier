---

name: business-purpose
description: Reconstruct the fundamental purpose and motivating need behind a software repository from repository evidence. Use when determining why the software was created, what need, problem, opportunity, experiment, capability, or objective it serves, who benefits from it, and what outcome its creators appear to have intended.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Business Purpose Reverse-Engineering Skill

## Objective

Determine the most defensible explanation of **why this software exists**.

For an enterprise application, this usually means reconstructing the business need that motivated the application.

However, do not assume that every repository represents an enterprise application or that every software system exists primarily to satisfy a commercial or organizational business need.

The repository may instead exist to:

* solve an operational problem
* automate a technical activity
* enable another system
* provide infrastructure
* demonstrate a technology
* explore a research question
* experiment with a new capability
* prototype an idea
* teach or demonstrate a concept
* provide a reusable library or framework
* serve as a reference implementation
* benchmark an approach
* evaluate a product or platform
* reproduce or investigate an existing system

The task is therefore broader than asking:

"What business problem does this application solve?"

The fundamental question is:

**"What motivating need, problem, opportunity, objective, or purpose appears to have caused this software to be created?"**

When the repository represents an enterprise or organizational application, translate that answer into the business-need perspective where evidence permits.

The output must remain grounded in repository evidence.

Do not infer purpose merely from the repository name, technology stack, fashionable terminology, or assumptions about what similar applications normally do.

## The role of Business Purpose in the reverse-engineering workflow

Business Purpose is the first interpretive phase of the reverse-engineering process.

It establishes the motivation that makes the later phases meaningful.

For an enterprise-oriented system, the conceptual relationship is often:

organizational vision
→ organizational strategy
→ business or operational need
→ enterprise technology response
→ business requirements
→ software requirements
→ design and implementation

The repository will rarely contain enough evidence to reconstruct this entire chain.

Do not invent corporate strategy, organizational vision, or management intent merely because they are absent from the source.

Instead, reconstruct the highest level of motivation that the repository evidence can support.

The preferred outcome for an enterprise application is to identify:

**The business need that the application appears intended to address.**

That business need then provides the conceptual starting point for the next phase, Business Requirements.

For other kinds of repositories, identify the equivalent motivating purpose.

For example:

technology limitation
→ technical need
→ system or tool

research question
→ experimental objective
→ prototype

new technology
→ demonstration objective
→ demonstrator application

developer pain point
→ productivity need
→ library or framework

operational problem
→ operational objective
→ automation or system capability

The agent must determine which model best fits the repository before forcing it into enterprise terminology.

## Core principle

Do not begin by asking:

"What does the code do?"

That question is necessary, but it is insufficient.

The objective is to move through the following chain:

**observable implementation and behavior
→ supported capabilities and workflows
→ problem or objective addressed
→ motivating need or purpose**

The final conclusion should explain why the capabilities appear to exist.

A repository that can "create reports" is not yet understood.

The relevant question is:

"Why would its intended users need those reports, and what outcome does the repository appear intended to enable?"

Similarly, a repository that "uses an AI model" has not thereby revealed its purpose.

The relevant question is:

"What problem, experiment, demonstration, capability, or opportunity motivated the use of the AI model?"

## Determine the purpose model first

Before reconstructing the purpose, determine what broad kind of repository you are investigating.

Do not force a single classification when the repository legitimately serves multiple purposes.

Consider the following purpose models.

### Enterprise or business application

The repository primarily appears intended to help an organization, business, customer, employee, partner, or market-facing process achieve a business outcome.

Look for evidence of:

* customers
* employees
* departments
* business processes
* transactions
* products or services
* revenue-related activity
* compliance
* operational efficiency
* decision-making
* workflow management

The central question becomes:

**"What business or organizational need is this software intended to serve?"**

### Operational or institutional system

The repository may serve an organization without having a commercial business objective.

Examples include:

* laboratory systems
* university systems
* government systems
* research infrastructure
* internal operational tools
* nonprofit applications

The central question becomes:

**"What operational or institutional need motivated this system?"**

### Infrastructure or system software

The repository may primarily enable other software or computing environments.

Examples include:

* databases
* runtimes
* orchestration tools
* monitoring systems
* developer infrastructure
* networking software

The central question becomes:

**"What technical capability or infrastructure problem does this software exist to provide or solve?"**

### Library, framework, SDK, or developer tool

The primary users may be developers or other software systems.

The central question becomes:

**"What capability, abstraction, productivity improvement, integration, or technical problem does this repository provide to its consumers?"**

### Prototype or proof of concept

The repository may exist primarily to validate whether an idea or approach can work.

The central question becomes:

**"What hypothesis, feasibility question, or proposed solution is this implementation intended to demonstrate?"**

Do not mistake incomplete implementation for accidental incompleteness when the repository may intentionally be a proof of concept.

### Technology demonstrator

The repository may exist to demonstrate a new technology, platform, model, framework, integration, or technical technique.

The central question becomes:

**"What technology or capability is being demonstrated, and what aspect of it is the repository intended to make concrete?"**

A technology demonstrator does not require a conventional business problem.

The demonstration objective itself may be the primary purpose.

### Research or experimentation

The repository may exist to investigate a question rather than deliver a finished application.

The central question becomes:

**"What is being explored, evaluated, compared, measured, or learned?"**

Look for experiments, benchmarks, hypotheses, datasets, evaluation logic, alternative implementations, and research-oriented documentation.

### Educational or learning repository

The primary purpose may be teaching, illustrating, or practicing a concept.

The central question becomes:

**"What knowledge, technique, technology, or workflow is the repository intended to teach or demonstrate?"**

### Reference implementation or template

The repository may exist to provide an example for others to copy, adapt, study, or extend.

The central question becomes:

**"What architecture, pattern, technology combination, or implementation approach is the repository intended to exemplify?"**

### Unknown or mixed-purpose repository

Some repositories contain insufficient evidence to establish a single purpose.

Others combine multiple purposes.

For example, a prototype may simultaneously:

* demonstrate a new technology
* explore product feasibility
* provide a learning example

Do not artificially select one purpose if the evidence supports multiple motivations.

State the primary purpose and secondary purposes separately when necessary.

## Required questions

Determine, as far as repository evidence permits:

1. What appears to have motivated the creation of this software?
2. What kind of need, problem, objective, opportunity, experiment, or purpose does the repository address?
3. Which purpose model best fits the repository?
4. Who are the apparent beneficiaries, users, consumers, operators, developers, researchers, or audiences?
5. What activity, workflow, capability, experiment, or outcome does the software enable?
6. What would remain difficult, impossible, inefficient, or unexplored without the software?
7. What evidence most strongly supports the inferred purpose?
8. Is the purpose explicitly stated, strongly implied, partially inferable, or genuinely unknown?
9. Does the implemented behavior support the stated purpose?
10. Are there multiple purposes or audiences?
11. What important aspects of the original motivation cannot be reconstructed from the repository?

Do not force answers where evidence is insufficient.

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.

## Investigation workflow

### Step 1: Establish repository context

Begin with reconnaissance.

Identify:

* repository structure
* major applications or packages
* README files
* documentation
* package metadata
* application entry points
* UI pages
* APIs
* command-line interfaces
* domain models
* schemas
* integrations
* configuration
* tests
* examples
* demos
* benchmarks
* datasets
* infrastructure artifacts

Determine whether the repository contains:

* one coherent system
* multiple related applications
* a monorepo
* examples accompanying a library
* prototypes alongside production code
* generated or vendored material

Do not assume that the repository name accurately describes its purpose.

### Step 2: Classify the repository's apparent purpose model

Before constructing a purpose statement, determine what kind of motivating context best fits the evidence.

Ask:

* Is this solving a business need?
* Is it supporting an organizational operation?
* Is it enabling developers or other systems?
* Is it infrastructure?
* Is it a prototype?
* Is it an experiment?
* Is it demonstrating a technology?
* Is it educational?
* Is it a reference implementation?
* Is it a combination?

Treat this classification as a hypothesis.

Do not finalize it until later evidence supports or challenges it.

### Step 3: Find explicit statements of intent

Inspect the strongest available sources of stated purpose.

Prioritize:

* README files
* project documentation
* product descriptions
* package metadata
* repository descriptions
* application titles
* example descriptions
* architecture documentation
* API documentation
* comments describing intent
* benchmark or experiment descriptions

Record the stated purpose.

Do not automatically accept it as proof of implemented purpose.

Documentation may describe:

* an earlier version
* an aspirational product
* a prototype
* an abandoned direction
* an incomplete implementation

Explicit intent is strong evidence of motivation, but implementation determines whether that intent is reflected in the repository's actual behavior.

### Step 4: Identify externally meaningful behavior

Determine what users or consuming systems can actually do.

For applications, inspect:

* pages
* forms
* routes
* workflows
* API endpoints
* commands
* outputs

For libraries or developer tools, inspect:

* public APIs
* commands
* documented usage
* integration points
* example applications

For experiments, inspect:

* inputs
* experimental variables
* execution paths
* evaluation logic
* outputs
* measurements

Ask:

**"What meaningful capability does this repository make possible?"**

Do not mistake isolated utility functions for the repository's primary purpose.

### Step 5: Identify the problem, need, or objective behind the behavior

For each significant capability, ask why it exists.

Move beyond implementation language.

For example:

"Uploads documents"

is a capability.

Ask:

"Why does the intended audience need documents uploaded?"

"Automates deployment"

is a capability.

Ask:

"What operational or technical burden does deployment automation reduce?"

"Demonstrates a model"

is a capability.

Ask:

"What capability or hypothesis is the demonstration intended to reveal?"

Continue tracing until reaching the highest-level motivation that repository evidence can support.

Do not invent motivations beyond the evidence.

### Step 6: Identify beneficiaries and audiences

Determine who benefits from the software.

Possible beneficiaries include:

* end users
* customers
* employees
* administrators
* developers
* operators
* researchers
* students
* consuming applications
* system owners

For enterprise applications, distinguish between:

* the person using the software
* the organizational unit benefiting from the outcome
* the enterprise need being served

Do not assume these are the same.

For example, an employee may operate a system while the underlying purpose is regulatory compliance or operational control.

### Step 7: Identify domain concepts and purpose signals

Look for recurring concepts in:

* models
* schemas
* APIs
* UI labels
* validation
* services
* events
* configuration
* tests
* fixtures

Determine what these concepts reveal about the problem domain.

Recurring domain concepts are particularly valuable when documentation is weak.

However, do not treat model names as conclusive.

Verify their actual relationships and usage.

### Step 8: Trace a representative meaningful workflow

Identify at least one workflow that demonstrates why the major components exist.

Trace:

external trigger
→ meaningful action
→ application behavior
→ resulting outcome

For an enterprise application, prefer a workflow that connects to an apparent business or operational outcome.

For a technology demonstrator, prefer the workflow that demonstrates the target capability.

For a research repository, prefer the workflow that produces an experiment or evaluation result.

The workflow should explain purpose, not merely control flow.

### Step 9: Identify the "without this software" condition

Ask what need remains if the repository does not exist.

Possible answers include:

* a manual process remains manual
* a technical capability is unavailable
* a system cannot integrate with another system
* an experiment cannot be conveniently performed
* a technology cannot be practically demonstrated
* developers must repeatedly solve the same problem
* an organizational workflow remains unsupported

This question often reveals the motivating need more clearly than a list of features.

Do not invent a pain point merely to make the repository sound commercially important.

### Step 10: Cross-check stated intent against implemented evidence

Compare documentation with:

* actual entry points
* primary workflows
* domain models
* public interfaces
* tests
* runtime behavior
* examples

Look for:

* documented purpose without implementation support
* implemented capabilities absent from documentation
* prototype-only behavior
* placeholder functionality
* competing purposes
* deprecated functionality
* example code mistaken for the product
* declared integrations that are not active

When contradictions materially affect the purpose conclusion, state them explicitly.

### Step 11: Form the purpose hypothesis

Construct a concise primary purpose statement.

Use the appropriate conceptual form.

For a business application:

**The business purpose is to address [business or operational need] by enabling [core capability or workflow], producing [intended organizational outcome] for [beneficiary].**

For an enterprise or business application, the final Business Purpose statement should be expressed primarily in business terms: the business need, problem, opportunity, or objective; who or what in the business benefits; and the outcome the software enables. Describe technology only to the extent necessary to explain how the business need is addressed.

The phrase "business purpose" should not be reduced to a description of what the software technically does. Move from the observable capability to the underlying business need and outcome. For example, "provides an online storefront" is a capability; the business purpose may be to give businesses a cost-effective and practical way to establish an online sales channel, when the repository evidence supports that interpretation.

For repositories that are not enterprise or business applications, do not force a business interpretation. Use the appropriate purpose model below and describe the motivating technical, operational, research, educational, demonstrator, developer, or other objective instead.

For infrastructure or developer software:

**The repository appears to exist to provide [technical capability or abstraction] that enables [users or systems] to [achieve outcome or avoid technical problem].**

For a demonstrator:

**The repository appears primarily intended to demonstrate [technology or capability] by implementing [representative scenario or workflow].**

For research:

**The repository appears intended to investigate or evaluate [question, hypothesis, or approach] through [experimental mechanism].**

For a mixed-purpose repository:

State the primary purpose first and explicitly identify secondary purposes.

### Step 12: Test the hypothesis against the entire repository

Ask:

* Does the major functionality support this purpose?
* Do the central domain concepts make sense under this interpretation?
* Do the primary workflows support it?
* Does the purpose explain why the main components exist?
* Is a simpler explanation more consistent with the evidence?
* Is the conclusion dependent on one weak clue?
* Could the repository instead be a demo, template, experiment, or example?

Revise the hypothesis if the evidence does not hold together.

## Evidence requirements

A strong purpose conclusion should use multiple evidence types where available.

Prefer combinations such as:

* documentation + implemented workflow
* domain concepts + user-facing behavior
* public API + consuming examples
* experiment description + evaluation logic
* tests + implementation
* configuration + actual integration usage

Do not treat any of the following as sufficient evidence by themselves:

* repository name
* technology stack
* dependency list
* directory name
* single model name
* generic README tagline

For each major conclusion, identify the relevant repository artifacts.

## Internal Reasoning Classification

Use calibrated conclusions.

**Verified purpose:** Explicitly stated and materially supported by implementation evidence.

**Strongly inferred purpose:** Not directly stated, but strongly supported by connected workflows, domain concepts, interfaces, and implementation.

**Partial purpose:** Some motivation is evident, but the full problem or intended outcome cannot be established.

**Mixed purpose:** Multiple legitimate purposes are supported by evidence.

**Unverified hypothesis:** A plausible interpretation exists, but the evidence is too weak to treat it as established.

**Unknown:** The repository does not provide enough evidence to reconstruct its motivating purpose.

Do not force certainty where the original organizational context has been lost.

## Anti-patterns and rationalizations

| Rationalization                                                           | Required response                                                                                                                                  |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Every repository has a business purpose."                                | First determine whether the repository is an enterprise application, system tool, experiment, demonstrator, library, prototype, or something else. |
| "The repository name tells us why it exists."                             | Treat the name as a clue only. Verify purpose through behavior and evidence.                                                                       |
| "The technology stack tells us the purpose."                              | Technology explains implementation choices, not necessarily motivation.                                                                            |
| "The README already explains the purpose."                                | Cross-check stated intent against implementation.                                                                                                  |
| "This looks like a common application, so we know the problem it solves." | Do not substitute industry stereotypes for repository evidence.                                                                                    |
| "The code is incomplete, so we should infer the finished product."        | Describe what is supported and explicitly identify uncertainty.                                                                                    |
| "A demo has no real purpose."                                             | Demonstrating or evaluating a technology may itself be the primary purpose.                                                                        |
| "A library does not have a business purpose."                             | Reconstruct the user, developer, or system need the library exists to address.                                                                     |
| "The most sophisticated feature must be the purpose."                     | Determine whether it is central to the repository's actual workflow.                                                                               |
| "The user and the beneficiary are obviously the same."                    | Distinguish operator, consumer, and organizational beneficiary where relevant.                                                                     |
| "We should infer the company's strategy from the application."            | Reconstruct only the highest-level motivation supported by repository evidence.                                                                    |
| "Purpose means explaining every feature."                                 | Purpose explains why the important features collectively exist. Features are analyzed separately.                                                  |

## Red flags

Investigate further when:

* the conclusion only describes technology
* the conclusion could apply to thousands of unrelated repositories
* no distinction has been made between purpose and functionality
* enterprise terminology has been forced onto a technical repository
* a demo or experiment has been incorrectly treated as a product
* the repository contains multiple unrelated systems
* examples have been mistaken for the main application
* the README and implementation describe different purposes
* the main domain concepts are unused
* the apparent core workflow leads only to placeholders
* the proposed purpose depends on a single weak clue
* the purpose statement does not explain why the major components exist
* organizational strategy has been invented without evidence
* the analysis cannot explain what need or objective would remain without the software

## Verification gate

Before completing this phase, verify:

* [ ] The repository's likely purpose model has been considered rather than assumed.
* [ ] Enterprise business need has been used when appropriate but not forced onto other repository types.
* [ ] The proposed purpose is supported by concrete repository evidence.
* [ ] Explicit statements of intent have been checked against implementation where possible.
* [ ] At least one representative meaningful workflow has been traced where the repository permits it.
* [ ] The apparent beneficiaries, users, consumers, or audiences are supported by evidence.
* [ ] Core domain concepts or equivalent technical concepts have been considered.
* [ ] The analysis distinguishes capability from motivating need or objective.
* [ ] The analysis considers what problem, limitation, opportunity, or objective would exist without the software.
* [ ] Multiple purposes are acknowledged where evidence supports them.
* [ ] Important contradictions and implementation gaps are disclosed.
* [ ] Facts, inferences, hypotheses, and unknowns are distinguishable.
* [ ] The conclusion does not rely primarily on repository naming or technology terminology.
* [ ] The resulting purpose provides a meaningful conceptual starting point for the Business Requirements phase.

If these conditions cannot be satisfied because the repository is incomplete or lacks historical context, state the limitation explicitly.

## Output expectations

### Output boundary
The certainty and support distinctions used during investigation are internal reasoning controls. Do not reproduce them as labels, metadata, evidence sections, or confidence statements in the normal Business Purpose document. Present the resulting purpose model and conclusions directly. The document may describe material limitations or open questions when they are necessary for an accurate understanding.


Return a professional, comprehensive but focused Business Purpose analysis. The depth should be proportional to the complexity and ambiguity of the repository; do not artificially shorten the document. The reasoning and conclusions must be grounded in repository analysis, but the final document should present the resulting purpose model directly rather than reproducing the investigation trail or internal confidence classifications.

Do not reproduce the investigation process.

Synthesize the repository findings into a coherent explanation of the repository's motivating purpose.

Begin by identifying the most appropriate purpose model:

* enterprise/business need
* operational need
* technical capability
* infrastructure enablement
* developer enablement
* prototype
* research
* experimentation
* technology demonstration
* education
* reference implementation
* mixed or unknown purpose

Then explain the strongest repository-supported answer to:

**"Why was this software created?"**

For an enterprise-oriented application, clearly identify the apparent business or organizational need and the outcome the application is intended to enable.

For other repository types, identify the equivalent motivating objective without artificially translating it into business language.

Explain the relationship between:

**motivating need or objective
→ core capability or workflow
→ intended outcome
→ beneficiary or audience**

Include important uncertainty and contradictions.

Do not analyze technology in depth unless it materially helps establish purpose.

Do not provide detailed requirements, architecture, design, implementation mechanics, testing analysis, or future recommendations in this phase.

Those belong to later phases.

The completed analysis should allow a reader to answer:

**"What motivating need, problem, opportunity, objective, or purpose caused this software to exist, who or what benefits from it, and what fundamental outcome is it intended to make possible?"**

## Runtime Resource Usage

The harness supplies the selected skill together with a runtime resource inventory. The available resources may include an output template, checklist, schema, domain artifact, example, reference material, or other skill-specific files.

Use the generic runtime-resource tools when a supplied resource is needed:
- `list_resources` discovers the files available to this phase.
- `read_resource` reads a supplied resource using its resource-relative path.

For this phase, read `OUTPUT_TEMPLATE.md` when it is supplied and use it as the required structural starting point for the final document. Other supplied artifacts should be consulted when relevant to the methodology or when they provide information needed to complete or verify the phase.

Do not use repository `read_file` to access these runtime resources, and do not construct host filesystem paths. Runtime resources are not repository evidence and must not be represented as evidence of implementation behavior.

The resource set is extensible. Do not assume that only the currently known artifact types exist; use the runtime inventory to determine what is actually available.
