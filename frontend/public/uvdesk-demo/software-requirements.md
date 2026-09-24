---
model: openai/gpt-6-astra
---

# Software Requirements Specification

## 1. Document Control

- **Document title:** Software Requirements Specification — UVdesk Community Helpdesk
- **Version:** 1.0
- **Status:** Current-system requirements baseline
- **Approvals / reviewers:** Approval status not specified

## 2. Introduction

### 2.1 Purpose

This specification describes the behaviors, interfaces, data constraints, security controls, and operating conditions represented by the UVdesk Community Helpdesk distribution.

It provides detailed requirements for the locally defined installation and configuration behavior. Helpdesk capabilities supplied by external UVdesk bundles are described at the level established by this distribution; their detailed business rules are not defined here.

### 2.2 Scope

The scope covers the Community project skeleton, installation wizard, application configuration, and bundled helpdesk capabilities.

The system supports deployment of a self-hosted helpdesk comprising:

- A customer support center and staff-facing administration area.
- Ticket handling and customer communication.
- Email-to-ticket integration.
- Workflow automation and prepared responses.
- Knowledge-base and FAQ content.
- Configurable branding, localization, and extensions.
- Browser-based installation and a documented console configuration path.
- Database, mail, session, and access-control configuration.

This specification does not define undocumented API operations, ticket lifecycle transitions, workflow execution semantics, or bundle-internal persistence rules.

### 2.3 Product / System Overview

UVdesk Community is distributed as an application skeleton that assembles separately maintained packages for core helpdesk services, automation, extensions, mailbox processing, the support center, and APIs.

The distribution contains concrete installation behavior and runtime configuration. Most ticket-management and customer-service operations are implemented by the installed packages rather than by application source contained in the skeleton.

### 2.4 Intended Audience

- Product owners and helpdesk administrators.
- Developers maintaining the distribution or its component packages.
- Installation and infrastructure operators.
- Test engineers defining installation and integration acceptance tests.
- Security reviewers assessing configured access boundaries.

### 2.5 Definitions, Acronyms, and Abbreviations

| Term | Meaning |
|---|---|
| Member | Staff user accessing the agent or administrator area |
| Customer | User accessing customer support services |
| Super administrator | Highest configured staff role, inheriting administrator access |
| Mailbox | Configured incoming and outgoing email integration |
| Prepared response | Named reusable helpdesk capability supplied by the automation bundle |
| Website prefix | Configurable URL segment identifying the staff or customer area |
| DSN | Connection descriptor used to configure a database or mail transport |
| Installation preflight | Checks presented before database and administrator configuration |

### 2.6 References

Product and operator documentation consists of:

- Project README.
- Installation Guide.
- Release changelogs.
- UVdesk documentation site: <https://docs.uvdesk.com/>.

Detailed public API documentation is maintained with the UVdesk API bundle.

## 3. Overall Description

### 3.1 Product Perspective

The application requires its UVdesk packages and their installation recipes to provide the complete helpdesk. Routes are loaded through UVdesk and extension route loaders.

The API, mailbox, automation, support-center, core, and extension bundles are enabled across application environments. Their presence establishes integration boundaries, not independent service deployments.

### 3.2 Product Functions

The principal product functions are:

1. Configure a new helpdesk installation.
2. Authenticate staff and customers through separate login areas.
3. Receive, organize, and manage support tickets.
4. Exchange customer communications and notifications.
5. Automate support operations.
6. Publish organized self-service information.
7. Customize deployment identity, language, and extensions.

### 3.3 User Classes and Characteristics

| User class | Responsibilities and interactions |
|---|---|
| Customer | Access support-center services and ticket conversations; consult self-service content |
| Agent | Manage support requests and customer communications |
| Administrator | Perform staff administration with inherited agent access |
| Super administrator | Perform higher-level administration with inherited administrator access |
| Installation operator | Supply database credentials, create the initial administrator, configure URL prefixes, and complete setup |
| Extension developer | Add application capabilities through the extension framework |

A separate customer read-only role is recognized for ticket viewing. This does not establish a complete read-only permission model.

### 3.4 Operating Environment

The published deployment baseline specifies:

| Component | Published baseline |
|---|---|
| Operating system | Ubuntu 16.04 LTS or later, or Windows 7 or later using WAMP/XAMPP |
| Web server | Apache 2 or NGINX |
| Memory | At least 4 GB |
| Processor | At least 1 GHz |
| PHP | README baseline: 8.1 |
| MySQL | 5.7.23 or later |
| Composer | Version 2 or later |
| Email-related PHP extensions | IMAP and Mailparse |

These are deployment guidance, not measured capacity guarantees. Historical operating-system versions listed by the product do not establish present-day vendor support.

The Composer PHP constraint is `^7.2.5 || ^8.0`; the application targets Symfony 5.4. The Installation Guide demonstrates PHP 8.2, while the Docker build installs PHP 8.1. These are distinct compatibility declarations and examples, not a tested version matrix.

### 3.5 Design and Implementation Constraints

- The browser installer requires JavaScript and the supplied jQuery, Backbone, Underscore, validation, and template assets.
- The configured database driver is `pdo_mysql`.
- Database text uses `utf8mb4` with `utf8mb4_unicode_ci` table defaults.
- The database connection removes `ONLY_FULL_GROUP_BY` from its session SQL mode.
- The default upload manager stores files locally.
- Extensions are located under the application’s `apps` directory.

### 3.6 User Documentation

The project README, Installation Guide, release changelogs, and UVdesk documentation site provide product and operator documentation. Public API documentation is maintained with the UVdesk API bundle.

### 3.7 Assumptions and Dependencies

Installation assumes an accessible database, sufficient filesystem permissions, an operational web server, and successful dependency installation.

No mailbox is configured by default. Email operation requires deployment-specific incoming and outgoing settings. The default site URL is `localhost:8000`, and the support email is initially unset.

## 4. External Interface Requirements

### 4.1 User Interfaces

**UI-01 — Separate login areas.**  
The application shall provide distinct staff and customer login destinations. The documented defaults are:

- Staff: `/en/member/login`
- Customer: `/en/customer/login`

The `member` and `customer` segments are configurable.

**UI-02 — Installation wizard.**  
The installer shall present the following ordered stages:

1. Welcome.
2. System requirements.
3. Database configuration.
4. Administrator creation.
5. Website-prefix configuration.
6. Installation and completion.

It shall provide progress indicators, field notices, forward navigation, backward navigation, and a return-to-welcome action.

**UI-03 — Completion destinations.**  
After installation requests complete, the installer shall render a completion view using the returned staff-login and knowledge-base destinations. Completion displays navigation options; it does not automatically navigate to the staff dashboard.

### 4.2 Software Interfaces

#### Installer interface

The browser uses the following relative HTTP interfaces. These define the client integration contract; server-side handlers and their complete validation rules belong to the installed packages.

| Method and relative path | Input | Response consumed by the browser |
|---|---|---|
| `POST ./wizard/xhr/check-requirements` | `specification` | Check-specific status, message, description, or result collection |
| `POST ./wizard/xhr/verify-database-credentials` | Database fields listed in §6.2 | Boolean `status` |
| `POST ./wizard/xhr/intermediary/super-user` | `name`, `email`, `password` | Boolean `status` |
| `GET ./wizard/xhr/website-configure` | None | `status`, `memberPrefix`, `knowledgebasePrefix` |
| `POST ./wizard/xhr/website-configure` | `member-prefix`, `customer-prefix` | Boolean `status` |
| `POST ./wizard/xhr/load/configurations` | No explicit payload | Successful request completion |
| `POST ./wizard/xhr/load/migrations` | No explicit payload | Successful request completion |
| `POST ./wizard/xhr/load/entities` | No explicit payload | Successful request completion |
| `POST ./wizard/xhr/load/super-user` | No explicit payload | Successful request completion |
| `POST ./wizard/xhr/load/website-configure` | No explicit payload | `memberLogin`, `knowledgebase` |

Database, administrator, and prefix submissions advance only when the response contains `status` equal to Boolean `true`. A truthy string is not equivalent.

Preflight accepts these specification values:

- `php-version`
- `php-extensions`
- `php-maximum-execution`
- `php-envFile-permission`
- `php-configFiles-permission`
- `redis-status`

#### Helpdesk API interface

The distribution configures an API security boundary matching `^/api`, with a dedicated credential provider and guard authenticator.

Endpoint methods, payloads, token formats, response codes, rate limits, and API authorization rules are not specified by the skeleton. The configured anonymous firewall setting must not be interpreted as proof that all API operations are publicly accessible.

#### Extension interface

**INT-04 — Extension integration.**  
The distribution shall support application extensions through the configured extension directory and route loader.

### 4.4 Communications Interfaces

The browser uses ordinary jQuery form submissions for the installer HTTP interfaces. No general JSON request-envelope requirement is established.

**INT-01 — Database connectivity.**  
The application shall obtain its database connection from `DATABASE_URL`.

**INT-02 — Outbound mail.**  
The main mail transport shall obtain its connection configuration from `MAILER_DSN`.

**INT-03 — Mailbox configuration.**  
Mailbox integration supports configuration of incoming IMAP connection details and outgoing mail-server details. The sample configuration includes mailbox enablement, outbound-mail suppression, strict-mode selection, credentials, and sender address. No sample mailbox is active by default.

### 4.5 External Services / Systems

Google reCAPTCHA is an available product option, not an enabled-by-default protection established by this configuration.

Microsoft Apps and marketplace applications are advertised integrations without a defined local interface contract.

## 5. Functional Requirements

### FR-01 — Control installation progression

- **Requirement ID:** FR-01
- **Requirement statement:** The wizard shall control forward and backward installation progression using stage-completion results.
- **Trigger / input:** The operator starts installation or navigates between setup stages.
- **Expected behavior:**
  - Starting installation shall enter the system-requirements stage.
  - Forward progression shall use the active stage’s completion result.
  - Attempting to open later stages before preceding stages have been marked complete shall return the wizard to its welcome flow.
  - Backward navigation shall permit returning to earlier setup stages.
  - Returning to the requirements stage from database configuration shall initiate a new requirements view and checks.
- **Outputs / postconditions:** Returning to welcome resets the wizard’s completion markers.
- **Business rules:** Returning to welcome does not establish rollback of server-side changes.
- **Verification method:** Browser interaction tests for validation and navigation.

### FR-02 — Present system-readiness checks

- **Requirement ID:** FR-02
- **Requirement statement:** The wizard shall request and present system-readiness checks on entering preflight.
- **Trigger / input:** Entry into the preflight stage.
- **Expected behavior:**
  - Request checks for PHP version, PHP extensions, maximum execution time, `.env` permissions, configuration-file permissions, and Redis status.
  - Show check results and expandable details where supplied.
  - Show the number of satisfied extension and configuration-file checks relative to their totals.
  - Provide specific remediation links for missing IMAP and Mailparse extensions.
- **Business rules:**
  - Redis status is advisory in the current progression logic; it is not a mandatory progression condition.
  - Preflight is not a comprehensive all-checks-success barrier.
  - PHP version, execution-time, and environment-permission failures can block progression, but configuration-file evaluation takes precedence over extension evaluation.
  - Pending responses can leave progression enabled. Continuing does not prove that every prerequisite has passed.
- **Verification method:** Browser interaction tests and controlled HTTP responses for installer success and failure branches.

### FR-03 — Collect and verify database configuration

- **Requirement ID:** FR-03
- **Requirement statement:** The wizard shall collect database configuration and require Boolean success from database verification before progression.
- **Trigger / input:**
  - Server address.
  - Server version.
  - Server port.
  - Username.
  - Password.
  - Database name.
  - Whether to create the database.
- **Expected behavior:**
  - Initialize the server address to `127.0.0.1`, port to `3306`, username to `root`, and database creation to selected.
  - Require nonempty server address, username, password, and database name before enabling progression.
  - Send the fields to database verification when the stage is submitted.
  - Prevent progression for any response other than Boolean success.
  - Display the following notice for a negative application response:

    > Details are incorrect ! Connection not established.

- **Business rules:**
  - Server version and port have no additional mandatory or format checks in the local validator.
  - The create-database choice shall be transmitted as `1` or `0`.
- **Verification method:** Browser interaction tests, controlled HTTP responses, and integration tests for database creation.

### FR-04 — Collect initial administrator credentials

- **Requirement ID:** FR-04
- **Requirement statement:** The wizard shall require and validate initial administrator credentials before advancing.
- **Trigger / input:** Name, email, password, and password confirmation.
- **Expected behavior:**
  - Submit only name, email, and password to the intermediary administrator endpoint.
  - Require Boolean success from the server before progression.
- **Outputs / postconditions:** Actual administrator creation occurs later in the final installation sequence.
- **Business rules:**
  - Name begins with an ASCII letter and contains only ASCII letters and whitespace.
  - Email follows the browser’s configured address pattern.
  - Password contains at least eight characters.
  - Password contains at least two ASCII letters, one digit, and one special character; underscore qualifies.
  - Password contains no whitespace.
  - Confirmation equals the password.
  - Confirmation is a local validation field and is not submitted.
  - These rules describe installer client validation, not a universal password policy for every account-management operation.
- **Verification method:** Browser interaction tests, controlled HTTP responses, and integration tests for administrator creation.

### FR-05 — Configure website prefixes

- **Requirement ID:** FR-05
- **Requirement statement:** The wizard shall retrieve and submit staff and customer website prefixes.
- **Trigger / input:** Entry into the prefix stage, field validation, and submission of the two prefixes.
- **Expected behavior:**
  - Retrieve saved staff and customer prefixes before displaying the prefix form.
  - Validate both prefixes on field validation.
  - Send the two prefixes when the stage is submitted.
  - Advance only on Boolean success.
- **Business rules:**
  - Both prefixes shall be nonempty.
  - Each shall contain only ASCII letters and digits.
  - The two values shall differ using case-sensitive comparison.
  - The client does not impose a maximum length or reserved-word list.
  - Progression is initially enabled before prefix loading and field validation complete. Server-side rejection remains necessary to establish a complete input contract.
- **Verification method:** Browser interaction tests and controlled HTTP responses.

### FR-06 — Execute installation in order

- **Requirement ID:** FR-06
- **Requirement statement:** The browser shall execute final installation operations sequentially.
- **Trigger / input:** The operator starts final installation.
- **Expected behavior:**
  1. Load configuration.
  2. Load migrations.
  3. Populate datasets.
  4. Create the super user.
  5. Configure website routes.

  Each request shall wait for completion of the preceding request. The wizard shall display the current operation and a processing indicator.
- **Outputs / postconditions:** After the final response, the wizard shall use `memberLogin` and `knowledgebase` to populate the completion view.
- **Business rules:**
  - The browser does not inspect a Boolean application-success field for these final operations.
  - Transactional installation, idempotency, and rollback are not defined.
- **Verification method:** Controlled HTTP responses and integration tests for database, administrator, and route creation.

### FR-07 — Provide installation feedback

- **Requirement ID:** FR-07
- **Requirement statement:** The wizard shall show processing indicators and selected installation error guidance.
- **Trigger / input:** Database, administrator, and prefix submissions; preflight failures; final installation failures.
- **Expected behavior:**
  - Show a processing indicator during database, administrator, and prefix submissions, and remove it when the request finishes.
  - For HTTP 500 during configuration loading, display guidance concerning `.env` read/write permissions.
  - For HTTP 500 during later installation operations, display a general retry message.
  - During preflight, HTTP 404 guidance shall mention the application path, `index.php`, Apache rewriting, and `AllowOverride`.
  - During preflight, HTTP 500 guidance shall suggest returning, refreshing, or restarting the wizard.
- **Business rules:**
  - Automatic retries, resumable installation, and comprehensive error rendering for every failure path are not established.
  - Saved-prefix retrieval and malformed configuration-check responses contain error-handling paths that may fail to render the intended feedback.
- **Verification method:** Browser interaction tests and controlled HTTP responses for installer success and failure branches.

### FR-08 — Convert incoming email into tickets

- **Requirement ID:** FR-08
- **Requirement statement:** The system shall convert incoming mailbox email into support tickets.
- **Rationale / source:** Documented bundle-supplied helpdesk capability.
- **Trigger / input:** Incoming mailbox email.
- **Outputs / postconditions:** Support tickets.
- **Business rules:** Polling, duplicate detection, threading, and malformed-message handling are unspecified.
- **Verification method:** Bundle-level functional and integration tests against the installed packages.

### FR-09 — Filter and organize tickets

- **Requirement ID:** FR-09
- **Requirement statement:** The system shall allow staff to filter tickets by status, identifier, agent, and customer, and organize tickets using types and tags.
- **Rationale / source:** Documented bundle-supplied helpdesk capability.
- **Business rules:** Filter composition, sorting, and pagination are unspecified.
- **Verification method:** Bundle-level functional and integration tests against the installed packages.

### FR-10 — Support customer communication

- **Requirement ID:** FR-10
- **Requirement statement:** The system shall support customer communication through replies, notifications, forwarding, collaborators, and multiple attachments.
- **Rationale / source:** Documented bundle-supplied helpdesk capability.
- **Business rules:** Recipient rules, delivery guarantees, and collaborator permissions are unspecified.
- **Verification method:** Bundle-level functional and integration tests against the installed packages.

### FR-11 — Support reusable responses and ticket or thread operations

- **Requirement ID:** FR-11
- **Requirement statement:** The system shall support saved replies, prepared responses, agent notes, and editing, deletion, and pinning of tickets or threads.
- **Rationale / source:** Documented bundle-supplied helpdesk capability.
- **Business rules:** Visibility, history, and deletion semantics are unspecified.
- **Verification method:** Bundle-level functional tests for the advertised helpdesk workflows.

### FR-12 — Support workflow automation

- **Requirement ID:** FR-12
- **Requirement statement:** The system shall support automated workflows and prepared responses.
- **Rationale / source:** Documented bundle-supplied helpdesk capability.
- **Business rules:** Trigger vocabulary, action ordering, retries, and failure handling are unspecified.
- **Verification method:** Bundle-level functional and integration tests against the installed packages.

### FR-13 — Provide self-service information

- **Requirement ID:** FR-13
- **Requirement statement:** The system shall provide a knowledge base and FAQ system organized using articles, categories, and folders.
- **Rationale / source:** Documented bundle-supplied helpdesk capability.
- **Business rules:** Publication states, hierarchy cardinalities, and authoring permissions are unspecified.
- **Verification method:** Bundle-level functional and integration tests against the installed packages.

### FR-14 — Support branding and multilingual presentation

- **Requirement ID:** FR-14
- **Requirement statement:** The system shall support branding changes, logo and favicon customization, and multilingual presentation.
- **Rationale / source:** Documented bundle-supplied helpdesk capability.
- **Business rules:** Translation completeness and layout conformance are not defined.
- **Verification method:** Bundle-level functional tests for the advertised helpdesk workflows.

### FR-15 — Provide agent privileges and spam blocking

- **Requirement ID:** FR-15
- **Requirement statement:** The system shall provide agent privileges and spam-blocking capabilities.
- **Rationale / source:** Documented bundle-supplied helpdesk capability.
- **Business rules:** A full permission matrix and abuse-detection policy are not defined.
- **Verification method:** Bundle-level functional tests for the advertised helpdesk workflows.

Detailed acceptance rules for FR-08 through FR-15 depend on the installed bundles and are not fully specified by the skeleton.

Agent activity, announcements, broadcasting, marketing modules, Kudos, and application integrations are also advertised. Their names alone do not define executable requirements or acceptance scenarios.

## 6. Data Requirements

### 6.1 Data Entities

The helpdesk domain includes:

- Users, customers, agents, administrators, teams, and groups.
- Tickets, conversation threads, notes, attachments, tags, and ticket types.
- Mailboxes and mail templates.
- Saved replies, prepared responses, and workflows.
- Knowledge-base articles, categories, and folders.

Exact schemas, keys, relationship cardinalities, and uniqueness rules are supplied by component packages rather than defined in this skeleton.

### 6.2 Data Structures

#### Installation data

| Data group | Fields and constraints |
|---|---|
| Database configuration | `serverName`, `serverVersion`, `serverPort`, `username`, `password`, `database`, `createDatabase` |
| Administrator submission | `name`, `email`, `password`; confirmation is not submitted |
| Website-prefix submission | `member-prefix`, `customer-prefix` |
| Preflight scalar result | `status`, with optional `message` and `description` |
| Extension result | `extensions`: collection of name-to-status objects |
| Configuration-permission result | `configfiles`: collection of name-to-status objects |
| Installation completion | `memberLogin`, `knowledgebase` |

Setup models hold submitted data while navigating the wizard. Durable browser storage and restoration after refresh are not defined.

#### Data defaults and representation

**DATA-01 — Default ticket settings.**  
The distribution shall configure new-ticket defaults as type `support`, status `open`, and priority `low`. These values do not define the full allowed vocabulary or transition model.

**DATA-02 — Text representation.**  
The configured database shall support `utf8mb4` text.

**DATA-03 — Upload configuration.**  
The distribution shall supply these upload-related parameters:

| Parameter | Default |
|---|---:|
| Maximum post size | 8,388,608 bytes |
| Maximum number of uploaded files | 20 |
| Maximum uploaded-file size | 2,097,152 bytes |

These are application configuration values. Their enforcement and alignment with PHP and web-server limits are not demonstrated by the skeleton.

### 6.3 Data Relationships

Exact relationship cardinalities are supplied by component packages rather than defined in this skeleton. Knowledge-base and FAQ content is organized using articles, categories, and folders, but hierarchy cardinalities are unspecified.

### 6.4 Data Retention

Ticket or attachment retention periods, soft versus permanent deletion, and backup retention are not defined.

### 6.5 Data Integrity

Transaction boundaries across setup operations and concurrent-update resolution are not defined.

### 6.6 Data Migration / Conversion

The installation flow includes migration and initial dataset operations.

Migration rollback and upgrade compatibility guarantees are not defined.

## 7. Quality / Non-Functional Requirements

### 7.1 Performance

The installer shall debounce field validation by 400 milliseconds.

No response-time, throughput, concurrent-user, or installation-duration target is specified. Published “unlimited” counts for agents, customers, tickets, teams, groups, and mailbox integrations do not establish unlimited operational capacity.

### 7.2 Reliability / Availability

The installer shall sequence finalization requests and expose processing and selected failure states.

There is no defined availability objective, automatic failover, retry policy, or recovery-time target. Failed installation can leave server-side work completed by earlier stages; cancellation is not a rollback guarantee.

### 7.3 Usability / Human Factors

**NFR-01 — Validation feedback.**  
The installer shall display field notices for missing or invalid values and disable forward navigation when its validators detect errors. Valid input followed by Enter shall activate the next action where that action exists.

**NFR-02 — Locale configuration.**  
The application shall configure these locale identifiers:

`en`, `fr`, `it`, `de`, `da`, `ar`, `es`, `tr`, `zh`, `pl`, `he`, `pt_BR`.

English shall be the default and translation fallback.

No accessibility conformance level, supported-browser matrix, or right-to-left layout guarantee is specified.

### 7.4 Security

**SEC-01 — Staff role inheritance.**

- Administrators inherit agent access.
- Super administrators inherit administrator access.
- Customer roles are separate from the staff hierarchy.

**SEC-02 — Staff access boundary.**  
The general staff-prefix area shall require `ROLE_AGENT`, after the configured exceptions for login, account creation, password recovery, credential updates, and the mailbox listener. The listener is configured for anonymous access; its handler-level protections are outside this specification.

**SEC-03 — Customer access boundary.**

- Login, ticket creation, password recovery, and credential updates have anonymous-access rules.
- The public read-only intermediary path permits anonymous, remembered, or read-only customer access.
- Ticket viewing permits `ROLE_CUSTOMER` or `ROLE_CUSTOMER_READ_ONLY`.
- The general customer-prefix area requires `ROLE_CUSTOMER`.

These path rules do not establish ticket ownership checks or data-level authorization.

**SEC-04 — Authentication destinations.**  
Successful staff form login shall target the staff dashboard. Successful customer form login shall target the customer ticket collection. Logout shall target the corresponding login route.

**SEC-05 — Remembered staff authentication.**  
Staff authentication shall offer a `REMEMBERME` cookie, activated by `_remember_me`, with a configured lifetime of 604,800 seconds and path `/`.

**SEC-06 — Session configuration.**  
Session cookies shall use automatic secure-cookie selection and `SameSite=Lax`. Cookie lifetime and session garbage-collection lifetime shall obtain their integer value from `UV_SESSION_COOKIE_LIFETIME`.

**SEC-07 — Application secret and password encoding.**  
The application shall obtain its framework secret from `APP_SECRET`. User password encoding shall use the configured automatic encoder.

The distribution does not establish universal TLS enforcement, CSRF coverage, credential rotation, account lockout, encryption at rest, or comprehensive API authorization. Client-side installer validation is not a substitute for server-side controls.

### 7.5 Maintainability

The distribution shall support package-based extension.

Composer installation and update hooks shall clear application cache and install public assets.

### 7.6 Portability

The distribution shall support locale-based presentation.

Platform compatibility remains constrained by installed dependency versions, required PHP extensions, and the MySQL configuration.

### 7.7 Scalability

No horizontal-scaling topology, shared-session backend, shared-upload storage, queue capacity, or distributed scheduling contract is defined.

### 7.8 Interoperability

Interoperability centers on MySQL, configured mail transports, mailbox integrations, and the bundle-provided API.

## 8. Operational and Environmental Requirements

### 8.1 Operational Modes

The distribution supports browser installation and normal helpdesk operation. Test-environment configuration uses mock-file session storage; this is not evidence of an executable acceptance-test suite.

#### Container operation

At startup, the container entry script restarts Apache and MySQL. It attempts local database configuration only when database username, password, and name are all supplied. Otherwise, it reports that configuration was skipped. A failed database ping during this branch terminates startup with an error.

The bootstrap does not separately require `MYSQL_ROOT_PASSWORD` before using it. Its user-grant syntax is not a portable compatibility guarantee for every MySQL version.

The default command is `/bin/bash`; a foreground service-supervision and container-liveness contract is not defined. The script invokes the supplied command as the `uvdesk` user and may subsequently execute it again after that invocation returns. Uniform non-root execution cannot therefore be assumed.

### 8.2 Installation / Deployment

**OPS-01 — Project acquisition.**  
Operators may create the project through Composer or unpack the published archive containing dependencies.

**OPS-02 — Configuration entry points.**  
After dependency installation, operators may use the browser wizard or the documented command:

```bash
php bin/console uvdesk:configure-helpdesk
```

The console interaction details are package-supplied.

**OPS-03 — Public document root.**  
Web serving shall expose the application’s `public` directory. Apache deployments require appropriate rewrite and override configuration for routed URLs.

**OPS-04 — Writable installation resources.**  
Installation requires suitable permissions for configuration and runtime resources, including `.env`. The container build explicitly adjusts permissions on `var`, `config`, `public`, `migrations`, and `.env`.

**OPS-05 — Runtime settings.**

| Setting | Purpose |
|---|---|
| `APP_SECRET` | Framework and remembered-login secret |
| `DATABASE_URL` | Database connection |
| `MAILER_DSN` | Main outbound transport |
| `UV_SESSION_COOKIE_LIFETIME` | Session cookie and garbage-collection lifetime |
| `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` | Optional local database bootstrap in the container |
| `MYSQL_ROOT_PASSWORD` | Root database credential used during container bootstrap |

An empty fallback for `DATABASE_URL` permits cache warmup before a database connection is available; it does not enable normal database operation.

The container build installs Apache, MySQL, PHP 8.1, required supporting packages, and Composer dependencies. Its web document root is `/var/www/uvdesk/public`, served on port 80.

### 8.3 Backup / Recovery

No backup schedule, restore procedure, recovery objective, or persistent-container volume contract is defined by the local deployment configuration.

### 8.4 Monitoring / Diagnostics

The framework shall log PHP errors. The container’s Apache configuration shall produce access and error logs.

No dedicated health endpoint, metrics contract, alerting policy, or distributed tracing requirement is specified.

### 8.5 Support / Maintenance

Product documentation directs installation support to the community forums and component-specific defects to the relevant package maintainers.

Security vulnerabilities are to be reported privately to `support@uvdesk.com`, rather than disclosed publicly.

## 9. Constraints

### 9.1 Technical Constraints

The principal constraints are:

- Dependency-provided helpdesk behavior and routes.
- A JavaScript-dependent browser installer.
- MySQL-oriented database configuration.
- Locally configured upload storage.
- Writable installation resources.
- External package and recipe availability during Composer-based setup.

The following remain unresolved for a complete production acceptance specification:

- Bundle-level field validation and ticket state transitions.
- Fine-grained staff permissions and ticket ownership enforcement.
- API authentication details and operation schemas.
- Mailbox scheduling, deduplication, and delivery guarantees.
- Workflow ordering and failure semantics.
- Attachment-limit enforcement.
- Installation rollback and safe retry behavior.
- Tested runtime-version compatibility.

### 9.2 Regulatory Constraints

No regulatory compliance, data-residency, or certification requirement is established.

### 9.3 Standards / Policy Constraints

The project manifest declares MIT licensing, while the README states that included libraries and bundles use OSL-3.0. These may concern different distribution components; this specification does not collapse them into a single license obligation.

### 9.4 Resource Constraints

Published deployment guidance specifies at least 4 GB of memory and a processor of at least 1 GHz. These values are not measured capacity guarantees.

## 10. Verification and Acceptance

### 10.1 Requirement Verification Criteria

Acceptance shall distinguish browser behavior from server-side effects. Displaying a successful response is insufficient to establish database creation, administrator persistence, or access enforcement.

| Area | Verification criteria |
|---|---|
| Wizard order | Starting opens preflight; premature direct navigation returns to welcome |
| Preflight presentation | Each check renders its result; extension and permission counts are displayed; Redis remains advisory |
| Database validation | Empty required fields disable progression; create-database choice is transmitted as `1` or `0` |
| Database response | Only Boolean `status: true` advances; a negative result displays the connection-failure notice |
| Administrator validation | Invalid names, malformed addresses, weak passwords, and mismatched confirmation prevent progression |
| Prefix validation | Empty, identical, and non-alphanumeric values fail field validation |
| Finalization | Requests occur in the specified order; returned destinations populate the completion view |
| Access control | Staff and customer requests follow their configured roles and exceptions |
| Session behavior | Configured session lifetime and staff remember-me settings are applied |
| Localization | English is the default and fallback; configured locale identifiers are available to the application |
| Deployment | Public-directory serving, database connectivity, mail configuration, and required permissions support startup |

### 10.2 Acceptance Criteria

The criteria in §10.1 apply subject to the following acceptance boundaries:

- Bundle-supplied capabilities require integration tests against the installed packages.
- Ticket ingestion, communication, filtering, automation, and self-service publication cannot be accepted solely from package registration or product descriptions.
- Preflight completion shall not be treated as certification that every system prerequisite has passed.

No local executable test suite was identified to establish that these acceptance criteria currently pass.

### 10.3 Verification Methods

Appropriate verification consists of:

- Browser interaction tests for validation and navigation.
- Controlled HTTP responses for installer success and failure branches.
- Integration tests for database, administrator, and route creation.
- Role-based access tests for staff, customer, and read-only paths.
- Deployment smoke tests for configuration and container startup.
- Bundle-level functional tests for the advertised helpdesk workflows.

## 12. Requirements Management Information

### 12.1 Requirement Attributes

Identifiers distinguish the following requirement categories:

| Prefix | Requirement category |
|---|---|
| `FR` | Functional |
| `UI` | User interface |
| `INT` | Integration interface |
| `DATA` | Data |
| `SEC` | Security |
| `NFR` | Quality |
| `OPS` | Operational |

### 12.2 Status

This document describes the current distribution and its contract boundaries. It does not assign release commitments or approval ownership that the product has not specified.

Changes to installed bundle versions, authentication configuration, installer endpoints, field validation, database configuration, or deployment scripts can change this baseline.

Detailed helpdesk requirements must be updated alongside the responsible component contracts rather than assumed to remain constant across package upgrades.

### 12.3 Priority

Business priorities are not assigned by this specification.
