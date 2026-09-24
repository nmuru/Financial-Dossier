---
name: testing-harness
description: Reconstruct the repository's testing strategy, test architecture, harnesses, fixtures, mocks, coverage, execution paths, and verification gaps. Use when determining how the software is tested and how confidently the implementation can be validated from repository evidence.
---

# Testing Harness Reverse-Engineering Skill

## Objective

Reconstruct how the repository verifies its own behavior.

The analysis must explain what kinds of tests exist, what they test, how the test harness is structured, how fixtures and dependencies are controlled, what execution environments are used, how tests are invoked, what coverage they provide, and what important behavior remains unverified.

This is not a generic recommendation for how the software should be tested. It is a reconstruction of the testing strategy and harness that actually exists.

The analysis must distinguish between:

- tests that exist
- tests that are executed by configured workflows
- tests that appear incomplete or obsolete
- behavior that is covered
- behavior that is only indirectly covered
- behavior that appears untested

Do not infer test coverage merely from the existence of test files.

## Relationship to other phases

Use the Features, Requirements, Technology Architecture, High-Level Design, Low-Level Design, and Implementation Detail results as context.

The Testing Harness phase should determine how the repository validates those behaviors and structures.

This phase should answer:

"How does this repository test the system, what does the test harness actually verify, and where are the important verification gaps?"

Do not redesign the testing strategy. Recommendations belong to Future Directions unless explicitly requested.

## Testing scope

Investigate, where applicable:

- unit tests
- integration tests
- API tests
- component tests
- UI tests
- end-to-end tests
- contract tests
- database tests
- migration tests
- worker/job tests
- event/message tests
- CLI tests
- performance/load tests
- security tests
- snapshot/golden tests
- static analysis
- type checking
- linting
- build verification
- CI test execution
- test fixtures
- factories
- mocks
- stubs
- fakes
- dependency injection for testing
- test databases
- containers or emulators
- test configuration
- coverage measurement

Do not assume a category exists merely because the technology commonly supports it.

## Runtime resources and tools

The runtime supplies the selected skill and exposes the tools available for executing this methodology.

Use the repository tools (`list_files`, `read_file`, `search_repository`) for evidence in the target repository.

Use `list_resources` and `read_resource` for runtime-owned files supplied alongside this skill. These may include `OUTPUT_TEMPLATE.md`, checklists, schemas, domain artifacts, examples, or other supporting resources. The runtime inventory is dynamic; do not assume that a particular optional artifact exists unless it is listed.

When `OUTPUT_TEMPLATE.md` is supplied, read it before producing the final documentation and use its structure as required by the common agent contract.

Use `list_previous_phase_outputs` and `read_previous_phase_output` for workflow artifacts supplied from earlier phases. Do not use repository tools for those artifacts.

Resource paths are runtime-relative identifiers. Do not construct host filesystem paths.


## Investigation workflow

### Step 1: Discover the testing surface

Identify all likely test locations and test-related configuration.

Inspect:

- test directories
- test files
- package scripts
- pytest/Jest/Vitest/Playwright/Cypress/etc. configuration where present
- CI workflows
- build scripts
- Makefiles/task runners
- dependency manifests
- coverage configuration
- test environment configuration
- Docker or container definitions used by tests

Determine how tests are intended to be invoked.

### Step 2: Identify the test framework and harness

Determine:

- test framework
- assertion library
- runner
- discovery rules
- configuration
- setup/teardown
- environment initialization
- parallelization
- retries
- timeouts
- reporting
- coverage tooling

Verify these from configuration and actual usage.

Do not report a dependency as the active test framework without evidence that it participates in test execution.

### Step 3: Classify tests by level

Classify meaningful tests into levels such as:

- unit
- component
- integration
- end-to-end
- contract
- system
- operational

Use actual dependencies and execution behavior to determine the level.

For example, a test that invokes a service function while mocking all dependencies is materially different from one that starts the application and calls its HTTP endpoint.

Do not classify based solely on directory names.

### Step 4: Map tests to features and requirements

Use earlier phase results to determine which important behaviors are actually tested.

Create an evidence-backed relationship:

feature/requirement → relevant test(s) → level of verification.

Look for tests covering:

- normal workflows
- boundary conditions
- validation
- error handling
- authorization
- persistence
- integrations
- state transitions
- asynchronous behavior

Do not claim complete coverage merely because a feature has one test.

### Step 5: Analyze test fixtures and controlled dependencies

Inspect:

- fixtures
- factories
- test data
- mocks
- stubs
- fakes
- monkeypatching
- dependency injection
- test servers
- test databases
- containers
- service emulators
- network interception

Determine what the tests replace, isolate, or execute for real.

This is critical for understanding what the tests actually prove.

For example, an integration test that mocks the external service does not verify the external service integration itself.

### Step 6: Analyze test data and state

Determine how tests create and clean up state.

Inspect:

- database setup
- migrations
- transactions
- fixture lifecycle
- temporary directories
- seeded data
- test isolation
- cleanup
- shared state

Identify whether tests are deterministic and independent where the repository provides evidence.

Do not claim complete isolation merely because teardown functions exist.

### Step 7: Analyze external integration testing

For each significant external dependency, determine whether tests:

- call the real service
- use a sandbox
- use a mock
- use a stub
- use a local emulator
- do not test the integration

Distinguish testing application behavior around an integration from testing the integration itself.

### Step 8: Analyze API/UI/end-to-end verification

Where applicable, inspect tests that exercise:

- HTTP routes
- authentication flows
- UI interactions
- browser behavior
- API contracts
- full workflows

Determine whether these tests start the real application or invoke isolated components.

Trace the execution path enough to establish the verification level.

### Step 9: Analyze asynchronous and background testing

Inspect tests for:

- queues
- workers
- scheduled jobs
- events
- retries
- polling
- callbacks
- asynchronous workflows

Determine whether tests verify only job functions or the complete producer-to-consumer flow.

### Step 10: Analyze coverage and quality gates

Inspect:

- coverage reports/configuration
- minimum thresholds
- CI gates
- branch coverage
- mutation testing
- linting
- type checking
- build checks
- required status checks

Do not equate code coverage percentage with behavioral coverage.

If a threshold exists, identify what it actually measures.

### Step 11: Trace CI and execution reality

Determine which tests are actually run in CI or other automated workflows.

Distinguish:

- locally available tests
- configured tests
- CI-executed tests
- optional/manual tests
- obsolete tests

A test file that is never discovered or invoked should not be treated as part of the active verification pipeline without qualification.

### Step 12: Identify testing gaps

Compare the major features and requirements against the evidence of testing.

Identify important areas that appear:

- well covered
- partially covered
- indirectly covered
- untested
- untestable with the current harness
- covered only by mocks
- covered only in local/manual workflows

Focus on material verification gaps, not a complaint that every line lacks a test.

## Test effectiveness analysis

For important tests, determine what they actually establish.

A test may establish:

- a function produces a result for a given input
- an API contract is respected
- multiple components work together
- a complete workflow succeeds
- an error is handled
- a persistence operation occurs

Do not claim that a test proves more than its execution path demonstrates.

Consider false confidence caused by:

- excessive mocking
- unreachable test code
- fixed fixtures that omit important cases
- tests of implementation details rather than behavior
- snapshots without meaningful assertions
- tests that never exercise real external boundaries
- tests that bypass authentication or validation
- tests that share state
- disabled or skipped tests

## Coverage model

Use a practical classification for important features and requirements:

**Directly covered:** A test explicitly exercises the behavior.

**Indirectly covered:** The behavior is exercised as part of another test.

**Partially covered:** Some meaningful paths or conditions are tested, but important cases are absent.

**Harness-only:** The test validates the test setup or a mocked boundary rather than the real behavior.

**No credible test identified:** No credible test was found. Treat this as an internal assessment; do not use the phrase as a final-document status label.

Use this classification rather than inventing numerical coverage where the repository does not provide it.

## Evidence requirements

For important testing conclusions, identify:

- test file
- test suite or test name
- test runner/configuration
- fixture or factory
- mock/stub/fake
- CI workflow
- coverage configuration
- command/script

Prefer concrete evidence over assumptions from filenames.

## Anti-patterns and rationalizations

| Rationalization | Required response |
|---|---|
| "There is a tests directory, so the system is well tested." | Inspect what tests execute and what behavior they cover. |
| "Every test file represents an active test." | Verify discovery and invocation. |
| "A mocked integration is integration-tested." | Distinguish application-side behavior from the real external integration. |
| "High code coverage means high behavioral coverage." | Coverage measures executed code, not complete requirements or workflows. |
| "One test per endpoint is sufficient." | Examine meaningful workflows, edge cases, authorization, errors, and state. |
| "The CI pipeline runs tests because a test command exists." | Inspect the actual CI workflow. |
| "A test framework dependency proves its use." | Verify configuration and executed tests. |
| "Skipped tests count as coverage." | Treat disabled or skipped tests as gaps unless execution is otherwise established. |
| "Snapshots prove behavior." | Determine what meaningful behavior the snapshot actually verifies. |
| "Mocks make tests more reliable, so they prove the integration." | Mocks isolate behavior but do not validate the real boundary. |
| "No tests means the requirement is unimportant." | Absence of tests is a verification gap, not evidence about business importance. |

## Red Flags

Investigate further when:

- test files exist but no test runner configuration is found
- CI does not invoke the tests
- many tests are skipped or disabled
- almost every external dependency is mocked
- end-to-end tests exist but never start the real application
- coverage configuration exists without evidence that coverage is enforced
- tests depend on shared persistent state
- test fixtures do not resemble actual application data
- important features have no corresponding tests
- only happy paths are tested
- authentication and authorization are bypassed in most tests
- asynchronous workflows are tested only at the individual function level
- a test suite appears to test an older or alternate implementation
- test commands differ between local documentation and CI

## Verification Gate

Before completing this phase, verify:

- [ ] The active test framework and harness have been identified.
- [ ] Test discovery and execution configuration have been examined.
- [ ] Meaningful tests have been classified by level.
- [ ] Important features and requirements have been mapped to test evidence where possible.
- [ ] Fixtures, mocks, stubs, and controlled dependencies have been examined.
- [ ] Test state setup and cleanup have been considered.
- [ ] External integrations have been classified according to whether they are real or simulated.
- [ ] API/UI/end-to-end verification has been examined where relevant.
- [ ] Background and asynchronous workflows have been examined where relevant.
- [ ] CI and automated execution have been verified.
- [ ] Coverage and quality gates have been examined where present.
- [ ] Important verification gaps have been identified.
- [ ] Tests are not assumed active merely because files exist.
- [ ] Test effectiveness is not overstated.
- [ ] Facts, inferences, and unknowns are distinguishable.

## Output Expectations

### Output boundary
The repository-analysis and classification mechanisms used to assess tests are internal reasoning controls. Do not reproduce evidence trails, certainty/confidence labels, or source-by-source investigation notes in the final Testing Harness document. Present the resulting testing capability, strengths, and gaps directly.


Return a professional, sufficiently detailed Testing Harness analysis. Cover the testing mechanisms and meaningful verification gaps needed for comprehensive understanding without artificially constraining the document length.

Explain:

- the overall testing strategy
- the test framework and execution harness
- major test levels
- important fixtures and controlled dependencies
- how tests exercise features and requirements
- how external systems are tested
- how state and test data are managed
- how CI executes the test suite
- coverage and quality gates
- important verification gaps

Where useful, include a concise test architecture or verification-flow diagram in Mermaid syntax.

Distinguish directly tested behavior from indirectly tested behavior, simulated boundaries, and areas that the current harness does not exercise. Do not expose internal evidence or confidence classifications.

Do not recommend a new testing strategy in this phase. Describe the existing harness and its actual verification capability.

The final analysis should allow a reader to answer:

"How is this system tested, what does the current test harness genuinely verify, how is testing executed and controlled, and where does meaningful verification remain absent?"
