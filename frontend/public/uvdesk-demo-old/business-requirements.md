---
model: deepseek/deepseek-v4-flash-0731
---

# Business Requirements — UVdesk Community Skeleton

## 1. Business Context

UVdesk Community is an open-source customer-support helpdesk system intended for organisations that want to operate their own support operation rather than rely on a hosted third-party service. This repository — the *Community Skeleton* — is the distribution and composition layer of that product: it is the package that an organisation obtains, installs, and configures on its own systems, and it assembles the full helpdesk from a defined set of product components (core helpdesk framework, support centre, mailbox/email handling, workflow automation, extension mechanism, and API access).

The repository therefore exists to satisfy two distinct organisational needs: (a) the need of an organisation to obtain, deploy, and activate a self-hosted helpdesk, and (b) the open-source project's own need to distribute, measure usage of, and govern contributions to that product. Most day-to-day helpdesk behaviour (ticket handling, agent work, email conversion, automation, knowledge base) is delivered through the composed components and is only evidenced here through distribution documentation; the requirements reconstructed below concentrate on what this layer verifiably does, with product-level claims identified where they come from product documentation rather than in-repository behaviour.

## 2. Business Objectives

- Provide organisations with a freely available, self-hosted customer-support helpdesk that can be customised and extended to their own workflows.
- Make deployment achievable by a technical but non-specialist staff member through a guided, validated setup process with clearly stated prerequisites.
- Support a worldwide audience by localising the setup and system interface into multiple languages and by distributing through several channels (package manager, downloadable archive, container image, pre-built cloud image).
- Keep installations maintainable over time by providing a repeatable configuration/sanity-check routine that verifies connections, keeps the stored data structure in step with the application version, and allows controlled data migration.
- Sustain an open-source project through governed contribution channels, private security reporting, funding, and basic product-usage measurement.

## 3. Stakeholders and Actors

| Actor | Role in the business process |
|---|---|
| **Organisation / helpdesk operator** | The business that acquires and runs the helpdesk to serve its customers. |
| **Installer (system administrator)** | Person who obtains the package, prepares the operating environment, and runs the guided installation or command-line configuration routine. |
| **Super administrator** | The first administrative account created during installation; owns the initial access to the administration area and enables further staff provisioning. |
| **Support agents / members** | Helpdesk staff who work tickets in the administration area (member-level access). |
| **End customers** | People who interact with the customer-facing support portal and knowledge base, including by email. |
| **Contributors and reporters** | Community members who report defects, request features, or submit code. |
| **Product vendor / project maintainers** | Operate distribution outlets, documentation, community support channels, and receive installation-usage records. |

## 4. Business Capabilities Required

**Acquisition and deployment.** The organisation must be able to obtain a complete, ready-to-install product package via multiple distribution routes (creator package, downloadable stable archive, pre-built container image, and a pre-configured cloud image on a public marketplace) and deploy it on its own hardware or infrastructure.

**Guided first-run installation.** The organisation must be able to complete setup through a web-based installer that leads the installer through a fixed sequence: welcome, system readiness check, database connection, administrator account details, and site access configuration, followed by an automated finalisation phase with visible progress.

**System readiness verification.** Before installation proceeds, the installer must verify that the target environment satisfies the product's prerequisites: a supported runtime version, the required supporting capabilities (mail-reading, mail-parsing, and database access), sufficient script execution time allowance, and write access to the files the installer must update — with clear remediation guidance when a check fails.

**Database provisioning and lifecycle management.** The installer must be able to connect to the organisation's existing database server using supplied credentials, use an existing database or create one on request, populate the initial required data, and keep the stored data structure aligned with the product version. The same alignment routine must support upgrading an already-running installation.

**Administrator account provisioning.** Every installation must result in at least one active administrative account usable to enter the administration area, created only after the supplied details pass validity rules. The process must be idempotent: re-running it must not create duplicate or conflicting administrative accounts.

**Site access configuration.** The organisation must be able to choose the web addresses under which the administration area and the customer-facing portal are reachable, with sensible defaults and validation that the two chosen addresses are distinct and usable.

**Localisation.** Setup and system-facing texts must be available in the organisation's chosen language from a supported set of languages, so that the product is approachable across markets.

**Maintainability and consistency checking.** The organisation must be able to re-run the configuration routine after installation to detect mis-configuration, re-establish database connectivity, and bring the data structure back in line with the product version.

**Containerised operation.** The organisation must be able to run the product inside a container with the supporting services brought up together, while retaining control of the database credentials used.

**Usage awareness.** The project must be able to record basic installation facts (deployed site address and administrator contact details) at completion of setup, for the purpose of measuring adoption and active use.

**Community governance.** The project must provide channelled intake of defect reports, feature requests, support questions, and security disclosures, with defined expectations for contribution quality (duplicate checks, problem-scope classification, branch and message conventions, pull-request review template).

## 5. Principal Business Workflows

### 5.1 First-run installation via the web installer

1. The installer opens the product's public site and starts the wizard.
2. The wizard verifies environment readiness — runtime version, required supporting capabilities, execution-time allowance, file write permissions, and a warning check on optional caching services — and blocks progression until the checks pass or the installer rectifies the environment.
3. The installer supplies database server details (host, port, optional version, user, password, database name) and chooses whether the system may create the database if it does not exist. The system verifies the connection before proceeding.
4. The installer provides the super administrator's name, email address, and a password (entered twice). The system validates format and strength rules and stores the details pending finalisation.
5. The installer configures the web addresses for the administration area and the customer portal, with defaults provided; the system validates that both are non-empty, use only letters and numbers, and are not identical.
6. The system finalises the installation in sequence: persists the database configuration, creates/aligns the data structure (initialising it when new), loads the initial dataset, creates the super administrator account, and stores the chosen web addresses — showing progress for each stage.
7. On success, the installer is presented with direct links to the administration area and the customer portal.

### 5.2 First-run installation or re-configuration via command line

The command-line routine performs the same checks: establish a database connection from the stored configuration or re-prompt for corrected details; verify or create the database; compare the data structure against the product version and migrate if needed; load initial data; confirm whether a super administrator exists and, if not, interactively collect valid details and create the account; then report completion.

### 5.3 Upgrade or data-structure alignment

When an instance's data structure is out of step with the product version (for example after a version update), the organisation runs the alignment routine, which either initialises a fresh structure or applies versioned updates in an ordered manner, loading any required base data alongside. The wizard's finalisation phase performs the same step for new installations.

### 5.4 Containerised deployment

On first start of the containerised product, the environment brings up the web service and the database service and, when the operator supplies database credentials via the container settings, provisions the required database and access. The application then runs under an unprivileged account for safety.

### 5.5 Community contribution and support intake

- **Defect reporting:** verify the defect is not already reported (including in the component repositories); verify the defect is general rather than specific to one installation; if installation-specific, use the community forum instead; otherwise file a report with environment details, reproduction steps, expected and actual results.
- **Feature requests:** file through the dedicated request channel before contributing code.
- **Security disclosures:** report privately to the product team rather than publicly.
- **Code contributions:** fork the relevant component repository, create a branch named after the issue, format commit messages as `Fixed #<issue> - <subject>`, and submit a pull request following the provided template.
- **Support questions:** directed to the commercial support site or community forums rather than the issue tracker.

## 6. Business Rules

### Environment readiness

- The installable environment must run a supported product-runtime version; installations on unsupported versions are refused with an explanatory message.
- The environment must provide the three required supporting capabilities (mail reading, mail parsing, database connectivity); each missing capability fails the readiness check.
- The execution-time allowance must be at least 30 seconds; insufficient allowance fails the readiness check with remediation guidance.
- The configuration files the installer must modify must be writable by the web process; the check attempts to repair permissions and reports failure with guidance if repair is not possible.
- An optional caching service, when present, must be correctly configured; the checker surfaces configuration instructions rather than silently ignoring it.

### Database rules

- The supplied database server and credentials must be verified before installation may proceed.
- The target database must exist or the installer must explicitly authorise the system to create it.
- The stored database configuration must reflect the verified, working connection.
- The data structure must match the product version's expected structure; the installation or alignment process must not complete successfully while a mismatch remains unresolved.
- For a new installation, the structure is initialised and the initial dataset loaded; for an existing installation, versioned updates are applied in order.

### Administrator account rules

- Account details are mandatory: name, valid email address, and password.
- Passwords must be at least 8 characters and no longer than 32, contain at least two letters, at least one digit, and at least one symbol, and contain no spaces; the two password entries must match.
- Each installation must end with exactly one active super administrator; if an account already exists in the target role, re-running the routine must not create a duplicate, and an existing user promoted to the role must not end up with conflicting assignments.

### Site access rules

- The administration-area address and the customer-portal address are both mandatory.
- Both may contain only letters and numbers and must be different from each other.

### Configuration safety

- The routine that rewrites stored configuration is restricted to non-production environments, protecting live installations from accidental reconfiguration.

### Usage recording

- On completion of setup (by either path), a lightweight record of the deployed site and administrator contact details is transmitted to the project's usage-collection service; failures in transmission must not break installation.

## 7. Required Business Outcomes

- A newly obtained product package can be transformed, by a guided and validated process, into a running helpdesk whose administration area and customer portal are reachable at addresses the organisation chose.
- The organisation ends the setup with working administrative access and with the stored data structure and initial data consistent with the product version.
- Existing installations can be brought back into consistency and upgraded without data-structure drift.
- The product is usable in the organisation's language, deployable on its own systems including containerised or marketplace cloud images, and maintainable by a technical administrator.
- The open-source project receives structured defect/feature/security intake and basic adoption measurement while protecting installation from tracking failures.

## 8. Scope Boundaries and Exclusions

- **Delegated helpdesk behaviour.** Ticket lifecycle management, agent work, email-to-ticket conversion, automation rules, knowledge-base authoring, and third-party extensions are delivered by separately maintained product components and are outside this repository's own code. Product documentation in this repository describes them, but their runtime behaviour is not verifiable from this repository alone.
- **Hosting model.** The product is oriented to self-hosting on the organisation's own environment; there is no evidence of a vendor-operated hosted service delivered from this repository.
- **Support entitlement.** The open-source distribution does not include a support obligation; assistance is channelled to community forums and a commercial support service.
- **Commercial extensions.** Additional paid modules and apps are advertised through the vendor's store and are not part of this distribution.
- **Tracking details.** The usage record includes site address and administrator name/email; how this is retained, used, or opted out of is not verifiable from this repository.

## 9. Business Requirements

### Acquisition and deployment

- Organisations must be able to obtain a complete, ready-to-run helpdesk package through the distribution channels the project publishes (package manager, stable archive, container image, and cloud marketplace image).
- Organisations must be able to deploy the product on their own systems, including inside a containerised environment where supporting services are started together.
- The deployment must be safe by default: where the operator supplies database credentials through the container settings, the required database and access must be provisioned automatically, and day-to-day operation must not run under a privileged account.

### Guided installation and configuration

- Installers must be able to complete setup through a guided web-based installer covering welcome, readiness, database, administrator, and site-access steps, or through an equivalent command-line routine.
- The installer must complete only when the target environment satisfies the product's prerequisites, and must clearly explain what to fix when it does not.
- The organisation must be able to point the installation at its existing database server, use an existing database or authorise creation of a new one, and have the connection verified before proceeding.
- Installers must not be able to accidentally proceed past a prerequisite failure, an unverified database connection, or invalid administrator details.
- Re-running the setup routine must not corrupt or duplicate an already-configured installation; it must detect existing state and only complete what is missing.

### Data structure and upgrade integrity

- A new installation must end with a data structure and initial dataset consistent with the product version.
- Existing installations must be able to have their data structure aligned to the product version through ordered, versioned updates without losing existing data.
- The setup or alignment routine must not report success while the data structure is out of step with the product version.

### Administrator access

- Every installation must result in exactly one active super administrator account that can access the administration area.
- Administrator details (name, email, password) must be validated before account creation, including a password-strength policy (minimum length, minimum letters, digit, symbol, no spaces) and matching confirmation entries.
- The process must prevent the creation of duplicate or conflicting administrative accounts when run more than once.

### Site access

- The organisation must be able to choose the web addresses for the administration area and the customer portal, with sensible defaults.
- The chosen addresses must be mandatory, restricted to letters and numbers, and distinct from each other.

### Localisation

- Setup and system-facing texts must be available in the organisation's language from the supported language set.

### Maintainability

- The organisation must be able to re-run the configuration routine after installation to detect mis-configuration and restore database connectivity and data-structure consistency.
- Static environment configuration must be safe from accidental modification outside non-production environments.

### Usage awareness (project-level)

- The project must be able to record basic adoption facts (deployed site address and administrator contact details) at the completion of setup, using either installer path, without allowing tracking failures to disrupt installation.

### Community and support governance (project-level)

- Defect reports must be checked against existing reports and across component trackers before being filed, and setup-specific problems must be routed to the community forum rather than the issue tracker.
- Security vulnerabilities must be disclosed privately to the project team rather than publicly.
- Feature requests must enter through the dedicated request channel before implementation.
- Code contributions must follow the project's conventions: fork the relevant component repository, name branches after the issue, use the prescribed commit-message format, and submit pull requests through the provided template.
- Support questions must be directed to the community forums and commercial support services rather than the issue tracker.

## 10. Constraints and Dependencies

- The organisation's environment must meet the published prerequisites (supported runtime version, required supporting capabilities, execution-time allowance, and write permissions) or installation cannot complete.
- During first-run setup, the system depends on the organisation providing a reachable database server with valid credentials.
- The web installer depends on external script libraries hosted on public content networks to render and drive the wizard; without network access to those libraries the wizard may not operate.
- The project's adoption measure depends on the completion of setup and on the availability of the project's usage-collection service; transmission failure is tolerated.
- The product's helpdesk capabilities depend on the separately maintained components it composes; changes in those components change product behaviour independently of this repository.
- The open-source project depends on community contributions, funding, and maintainer activity for continued evolution.

## 11. Uncertainties and Open Questions

- **Feature-set breadth.** The README's feature list (e.g., saved replies, ticket filtering, spam blocking, knowledge-base structure, reCAPTCHA, agent activity, marketing announcements) describes the composed product; the actual behaviour is delivered by external components and could not be verified in this repository. These should be treated as product-documentation claims rather than verified requirements of this layer.
- **Usage tracking governance.** The privacy terms, storage, and any opt-out mechanism for the installation/usage record are not documented in this repository.
- **Supported languages scope.** Twelve languages are evidenced; the exact completeness of each translation cannot be verified programmatically here.
- **Cloud image maintenance.** An AWS marketplace image is advertised in the README, but its content and update cadence are not verifiable from this repository.
