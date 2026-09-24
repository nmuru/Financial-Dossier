---
model: anthropic/claude-haiku-4.5
---

# Scope Description

## 1. Document Control
- **Document title:** UVdesk Community Skeleton – System Scope
- **Version:** 1.0
- **Status:** Final
- **Date:** 2024
- **Author / owner:** UVdesk Community Project
- **Repository:** `uvdesk/community-skeleton`

## 2. Purpose and Scope of This Document

### 2.1 Purpose

This document defines the system boundary, included capabilities, external dependencies, and material constraints of the UVdesk Community Skeleton repository as implemented. It establishes what the repository is responsible for, what functionality lies within its scope, what external systems it depends on, and which capabilities are deliberately external to this codebase.

### 2.2 Scope of the Description

This scope analysis focuses on the UVdesk Community Skeleton as a complete runtime artifact, including:

- The PHP/Symfony application initialization layer
- Installation and configuration orchestration
- Environment and deployment support
- Integration and bundling of dependent modules
- Internationalization infrastructure
- Community contribution and governance mechanisms

Excluded from this scope document:

- Detailed architecture of dependent bundles (stored in separate repositories)
- Internal implementation details of the skeleton's supporting utilities
- Development-only tooling and testing infrastructure
- Future product roadmap or planned capabilities

### 2.3 Intended Audience

- Software engineers and architects evaluating the UVdesk platform
- Deployment engineers planning installation and operation
- Open-source contributors understanding the repository structure
- Product owners and stakeholders defining integration scope

## 3. System / Product Overview

### 3.1 System Identification

**UVdesk Community Skeleton** is an open-source helpdesk and customer support ticketing platform. It is distributed via Packagist as `uvdesk/community-skeleton` and serves as the **deployment entry point and configuration orchestration layer** for a modular, multi-repository helpdesk system. The skeleton itself is not a monolithic application but rather a bootstrapping and integration framework that brings together five separately-maintained functional modules.

**Repository:** https://github.com/uvdesk/community-skeleton  
**License:** Open Software License (OSL) v3.0  
**Language:** PHP (Symfony framework)  
**Package Type:** Symfony Flex project skeleton

### 3.2 Business or Operational Context

UVdesk addresses the **customer support and helpdesk management** domain. The system is designed for organizations that need to:

- Manage customer support requests and issues through a centralized helpdesk
- Ingest and respond to support communications via email
- Automate support workflows and ticket routing
- Extend the platform with custom functionality
- Operate a multi-agent support team across multiple communication channels

The platform positions itself as an open-source alternative to commercial helpdesk systems, with a community-driven governance model and global market positioning (12-language support).

### 3.3 System Objectives

The UVdesk Community Skeleton fulfills these primary objectives:

1. **Deployment orchestration:** Provide a unified entry point for downloading, installing, and configuring the complete UVdesk platform from source
2. **Configuration management:** Establish Symfony framework, Doctrine ORM, security, and service configurations needed for helpdesk operation
3. **Setup automation:** Guide administrators through initial installation and configuration via wizard-based UI and command-line tools
4. **Module integration:** Load and coordinate five functional bundles (Core Framework, Automation, Mailbox, Support Center, Extension Framework) in a coherent runtime
5. **Community enablement:** Maintain issue tracking, contribution workflows, and governance structures for open-source collaboration
6. **Internationalization:** Provide translation infrastructure for 12 supported languages

### 3.4 Major Capabilities

**Implemented in the Skeleton:**

- **Installation Wizard:** Browser-based configuration interface guiding administrators through system setup, database configuration, user creation, and initial deployment
- **Database Setup and Migration:** Automated schema creation, entity population, and database connection verification
- **Environment Configuration:** Application-level configuration for supported locales, asset paths, file upload limits, and site parameters
- **Symfony Framework Initialization:** Full Symfony 5.4+ framework setup with security, routing, templating, ORM, and service management
- **Docker Deployment Support:** Containerized deployment with Apache2, PHP 8.1, MySQL integration, and pre-configured runtime environment
- **Internationalization Infrastructure:** Translation catalogs and locale management for 12 languages (Arabic, Danish, German, English, Spanish, French, Hebrew, Italian, Polish, Portuguese Brazilian, Turkish, Chinese)
- **Image Cache Tracking:** Caching and serving of external images referenced in support communications
- **Community Governance:** Issue templates, contribution guidelines, and collaboration workflows

**Provided by Dependent Bundles (Out-of-Scope in This Repository):**

- Ticket lifecycle management
- Agent and customer user management
- Email mailbox integration and processing
- Automation rules and workflows
- API endpoints for external integration
- Customer-facing support portal
- Extension and plugin architecture

## 4. System Context and Boundaries

### 4.1 System Boundary

The UVdesk Community Skeleton constitutes a **configuration and orchestration layer** for a modular helpdesk platform distributed across six separate repositories. The skeleton boundary encompasses:

- **Inside:** Framework initialization, deployment wizards, environment configuration, routing coordination, base controllers, installation verification, image caching
- **Outside:** Business entity models, ticket workflows, customer portal UI, email processing, automation rule execution, extension loading (implemented in dependent bundles)

### 4.2 Internal Scope

**Repository Structure (78 tracked files):**

```
src/                    (15 files) - PHP application code
├── Console/            - CLI commands for wizards and environment setup
├── Controller/         - HTTP controllers for setup wizard and image caching
├── Entity/             - Skeleton-specific entity placeholders
├── EventListener/      - Exception event handling
├── Migrations/         - Database migration scaffolding
├── Repository/         - Repository pattern interfaces
├── Resources/          - Configuration and routing
├── Routing/            - Symfony routing resource orchestration
└── Service/            - URL image cache service

config/                 (12 files) - Symfony framework configuration
├── bundles.php         - Bundle registration
├── packages/           - Framework, Doctrine, Security, Mailer, Twig configs
├── routes.yaml         - Wizard and infrastructure routes
└── services.yaml       - Service definitions

public/                 (9 files) - Web-accessible assets
├── index.php           - Symfony application entry point
├── css/                - Wizard UI styling
├── scripts/            - Wizard JavaScript
└── attachments/        - Directory for uploaded files

templates/              (3 files) - Twig templates
├── installation-wizard/ - Setup UI
├── errors/             - Error pages
└── mail.html.twig      - Email template

translations/           (13 files) - Language catalogs (12 languages + .gitignore)

.docker/                (5 files) - Docker build and runtime configuration
├── bash/               - Container entrypoint script
└── config/             - Apache, PHP configuration

.github/                (7 files) - GitHub community workflows
├── CONTRIBUTING.md     - Contribution guidelines
├── ISSUE_TEMPLATE/     - Bug report, feature request templates
├── PULL_REQUEST_TEMPLATE.md
└── SECURITY.md         - Security policy

Root configuration files
```

### 4.3 External Entities and Systems

**Dependent Software Bundles (Required Runtime Dependencies):**

1. **`uvdesk/core-framework` (^1.1.7)** — Implements core business entities (Users, Tickets, Roles), ORM layer, common services, and controller base classes.

2. **`uvdesk/automation-bundle` (^1.1.4)** — Handles workflow automation, rule processing, and conditional ticket routing.

3. **`uvdesk/mailbox-component` (^1.1.5)** — Manages email ingestion via IMAP, outbound email sending via SMTP, and integration of customer communications into the ticketing system.

4. **`uvdesk/support-center-bundle` (^1.1.3)** — Provides customer-facing web portal for submitting support tickets, tracking existing tickets, and viewing the knowledge base.

5. **`uvdesk/extension-framework` (^1.1.2)** — Enables third-party developers to create and register custom extensions, plugins, and functionality.

6. **`uvdesk/api-bundle` (^1.1.4)** — Implements REST API endpoints for programmatic access to helpdesk functions.

**External Infrastructure and Services:**

- **Relational Database:** MySQL/MariaDB (Doctrine ORM abstraction supports multiple databases; MySQL is primary in Docker deployment)
- **Email Services:** IMAP servers (for mailbox ingestion) and SMTP servers (for outbound communications)
- **Web Server:** Apache2 with PHP FPM or mod_php
- **Update Service:** `https://updates.uvdesk.com/api/updates` (referenced in setup wizard for version checks)
- **Package Repository:** Packagist (PHP package distribution)

### 4.4 Interfaces Across the Boundary

**HTTP Request/Response Interfaces:**

The skeleton provides these HTTP entry points:

| Route | Method | Purpose |
|-------|--------|---------|
| `/wizard/xhr/check-requirements` | POST | Verify system requirements during installation |
| `/wizard/xhr/verify-database-credentials` | POST | Validate database connection parameters |
| `/wizard/xhr/intermediary/super-user` | POST | Store initial administrator credentials |
| `/wizard/xhr/website-configure` | POST | Configure website name and URL |
| `/wizard/xhr/load/configurations` | POST | Load and apply Symfony configurations |
| `/wizard/xhr/load/migrations` | POST | Execute database schema migrations |
| `/wizard/xhr/load/entities` | POST | Populate database with initial entities |
| `/wizard/xhr/load/super-user` | POST | Create initial admin user account |
| `/wizard/xhr/load/website-configure` | POST | Update website configuration in database |
| `/tracker/xhr/get/cacheImage` | — | Fetch cached external images |
| `/` (wizard GET) | GET | Display installation wizard UI |

**CLI Interfaces:**

The skeleton provides these command-line interfaces:

- `uvdesk:configure-helpdesk` — Post-deployment configuration verification and setup
- `uvdesk_wizard:env:update` — Update environment variables in `.env` file

**Configuration Interfaces:**

- `.env` file — Runtime environment variables (database credentials, app name, mail settings, cache drivers)
- `config/packages/uvdesk.yaml` — Application parameters (locale settings, asset paths, upload limits, site configuration)
- `config/packages/uvdesk_mailbox.yaml` — Mailbox configuration (IMAP/SMTP servers, email delimiters)
- `config/bundles.php` — Bundle registration and enablement

### 4.5 Organizational / Operational Boundaries

**Community Governance:**

- **Issue Tracking:** Separate issue repositories for Core Framework, Support Center, Mailbox Component, Automation Bundle, and Extension Framework. Bug reports are triaged to the appropriate repository.
- **Contribution Workflow:** GitHub-based pull request process with issue-based branching (`issue-<ID>` format), contribution guidelines, and community forum integration.
- **Licensing:** Open Software License (OSL) v3.0

**Deployment Boundary:**

- **Docker:** Complete containerized deployment via Dockerfile (Ubuntu 20.04+, Apache2, PHP 8.1, MySQL)
- **Non-Docker:** Manual installation on Ubuntu/Debian with Apache, PHP, MySQL (documented in INSTALLATION GUIDE.md)

## 5. In-Scope Areas

### 5.1 Capabilities

**1. Installation and Configuration Orchestration**

- Web-based installation wizard guiding administrators through setup
- System requirements verification (PHP extensions: imap, mailparse, mysqli)
- Database connectivity validation and connection parameter storage
- Environment variable management and `.env` file configuration
- Doctrine schema migration execution
- Initial user account (super-admin) creation
- Website configuration (site URL, site name, localization)

**2. Framework and Dependency Initialization**

- Symfony 5.4+ framework bootstrap and configuration
- Doctrine ORM entity manager setup and database abstraction
- Security framework initialization (authentication/authorization infrastructure)
- Twig template engine configuration
- Service container and dependency injection setup
- Bundle lifecycle management and registration
- Event subscriber and listener registration

**3. Routing and Request Handling**

- Installation wizard HTTP endpoints (10+ routes)
- Image caching service endpoint
- Route delegation to dependent bundles via custom routing resource
- Request routing from HTTP to controller actions

**4. Error Handling and Exception Management**

- Global exception subscriber for standardized error responses
- Error page template rendering
- Exception logging and reporting

**5. Internationalization (i18n) Infrastructure**

- Translation message catalogs for 12 languages (Arabic, Danish, German, English, Spanish, French, Hebrew, Italian, Polish, Portuguese Brazilian, Turkish, Chinese)
- Language selection and locale configuration
- Message extraction and translation coverage

**6. External Image Caching Service**

- Fetching and caching of external images referenced in email communications
- Image URL transformation for cache hits
- Image cache manager service

**7. Environment and Deployment Support**

- Docker containerization (Apache2, PHP 8.1, MySQL)
- Environment variable templating (.env.example)
- Application runtime configuration
- Multi-stage Docker build
- Container entrypoint and lifecycle management

### 5.2 Processes

**Installation Process:**

1. Administrator accesses installation wizard via `/` route
2. System requirements are checked (PHP version, required extensions)
3. Database credentials are validated (connectivity, permissions)
4. Administrator provides helpdesk configuration (site name, site URL, locale)
5. Administrator creates initial super-admin user account
6. System executes database migrations (Doctrine schema creation)
7. System populates database with initial entities (roles, ticket types, priorities, etc.)
8. System applies website configuration to database
9. Installation completes; administrator is directed to main application
10. Dependent bundles (Core Framework, Support Center, Mailbox, etc.) initialize and provide business functionality

**Configuration Update Process:**

1. Administrator runs `uvdesk:configure-helpdesk` command or wizard
2. System verifies setup and identifies any mis-configurations
3. Wizard prompts for required configurations
4. System updates `config/packages/uvdesk.yaml` or `.env` file
5. Changes are applied immediately or require cache clear

**Request Handling Process:**

1. Client sends HTTP request to Apache web server
2. Apache routes to `public/index.php` (Symfony front controller)
3. Symfony kernel bootstraps and loads configuration
4. Framework routes request to appropriate controller or bundle
5. Controller executes business logic (delegated to bundles for core functions)
6. Response is rendered and returned to client

### 5.3 Data

**Configuration Data:**

- Database connection strings (host, port, user, password, database name)
- Application parameters (site URL, site name, locales, timezone, currency)
- Mailbox configurations (IMAP/SMTP server credentials, email delimiters)
- Security credentials (admin user, password hash)
- Environment variables (app mode, debug mode, logging)

**Application Data (Persisted in Database):**

- Users (agents, admins, customers)
- Support tickets
- Communications (email, comments)
- Roles and permissions
- Automation rules
- Configuration settings
- Extensions and plugins
- Knowledge base articles

**Translation Data:**

- Message catalogs (YAML format, 12 languages)
- Locale-specific formatting (dates, times, currencies)

**Transient Data:**

- Session state (authenticated user, CSRF tokens)
- Cache entries (image cache, application cache)

### 5.4 Components / Subsystems

**Web Application Framework:**
- Symfony kernel and request/response cycle
- Service container and dependency injection
- Security framework (authentication/authorization)
- Routing system

**Database Layer:**
- Doctrine ORM entity manager
- Database abstraction and schema management
- Migrations system

**Installation Subsystem:**
- Setup wizard controller and CLI commands
- Requirements verification
- Database connection validation
- Configuration storage

**Internationalization Subsystem:**
- Translation loader and cache
- Locale provider and switcher
- Message catalog management

**Image Caching Subsystem:**
- External image fetcher
- Cache storage manager
- Image URL transformer

**Request Handling Subsystem:**
- HTTP routing
- Controller execution
- Response rendering
- Error handling

**Dependent Module Integrations:**
- Bundle loader (Symfony bundles from dependent repositories)
- Route delegation to bundles
- Service cross-registration

### 5.5 Operational Environments

**Supported Environments:**

1. **Local Development:** On-machine installation with Symfony built-in web server or local Apache
2. **Docker Container:** Containerized deployment using provided Dockerfile
3. **Ubuntu/Debian Server:** Manual installation on Ubuntu/Debian Linux with Apache, PHP, MySQL
4. **Cloud Platforms:** Any environment supporting PHP 7.2.5+, Apache/Nginx, and MySQL

**Configuration Modes:**

- **Development Mode:** APP_ENV=local, APP_DEBUG=true, verbose logging
- **Production Mode:** APP_ENV=prod, APP_DEBUG=false, optimized caching

**Database Support:**

- Primary: MySQL 5.7+ / MariaDB (Docker default)
- Supported via Doctrine: PostgreSQL, SQLite, SQL Server (not tested in this skeleton)

## 6. Out-of-Scope Areas

### 6.1 Explicit Exclusions

**Business Entity Management:** The skeleton does not implement user, ticket, role, or permission entities. These are implemented in `uvdesk/core-framework` (separate repository). The skeleton contains only configuration and placeholders.

**Ticket Lifecycle Logic:** Ticket creation, assignment, status transitions, and resolution workflows are not implemented in the skeleton. This is the responsibility of the Core Framework and Automation Bundle.

**Email Processing:** The skeleton does not process incoming email or send outbound communications. This is delegated to `uvdesk/mailbox-component` via IMAP/SMTP configuration.

**Customer Portal:** The skeleton does not provide a customer-facing support portal. This is implemented in `uvdesk/support-center-bundle`.

**REST API:** API endpoints are not implemented in the skeleton. The `uvdesk/api-bundle` provides REST API functionality.

**Extension Registry:** The skeleton does not provide extension loading, marketplace, or plugin architecture. This is handled by `uvdesk/extension-framework`.

**Multi-Tenancy:** The skeleton does not support multi-tenant architectures. A single installation serves a single organization with a shared database schema.

**Scheduled Jobs / Background Workers:** The skeleton does not implement background job processing, queues, or scheduled tasks.

**Real-Time Notifications:** The skeleton does not implement WebSocket connections, push notifications, or real-time updates.

**Single Sign-On (SSO) / SAML:** The skeleton does not implement enterprise authentication mechanisms. Skeleton security is limited to local username/password authentication.

**Audit Logging:** The skeleton does not implement comprehensive audit trails or user activity logging beyond application error logs.

**Multi-Language Support for Data:** While the skeleton provides translation infrastructure, it does not translate user-submitted content (ticket messages, knowledge base articles). Localization is limited to UI messages.

### 6.2 Adjacent Systems / Responsibilities

**Version Control / CI/CD:** GitHub Actions workflows and CI/CD pipelines are not part of the skeleton; these are community infrastructure.

**Hosting Infrastructure:** The skeleton does not manage cloud deployment, load balancing, database replication, or disaster recovery.

**Email Service Management:** While the skeleton configures mailbox access, it does not manage email servers or SMTP/IMAP providers. These are external services configured by the administrator.

**Monitoring and Observability:** Application performance monitoring (APM), error tracking services (Sentry, etc.), and operational dashboards are not part of the skeleton.

**Documentation Hosting:** The skeleton does not host or serve documentation. Docs are at docs.uvdesk.com (external).

**Community Forum / Support:** Community support infrastructure is hosted externally at forums.uvdesk.com.

### 6.3 Deferred or Future Scope

No explicit future scope commitments are documented in the repository. The skeleton focuses on deployment orchestration for the current modular architecture. Future enhancements would be addressed in dependent bundles or new bundles added to the ecosystem.

## 7. Stakeholders and Concerns

### 7.1 Stakeholders

**System Administrators:**
- Concern: Easy installation, clear configuration requirements, troubleshooting guidance
- Supported by: Installation wizard, system requirements checker, configuration validation, INSTALLATION GUIDE.md, Docker deployment

**Developers / System Integrators:**
- Concern: Clear module boundaries, extensibility, API documentation, integration points
- Supported by: Modular architecture with separate repositories, Extension Framework, API Bundle, contribution guidelines

**End Users (Customers / Support Agents):**
- Concern: Reliable ticket management, responsive interface, email integration
- Supported by: Core Framework entities, Support Center Bundle UI, Mailbox Component integration

**Open-Source Contributors:**
- Concern: Clear governance, contribution workflow, issue tracking, code review process
- Supported by: CONTRIBUTING.md, issue templates, pull request template, separate repository issue tracking, GitHub community guidelines

**Hosted Service Providers / DevOps Teams:**
- Concern: Containerization, scalability, environment flexibility, deployment repeatability
- Supported by: Dockerfile, Docker Compose support (implied), environment variable configuration, modular dependency structure

**Product / Business Stakeholders:**
- Concern: Platform viability, market positioning, competitive features, sustainability
- Supported by: Open source licensing (OSL v3.0), community governance, documentation and guides, version management (changelogs)

### 7.2 Stakeholder Concerns and Mitigation

| Concern | Stakeholder | Mitigation in Skeleton |
|---------|-------------|----------------------|
| Complex installation | Administrators | Web-based wizard, system requirements checker, INSTALLATION GUIDE.md |
| Version conflicts | Developers | Explicit version constraints in composer.json, semantic versioning |
| Missing features | End users | Modular architecture allows adding bundles (Automation, Support Center, API) |
| Contribution friction | Contributors | Issue templates, contribution guidelines, separate module repositories |
| Deployment complexity | DevOps | Dockerfile, .env configuration, automated setup scripts |
| Data integrity | All stakeholders | Doctrine ORM with migrations, database validation, transaction support (in bundles) |
| Localization gaps | Global users | 12-language translation infrastructure |
| Security issues | All stakeholders | Security.md policy, vulnerability handling process |

### 7.3 Business / Operational Constraints

**Licensing:**
- Open Software License (OSL) v3.0 — Copyleft license requiring derivative works to remain open source
- Implications: Commercial forks must share modifications

**Development Model:**
- Community-driven open source with structured contribution process
- Separate repositories for modules enable independent release cycles

**Support Model:**
- Community forums (forums.uvdesk.com) for general support
- GitHub issues for bug tracking and feature requests
- Commercial support offerings are separate (not in skeleton)

**Market Positioning:**
- Positioned as open-source alternative to commercial helpdesk platforms (Zendesk, Jira Service Management, etc.)
- Global market focus (12-language support, international community)

## 8. Assumptions, Constraints, and Dependencies

### 8.1 Assumptions

1. **Target Organizations:** Organizations seeking customer support ticketing systems, support teams with 1–100+ agents, small to mid-market businesses
2. **Deployment Model:** Self-hosted or private cloud deployment (not SaaS by default)
3. **Technical Capability:** Administrators have Linux/DevOps knowledge or access to hosting providers
4. **Database:** MySQL/MariaDB is the primary supported database (though Doctrine supports others)
5. **Web Server:** Apache2 with PHP (Docker Compose or manual setup)
6. **Email:** Organizations have existing email infrastructure (IMAP/SMTP) for ticket ingestion

### 8.2 Constraints

**Technical Constraints:**

1. **PHP Version:** Requires PHP 7.2.5 or 8.0+. Support for PHP 5.6 and earlier has been dropped.
2. **Extensions Required:** PHP extensions: imap, mailparse, mysqli (enforced in requirements checker)
3. **Database:** Doctrine ORM provides abstraction, but Relational databases only (no NoSQL support in skeleton)
4. **Temporary File Size:** PHP upload limits (max_post_size: 8MB, upload_max_filesize: 2MB by default in config)
5. **File Uploads:** Max 20 files per request
6. **Session Storage:** Defaults to file-based (configurable: file, database, Redis via dependent bundles)
7. **Single Process:** No distributed job queue in skeleton; dependent bundles may add this

**Operational Constraints:**

1. **Locales:** Hard-coded to 12 supported locales (app_locales parameter). Adding new languages requires code modification.
2. **Timezone:** Application-wide timezone (APP_TIMEZONE). Per-user timezone support must be implemented in dependent bundles.
3. **Single Site URL:** Configuration assumes single site URL. Multi-domain support would require dependent bundle enhancements.
4. **Security:** Password encoding is delegated to Symfony Security (no custom password hashing logic in skeleton).
5. **Email:** Mailbox configuration is static (cannot be modified via UI in skeleton; must edit config files or use wizard).

**Deployment Constraints:**

1. **Docker Base:** Ubuntu:latest image (not Alpine or other lightweight images) — larger container size
2. **No Load Balancing:** Single-instance deployment. Load balancing would require external infrastructure.
3. **No Replication:** Database replication is not configured in skeleton; must be set up separately.
4. **Stateful:** Relies on filesystem for sessions, cache, temporary files (not horizontally scalable by default).

**Modular Architecture Constraints:**

1. **Dependency Management:** Five required bundles must be installed and compatible (version constraints in composer.json)
2. **Bundle Versioning:** If dependent bundles have incompatible versions, installation fails (Composer version resolution)
3. **Custom Routing:** Routing system uses custom resource type (uvdesk) defined in dependent bundles; must be registered to work

### 8.3 Dependencies

**Hard Dependencies (Required for Operation):**

1. **PHP Runtime:** 7.2.5+ or 8.0+
2. **Symfony Framework:** 5.4+ (specified in composer.json)
3. **Doctrine ORM:** 2.x (via orm-pack)
4. **Twig Templating:** 2.12+ or 3.0+
5. **uvdesk/core-framework:** ^1.1.7 (business entities and services)
6. **uvdesk/mailbox-component:** ^1.1.5 (email integration)
7. **uvdesk/automation-bundle:** ^1.1.4 (workflow automation)
8. **uvdesk/support-center-bundle:** ^1.1.3 (customer portal)
9. **uvdesk/extension-framework:** ^1.1.2 (extensibility)
10. **uvdesk/api-bundle:** ^1.1.4 (REST API)

**Conditional Dependencies (Flex recipes; enabled during installation):**

1. **Doctrine Annotations:** ^1.0 (entity mapping)
2. **Doctrine Fixtures:** ^3.4 (development data seeding)
3. **Google reCAPTCHA:** ^1.2 (form protection)
4. **Knp Paginator:** ^5.8 (list pagination)
5. **Symfony Security:** ^6.1 (authentication/authorization)
6. **Symfony Mailer:** * (email sending)
7. **Symfony Console:** * (CLI commands)
8. **Intervention Image:** ^2.4 (image manipulation for cache)
9. **Intervention ImageCache:** ^2.5.2 (image caching)

**External Runtime Dependencies (Not in Code):**

1. **MySQL 5.7+ or MariaDB 10.3+** (relational database)
2. **Apache 2.4+ with mod_rewrite** or Nginx (web server)
3. **IMAP-enabled email server** (for mailbox ingestion)
4. **SMTP-enabled email server** (for outbound mail)

**Development Dependencies (Not in Production):**

- Symfony Maker Bundle (scaffolding)
- Symfony Profiler Pack (debugging)
- Symfony Test Pack (testing)
- PHPUnit (unit testing)

## 9. Scope Acceptance Criteria

A deployment of UVdesk Community Skeleton is considered within scope when:

- ✓ Symfony framework is fully initialized and responding to HTTP requests
- ✓ Installation wizard completes successfully or is skipped for an already-configured installation
- ✓ All five dependent bundles (Core Framework, Automation, Mailbox, Support Center, Extension Framework) are registered and loaded
- ✓ Database schema is migrated and initial entities are populated
- ✓ Administrator user account is created with valid credentials
- ✓ Mailbox configuration is stored and retrievable
- ✓ System requirements verification passes for PHP version and required extensions
- ✓ Application responds to setup wizard routes (`/wizard/xhr/*`) and configuration endpoints
- ✓ Internationalization system loads configured locale and translations
- ✓ Image caching service endpoint is functional
- ✓ Environment variables are properly loaded from `.env` file
- ✓ Security framework is initialized with authentication ready
- ✓ CLI commands (`uvdesk:configure-helpdesk`, `uvdesk_wizard:env:update`) execute successfully
- ✓ Docker deployment (if used) starts Apache, MySQL, PHP without errors and wizard is accessible via browser

## 10. References

**Official Documentation:**
- UVdesk OpenSource: https://www.uvdesk.com/en/opensource/
- UVdesk Documentation: https://docs.uvdesk.com/
- Community Forum: https://forums.uvdesk.com/
- Installation Guide (in repo): INSTALLATION GUIDE.md

**Repository References:**
- Community Skeleton: https://github.com/uvdesk/community-skeleton
- Core Framework: https://github.com/uvdesk/core-framework
- Support Center Bundle: https://github.com/uvdesk/support-center-bundle
- Mailbox Component: https://github.com/uvdesk/mailbox-component
- Automation Bundle: https://github.com/uvdesk/automation-bundle
- Extension Framework: https://github.com/uvdesk/extension-framework
- API Bundle: https://github.com/uvdesk/api-bundle

**Technical References:**
- Symfony Framework Docs: https://symfony.com/doc/5.4/
- Doctrine ORM Docs: https://www.doctrine-project.org/projects/orm.html
- Packagist Package: https://packagist.org/packages/uvdesk/community-skeleton

**Community and Governance:**
- GitHub Contributing Guide: .github/CONTRIBUTING.md
- Security Policy: .github/SECURITY.md
- Issue Templates: .github/ISSUE_TEMPLATE/
- License: LICENSE.txt (OSL v3.0)
- Changelogs: CHANGELOG-1.0.md, CHANGELOG-1.1.md, CHANGELOG-1.2.md
