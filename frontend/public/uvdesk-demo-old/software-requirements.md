---
model: deepseek/deepseek-v4-flash-0731
---

# Software Requirements — UVdesk Community Skeleton

## 1. Scope and Requirements Boundary

This document reconstructs the requirements evidenced by the `uvdesk/community-skeleton` repository (community edition of the UVdesk helpdesk product). The repository is deliberately a **project skeleton and installation/composition layer** rather than the helpdesk application itself: it packages the UVdesk bundles (core framework, support center, mailbox component, automation bundle, extension framework, API bundle) as Composer dependencies and contributes the first-run installation experience, localization catalogs, error handling, image caching, and containerized deployment packaging.

Consequently, the requirements verified here are those of the skeleton layer: first-run installation, system-requirement assessment, database/website configuration, super-admin provisioning, CLI-based configuration commands, and deployment packaging. The customer- and agent-facing helpdesk behaviors (ticket lifecycle, support center, mailbox ingestion, automation rules, extension marketplace) are dependencies of the composed bundles; their existence is architecturally confirmed by this repository but their detailed behavior cannot be verified from this repository's source and is treated as inherited product capability, not as an in-repo requirement.

---

## 2. Actors and Trigger Conditions

| Actor | Demonstrated interaction |
|---|---|
| **Installer (web)** | Opens the site root and runs the browser-based installation wizard, entering system, database, admin, and website-prefix configuration. |
| **Installer (terminal)** | Runs `php bin/console uvdesk:configure-helpdesk` and answers interactive prompts for database and super-admin configuration. |
| **Operator / developer** | Deploys via Composer, zip archive, or Docker; provisions the `apps/` extension directory; manages `.env` and file permissions. |
| **End customer / agent / admin** | Consumes the helpdesk behavior delivered by the composed bundles (login flows, ticket workflows, knowledge base). These flows are governed by the skeleton's security and routing configuration. |
| **UVdesk update service** | Receives installation attribution records posted to `https://updates.uvdesk.com/api/updates`. |

Trigger conditions: the wizard is entered when the application is not yet configured (no support roles/admin users in the database); the terminal configuration command is invoked explicitly; the tracker image endpoint is requested by an external tracker script.

---

## 3. Functional Requirements

### 3.1 First-run detection and entry routing

The application root (`/`) must determine installation state and route accordingly:

- If the database contains support roles (`ROLE_SUPER_ADMIN`/`ROLE_ADMIN`) and at least one administrator user instance, the system is considered installed:
  - If the support-center bundle is present and a `knowledgebase` website record exists, redirect (HTTP 301) to the knowledge base front panel.
  - Otherwise redirect to the member/agent login page.
- If the system is not installed or the database is not reachable, forward the request to the installation wizard, rendering the wizard page.
- The routing decision must tolerate database/configuration failure (falling back to the wizard rather than failing hard).

### 3.2 Web installation wizard

The wizard must present a guided, step-sequenced flow: **Welcome → System Requirements → Database Configuration → Admin Details → Website Configuration → Installation**, with navigation protected so that later steps cannot be reached before earlier steps validate successfully.

The wizard must:

- Load from CDNs (jQuery, Underscore, Backbone, Backbone.Validation) and drive the UI entirely client-side against wizard XHR endpoints.
- Gate the "Proceed" control: it must remain disabled until the active step's procedure reports completion, and re-enabled only when validation passes.
- Support backward navigation to re-edit earlier steps, cancellation back to the Welcome screen, and Enter-key submission.
- Display a sequential installation progress indicator (five stages) during the final install run and a completion screen linking to the configured admin panel and knowledge base URLs.

### 3.3 System requirements assessment

The wizard must evaluate the host environment before installation and prevent continuation until all mandatory criteria pass. Criteria are evaluated in parallel and aggregated:

| Check | Pass condition |
|---|---|
| PHP version | PHP ≥ 7.0.0 |
| PHP extensions | `imap`, `mailparse`, and `mysqli` loaded |
| PHP `max_execution_time` | ≥ 30 seconds |
| `.env` file | writable (the system may attempt `chmod 0666`) |
| `config/packages/uvdesk.yaml` and `config/packages/uvdesk_mailbox.yaml` | writable (the system may attempt `chmod 0666`) |
| Redis | advisory only: if the `redis` extension is loaded, report a warning with Redis-server configuration guidance; the result must not block installation |

Failed checks must produce user-actionable remediation messages (for example, links for enabling the `imap`/`mailparse` extensions or increasing maximum execution time), and the step must remain incomplete until the criteria pass.

### 3.4 Database configuration and verification

The wizard must collect MySQL connection details — server name (default `127.0.0.1`), optional server version, port (default `3306`), username (default `root`), password, database name — and a "create database if not found" option (default enabled).

On submission it must:

- Establish a connection using the supplied credentials (optionally appending `serverVersion` to the DSN).
- Verify the named database exists, or, if absent, require the create-database option to be enabled; otherwise report failure ("The requested database was not found").
- Report a generic connection failure without exposing server error details.
- Persist the accepted credentials to the server session (`DB_CONFIG`) for use by later installation stages.

The database step must validate that server name, username, password, and database are non-empty before enabling submission.

### 3.5 Super-admin account configuration

The wizard must collect the initial administrator's name, email, password, and password confirmation, validating:

- Name: letters and spaces only, starting with a letter.
- Email: RFC-style format.
- Password: at least 8 characters, at least two letters, at least one digit, and at least one special character or underscore; spaces forbidden.
- Password confirmation must match.

Valid details are stored in the server session (`USER_DETAILS`) for the final install stage.

### 3.6 Website prefix configuration

The wizard must let the installer define the URL prefixes for the member (agent/admin) panel and the customer (knowledge base) panel, pre-filled from the current site configuration (defaults `member` and `customer`). Validation rules: both fields mandatory; the two prefixes must differ; each prefix may contain only letters and digits. Accepted prefixes are stored in the server session (`PREFIXES_DETAILS`).

### 3.7 Installation execution pipeline

On "Install Now", the wizard must execute five ordered server-side stages and reflect progress:

1. **Load configurations** — create the database if it does not exist and the option is enabled; write the resulting `DATABASE_URL` (MySQL DSN with credentials, host, port, database) into the project's `.env` via `uvdesk_wizard:env:update`.
2. **Load migrations** — run `uvdesk_wizard:database:migrate`, which either initializes a fresh schema (no tables: `doctrine:schema:create` plus fixture load) or synchronizes and applies Doctrine migrations for an existing database.
3. **Load entities** — load database fixtures (`doctrine:fixtures:load --append`) to populate the initial helpdesk dataset.
4. **Create super user** — create an active, verified super-admin user instance from the session-stored details, associating the `ROLE_SUPER_ADMIN` support role; if an active super-admin already exists, creation must be skipped (idempotence). Existing users with other roles must be promoted only when needed.
5. **Load website prefixes** — persist the member/customer prefixes through the UVDesk service and report the resulting member-login and knowledge-base URLs for the completion screen.

Each stage must surface failure (for example, `.env` permission problems during the configuration stage) without proceeding to subsequent stages. The returned prefix URLs are rendered as links on the completion screen. Completion must also post the installer's name, email, and site domain to the UVdesk tracker endpoint as a fire-and-forget attribution record that must never break installation when the remote service is unavailable.

### 3.8 Terminal-based configuration command (`uvdesk:configure-helpdesk`)

The CLI must scan an existing helpdesk setup and remediate or reconfigure:

- Parse current database credentials from `.env`, establish a DB connection, and, on failure, interactively re-prompt for host (default `127.0.0.1`), port (default `3306`), database, username, and hidden password, with retry loops and an option to create a missing database.
- Write corrected credentials back to `.env` through `uvdesk_wizard:env:update`.
- Compare the database schema against mapping metadata (version migrations, diff, status) and, when out of date, migrate (with a 900-second timeout) and reload fixtures (120-second timeout).
- Detect whether a super-admin user exists; if not, interactively prompt for email (validated), name, and matching password (8–32 characters), then create the account via `uvdesk_wizard:defaults:create-user`.
- Terminate with a non-zero exit code on unrecoverable connection, migration, or account-creation failure, and post attribution details to the tracker on success or when an account already exists.

### 3.9 Auxiliary CLI commands

- `uvdesk_wizard:env:update <name> <value>` — update or insert an environment variable in the project-root `.env`, preserving other content and comments; must be restricted to the `dev` environment (rejecting execution otherwise).
- `uvdesk_wizard:database:migrate` — hidden command: initialize and seed an empty database, or bring an existing database to the latest migration version.
- `uvdesk_wizard:defaults:create-user <role> [name] [email] [password]` — hidden command: create (or reuse) a user with the given support role, with interactive prompting when arguments are absent, email validation, hidden password entry, password-length policy (8–32 characters), and duplicate-account avoidance based on role level (member-level roles 1–3 versus customer role 4).

### 3.10 Tracker image cache endpoint

A GET endpoint (`/tracker/xhr/get/cacheImage`) must return the UVDesk logo URL hosted on the current site by:

- Fetching the canonical logo (`https://updates.uvdesk.com/uvdesk-logo.png`), caching a PNG copy under `public/cache/images` with a cache key derived from the source URL.
- Serving the cached image for up to 7 days, after which it must be re-fetched.
- Responding with the site-relative image URL as JSON.

### 3.11 Composed product delivery

The skeleton must assemble the helpdesk product by installing the UVDesk bundles (core framework, support center, mailbox, automation, extension framework, API bundle) as Composer dependencies, registering them in `config/bundles.php`, exposing their routes/services, provisioning a writable `apps/` extension directory (`uvdesk_extensions.dir`), and wiring Twig globals for bundle services (user, ticket, email, reCAPTCHA, automations, extensibles, file system). It must ship default content assets (profile images for agent/customer/helpdesk), an upload-manager binding (localhost filesystem), default email template (`mail.html.twig`), and default ticket semantics (type `support`, status `open`, priority `low`) as configuration defaults.

### 3.12 Localization surface

The skeleton must ship translation catalogs for Arabic, Danish, German, English, Spanish, French, Hebrew, Italian, Polish, Brazilian Portuguese, Turkish, and Chinese, default to English, and fall back to English for untranslated messages (translation catalog domain `messages`). The wizard's own UI text is hardcoded English and is not localized (see Section 9).

---

## 4. Business and Domain Rules

- **Installation gating:** installation execution must be reachable only after the requirement, database, admin, and prefix steps have each reported completion; each step's completion is validated server- or client-side before the next step unlocks.
- **Super-admin uniqueness:** the system must not create a second super-admin through the wizard when an active super-admin already exists (`ROLE_SUPER_ADMIN` user instance with active flag); on the CLI, account creation is skipped (exit code 1) when an account of the same role level already exists.
- **Role-level equivalence:** membership-role assignment must treat support roles 1–3 as interchangeable for duplicate detection (an agent-level account already existing for an email prevents another member-level account), while the customer role (4) is distinct.
- **User promotion:** when a super-admin account is created for an email that already exists with an agent instance of a different role, the existing instance's role must be upgraded to super-admin rather than creating a duplicate.
- **Fresh versus existing database:** an empty database (no tables) must be created via schema generation and default fixture loading; a non-empty database must be migrated to the latest Doctrine migration version with metadata-storage synchronization, never re-created.
- **Schema drift:** terminal configuration must detect divergence between the database and mapping metadata and require explicit operator consent before applying migrations; declining the update must abort the command with a failure result.
- **Prefix integrity:** member and customer URL prefixes must be non-empty, unique, and alphanumeric, since the security firewalls and route access rules are bound to these prefixes.
- **Password policy:** web installer requires ≥ 8 characters with two letters, one digit, and one special character; CLI tooling requires 8–32 characters; both require confirmation matching and use the framework password encoder (auto algorithm) for persisted credentials.
- **Requirement thresholds:** PHP `max_execution_time` must be ≥ 30 seconds (guidance recommends 60+), because migration and fixture phases queue long-running Doctrine tasks (with CLI timeouts of 900 s and 120 s respectively).

---

## 5. Interface Requirements

### 5.1 HTTP interfaces (wizard XHR)

All wizard endpoints are JSON (or JSON-encoded bodies) under `/wizard/xhr/…`:

| Method | Path | Purpose | Response contract |
|---|---|---|---|
| POST | `/wizard/xhr/check-requirements` | Evaluate one requirement specification | JSON with `status` (bool), human `message`, optional `description`; extension/config-file variants return arrays keyed by extension/filename |
| POST | `/wizard/xhr/verify-database-credentials` | Validate DB credentials and database existence | `{"status": true}` or `{"status": false, "message": …}` |
| POST | `/wizard/xhr/intermediary/super-user` | Buffer admin details in session | `{"status": true}` |
| GET | `/wizard/xhr/website-configure` | Return current member/customer prefixes | `{"status": true, memberPrefix, knowledgebasePrefix}` (or `status: false`) |
| POST | `/wizard/xhr/website-configure` | Buffer chosen prefixes in session | `{"status": true}` |
| POST | `/wizard/xhr/load/configurations` | Create DB, write `.env` `DATABASE_URL` | `{"success": true}` or failure JSON (HTTP 500) |
| POST | `/wizard/xhr/load/migrations` | Migrate/initialize schema | JSON `[]` on completion |
| POST | `/wizard/xhr/load/entities` | Load fixtures | JSON `[]` on completion |
| POST | `/wizard/xhr/load/super-user` | Create super admin | JSON `[]` on completion |
| POST | `/wizard/xhr/load/website-configure` | Persist prefixes; tracker call | JSON containing `memberLogin` and `knowledgebase` URLs |
| GET | `/tracker/xhr/get/cacheImage` | Return cached logo URL | JSON string of site-relative image URL |

Unknown requirement specifications must return HTTP 404.

### 5.2 Console interfaces

- `bin/console uvdesk:configure-helpdesk` — interactive evaluation command with prompts, hidden password input, ANSI progress/status output, and non-zero exit codes on failure.
- `bin/console uvdesk_wizard:env:update <name> <value>` — non-interactive; dev-environment only.
- `bin/console uvdesk_wizard:database:migrate` — non-interactive (hidden).
- `bin/console uvdesk_wizard:defaults:create-user <role> [name] [email] [password] [--no-interaction]` — hidden; interactive fallback.

### 5.3 Configuration-file interfaces

- `.env` (project root): `APP_ENV`, `APP_SECRET`, `DATABASE_URL` (MySQL DSN), `UV_SESSION_COOKIE_LIFETIME` (seconds, default 1440), `MAILER_DSN`, optional `TRUSTED_PROXIES`/`TRUSTED_HOSTS`. The wizard and CLI commands must read and rewrite this file.
- `config/packages/uvdesk.yaml` and `uvdesk_mailbox.yaml`: written with runtime configuration during/after installation; must be writable by the web server.
- `config/packages/doctrine.yaml`: database driver (`pdo_mysql`), server version (default 5.7), `utf8mb4` charset/collation, and a SQL-mode workaround for `ONLY_FULL_GROUP_BY`.
- `config/packages/security.yaml`: firewall patterns and access-control rules keyed to the member/customer URL prefixes; remember-me cookie `REMEMBERME` with 7-day lifetime.
- `config/packages/framework.yaml`: session cookie settings (lax SameSite, `auto` secure, lifetime driven by `UV_SESSION_COOKIE_LIFETIME`).
- `config/packages/mailer.yaml`: mail transport bound to `MAILER_DSN`.
- `config/packages/uvdesk_extensions.yaml`: extension/plugin directory fixed to `<project>/apps`.

### 5.4 Web-server interface

Apache must serve the `public/` directory as document root with `mod_rewrite` (front-controller rewrite to `index.php`, preserving `HTTP_AUTHORIZATION` for API authentication). The Docker runtime specifically requires Apache `mod_rewrite` and PHP 8.1 (`mod_php`), MySQL server, Composer, and the `imap`/`mailparse`/`mysqli`/`curl` extensions.

---

## 6. Data Requirements

- **Database configuration data:** host, port, username, password, database name, optional server version, and a create-database flag must be captured, verified, and ultimately persisted as `DATABASE_URL` in `.env`; the same data must survive across wizard stages via server session state (`DB_CONFIG`, `USER_DETAILS`, `PREFIXES_DETAILS`).
- **Schema and seed data:** an installed instance must contain the bundle-defined tables (including `uv_support_role`, `uv_user`, `uv_user_instance`, `uv_website`) created via Doctrine, with support roles including at least `ROLE_SUPER_ADMIN` and `ROLE_ADMIN`, default fixtures, and knowledge-base/helpdesk website records, since these drive post-install routing.
- **Website prefix data:** member and customer URL prefixes must be persisted through the bundled website service and reflected in security firewall configuration.
- **Cached asset data:** cached images are stored as PNG files under `public/cache/images` keyed by `md5(source URL)` with a 7-day freshness window; expired files are removed and re-fetched, and the directory is created on demand (mode 0775).
- **Transactional behavior:** user/role/user-instance creation and super-admin promotion are persistence operations executed through Doctrine with flush semantics; prematurely aborting installation leaves a partially configured instance that the terminal command must detect and offer to repair (schema comparison, super-admin existence check).

---

## 7. Security Requirements

- **Credential handling during installation:** database credentials and the initial admin password are held in the server session while the wizard stages execute; the admin password must never be rendered back into the UI and must be hashed through the Symfony user encoder before persistence.
- **Environment mutation control:** rewriting `.env` must be restricted to the development environment (`uvdesk_wizard:env:update` rejects non-dev kernels), constraining writing of secrets/database credentials to installation contexts.
- **Error disclosure:** database connection failures during the wizard must return generic messages ("Failed to establish a connection with database server") rather than underlying exception details.
- **AuthN/AuthZ baseline for the composed product:** the configuration must define a role hierarchy (`ROLE_SUPER_ADMIN` ⊇ `ROLE_ADMIN` ⊇ `ROLE_AGENT`; `ROLE_CUSTOMER`), form-login firewalls for the member and customer areas with distinct login/check/default-target routes, an API firewall with credential-based guard for `/api`, remember-me sessions (`REMEMBERME`, 7 days), and access-control rules that keep the member panel behind `ROLE_AGENT+`, the customer panel behind `ROLE_CUSTOMER`, and explicitly public login/registration/password-recovery and the mailbox listener route.
- **Cookie/session posture:** session cookie uses SameSite `lax`, `secure: auto`, and configurable lifetime via `UV_SESSION_COOKIE_LIFETIME` (default 1440 s), with garbage-collection lifetime aligned.
- **Production error presentation:** in production, unhandled exceptions must render branded error pages (404/403/500) via a kernel exception subscriber; 403 handling must distinguish authenticated users (forbidden page) from anonymous users (redirect to login); in non-production environments exceptions must not be suppressed.
- **Secret management:** application secrets are supplied through environment variables (`APP_SECRET`); committed files must not contain production secrets.
- **Vulnerability disclosure:** the project must provide a documented security reporting channel (private disclosure per `.github/SECURITY.md`) rather than public issue filing.

---

## 8. Non-Functional Requirements

- **Compatibility:** PHP `^7.2.5 || ^8.0` (Docker packaging pins PHP 8.1), Symfony `^5.4`, MySQL (Doctrine DBAL with `pdo_mysql`, default server version 5.7), Composer 2, Apache 2 or NGINX with rewrite support; documented host guidance: Ubuntu 16.04+/Windows 7+ (WAMP/XAMPP), 4 GB RAM, ≥1 GHz processor.
- **Responsiveness/throughput constraints:** the install pipeline assumes `max_execution_time ≥ 30` seconds; migration and fixture commands are explicitly granted extended timeouts (900 s / 120 s) to accommodate long-running schema operations; Docker runtime raises `memory_limit` to 1024 M.
- **Resilience:** installation must be resumable/retryable at the step level; wizard XHR calls tolerate transient failure with visible error feedback; tracker calls fail silently; image caching tolerates upstream fetch failure by regenerating on the next request.
- **Observability:** PHP errors must be logged (`php_errors.log: true`), and the packaged runtimes expose Apache access/error logs and Monolog-based logging; no metrics/tracing endpoints are present in this layer.
- **Portability:** installation must work from a Composer-created project or from a pre-packaged zip archive, with the same configuration path in both cases; the web document root is the project's `public/` directory.
- **Upload limits (inherited UI surface):** default upload constraints are exposed to templates (max POST size 8388608 bytes, max 20 files, max file size 2097152 bytes) and must be honored by the composed product's attachment features.
- **Localization:** UI strings of the composed bundles must be translatable across the 12 shipped locales with English fallback; the wizard UI is not localized (Section 9).

---

## 9. Operational and Deployment Requirements

- **Installation paths:** the skeleton must be installable via `composer create-project uvdesk/community-skeleton <dir>` or by extracting the stable zip archive (`https://cdn.uvdesk.com/uvdesk/downloads/opensource/uvdesk-community-current-stable.zip`); Symfony Flex recipes run post-install scripts (`cache:clear`, `assets:install`) and generate project scaffolding such as `App\Kernel` (referenced by `public/index.php` but not committed in this repository — it is produced during the Flex-based install).
- **File-system permissions:** before installation, the `.env`, `config/`, `config/packages/*.yaml` (notably `uvdesk.yaml`, `uvdesk_mailbox.yaml`), `var/`, `public/`, and `migrations/` paths must be writable by the web server; the tooling attempts `chmod 0666`/`0775` remediation and verifies writability, and the Docker image pre-chmods these paths to 775 with `uvdesk` ownership.
- **Containerized runtime:** the Docker image must provide Ubuntu-based Apache 2 + PHP 8.1, MySQL server, Composer-installed dependencies, and an entrypoint that starts Apache and MySQL, and optionally provisions the database from `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_ROOT_PASSWORD` environment variables (creating the schema, granting privileges, and writing client config); it must drop privileges from root to the `uvdesk` user via `gosu`.
- **Environment configuration:** instances are configured through `.env` (`APP_ENV`, `APP_SECRET`, `DATABASE_URL`, `UV_SESSION_COOKIE_LIFETIME`, `MAILER_DSN`); a default `.env` ships with `APP_ENV=dev` and placeholder values that must be replaced during installation.
- **Health/readiness:** no dedicated health-check endpoint exists in this layer; post-install readiness is implied by successful routing from `/` to the knowledge base or member login (Section 3.1).
- **Extension hosting:** an `apps/` directory must exist and be writable for third-party extension installation via the extension framework.
- **Production hardening:** production deployments must render generic error pages, rely on environment-provided secrets, and enable HTTPS-terminating infrastructure (cookie `secure: auto`); an AWS Marketplace AMI is offered as an official deployment path (documented, not in-repo).

---

## 10. Documentation versus Implementation Discrepancies

- **PHP version guidance:** the README lists "PHP 8.1" as the requirement, while the wizard's version check passes at PHP ≥ 7.0 and `composer.json` accepts `^7.2.5 || ^8.0`; the Docker image uses 8.1. The enforced minimum is materially below the documented recommendation; compatibility across 7.2.5–8.x is the claimed range.
- **Sample environment file:** `.env.example` is a Laravel-style variable set (`APP_NAME`, `APP_KEY`, `DB_HOST`, `MAIL_DRIVER`, …) that does not correspond to the Symfony variables actually consumed (`APP_ENV`, `APP_SECRET`, `DATABASE_URL`, `MAILER_DSN`); it is a stale artifact and should not be treated as the operative interface.
- **Redis guidance:** the requirement check flags the Redis extension as needing configuration only when loaded (`setup.php` host noted in remediation), without a hard requirement; the terminal command echoes the same advisory.
- **Wizard localization:** although 12 translation catalogs are shipped, all wizard UI strings are hardcoded English; the translated surface is the composed bundles' UI, not the installer.
- **Incomplete scaffolding:** `src/Kernel.php` is absent from the repository and is generated by the Symfony Flex recipe during project creation; the Docker build tolerates cache-clear failure (`|| true`), consistent with pre-install (unconfigured) operation.

### Gaps and open questions

- The detailed functional requirements of the helpdesk domain (tickets, support center, mailboxes, automations, API) are not verifiable from this repository; they live in the bundled dependencies (`uvdesk/core-framework`, `uvdesk/mailbox-component`, `uvdesk/automation-bundle`, `uvdesk/support-center-bundle`, `uvdesk/api-bundle`) and should be reconstructed from those repositories.
- No automated tests are present for the skeleton layer; behavioral guarantees above rest on the implemented controllers, commands, and client-side validation, not on test evidence.
- No numerical performance targets (beyond the execution-time thresholds above), availability commitments, or retention policies are evidenced anywhere in this repository and therefore are not stated as requirements.
