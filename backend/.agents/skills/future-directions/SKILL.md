---
name: future-directions
description: Derive evidence-backed future directions, limitations, risks, and improvement opportunities for an existing software repository. Use when assessing what should realistically evolve next based on current architecture, requirements, implementation, testing, and observed gaps.
---

# Future Directions Reverse-Engineering Skill

## Objective

Identify realistic future directions for the software based on what the repository actually contains.

This phase is deliberately different from generic brainstorming. Recommendations must emerge from evidence gathered in the earlier phases: business purpose, features, requirements, technology architecture, high-level design, low-level design, implementation detail, and testing.

The objective is to explain where the system could reasonably go next, why those directions matter, what current limitations or risks motivate them, and what evidence supports each recommendation.

Do not invent a product roadmap.

Do not recommend changes merely because they are fashionable, technically elegant, or common in similar systems.

## Relationship to earlier phases

Use the earlier phase results as the primary foundation.

Business Purpose establishes why the system exists.

Features establish what it currently does.

Requirements establish what it needs to satisfy.

Technology Architecture and High-Level Design establish its structural constraints.

Low-Level Design and Implementation Detail reveal implementation limitations, technical debt, coupling, configuration constraints, and operational behavior.

Testing Harness reveals verification gaps and reliability risks.

Future Directions synthesizes these findings into realistic next steps.

This phase should answer:

"Given what this repository is, how it is built, what it currently does, and where its evidence shows limitations, what are the most credible directions for its future evolution?"

## Direction categories

Consider the following categories where evidence supports them:

- Product or capability evolution
- Functional completeness
- Architecture evolution
- Scalability
- Reliability and resilience
- Security
- Observability and operations
- Testing and verification
- Maintainability
- Developer experience
- Deployment and infrastructure
- Performance
- Data management
- Integration strategy
- Configuration and provider flexibility
- Technical debt reduction

Do not force every category into the analysis.

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.


## Investigation workflow

### Step 1: Establish the current-state baseline

Review the conclusions from all earlier phases.

Identify:

- core purpose
- major current features
- key requirements
- architecture
- major design characteristics
- implementation constraints
- testing maturity
- known unknowns

Do not propose future directions until the current state is understood.

### Step 2: Identify explicit future intent

Search the repository for evidence of planned or intended evolution:

- TODOs
- FIXME comments
- roadmap documents
- issue references
- planning files
- changelogs
- deprecated APIs
- feature flags
- experimental modules
- placeholder implementations
- commented-out future functionality
- migration plans

Treat these as evidence of intent, not commitments.

An explicit TODO is not automatically a high-priority recommendation.

### Step 3: Identify functional gaps

Compare the Business Purpose, Features, and Requirements results.

Look for:

- stated capabilities that are incomplete
- requirements that are only partially satisfied
- workflows that terminate prematurely
- important error cases that are unsupported
- missing integrations required by existing workflows
- placeholder behavior
- incomplete user journeys

Only identify a gap when the repository provides evidence.

### Step 4: Identify architectural constraints

Review the Technology Architecture and High-Level Design.

Look for structural constraints such as:

- tightly coupled components
- single-process assumptions
- provider-specific coupling
- lack of clear persistence boundaries
- synchronous processing where repository behavior creates scalability constraints
- limited deployment flexibility
- shared state
- fragile integration boundaries
- configuration limitations

Do not label something a problem simply because a different architecture would be more modern.

Explain the concrete consequence supported by repository evidence.

### Step 5: Identify implementation and maintainability risks

Review Low-Level Design and Implementation Detail.

Look for:

- duplicated logic
- dead or legacy code
- placeholder implementations
- excessive coupling
- inconsistent abstractions
- hard-coded configuration
- provider lock-in
- fragile error handling
- unclear ownership
- difficult-to-test code
- obsolete dependencies
- duplicated configuration
- large components with multiple responsibilities

Only elevate an observation into a future direction when it has a meaningful consequence.

### Step 6: Identify testing and verification gaps

Review the Testing Harness phase.

Determine whether important future work should address:

- missing unit tests
- missing integration tests
- missing end-to-end coverage
- untested failure paths
- mocked integrations that need real boundary verification
- weak CI gates
- missing regression coverage
- insufficient test isolation
- important unverified requirements

Do not recommend "more tests" generically. Identify what important behavior requires stronger verification and why.

### Step 7: Identify operational and scalability directions

Where evidence supports it, examine:

- performance constraints
- resource-intensive operations
- synchronous bottlenecks
- retry behavior
- timeouts
- concurrency
- queueing
- caching
- observability
- deployment complexity
- reliability
- recovery behavior

Do not claim scalability problems without evidence of a relevant constraint or expected workload.

### Step 8: Identify security and resilience directions

Consider future directions suggested by:

- authentication gaps
- authorization gaps
- secret handling
- input validation
- external trust boundaries
- error exposure
- dependency vulnerabilities
- missing auditability
- lack of resilience around external services

Do not perform a full security audit unless the repository provides evidence requiring one. Phrase these as evidence-backed areas for further strengthening.

### Step 9: Identify strategic technical directions

Determine whether the repository's architecture suggests realistic evolution such as:

- provider abstraction
- modularization
- service separation
- asynchronous processing
- persistence evolution
- improved integration boundaries
- deployment automation
- observability
- extensibility

A technical direction should connect to a concrete current-state constraint or opportunity.

### Step 10: Prioritize directions

Do not produce an unranked list of every possible improvement.

Prioritize directions using factors such as:

- impact on the core business purpose
- severity of the current limitation
- strength of current-state support
- implementation feasibility
- architectural leverage
- risk reduction
- dependency on other work

A useful priority model is:

**High priority:** Addresses a material limitation, risk, or incomplete core capability with strong repository evidence.

**Medium priority:** Meaningfully improves reliability, maintainability, extensibility, or user value but is not immediately blocking.

**Longer-term:** Strategic evolution that becomes valuable as scale, complexity, or product scope increases.

Do not assign priority merely because an item is technically interesting.

## Recommendation structure

For each significant future direction, explain:

- Current-state basis
- Limitation or opportunity
- Proposed direction
- Expected benefit
- Dependencies or prerequisites
- Priority
- Recommendation rationale

The proposed direction should be concrete enough to guide future engineering work but should not become a detailed implementation plan.

For example, prefer:

"Move repository analysis from a single synchronous request path toward asynchronous job execution if repository analysis duration continues to approach API timeout limits."

over:

"Use Celery and Redis."

The first expresses the direction and the current-state motivation. The second prematurely selects implementation technology without establishing that it is necessary.

## Evidence discipline

Every major recommendation should be traceable to an earlier phase finding or concrete repository evidence.

Useful evidence includes:

- incomplete workflows
- explicit TODOs
- configuration constraints
- architectural coupling
- measured or configured timeouts
- error-handling gaps
- test gaps
- deployment constraints
- provider-specific code
- duplicated implementation
- documented roadmap items

Do not use generic industry practice as the primary justification.

## Distinguish evidence from speculation

Use clear confidence levels:

**Evidence-backed:** Directly supported by repository findings.

**Strongly justified:** Supported by multiple current-state findings, although the repository does not explicitly propose the direction.

**Exploratory:** A plausible longer-term direction that depends on future scale, product scope, or requirements not established by the repository.

Exploratory directions should be clearly labeled and should not be presented as necessary changes.

## Anti-patterns and rationalizations

| Rationalization | Required response |
|---|---|
| "Every software project should move to microservices." | Recommend architectural separation only when current evidence establishes a meaningful need. |
| "The code should use the newest framework." | Technology upgrades require repository-specific justification. |
| "Add AI because the project could use AI." | Future directions must connect to the actual business purpose and evidence. |
| "The TODO list is the roadmap." | TODOs are evidence of intent, not proof of priority or feasibility. |
| "Add more tests." | Identify specific unverified behavior and the test level needed. |
| "Scale the database." | Establish an actual data or workload constraint first. |
| "Rewrite the codebase." | Prefer targeted evolution unless evidence demonstrates that the current design prevents required behavior. |
| "Adopt a standard architecture." | Describe why the existing architecture creates a concrete limitation before recommending change. |
| "Use a particular technology because it is popular." | Recommend outcomes and directions first; technology selection belongs to a later engineering decision. |
| "Fix everything that looks imperfect." | Prioritize material risks and opportunities rather than cosmetic improvements. |

## Red Flags

Investigate further when:

- recommendations are generic enough to apply to any repository
- every category produces a recommendation regardless of evidence
- future directions simply repeat TODO comments
- recommendations specify technologies without establishing the need
- architectural rewrites are proposed without a current-state limitation
- security recommendations are unsupported by repository evidence
- scalability recommendations lack workload or architectural evidence
- test recommendations do not identify the behavior being verified
- speculative product features dominate the analysis
- recommendations contradict the repository's business purpose
- the priority order appears arbitrary
- current-state uncertainty is being treated as a known problem

## Verification Gate

Before completing this phase, verify:

- [ ] The current state has been grounded in the earlier phases.
- [ ] Explicit roadmap or TODO evidence has been considered where present.
- [ ] Functional gaps are evidence-backed.
- [ ] Architectural constraints are evidence-backed.
- [ ] Implementation and maintainability risks have been considered.
- [ ] Testing and verification gaps have been considered.
- [ ] Operational, scalability, reliability, and security directions are included only where relevant.
- [ ] Major recommendations have identifiable evidence.
- [ ] Recommendations are prioritized.
- [ ] Confidence or certainty is distinguishable.
- [ ] Exploratory ideas are clearly separated from evidence-backed directions.
- [ ] Recommendations do not silently assume a particular technology.
- [ ] The analysis does not become a generic modernization checklist.
- [ ] No future direction is presented as necessary when the repository does not establish the need.

## Output Expectations

Return a professional, sufficiently detailed Future Directions analysis. Depth should follow the number and significance of credible directions; do not artificially constrain the document length.

Begin with a concise synthesis of the most important current limitations and opportunities.

Then present the highest-value future directions, prioritized by impact, urgency, strength of the current-state rationale, and feasibility.

For each major direction, explain the current-state limitation or opportunity, the proposed evolution, expected benefit, prerequisites, priority, and rationale for the recommendation.

Distinguish recommendations strongly grounded in the current implementation from longer-term exploratory possibilities. Do not expose internal evidence-strength or confidence labels.

Where useful, provide a phased evolution narrative showing what should logically come first and what depends on later scale or capability.

Do not produce a generic technology modernization checklist.

Do not write a detailed implementation plan or select specific technologies unless the repository itself establishes them as a natural continuation of the current design.

The final analysis should allow a reader to answer:

"Given the system's current purpose, capabilities, architecture, implementation, and testing maturity, what are the most credible next directions, why do they matter, and how strongly does the repository support each one?"
