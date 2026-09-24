---
model: qwen/qwen3.8-max-0902
---

# Feature / Functional Specification

## 1. Document Title

**UVDesk Community Skeleton — Installation, Assembly, and Bootstrap Feature Specification**

This document reconstructs the functional capabilities implemented by the `uvdesk/community-skeleton` repository (application version parameter `v1.1.8`). The repository is a Symfony 5.4 / PHP application shell whose own executable feature surface is dominated by a **guided helpdesk installation and configuration capability set**: a browser-based installation wizard, a family of console installer commands, an application-state router, an installation-telemetry/image-cache endpoint, production error presentation, and a containerized deployment image. The operational helpdesk features it is designed to host (ticketing, agent panel, customer portal, mailbox ingestion, automation, REST API, extensions) are supplied by six registered UVDesk bundles and are **assembled and configured here, not implemented here**.

## 2. Feature Overview

### 2.1 Feature Name

Helpdesk Installation, Configuration, and Component Assembly (UVDesk Community Skeleton)

### 2.2 Feature Summary

The repository provides everything required to take a freshly deployed codebase to a running UVDesk helpdesk:

| Capability | Surface | Status in this repository |
|---|---|---|
| Application state detection and entry routing (`/`) | Web | Implemented |
| Browser installation wizard (5-stage, AJAX-driven) | Web | Implemented |
| System requirements pre-flight evaluation | Web (XHR) | Implemented |
| Database credential verification and database creation | Web (XHR) / CLI | Implemented |
| Environment (`.env`) rewriting | CLI (`uvdesk_wizard:env:update`) | Implemented, dev-environment only |
| Database schema migration / fresh-install schema creation | Web (XHR) / CLI | Implemented |
| Seed dataset (fixtures) population | Web (XHR) / CLI | Implemented |
| Super-admin account creation | Web (XHR) / CLI | Implemented |
| Website URL prefix configuration (agent panel / customer portal) | Web (XHR) | Implemented (delegated to `UVDeskService`) |
| Interactive helpdesk setup doctor | CLI (`uvdesk:configure-helpdesk`) | Implemented |
| Hidden user-creation helper | CLI (`uvdesk_wizard:defaults:create-user`) | Implemented |
| Installation telemetry + logo image caching | Web (`/tracker/xhr/get/cacheImage`) | Implemented |
| Production error page rendering (403/404/500) | Web (event subscriber) | Implemented |
| Route contribution into the UVDesk routing loader | Framework integration | Implemented |
| Bundle/component assembly and default helpdesk configuration | Configuration | Implemented |
| Role hierarchy, firewalls, and URL access control | Configuration | Implemented (routes served by bundles) |
| Localization catalogs (12 locales) | Configuration/content | Implemented |
| Docker single-container LAMP image + entrypoint provisioning | Deployment | Implemented |
| Ticketing, support center, knowledgebase, mailbox-to-ticket, automation, extensions, REST API | Provided by `uvdesk/*` bundles | Enabled and configured here; **not implemented in this repository** |

### 2.3 Business Purpose

The business purpose is to lower the cost and risk of standing up an open-source helpdesk. Rather than requiring an operator to hand-edit Symfony configuration, create a MySQL schema, run Doctrine migrations, load fixtures, and hand-craft an administrator account, the skeleton offers two equivalent guided paths — a web wizard and an interactive console command — that perform the full bootstrap and leave behind a configured, authenticated, localized support system composed of the UVDesk bundles.

A secondary purpose is vendor-side install visibility: on successful installation the system reports the site domain, administrator name, and administrator e-mail to `https://updates.uvdesk.com`, and periodically retrieves and locally caches a UVDesk logo image while sending the site domain as an HTTP header.

### 2.4 Scope

**In scope (implemented in this repository):**
- `src/Controller/BaseController.php`, `src/Controller/ConfigureHelpdesk.php`, `src/Controller/ImageCache/*`
- `src/Console/EnvironmentVariables.php`, `src/Console/Wizard/{ConfigureHelpdesk,DefaultUser,MigrateDatabase}.php`
- `src/Service/UrlImageCacheService.php`, `src/Routing/RoutingResource.php`, `src/EventListener/ExceptionSubscriber.php`
- `src/Resources/config/routes.yaml`, `config/routes.yaml`, `config/services.yaml`, `config/bundles.php`, `config/packages/*.yaml`
- `templates/installation-wizard/index.html.twig`, `templates/errors/error.html.twig`, `templates/mail.html.twig`
- `public/scripts/wizard.js`, `public/css/{wizard,reset,main}.css`, `public/index.php`, `public/.htaccess`
- `translations/messages.*.yml`, `Dockerfile`, `.docker/**`, `.env`, `INSTALLATION GUIDE.md`

**Out of scope (external packages, wired but not implemented here):** `uvdesk/core-framework`, `uvdesk/support-center-bundle`, `uvdesk/mailbox-component`, `uvdesk/automation-bundle`, `uvdesk/extension-framework`, `uvdesk/api-bundle`.

**Explicitly empty/reserved:** `src/Entity/`, `src/Migrations/`, `src/Repository/`, `public/assets/`, `public/attachments/`, `apps/` contain only `.gitignore` placeholders — they are extension points, not implemented behavior. No test suite is present.

### 2.5 Stakeholders / Users

| Stakeholder | Relationship to the feature |
|---|---|
| Installer / system administrator | Primary actor of the wizard and CLI installer; owns `.env`, database, and file permissions |
| Super admin (created by the installer) | First helpdesk account; `ROLE_SUPER_ADMIN` |
| Support agents (`ROLE_AGENT`, `ROLE_ADMIN`) | Consume the assembled agent panel at `/{member_prefix}/` |
| Customers / requesters (`ROLE_CUSTOMER`, `ROLE_CUSTOMER_READ_ONLY`) | Consume the assembled portal at `/{customer_prefix}/` |
| Extension developers | Install add-ons into `apps/` (`uvdesk_extensions.dir`) |
| API consumers | Authenticate against the `^/api` firewall (`APIGuard`) |
| UVDesk (vendor) | Receives installation telemetry; serves the cached logo and update endpoint |
| Container operators | Build/run the Docker image with `MYSQL_*` environment variables |

## 3. User and Business Context

### 3.1 User Roles

Roles are defined declaratively in `config/packages/security.yaml`:

- **Role hierarchy:** `ROLE_SUPER_ADMIN ⊇ ROLE_ADMIN ⊇ ROLE_AGENT`; `ROLE_CUSTOMER` is separate. `ROLE_CUSTOMER_READ_ONLY` appears in access-control rules for public read-only ticket views.
- **Anonymous / unauthenticated visitor:** permitted on login, account creation, password reset, credential update, customer ticket creation, and the mailbox listener path.
- **Authenticated agent:** required for everything under `/{member_prefix}/`.
- **Authenticated customer:** required for everything under `/{customer_prefix}/`.
- **Installer (pre-installation):** no role model applies before the first super admin exists; the wizard endpoints themselves carry no `access_control` entry and are therefore reachable anonymously.

Two user providers are configured: `user_provider` (service id `user.provider`, supplied by the core bundle) for the web panels, and `api_user_provider` (`Webkul\UVDesk\ApiBundle\Providers\ApiCredentials`) for the API firewall. Password encoding is configured for `Webkul\UVDesk\CoreFrameworkBundle\Entity\User`.

### 3.2 User Goals

1. Verify that the server can run the helpdesk before committing to an install.
2. Point the application at a MySQL server, creating the database if it does not exist.
3. Create the first administrator account with a known e-mail and password.
4. Choose the URL prefixes that separate the agent panel from the customer portal.
5. Complete schema creation, seeding, and configuration writing without using a terminal.
6. Alternatively, diagnose and repair an existing broken installation from the terminal.
7. Reach the correct application surface automatically after installation (portal vs. agent login vs. wizard).
8. Run the whole stack in a single container for evaluation.

### 3.3 Business Processes

**Process A — First-time installation (web).** Visitor requests `/` → `BaseController::base` finds no `ROLE_SUPER_ADMIN`/`ROLE_ADMIN` support roles or no users holding them → forwards to `ConfigureHelpdesk::load` → wizard UI renders → requirements check → database verification → admin details → website prefixes → installation sequence (env update → migrations → fixtures → super user → prefix update) → completion screen with links to the agent panel and knowledgebase.

**Process B — First-time installation / repair (CLI).** Operator runs `uvdesk:configure-helpdesk` → permissions normalized → `.env` parsed → connectivity tested → optional interactive re-configuration and database creation → `.env` updated → migration version compared and applied → fixtures appended → super-admin existence checked and optionally created → telemetry sent.

**Process C — Post-install request routing.** Any visitor requesting `/` on an installed system is redirected (301) to `helpdesk_knowledgebase` when `UVDeskSupportCenterBundle` is loaded and a `knowledgebase` website record exists, otherwise to `helpdesk_member_handle_login` when a `helpdesk` website record exists.

**Process D — Operational helpdesk usage.** Ticket creation, agent handling, mailbox polling, automation rules, API access, and extension management are executed by the registered bundles under the firewalls, prefixes, defaults, and locales configured in this repository.

**Process E — Container provisioning.** Image build installs PHP 8.1/Apache/MySQL and Composer dependencies; at startup the entrypoint starts services, provisions the database and MySQL client credential files from `MYSQL_*` variables, then drops privileges to the `uvdesk` user.

### 3.4 Preconditions

- PHP `^7.2.5 || ^8.0`; the wizard's own check enforces ≥ 7.0 and reports the running version.
- PHP extensions `imap`, `mailparse`, `mysqli` (checked by the wizard; installed by the Dockerfile).
- `max_execution_time` ≥ 30 seconds.
- Writable `.env` and writable `config/packages/uvdesk.yaml` and `config/packages/uvdesk_mailbox.yaml`; the requirements check attempts `chmod 0666` on files that are not writable before reporting.
- Writable project directories for the CLI path: `.env`, `var`, `config`, `public`, `migrations` are `chmod 0775` by `uvdesk:configure-helpdesk` during initialization.
- A reachable MySQL server; credentials supplied by the operator.
- Composer dependencies installed (`composer install`), which materializes the six UVDesk bundles declared in `config/bundles.php`.
- For the web configuration step to succeed, the kernel must be running in the `dev` environment, because `uvdesk_wizard:env:update` throws otherwise.
- Outbound HTTPS access to `updates.uvdesk.com` for telemetry and logo caching (failures are silently swallowed).

### 3.5 Triggering Events

| Trigger | Effect |
|---|---|
| HTTP `GET /` | Installation-state detection; wizard render or panel redirect |
| HTTP `POST /wizard/xhr/check-requirements` | One requirements probe per `specification` value |
| HTTP `POST /wizard/xhr/verify-database-credentials` | Database connectivity/existence check; session capture |
| HTTP `POST /wizard/xhr/intermediary/super-user` | Session capture of admin identity |
| HTTP `GET|POST /wizard/xhr/website-configure` | Read current prefixes / capture chosen prefixes |
| HTTP `POST /wizard/xhr/load/{configurations,migrations,entities,super-user,website-configure}` | Each installation stage |
| HTTP `GET /tracker/xhr/get/cacheImage` | Logo fetch/cache and domain beacon; returns cached image URL |
| `php bin/console uvdesk:configure-helpdesk` | Interactive setup diagnosis and repair |
| `php bin/console uvdesk_wizard:defaults:create-user <role> …` | User/account provisioning |
| `php bin/console uvdesk_wizard:database:migrate` | Schema creation or migration |
| `php bin/console uvdesk_wizard:env:update <name> <value>` | `.env` rewrite (dev only) |
| Any uncaught exception in `prod` | Branded 403/404/500 error page |
| Container start | Service startup and MySQL provisioning |

## 4. Feature Description

### 4.1 Functional Overview

The skeleton implements a **bootstrap control plane**. It owns three things the assembled product depends on: (1) the transition from "code on disk" to "installed helpdesk", (2) the request-routing decision that sends a visitor to the wizard or to the installed panels, and (3) the declarative wiring — bundles, security, locales, upload limits, default ticket values, mailbox and extension configuration — that shapes how the UVDesk bundles behave once installed.

Two independent installers implement the same outcome. The web wizard is a Backbone.js single-page flow driven by nine XHR endpoints; the CLI installer is an interactive console command that shells out to `bin/console` sub-commands. Both converge on the same primitives: `uvdesk_wizard:env:update`, `uvdesk_wizard:database:migrate`, `doctrine:fixtures:load`, and `uvdesk_wizard:defaults:create-user`.

### 4.2 Primary Behavior

**4.2.1 Application-state routing (`BaseController::base`, route `base_route`, path `/`)**

The handler probes installation state through the entity manager:
1. Look up `SupportRole` records for codes `ROLE_SUPER_ADMIN` and `ROLE_ADMIN`.
2. If either exists, look up `UserInstance` records holding those roles.
3. If administrators exist, enumerate loaded bundles; if `UVDeskSupportCenterBundle` is present and a `Website` record with code `knowledgebase` exists, issue a 301 redirect to `helpdesk_knowledgebase`.
4. Otherwise, if a `Website` record with code `helpdesk` exists, redirect to `helpdesk_member_handle_login`.
5. Any exception during this probe is caught and discarded; the handler then falls through to `forward(ConfigureHelpdesk::class."::load")`, rendering the installation wizard.

The wizard page therefore has **no URL of its own** — it is reachable only through this forward from `/`. No route in `src/Resources/config/routes.yaml` maps to `ConfigureHelpdesk::load`.

**4.2.2 Wizard user interface**

`templates/installation-wizard/index.html.twig` renders a shell plus a library of Underscore `<script type="text/template">` blocks (loader/success/notice/warning icons, header, welcome content, setup navigation, per-step forms). It loads jQuery 2.2.4, Underscore 1.9.1, Backbone 1.3.3, and Backbone.Validation 0.7.1 from public CDNs, plus local `scripts/wizard.js`, `css/reset.css`, and `css/wizard.css`. The header template displays the configured `uvdesk_version` and a five-node progress checklist: **Welcome → System Requirements → Database Configuration → Admin Details → Installation**. `wizard.js` additionally implements a website-prefix (member panel / customer panel) configuration view and model, and an installation view that drives the five installation sub-steps with a live progress checklist.

The welcome screen links to per-OS prerequisite guides (Ubuntu, Windows/WAMP, CentOS, Mac). Client-side error templates explain two failure modes: a 404 (suggesting `index.php` in the URL, Apache `mod_rewrite`, and `AllowOverride All/FileInfo`) and a 500 (suggesting retry/refresh/cancel).

**4.2.3 Requirements evaluation (`evaluateSystemRequirements`)**

Accepts a `specification` POST parameter and returns JSON. Supported probes and their rules:

| `specification` | Rule evaluated | Response shape |
|---|---|---|
| `php-version` | `phpversion() >= 7.0.0` | `status`, `version` (`MAJOR.MINOR.RELEASE`), `message` |
| `php-extensions` | `extension_loaded()` for `imap`, `mailparse`, `mysqli` | `extensions: [{name: bool}, …]` |
| `php-maximum-execution` | `max_execution_time >= 30` | `status`, `message`, remediation `description` HTML |
| `php-envfile-permission` | `is_writable(<project>/.env)`, after attempting `chmod 0666` | `status`, `message`, remediation `description` |
| `php-configfiles-permission` | `is_writable()` for `config/packages/uvdesk.yaml` and `uvdesk_mailbox.yaml`, after attempting `chmod 0666` | `configfiles: [{name: bool}, …]`, `description` |
| `redis-status` | If the `redis` extension is loaded, returns `status: false` with guidance about the Redis host (a warning, not a hard failure) | `status`, `message`, `description` |
| *(anything else)* | — | HTTP **404** |

Remediation text embeds external links to `simplified.guide`, `uvdesk.com` blog posts, and a GitHub issue comment.

**4.2.4 Database verification (`verifyDatabaseCredentials`)**

Starts a PHP session if none exists, builds a DSN from the template `mysql://[user]:[password]@[host]:[port]` using `serverName`, `serverPort`, `username`, `password`, appends `?serverVersion=` when `serverVersion` is supplied, opens a Doctrine DBAL connection, connects if not already connected, and checks whether `database` appears in `getSchemaManager()->listDatabases()`.

- Database missing **and** `createDatabase` falsy → `{status: false, message: "The requested database was not found."}`
- Any exception → `{status: false, message: "Failed to establish a connection with database server."}`
- Success → the full credential set (`host`, `port`, `version`, `username`, `password`, `database`, `createDatabase`) is stored in `$_SESSION['DB_CONFIG']` and `{status: true}` is returned.

**4.2.5 Intermediary captures**

- `prepareSuperUserDetailsXHR` stores `name`, `email`, `password` in `$_SESSION['USER_DETAILS']` and returns `{status: true}`. A `unset($_SESSION['USER_DETAILS'])` line is present but commented out, so previously captured values persist across re-runs within a session.
- `websiteConfigurationXHR` is method-switched: `GET` returns `UVDeskService::getCurrentWebsitePrefixes()` augmented with `status: true`, or `{status: false}` when no prefixes are configured; `POST` stores `member-prefix` and `customer-prefix` in `$_SESSION['PREFIXES_DETAILS']` and returns `{status: true}`.

**4.2.6 Installation stages**

The wizard client posts the stages sequentially, updating the progress checklist between calls and rendering a failure icon plus an error bar on HTTP 500:

1. `POST /wizard/xhr/load/configurations` → `updateConfigurationsXHR`: reads `$_SESSION['DB_CONFIG']`, reconnects, creates the database when absent and `createDatabase` was requested, builds the final DSN including the database name, then runs `uvdesk_wizard:env:update DATABASE_URL <dsn>` **in-process** via a Symfony console `Application` with `ArrayInput`/`NullOutput`. Returns `{success: true}` when the command exit code is `0`; on exception returns `{status:false, message:"An unexpected error occurred: …"}`; otherwise `{success:false}` with HTTP 500.
2. `POST /wizard/xhr/load/migrations` → `migrateDatabaseSchemaXHR`: runs `uvdesk_wizard:database:migrate`; **always returns HTTP 200 with `[]`**, regardless of the command's exit code.
3. `POST /wizard/xhr/load/entities` → `populateDatabaseEntitiesXHR`: runs `doctrine:fixtures:load --append`; **always returns HTTP 200 with `[]`**.
4. `POST /wizard/xhr/load/super-user` → `createDefaultSuperUserXHR`: resolves `SupportRole` by code `ROLE_SUPER_ADMIN`; if no active `UserInstance` holds it, reads `$_SESSION['USER_DETAILS']`, finds an existing `User` by e-mail or constructs a new one, splits the supplied name on the first space into first/last name, encodes the password with `UserPasswordEncoderInterface`, sets `isEnabled(true)`, persists, then creates a `UserInstance` with `source='website'`, `isActive=true`, `isVerified=true`, and the super-admin role. If a user already exists with a different role, the existing instance's role is upgraded to super admin. Returns HTTP 200 with `[]`.
5. `POST /wizard/xhr/load/website-configure` → `updateWebsiteConfigurationXHR`: calls `UVDeskService::updateWebsitePrefixes($member, $customer)`, then posts `{name, email, domain: uvdesk.site_url}` to the UVDesk tracker, and returns the resulting URL collection (consumed by the client as `memberLogin` and `knowledgebase` links on the completion screen).

**4.2.7 CLI installer (`uvdesk:configure-helpdesk`)**

Described as "Scans through your helpdesk setup to check for any mis-configurations." Behavior:
- Normalizes permissions (`chmod 0775`) on `.env`, `var`, `config`, `public`, `migrations`.
- Parses `DATABASE_URL` from `.env` to recover host, port, name, user, password.
- Emits an advisory block when the `redis` PHP extension is loaded.
- Tests server and database accessibility; on failure, offers interactive re-configuration with prompted host (default `127.0.0.1`), port (default `3306`), name, user, and hidden password, looping until the server is reachable, and offering to create a missing database.
- Persists accepted credentials by invoking `php bin/console uvdesk_wizard:env:update DATABASE_URL mysql://user:pass@host:port/name` as a subprocess.
- Compares migration versions using `doctrine:migrations:version --add --all`, `doctrine:migrations:diff`, `doctrine:migrations:status`, and `doctrine:migrations:latest`; when versions differ it offers to migrate (`doctrine:migrations:migrate --no-interaction`, 900 s timeout) and then appends fixtures (`doctrine:fixtures:load --append`, 120 s timeout).
- Detects an existing super admin with direct PDO queries against `uv_support_role`, `uv_user_instance`, and `uv_user`; when none exists it offers interactive creation with e-mail format validation (`FILTER_SANITIZE_EMAIL` + `FILTER_VALIDATE_EMAIL`), required name, and matched hidden password entry, then delegates to `uvdesk_wizard:defaults:create-user ROLE_SUPER_ADMIN <name> <email> <password> --no-interaction`.
- Sends installation telemetry (name, e-mail, `uvdesk.site_url`) to `https://updates.uvdesk.com/api/updates` as JSON via cURL, swallowing all errors.

**4.2.8 Migration command (`uvdesk_wizard:database:migrate`, hidden)**

Validates the connection, then branches on schema emptiness:
- **No tables (fresh install):** `doctrine:schema:create --no-interaction` followed by `doctrine:fixtures:load --no-interaction --quiet`.
- **Existing database:** `doctrine:migrations:sync-metadata-storage`, version all migrations, run `diff` and `status`, compare against `doctrine:migrations:latest`, and migrate when versions differ; migration errors are caught and printed as an error line while the command still returns success.

It supports both DBAL 2 (`getSchemaManager()`) and DBAL 3 (`createSchemaManager()`).

**4.2.9 User provisioning command (`uvdesk_wizard:defaults:create-user`, hidden)**

Required argument `role` (a support-role code); optional `name`, `email`, `password`. Interactive mode prompts with validation: e-mail sanitized and format-checked, name required, password hidden and constrained to **8–32 characters**, confirmation must match. Non-interactive mode errors with exit code `2` on missing arguments or an unrecognized role. Duplicate protection: if the target role is in `{1,2,3}` (member-level) and the user already holds any role in `{1,2,3}`, or the target role is `4` (customer-level) and the user already holds `4`, the command returns `1` without creating a second instance. Otherwise it persists the `User` (with encoded password, `isEnabled(true)` for new users) and a `UserInstance` with `source='website'`, `isActive=true`, `isVerified=true`.

**4.2.10 Environment rewrite command (`uvdesk_wizard:env:update`)**

Arguments `name` and `value`. Loads and parses `.env`, overwrites the upper-cased variable, then rewrites the file line by line, preserving comments, blank lines, and the ordering of unrelated variables; writes only when content actually changed. **Throws immediately unless `kernel.environment == 'dev'`.**

**4.2.11 Tracker image cache (`GET /tracker/xhr/get/cacheImage`)**

Computes the current site URL (`scheme + host + base path`), delegates to `UrlImageCacheService::getCachedImage('https://updates.uvdesk.com/uvdesk-logo.png', $siteUrl)`, which:
- Uses `md5(url)` as the cache key and `public/cache/images/<key>.png` as the path, creating the directory with mode `0775` when absent.
- Treats the cache as expired when the file is missing or older than **7 days**, deletes and re-fetches on expiry.
- Fetches via a custom Intervention Image manager that performs an HTTP `GET` with `Accept-language: en`, a `Domain: <siteUrl>` header, and a desktop Chrome `User-Agent`, then decodes the binary and saves it as PNG.

The controller converts the cached file's real path into a public URL relative to `kernel.project_dir/public` and returns that URL as a JSON-encoded string body. This request is the mechanism by which the site domain is reported to the vendor host on a recurring (weekly) basis.

**4.2.12 Production error presentation (`ExceptionSubscriber`)**

Subscribes to `KernelEvents::EXCEPTION` at priority 10 and acts **only when the kernel environment is `prod`**. It renders `errors/error.html.twig` with:
- `403` — "Access Forbidden" / "You are not authorized to access this page.", and only when a token user exists and is not `"anon."`; otherwise no response is substituted.
- `404` — `NotFoundHttpException` or exception code `404`: "Page not Found".
- `500` — everything else: "Internal Server Error" / "Something has gone wrong on the server. Please try again later."

An in-code `@TODO` notes that response type (html/xml/json) is not yet taken into account, so JSON/API clients also receive an HTML error body in production.

**4.2.13 Routing contribution (`RoutingResource`)**

Implements `Webkul\UVDesk\CoreFrameworkBundle\Definition\RoutingResourceInterface`, pointing the core framework's route loader at `src/Resources/config/routes.yaml` as a YAML resource. `config/routes.yaml` activates two loaders — `type: uvdesk` and `type: uvdesk_extensions` — which is how the skeleton's ten routes enter the assembled application's routing table alongside bundle-provided routes.

**4.2.14 Component assembly and default configuration**

- `config/bundles.php` registers, for all environments: CoreFramework, Automation, ExtensionFramework, Mailbox, SupportCenter, and Api bundles.
- `config/packages/uvdesk.yaml` defines: `app_locales: en|fr|it|de|da|ar|es|tr|zh|pl|he|pt_BR`; default agent/customer/helpdesk avatar asset paths; URL prefixes `uvdesk_site_path.member_prefix: member` and `uvdesk_site_path.knowledgebase_customer_prefix: customer`; upload constraints `max_post_size: 8388608`, `max_file_uploads: 20`, `upload_max_filesize: 2097152`; `uvdesk.site_url: 'localhost:8000'`; `uvdesk.upload_manager.id: …\FileSystem\UploadManagers\Localhost`; `uvdesk.support_email: ~`; and default ticket values `type: support`, `status: open`, `priority: low` with default e-mail template `mail.html.twig`.
- `config/packages/uvdesk_mailbox.yaml` ships the mailbox schema (per-mailbox `name`, `enabled`, `disable_outbound_emails`, `use_strict_mode`, `imap_server.{host,username,password}`, `smtp_server.{host,port,client,type,username,password,sender_address}`, plus reply `delimiter`/`enable_delimiter`) entirely commented out with `mailboxes: ~` and `emails: ~`.
- `config/packages/uvdesk_extensions.yaml` sets the extension directory to `%kernel.project_dir%/apps`.
- `config/services.yaml` sets `locale: 'en'`, `uvdesk.version: "v1.1.8"`, autowires/autoconfigures everything under `src/` (excluding `DependencyInjection`, `Entity`, `Migrations`, `Tests`, `Kernel.php`), and tags `App\Controller\` with `controller.service_arguments`.
- `.env` provides `APP_ENV=dev`, a placeholder `APP_SECRET`, `DATABASE_URL=mysql://db_user:db_password@127.0.0.1:3306/db_name`, `UV_SESSION_COOKIE_LIFETIME=1440`, and `MAILER_DSN=null://null`.

**4.2.15 Containerized deployment**

`Dockerfile` builds an all-in-one Ubuntu image: PHP 8.1 with `xml`, `imap`, `mysql`, `mailparse`, `curl`, Apache 2 with `php8.1` and `rewrite` modules enabled, and a local `mysql-server`. It copies custom Apache `envvars`, `apache2.conf`, and `000-default.conf` from `.docker/config/apache2`, creates a non-root `uvdesk` user, installs signature-verified Composer and `gosu`, runs `composer install` and `composer dump-autoload --optimize`, attempts a prod cache clear (tolerating failure), sets ownership to `uvdesk` and mode `775` on `var`, `config`, `public`, `migrations`, and `.env`, and uses `.docker/bash/uvdesk-entrypoint.sh` as the entrypoint with `CMD ["/bin/bash"]`.

The entrypoint restarts Apache and MySQL, then — only when `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE` are all set and `mysqladmin ping` succeeds — creates the database if absent, grants all privileges on it to the configured user, resets the root password using `mysql_native_password`, and writes `/etc/mysql/my.cnf` (root) and `/home/uvdesk/.my.cnf` (application user) client credential files. If any variable is missing it prints a notice and skips database provisioning. It then steps down via `gosu uvdesk "$@"` and `exec "$@"`.

### 4.3 Alternate / Exceptional Behavior

| Situation | Observed behavior |
|---|---|
| Unknown `specification` in requirements check | HTTP 404 with an empty JSON body |
| `redis` extension loaded during requirements check | `status: false` returned with advisory text, even though Redis is not otherwise required |
| Database does not exist and `createDatabase` not requested | `{status:false, message:"The requested database was not found."}` |
| Database unreachable | Generic connection-failure JSON; the underlying exception detail is not exposed |
| `.env` update command returns non-zero | `{success:false}` with HTTP 500; the wizard surfaces an `.env` permission remediation message |
| Migration or fixture stage fails | The XHR still returns HTTP 200 with `[]`; the client marks the step complete and proceeds |
| A super admin already exists | Super-user stage performs no writes and returns `[]` |
| An existing user's role differs from super admin | The existing `UserInstance` role is upgraded rather than a duplicate account created |
| Duplicate account for the same role level via CLI | `uvdesk_wizard:defaults:create-user` returns exit code `1` without persisting |
| Invalid role code via CLI | Exit code `2` with an explicit error message |
| `uvdesk_wizard:env:update` outside `dev` | Throws "This command is only allowed to be used in development environment." (HTTP 500 through the wizard stage) |
| Schema version comparison finds equal versions in the CLI doctor | Prints "Unable to correctly determine database schema version." and exits `1` — the success and failure branches are inverted relative to their messages |
| CLI migration/fixtures subprocess failure | Error message printed, exit `1`, evaluation aborted |
| Telemetry or logo fetch fails | Exception caught and discarded; installation continues silently |
| Uncaught exception in `prod` | Branded 403/404/500 page; in non-`prod` environments the subscriber returns without altering the response |
| 403 with no authenticated user | No substituted response; default framework handling applies |
| `BaseController::base` throws during state detection | Exception swallowed; the request falls through to the installation wizard |
| Wizard XHR returns 404/500 | Dedicated client-side error templates explain rewrite/`index.php` configuration or suggest retry |
| `MYSQL_*` variables absent at container start | Database provisioning skipped with a notice; the application still starts against the `.env` DSN |

### 4.4 Business Rules

1. **Installation gate.** The wizard is presented only while no active user holds `ROLE_SUPER_ADMIN` or `ROLE_ADMIN`; once administrators and website records exist, `/` redirects to the installed surfaces.
2. **Super-admin uniqueness.** A super-admin account is created only if no active `UserInstance` already holds `ROLE_SUPER_ADMIN`; existing accounts are role-upgraded rather than duplicated.
3. **Role-level exclusivity (CLI).** A user may not hold two member-level roles (ids 1–3) simultaneously, nor two customer-level roles (id 4).
4. **Credential strength.** CLI passwords must be 8–32 characters and match on confirmation; e-mail addresses must pass `FILTER_VALIDATE_EMAIL` after sanitization. Web-side rules (in `wizard.js`) require a name matching `^[A-Za-z][A-Za-z]*[\sA-Za-z]*$`, a standard e-mail pattern, and a password matching `^(?=(.*[a-zA-Z].*){2,})(?=.*\d)(?=.*[^\w\s]|.*_)[^\s]{8,}$`.
5. **URL prefix rules.** Member and customer prefixes are both mandatory, must differ, and may contain only letters and numbers (`^[a-z0-9A-Z]*$`); defaults are `member` and `customer`.
6. **Platform minimums.** PHP ≥ 7.0 (composer requires ≥ 7.2.5), `max_execution_time` ≥ 30 s, and the `imap`, `mailparse`, `mysqli` extensions.
7. **Database creation is opt-in.** A missing database is created only when the operator explicitly requests it (`createDatabase` flag or CLI confirmation).
8. **Environment restriction on configuration writes.** `.env` may only be rewritten by `uvdesk_wizard:env:update` while `APP_ENV=dev`.
9. **Production error suppression.** Detailed error output is replaced by generic branded pages only in `prod`.
10. **Cache lifetime.** The tracker logo cache is valid for 7 days; the key is `md5(imageUrl)`.
11. **Default ticket semantics.** New tickets default to type `support`, status `open`, priority `low`, with `mail.html.twig` as the default e-mail template.
12. **Upload limits.** 20 files per request, 2 MiB per file, 8 MiB total post size.
13. **Anonymous-accessible paths.** Login, account creation, password reset, credential update, customer ticket creation, and the mailbox listener are explicitly exempted from authentication; all other member-panel paths require `ROLE_AGENT` and all other customer-panel paths require `ROLE_CUSTOMER`.

### 4.5 State Changes

| Stage | State mutated |
|---|---|
| Requirements check | Filesystem modes of `.env`, `config/packages/uvdesk.yaml`, `config/packages/uvdesk_mailbox.yaml` (attempted `0666`) |
| CLI doctor initialization | Filesystem modes of `.env`, `var`, `config`, `public`, `migrations` (`0775`) |
| Database verification | PHP session key `DB_CONFIG` |
| Admin details capture | PHP session key `USER_DETAILS` (plaintext password) |
| Prefix capture | PHP session key `PREFIXES_DETAILS` |
| Configuration stage | MySQL database created (optional); `.env` `DATABASE_URL` rewritten |
| Migration stage | Full relational schema created or migrated (`uv_*` tables) |
| Fixtures stage | Seed dataset appended (support roles, websites, default ticket metadata) |
| Super-user stage | `User` row inserted/updated (encoded password, enabled); `UserInstance` row inserted (`website` source, active, verified, super-admin role) |
| Prefix update stage | Website prefix configuration persisted through `UVDeskService`; outbound telemetry record created at the vendor endpoint |
| Tracker image request | File created/refreshed at `public/cache/images/<md5>.png`; directory created if absent |
| Container start | MySQL database, user grants, root password, `/etc/mysql/my.cnf`, `/home/uvdesk/.my.cnf` |

### 4.6 Inputs

**Wizard forms (browser):** `specification` (probe selector); `serverName`, `serverPort`, `username`, `password`, `database`, `serverVersion`, `createDatabase`; `name`, `email`, `password`, `confirm_password`; `member-prefix` / `memberUrlPrefix`, `customer-prefix` / `customerUrlPrefix`.

**CLI arguments:** `uvdesk_wizard:env:update <name> <value>`; `uvdesk_wizard:defaults:create-user <role> [name] [email] [password] [--no-interaction]`; `uvdesk:configure-helpdesk` (fully interactive).

**Environment:** `APP_ENV`, `APP_SECRET`, `DATABASE_URL`, `UV_SESSION_COOKIE_LIFETIME`, `MAILER_DSN`, `TRUSTED_PROXIES`/`TRUSTED_HOSTS` (commented); container-time `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_ROOT_PASSWORD`.

**Configuration:** YAML trees for `uvdesk`, `uvdesk_mailbox`, `uvdesk_extensions`, `security`, `doctrine`, `framework`, `mailer`, `translation`, `twig`.

### 4.7 Outputs

- **HTML:** the wizard single-page shell with embedded templates; the production error page; the default e-mail template.
- **JSON (wizard XHR):** `{status, version, message, description}`, `{extensions:[…]}`, `{configfiles:[…]}`, `{success:bool}`, `[]` for fire-and-forget stages, and the website URL collection (`memberLogin`, `knowledgebase`) on completion.
- **JSON (tracker):** a quoted absolute URL string pointing at the cached logo file.
- **HTTP redirects:** 301 to `helpdesk_knowledgebase`, or redirect to `helpdesk_member_handle_login`.
- **Filesystem:** rewritten `.env`; generated migration state; cached PNG under `public/cache/images/`; MySQL client credential files in the container.
- **Database:** schema, fixtures, user and user-instance records, website prefix records.
- **Console:** progress checklist output with success/warning/error markers and interactive prompts; exit codes `0`, `1`, `2`.
- **Outbound:** `POST https://updates.uvdesk.com/api/updates` with `{domain, email, name, country_code:null}`; `GET https://updates.uvdesk.com/uvdesk-logo.png` with a `Domain` header.

## 5. Use Cases / User Stories

For each use case:
- Identifier
- Name
- Primary actor
- Supporting actors / systems
- Preconditions
- Trigger
- Main success scenario
- Alternate flows
- Exception flows
- Postconditions
- Special requirements

### UC-01 — Install the helpdesk through the browser wizard

- Identifier: UC-01
- Name: Install the helpdesk through the browser wizard
- Primary actor: Installer / system administrator
- Supporting actors / systems: MySQL server; `UVDeskService` (core bundle); Doctrine; UVDesk updates endpoint
- Preconditions: Dependencies installed; web server serving `public/`; `.env` and UVDesk config files writable; MySQL reachable; kernel in `dev` for the configuration stage to succeed.
- Trigger: `GET /` on a system with no administrator account.
- Main success scenario:
  1. The operator opens the site root; `BaseController::base` finds no super-admin/admin role holders and forwards to the wizard.
  2. The Welcome screen renders with the version and prerequisite links; the operator clicks **LET'S BEGIN**.
  3. The System Requirements step probes PHP version, extensions, execution time, and file permissions, rendering pass/fail icons per criterion.
  4. The Database Configuration step submits server, port, user, password, database name, optional server version, and a create-database option; the server verifies connectivity and database existence and stores the result in the session.
  5. The Admin Details step submits name, e-mail, password, and confirmation; client-side regex validation gates the **Proceed** button; values are captured in the session.
  6. The website prefix step loads current prefixes (`GET ./wizard/xhr/website-configure`), lets the operator set member and customer prefixes, validates them, and stores them.
  7. The Installation step runs configurations → migrations → fixtures → super user → website prefixes, advancing the progress checklist after each call.
  8. Telemetry is posted to the vendor endpoint; the returned URL collection populates the completion screen with links to the agent panel login and the knowledgebase.
- Alternate flows: Database missing with create-database enabled → the database is created during the configuration stage. A super admin already exists → the super-user stage is a no-op. `GET` on the prefix endpoint returns existing prefixes → the form is pre-filled from `getDefaultAttributes()`.
- Exception flows: Requirements probe returns 404 for an unrecognized criterion; a 500 during the configuration stage surfaces an `.env` permission remediation message; a 404 anywhere surfaces rewrite/`index.php` guidance; migration and fixture failures are **not** surfaced because those endpoints always return 200.
- Postconditions: `.env` holds a working `DATABASE_URL`; schema and fixtures exist; a `ROLE_SUPER_ADMIN` user and user instance exist; website prefixes are persisted; the completion screen is displayed.
- Special requirements: jQuery/Underscore/Backbone loaded from CDNs; PHP session support; `max_execution_time` sufficient for migrations.

### UC-02 — Repair or complete an installation from the terminal

- Identifier: UC-02
- Name: Repair or complete an installation from the terminal
- Primary actor: Installer / operator
- Supporting actors / systems: `bin/console` sub-commands; MySQL; UVDesk updates endpoint
- Preconditions: Project directory present with `.env`; PHP CLI available.
- Trigger: `php bin/console uvdesk:configure-helpdesk`
- Main success scenario: permissions normalized → credentials parsed from `.env` → connectivity confirmed → schema version compared → super-admin presence confirmed → telemetry sent → exit `0`.
- Alternate flows: connectivity failure triggers an interactive re-configuration loop; a missing database triggers an offer to create it; a stale schema triggers an offer to migrate and append fixtures; a missing super admin triggers interactive account creation delegated to `uvdesk_wizard:defaults:create-user`.
- Exception flows: operator declines re-configuration → exit `1`; subprocess failure → error printed, exit `1`; equal migration versions → the command prints "Unable to correctly determine database schema version." and exits `1`.
- Postconditions: `.env`, schema, fixtures, and super-admin account brought to a consistent state.
- Special requirements: Interactive TTY for prompts; hidden password entry; up to 900 s for migrations.

### UC-03 — Create an additional helpdesk user account

- Identifier: UC-03
- Name: Create an additional helpdesk user account
- Primary actor: Operator (or the CLI doctor acting on the operator's behalf)
- Supporting actors / systems: Doctrine entity manager; password encoder
- Preconditions: Schema and fixtures loaded so that support roles exist.
- Trigger: `php bin/console uvdesk_wizard:defaults:create-user <ROLE_CODE> [name] [email] [password] [--no-interaction]`
- Main success scenario: role resolved by code → user found by e-mail or created → name split into first/last → password encoded → `User` and `UserInstance` (source `website`, active, verified) persisted → exit `0`.
- Alternate flows: interactive mode prompts for e-mail, name, password, and confirmation with per-field validation and hidden password entry.
- Exception flows: missing required arguments in non-interactive mode → exit `2`; unknown role code → exit `2`; user already holds an equivalent role level → exit `1`, nothing written.
- Postconditions: a new authenticated helpdesk identity exists with the requested access level.
- Special requirements: password length 8–32; e-mail must validate after sanitization.

### UC-04 — Reach the correct surface after installation

- Identifier: UC-04
- Name: Reach the correct surface after installation
- Primary actor: Any visitor (agent, customer, or anonymous)
- Supporting actors / systems: Kernel bundle registry; `Website`, `SupportRole`, `UserInstance` repositories
- Preconditions: None.
- Trigger: `GET /`
- Main success scenario: administrators exist and the SupportCenter bundle is loaded with a `knowledgebase` website record → 301 to `helpdesk_knowledgebase`; otherwise a `helpdesk` website record exists → redirect to `helpdesk_member_handle_login`.
- Alternate flows: no administrators → forward to the installation wizard.
- Exception flows: repository or bundle introspection throws → exception swallowed → the wizard is rendered even on an installed system.
- Postconditions: the visitor lands on the portal, the agent login, or the wizard.
- Special requirements: none.

### UC-05 — Retrieve the cached UVDesk logo

- Identifier: UC-05
- Name: Retrieve the cached UVDesk logo
- Primary actor: Web client (helpdesk UI)
- Supporting actors / systems: `updates.uvdesk.com`; local filesystem
- Preconditions: `public/` writable so `public/cache/images` can be created.
- Trigger: `GET /tracker/xhr/get/cacheImage`
- Main success scenario: cache hit within 7 days → the existing PNG path is converted to an absolute public URL and returned as JSON.
- Alternate flows: cache miss or expiry → the remote image is fetched with a `Domain` header and browser user agent, decoded, saved as PNG, then returned.
- Exception flows: remote unreachable or undecodable → `NotReadableException` propagates from the image manager; the endpoint has no local fallback image.
- Postconditions: a fresh cached PNG exists; the vendor host has observed the site domain.
- Special requirements: outbound HTTPS egress; the `intervention/image` driver configured by the manager.

### UC-06 — Provision the stack with Docker

- Identifier: UC-06
- Name: Provision the stack with Docker
- Primary actor: Container operator
- Supporting actors / systems: Apache, MySQL, Composer, gosu
- Preconditions: Docker available; optionally `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_ROOT_PASSWORD` supplied.
- Trigger: `docker build` then container start.
- Main success scenario: image builds with PHP 8.1, Apache (rewrite enabled), MySQL, and Composer dependencies installed; at start, services come up, the database and grants are created, client credential files are written, and an interactive shell runs as the `uvdesk` user.
- Alternate flows: `MYSQL_*` not fully supplied → database provisioning is skipped with a printed notice.
- Exception flows: `mysqladmin ping` fails → the entrypoint prints an error and exits `1`.
- Postconditions: a running LAMP container with the skeleton deployed at `/var/www/uvdesk`, ready for UC-01 or UC-02.
- Special requirements: default `CMD` is `/bin/bash`, so the container is evaluation-oriented; the operator must start/attach the web service workflow accordingly.

### UC-07 — Experience the helpdesk in a preferred language

- Identifier: UC-07
- Name: Experience the helpdesk in a preferred language
- Primary actor: Agent or customer
- Supporting actors / systems: Symfony translator; bundle-provided templates
- Preconditions: `app_locales` includes the desired locale.
- Trigger: Any rendered helpdesk page.
- Main success scenario: message catalogs for `ar, da, de, en, es, fr, he, it, pl, pt_BR, tr, zh` are available to the translator, with `en` as the default locale.
- Alternate flows: a locale outside `app_locales` falls back per framework translation configuration.
- Exception flows: a locale outside `app_locales` falls back per framework translation configuration.
- Postconditions: localized UI text.
- Special requirements: catalog completeness per locale is not verifiable from the skeleton alone; the bundles own most translatable strings.

### UC-08 — Use the assembled helpdesk (delivered by dependencies)

- Identifier: UC-08
- Name: Use the assembled helpdesk (delivered by dependencies)
- Primary actor: Agent, customer, API consumer, mailbox listener
- Supporting actors / systems: `uvdesk/core-framework`, `support-center-bundle`, `mailbox-component`, `automation-bundle`, `extension-framework`, `api-bundle`
- Preconditions: installation completed; bundles registered; prefixes, roles, upload limits, and defaults configured by this repository.
- Trigger: requests under `/{member_prefix}/…`, `/{customer_prefix}/…`, `^/api`, or `/{member_prefix}/mailbox/listener`.
- Main success scenario: the request is authenticated by the matching firewall and served by bundle-provided controllers (for example `helpdesk_member_dashboard`, `helpdesk_customer_ticket_collection`, `helpdesk_knowledgebase`, `create-ticket`).
- Alternate flows: anonymous access is allowed exactly on the login, registration, password-reset, credential-update, ticket-creation, and mailbox-listener paths.
- Exception flows: uncaught exceptions in `prod` are converted into the skeleton's branded error pages.
- Postconditions: ticket, conversation, and user state changes owned by the bundles.
- Special requirements: **No implementation of these workflows exists in this repository.** Mailbox ingestion is inert by default because `uvdesk_mailbox.mailboxes` and `uvdesk_mailbox.emails` are null/commented; outbound mail is inert because `MAILER_DSN=null://null`.

## 6. Functional Requirements

For each requirement:
- Requirement ID
- Requirement statement
- Rationale
- Priority
- Dependencies
- Verification criteria
- Traceability

| ID | Requirement statement | Rationale | Priority | Dependencies | Verification criteria | Traceability |
|---|---|---|---|---|---|---|
| FR-01 | The system shall detect whether the helpdesk is installed and route `/` to the knowledgebase, the agent login, or the installation wizard accordingly. | Single entry point must serve both installed and uninstalled states. | Must | Core-framework entities; SupportCenter bundle | Requesting `/` before install renders the wizard; after install redirects as specified. | UC-04, `BaseController::base` |
| FR-02 | The system shall provide a multi-stage browser installation wizard covering welcome, system requirements, database configuration, administrator details, website prefixes, and installation. | Enables non-expert installation. | Must | Wizard template, `wizard.js`, XHR endpoints | All five checklist stages are reachable and each XHR call succeeds. | UC-01 |
| FR-03 | The system shall evaluate PHP version, required extensions (`imap`, `mailparse`, `mysqli`), maximum execution time, and write permissions on `.env` and the UVDesk config files, returning machine-readable results with remediation guidance. | Prevents installs doomed by environment defects. | Must | `evaluateSystemRequirements` | Each supported `specification` returns the documented payload; unknown values return 404. | §4.2.3 |
| FR-04 | The system shall attempt to make `.env` and the UVDesk configuration files writable before reporting a permission failure. | Reduces manual chmod steps. | Should | Filesystem permissions | Non-writable files are chmod'ed to `0666` and re-tested. | §4.2.3 |
| FR-05 | The system shall verify MySQL credentials, optionally report a server version, determine whether the named database exists, and optionally create it. | Guarantees a usable persistence target before configuration writes. | Must | DBAL connection | Missing database without the create flag returns a "not found" message; with the flag the database is created later. | §4.2.4, §4.2.6 |
| FR-06 | The system shall persist wizard inputs (database credentials, administrator identity, URL prefixes) in the server-side session between stages. | Avoids re-entry and keeps secrets out of URLs. | Must | PHP sessions | Session keys `DB_CONFIG`, `USER_DETAILS`, `PREFIXES_DETAILS` are populated and consumed by later stages. | §4.5 |
| FR-07 | The system shall write the resolved `DATABASE_URL` into `.env` by invoking `uvdesk_wizard:env:update`. | Makes the configuration durable across requests. | Must | FR-11 | After the configuration stage, `.env` contains the working DSN. | §4.2.6 |
| FR-08 | The system shall create the database schema for a fresh database, or migrate an existing one to the latest mapping metadata, and load default fixtures. | Produces a usable data layer. | Must | FR-12, Doctrine migrations/fixtures | Empty database → schema created and fixtures loaded; existing database → migrated to the latest version. | §4.2.8 |
| FR-09 | The system shall create exactly one active `ROLE_SUPER_ADMIN` user with an encoded password, splitting the supplied name into first and last name, and shall not duplicate an existing super admin. | Bootstraps administrative access safely. | Must | Core-framework `User`, `UserInstance`, `SupportRole`; password encoder | Post-install, one active super-admin user instance exists; repeated runs change nothing. | §4.2.6, §4.2.9 |
| FR-10 | The system shall let the operator define distinct alphanumeric member-panel and customer-panel URL prefixes and persist them through the core `UVDeskService`. | Separates agent and customer surfaces and drives firewall/access-control patterns. | Must | `UVDeskService::updateWebsitePrefixes`; `uvdesk_site_path.*` parameters | Prefix validation rejects empty, identical, or non-alphanumeric values; the completion screen reflects the new prefixes. | §4.2.5, §4.2.6, §4.4 |
| FR-11 | The system shall provide a command that updates a single variable in `.env` while preserving comments and unrelated lines, and shall refuse to run outside the `dev` environment. | Safe, targeted configuration editing. | Must | Symfony Dotenv | Value replaced in place; comment lines retained; non-dev invocation throws. | §4.2.10 |
| FR-12 | The system shall provide a hidden migration command that distinguishes fresh from existing databases and supports both DBAL 2 and DBAL 3 schema managers. | One entry point for both install and upgrade. | Must | Doctrine migrations bundle | Empty schema → create+fixtures; populated schema → sync/version/diff/migrate. | §4.2.8 |
| FR-13 | The system shall provide an interactive console doctor that normalizes permissions, verifies connectivity, repairs `.env`, migrates the schema, and ensures a super admin exists. | Supports headless and recovery scenarios. | Must | FR-07…FR-09, FR-11, FR-12 | Each check reports success, warning, or failure and offers a corrective prompt. | UC-02 |
| FR-14 | The system shall provide a hidden command to create a user for a given support-role code with validation, duplicate-role protection, and both interactive and non-interactive modes. | Reusable provisioning primitive. | Must | FR-09 dependencies | Valid invocation creates `User`+`UserInstance`; invalid role or missing args exit `2`; duplicate role level exits `1`. | UC-03 |
| FR-15 | The system shall expose a tracker endpoint that caches the vendor logo locally for 7 days under `public/cache/images/` and returns its absolute URL as JSON. | Avoids repeated external fetches while branding the UI. | Should | `intervention/image`; writable `public/` | First call fetches and writes the PNG; subsequent calls within 7 days reuse it; the response is a quoted absolute URL. | UC-05 |
| FR-16 | On successful installation the system shall report the site domain, administrator name, and administrator e-mail to the vendor updates endpoint, and shall not fail the installation if reporting fails. | Vendor install telemetry without blocking the operator. | Could | cURL; outbound HTTPS | A JSON POST is issued; network errors are swallowed. | §4.2.6, §4.2.7 |
| FR-17 | In production the system shall replace uncaught exceptions with branded 403, 404, and 500 pages, and shall not alter responses in other environments. | Prevents information disclosure while retaining developer detail in dev. | Must | Twig template `errors/error.html.twig` | A 404 in `prod` renders the branded page; the same in `dev` does not. | §4.2.12 |
| FR-18 | The system shall register the six UVDesk bundles for all environments and contribute its own routes through the core framework's `uvdesk`/`uvdesk_extensions` routing loaders. | Assembles the product from components. | Must | Composer packages; `RoutingResourceInterface` | `config/bundles.php` entries load; the ten skeleton routes resolve. | §4.2.13, §4.2.14 |
| FR-19 | The system shall define a role hierarchy, per-surface firewalls (member panel, customer portal, API), and URL access-control rules that keep authentication-exempt paths anonymous and require `ROLE_AGENT`/`ROLE_CUSTOMER` elsewhere. | Establishes the authorization model for the assembled helpdesk. | Must | Security bundle; core/API user providers | Member paths require `ROLE_AGENT`; customer paths require `ROLE_CUSTOMER`; `^/api` uses `APIGuard`. | §3.1, §4.4 |
| FR-20 | The system shall ship default helpdesk configuration: locales, URL prefixes, upload limits, avatar defaults, site URL, upload manager, support e-mail, default ticket type/status/priority, and default e-mail template. | Gives the bundles deterministic defaults. | Must | `config/packages/uvdesk.yaml` | Values match the documented defaults and are consumed by bundle code. | §4.2.14 |
| FR-21 | The system shall provide message catalogs for twelve locales and a configurable locale list. | International reach of the community edition. | Should | Translation bundle | `app_locales` matches the catalog set; default locale `en`. | UC-07 |
| FR-22 | The system shall provide a Docker image containing PHP 8.1, Apache with rewrite, MySQL, Composer-installed dependencies, a non-root application user, and an entrypoint that provisions the database from `MYSQL_*` variables. | One-command evaluation environment. | Should | Dockerfile, `.docker/**` | Build succeeds; entrypoint creates the database and grants when variables are present and skips otherwise. | UC-06 |
| FR-23 | The system shall declare mailbox configuration structure (IMAP/SMTP per mailbox, outbound disable, strict mode, reply delimiter) without enabling any mailbox by default. | Documents the email-to-ticket surface while keeping it inert until configured. | Could | `uvdesk/mailbox-component` | `mailboxes` and `emails` are null/commented; no mailbox is active out of the box. | §4.2.14 |
| FR-24 | The system shall reserve an application extension directory (`apps/`) for installed add-ons. | Extension framework integration point. | Could | `uvdesk/extension-framework` | `uvdesk_extensions.dir` resolves to `%kernel.project_dir%/apps`; the directory is otherwise empty. | §4.2.14 |
| FR-25 | The wizard client shall surface actionable guidance when its own XHR calls return 404 or 500, including web-server rewrite instructions. | Self-service troubleshooting during install. | Should | `wizard.js` error templates | A 404 renders the rewrite/`index.php` message; a 500 renders the retry message. | §4.2.2, §4.3 |

## 7. Interfaces and Interactions

### 7.1 User Interface

- **Installation wizard** (`templates/installation-wizard/index.html.twig` + `public/scripts/wizard.js` + `public/css/wizard.css`, `reset.css`): a Backbone-driven single-page flow with a five-node progress checklist, per-step forms rendered from Underscore templates, inline field-level notices ("This field is mandatory", "Only letters and numbers are allowed", "Both prefixes can not be same.", "Invalid Name"), animated SVG status icons (loader, success, warning, error), Back/Proceed/Let's Begin/Cancel controls, a processing spinner on the Proceed button, an installation progress list with per-step loaders, and a completion screen linking to the agent panel and knowledgebase. Third-party libraries are loaded from `ajax.googleapis.com` and `cdnjs.cloudflare.com`.
- **Error page** (`templates/errors/error.html.twig`): code, message, and description supplied by the exception subscriber.
- **Console UI:** ANSI-colored, cursor-managed interactive prompts with hidden password entry and inline warnings.
- **Bundle-provided UI:** agent panel, customer portal, and knowledgebase pages are rendered by `uvdesk/support-center-bundle` and `uvdesk/core-framework`; they are not part of this repository.

### 7.2 System Interfaces

**HTTP routes owned by this repository** (declared in `src/Resources/config/routes.yaml`, loaded via the `uvdesk` routing resource):

| Method | Path | Handler |
|---|---|---|
| GET (annotation) | `/` | `BaseController::base` (`base_route`) |
| POST | `/wizard/xhr/check-requirements` | `ConfigureHelpdesk::evaluateSystemRequirements` |
| POST | `/wizard/xhr/verify-database-credentials` | `ConfigureHelpdesk::verifyDatabaseCredentials` |
| POST | `/wizard/xhr/intermediary/super-user` | `ConfigureHelpdesk::prepareSuperUserDetailsXHR` |
| GET/POST | `/wizard/xhr/website-configure` | `ConfigureHelpdesk::websiteConfigurationXHR` |
| POST | `/wizard/xhr/load/configurations` | `ConfigureHelpdesk::updateConfigurationsXHR` |
| POST | `/wizard/xhr/load/migrations` | `ConfigureHelpdesk::migrateDatabaseSchemaXHR` |
| POST | `/wizard/xhr/load/entities` | `ConfigureHelpdesk::populateDatabaseEntitiesXHR` |
| POST | `/wizard/xhr/load/super-user` | `ConfigureHelpdesk::createDefaultSuperUserXHR` |
| POST | `/wizard/xhr/load/website-configure` | `ConfigureHelpdesk::updateWebsiteConfigurationXHR` |
| GET | `/tracker/xhr/get/cacheImage` | `ImageCacheController::getCachedImage` |

**Console commands owned by this repository:** `uvdesk:configure-helpdesk`, `uvdesk_wizard:env:update`, `uvdesk_wizard:defaults:create-user` (hidden), `uvdesk_wizard:database:migrate` (hidden). Composer auto-scripts additionally invoke `cache:clear` and `assets:install %PUBLIC_DIR%` on install/update.

**In-process interfaces consumed from dependencies:** `UVDeskService::getCurrentWebsitePrefixes()` / `updateWebsitePrefixes()`; `UserPasswordEncoderInterface::encodePassword()`; `EntityManagerInterface` and repositories for `SupportRole`, `User`, `UserInstance`, `Website`; `RoutingResourceInterface`; `KernelInterface::getBundles()`, `getProjectDir()`, `getEnvironment()`; Symfony console `Application` with `ArrayInput`; `Symfony\Component\Process\Process` for `bin/console` subprocesses; Doctrine DBAL `DriverManager` and schema manager.

**Web-server boundary:** `public/index.php` front controller with `public/.htaccess` for Apache rewriting; the Docker image enables `mod_rewrite` and ships custom `envvars`, `apache2.conf`, and vhost configuration.

### 7.3 External Services

| Service | Direction | Purpose | Failure handling |
|---|---|---|---|
| `https://updates.uvdesk.com/api/updates` | Outbound POST (cURL, JSON) | Installation telemetry: domain, e-mail, name, `country_code: null` | All exceptions caught and ignored |
| `https://updates.uvdesk.com/uvdesk-logo.png` | Outbound GET with `Domain` header and browser `User-Agent` | Branding asset for the local image cache | `NotReadableException` on fetch/decode failure; no fallback asset |
| MySQL server | Outbound (Doctrine DBAL / PDO `pdo_mysql`) | Persistence for schema, fixtures, users, configuration | JSON failure responses; CLI retries interactively |
| CDN hosts (`ajax.googleapis.com`, `cdnjs.cloudflare.com`) | Browser-side | jQuery, Underscore, Backbone, Backbone.Validation for the wizard | Not handled; the wizard cannot start without them |
| SMTP / mail transport | Outbound | Configured via `MAILER_DSN`, defaulting to `null://null` (disabled) | Not exercised by default |
| IMAP mailboxes | Inbound/outbound | Declared in `uvdesk_mailbox.yaml` but not configured | Inert by default |
| GitHub API (`api.github.com/repos/uvdesk/recipes/…`) | Build-time | Symfony Flex recipe endpoint for dependency installation | Build-time only |
| Composer repositories | Build-time | Installs the six `uvdesk/*` packages and framework dependencies | Build-time only |

### 7.4 Notifications / Events

- **Framework events:** `KernelEvents::EXCEPTION` handled by `ExceptionSubscriber` at priority 10 (production only).
- **Console lifecycle:** `initialize()` / `interact()` / `execute()` hooks drive permission normalization, prompting, and command execution.
- **E-mail notifications:** the default e-mail template is `templates/mail.html.twig`, referenced by `uvdesk.default.templates.email`; actual dispatch belongs to the bundles and is disabled by the default null mailer DSN.
- **No message queue, webhook, or notifier channel configuration is present in this repository**, although `symfony/notifier` and `symfony/mailer` are declared as dependencies.

## 8. Data and Information

### 8.1 Data Inputs

Wizard POST bodies (requirements specification; database server/port/user/password/name/version/create flag; administrator name/e-mail/password/confirmation; member and customer URL prefixes), CLI arguments (role code, name, e-mail, password; environment variable name and value), `.env` variables, YAML configuration trees, and the remote logo binary.

### 8.2 Data Outputs

JSON status/payload objects for each wizard stage, the website prefix/URL collection, the cached-image URL string, HTTP redirects, rendered HTML pages, rewritten `.env` content, cached PNG files, generated migration artifacts, and the telemetry JSON payload.

### 8.3 Data Entities

`src/Entity/` and `src/Migrations/` are empty apart from `.gitignore`; all persistent entities come from `uvdesk/core-framework`. Entities directly manipulated by this repository:

| Entity | Namespace | Use here |
|---|---|---|
| `SupportRole` | `Webkul\UVDesk\CoreFrameworkBundle\Entity` | Looked up by `code` (`ROLE_SUPER_ADMIN`, `ROLE_ADMIN`) to gate installation and assign privileges |
| `User` | same | Found by e-mail or created; first/last name, encoded password, `isEnabled` |
| `UserInstance` | same | Created with `source='website'`, `isActive`, `isVerified`, linked `supportRole`; queried by support role to detect administrators |
| `Website` | same | Looked up by `code` (`knowledgebase`, `helpdesk`) to decide the post-install redirect |

Physical tables observed through raw SQL in the CLI doctor use the `uv_` prefix: `uv_support_role`, `uv_user_instance`, `uv_user`. Column naming observed includes `supportRole_id` and `user_id`. Session-resident structures (`DB_CONFIG`, `USER_DETAILS`, `PREFIXES_DETAILS`) are transient installation state. The filesystem cache (`public/cache/images/<md5>.png`) is derived data with a 7-day validity window.

### 8.4 Validation / Integrity Rules

- **Client-side (wizard.js):** debounced 400 ms keyup validation; mandatory-field checks; prefix inequality; alphanumeric-only prefixes (`^[a-z0-9A-Z]*$`); name pattern `^[A-Za-z][A-Za-z]*[\sA-Za-z]*$`; standard e-mail pattern; password pattern requiring at least two letter groups, a digit, a special character or underscore, no whitespace, and a minimum of 8 characters; Enter key submits when valid.
- **Server-side (wizard XHR):** database existence verified against `listDatabases()`; PHP version, extension, execution-time, and writability checks; unknown requirement probes rejected with 404. **No server-side re-validation** of the administrator name/e-mail/password or of prefix format is performed in `prepareSuperUserDetailsXHR`, `websiteConfigurationXHR`, or `createDefaultSuperUserXHR` — these trust the captured session values.
- **Server-side (CLI):** e-mail sanitized and validated in a loop; name mandatory; password 8–32 characters with matching confirmation; role code must resolve to a `SupportRole`; non-interactive mode rejects incomplete arguments with exit `2`; duplicate role-level assignment rejected with exit `1`.
- **Integrity:** passwords are stored only in encoded form (`UserPasswordEncoderInterface`); migrations are versioned and compared before being applied; fixtures are appended rather than replacing data during the wizard flow.

## 9. Quality and Operational Considerations

### 9.1 Performance

- The requirements gate enforces `max_execution_time >= 30` and links to guidance for raising it, because installation stages run synchronous schema work inside HTTP requests.
- CLI migration subprocesses carry explicit timeouts: 900 s for `doctrine:migrations:migrate`, 120 s for `doctrine:fixtures:load`.
- Installation stages execute sequentially and block; the wizard awaits each XHR before advancing, so total install time is the sum of schema creation, migration, and fixture loading.
- The tracker image is cached for 7 days, converting a recurring outbound fetch into a local file read; the cache directory is created on demand with mode `0775`.
- Upload ceilings are declared as parameters (20 files, 2 MiB per file, 8 MiB per post), bounding request size for the assembled helpdesk.
- Composer is configured with `optimize-autoloader: true` and the image runs `composer dump-autoload --optimize` plus a production cache clear.

### 9.2 Security

**Strengths**
- Passwords are hashed through the configured encoder before persistence; CLI password prompts are hidden with no plaintext fallback.
- A role hierarchy plus explicit `access_control` list confines the member panel to `ROLE_AGENT` and the customer portal to `ROLE_CUSTOMER`, with narrow anonymous exemptions and a dedicated `^/api` firewall using `APIGuard` with a separate credentials provider.
- Production exceptions are replaced with generic pages, avoiding stack-trace disclosure.
- The `.env` rewrite command is environment-gated to `dev`.
- The Docker image runs the application as a non-root `uvdesk` user via `gosu`, verifies the Composer installer signature against the published checksum, and verifies the `gosu` binary with GPG.
- Database credential failures return generic messages rather than driver details.

**Observed weaknesses / constraints**
- The nine `/wizard/xhr/*` endpoints have no `access_control` entry, so on a deployed-but-uninstalled (or partially installed) instance they are anonymously reachable and can create databases, rewrite `.env`, run migrations, load fixtures, and create a super-admin account.
- Administrator credentials and database credentials are held in plaintext in the PHP session (`$_SESSION['USER_DETAILS']['password']`, `$_SESSION['DB_CONFIG']['password']`) for the duration of the wizard.
- The requirements probe performs `chmod 0666` on `.env`, `config/packages/uvdesk.yaml`, and `config/packages/uvdesk_mailbox.yaml`, and the CLI doctor performs `chmod 0775` on `.env`, `var`, `config`, `public`, and `migrations` — world-writable configuration as a side effect of a GET-driven check.
- `.env` is committed with `APP_ENV=dev`, a placeholder `APP_SECRET`, and a template `DATABASE_URL`; the wizard's configuration stage only works in `dev`, which couples successful web installation to a development-mode kernel.
- `ImageManager::initFromUrl` performs a server-side fetch of a hardcoded HTTPS URL; the URL is not user-supplied, but the request transmits the site domain in a header.
- Installation telemetry transmits the administrator's name, e-mail, and site domain to a vendor endpoint with no opt-out mechanism present in the repository; errors are silently discarded.
- The custom image manager sets a spoofed desktop browser `User-Agent`.
- Wizard libraries are loaded from third-party CDNs without subresource integrity attributes.
- The production error subscriber ignores response content type, so API clients receive HTML error bodies (an in-code `@TODO` acknowledges this).

### 9.3 Availability / Reliability

- Migration and fixture XHR endpoints return HTTP 200 with an empty body regardless of the underlying command's exit code, so the wizard can report success while the schema is incomplete; the CLI doctor surfaces these failures properly.
- `BaseController::base` swallows all exceptions during state detection, which means a transient database error presents the installation wizard on an installed system.
- The CLI doctor's schema-version comparison has inverted branches: matching versions produce "Unable to correctly determine database schema version." and exit `1`, while differing versions trigger the migration offer.
- Telemetry and logo-cache failures are non-fatal by design.
- The Docker image bundles Apache, PHP, and MySQL in one container and defaults to `CMD ["/bin/bash"]`, making it an evaluation/development environment rather than a production service topology; the entrypoint also invokes the command twice (once through `gosu uvdesk "$@"`, once through `exec "$@"`).
- Outbound mail is disabled by default (`MAILER_DSN=null://null`) and no mailbox is configured, so notification-dependent helpdesk workflows are unavailable until the operator configures them.
- The wizard's client-side XHR paths are relative (`./wizard/xhr/...`), tying correct operation to the URL shape under which the wizard is served; the client-side 404 template explicitly anticipates sub-directory/rewrite problems.

### 9.4 Usability

- A guided, visually progressive wizard with per-step validation, inline notices, remediation hyperlinks keyed to specific failure modes (Ubuntu/WAMP/CentOS/Mac prerequisite guides, `.env` permission blog post, max-execution-time guide, Redis GitHub issue).
- Two equivalent installation paths (browser and terminal) plus a diagnostic/repair command for existing installs.
- Twelve locale catalogs and a configurable locale list; default locale `en`.
- Operator-chosen URL prefixes allow branding-neutral separation of agent and customer surfaces, with sensible defaults (`member`, `customer`).
- Console output uses a consistent success/warning/error marker vocabulary and clears prior prompt lines to keep the transcript compact.

### 9.5 Auditability / Logging

- No logging configuration file exists in `config/packages/` (no `monolog.yaml`), and no application-level logging calls appear in the skeleton's own code; `symfony/monolog-bundle` is declared as a dependency but is not configured here.
- The only outbound record of installation activity is the vendor telemetry POST (domain, administrator name, administrator e-mail, null country code) issued at the end of both the web and CLI installation paths, and the recurring `Domain` header sent with the logo fetch.
- Installation state changes are auditable only indirectly, through `.env` content, migration version records, and the `User`/`UserInstance` rows created.
- Console commands return distinct exit codes (`0` success, `1` failure, `2` invalid arguments), which supports scripted verification.

## 10. Acceptance Criteria

### 10.1 Functional Acceptance

1. On a codebase with no administrator accounts, `GET /` renders the installation wizard and displays the configured version string.
2. Each requirements probe returns a well-formed JSON result; an unrecognized `specification` returns HTTP 404.
3. Submitting valid MySQL credentials with an existing database returns `{status:true}`; a nonexistent database without the create flag returns the "not found" message; unreachable credentials return the connection-failure message.
4. After the configuration stage, `.env` contains `DATABASE_URL=mysql://<user>:<password>@<host>:<port>/<database>`.
5. After the migration stage against an empty database, the schema tables exist; against a populated database, the migration version equals the latest available version.
6. After the fixtures stage, `SupportRole` records for `ROLE_SUPER_ADMIN` and `ROLE_ADMIN` exist.
7. After the super-user stage, exactly one active `UserInstance` with `source='website'`, `isVerified=true`, and the `ROLE_SUPER_ADMIN` role exists, and the stored password is not plaintext.
8. After the prefix stage, the response contains `memberLogin` and `knowledgebase` URLs reflecting the submitted prefixes, and the completion screen links to them.
9. `uvdesk:configure-helpdesk` on a healthy install reports success for connectivity, schema, and super-admin checks and exits `0`.
10. `uvdesk_wizard:defaults:create-user` with an unknown role exits `2`; with a duplicate member-level role exits `1`; with valid new data creates both a `User` and a `UserInstance` and exits `0`.
11. `uvdesk_wizard:env:update NAME VALUE` rewrites only the targeted line, preserves comments, and throws when the kernel environment is not `dev`.
12. `GET /tracker/xhr/get/cacheImage` creates `public/cache/images/<md5>.png` on first call, reuses it within 7 days, and returns a JSON-quoted absolute URL.
13. In `prod`, requesting an unknown path renders the branded 404 page; in `dev`, the subscriber leaves the response untouched.
14. The Docker image builds, and with `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE` set the entrypoint creates the database, grants privileges, and writes both MySQL client configuration files.
15. All eleven skeleton routes resolve, and the six UVDesk bundles are registered.

### 10.2 Business Acceptance

1. A non-developer following `INSTALLATION GUIDE.md` can reach a working helpdesk login using either the browser wizard or the console doctor.
2. After installation, `/` no longer exposes the wizard and instead forwards visitors to the customer portal or the agent login.
3. The configured member and customer prefixes are reflected in the security firewall patterns and access-control rules without further edits.
4. Default ticket semantics (`support` / `open` / `low`) and upload limits take effect for the assembled helpdesk.
5. The twelve declared locales are available to the installed application.
6. The container path yields a runnable evaluation environment from a single `docker build`/`docker run` sequence.

### 10.3 Negative / Exception Cases

1. Missing `imap`, `mailparse`, or `mysqli` extensions is reported per-extension, and installation cannot proceed past the requirements step.
2. `max_execution_time` below 30 s is reported with remediation guidance.
3. A read-only `.env` that cannot be made writable is reported with a permission-remediation message; the configuration stage then fails with HTTP 500 and the client shows the same guidance.
4. An invalid e-mail or a password outside 8–32 characters is rejected repeatedly by the CLI until valid; mismatched confirmations are rejected.
5. Identical, empty, or non-alphanumeric URL prefixes block the Proceed control with an inline notice.
6. A migration or fixture failure during the web install is **not** reported to the operator — the endpoints still return HTTP 200 — so a broken schema can be followed by a "successful" completion screen. This is a known behavioral gap.
7. Running `uvdesk_wizard:env:update` in `prod` throws and aborts the configuration stage.
8. A failed telemetry POST or logo fetch is silently ignored and does not affect the installation result.
9. An unreachable remote logo causes a `NotReadableException` from the image manager with no fallback asset.
10. A 403 in production with no authenticated user yields no substituted response.
11. Absent `MYSQL_*` variables at container start skip database provisioning with a printed notice.
12. A `mysqladmin ping` failure in the entrypoint terminates container startup with exit `1`.

## 11. Dependencies, Constraints, and Assumptions

**Runtime dependencies (declared in `composer.json`)**
- PHP `^7.2.5 || ^8.0`, `ext-ctype`, `ext-iconv`, `symfony/flex`; Symfony `^5.4` via the Flex `require` setting.
- UVDesk packages: `uvdesk/core-framework ^1.1.7`, `uvdesk/support-center-bundle ^1.1.3`, `uvdesk/mailbox-component ^1.1.5`, `uvdesk/automation-bundle ^1.1.4`, `uvdesk/extension-framework ^1.1.2`, `uvdesk/api-bundle ^1.1.4`.
- Imaging: `intervention/image ^2.4`, `intervention/imagecache ^2.5.2`.
- Framework/features: doctrine ORM pack and fixtures, security bundle, form, validator, serializer, translator, twig (+ extra bundle), mailer, mime, swiftmailer bundle, notifier, http-client, process, asset, web-link, expression-language, intl, string, property-access/info, proxy-manager-bridge, runtime, monolog bundle, KNP paginator, Google reCAPTCHA, Sensio framework-extra, doctrine annotations, phpdocumentor reflection-docblock, phpstan phpdoc-parser.
- Dev: debug pack, maker bundle, profiler pack, test pack (Flex dev requirements).
- Custom Flex recipe endpoint: `https://api.github.com/repos/uvdesk/recipes/contents/index.json`.

**Client-side dependencies:** jQuery 2.2.4, Underscore 1.9.1, Backbone 1.3.3, Backbone.Validation 0.7.1 — all from public CDNs.

**Constraints**
- MySQL/MariaDB only: the DSN template is hardcoded to `mysql://`, the CLI doctor uses `pdo_mysql` and raw `uv_*` SQL, and the entrypoint provisions MySQL.
- `.env` writes require the `dev` environment.
- Web installation depends on PHP session state; losing the session between stages invalidates the flow.
- The wizard is reachable only through the `/` forward; there is no dedicated wizard path.
- `public/` must be writable for the image cache; project directories must be writable for installer permission normalization.
- Mailbox ingestion and outbound mail are unconfigured/disabled by default.
- Extensions live in `apps/`, which ships empty.
- No test suite, no CI workflow definitions, and no static-analysis configuration are present in the repository.
- The Docker image targets PHP 8.1 while the installation guide walks through PHP 8.2; the runtime PHP version therefore depends on the chosen installation path.

**Assumptions**
- The UVDesk bundles named in `config/bundles.php` supply the controllers behind the route names referenced in `security.yaml` (`helpdesk_member_handle_login`, `helpdesk_member_dashboard`, `helpdesk_member_handle_logout`, `helpdesk_customer_login`, `helpdesk_customer_logout`, `helpdesk_customer_ticket_collection`, `helpdesk_knowledgebase`) and the entities, repositories, and `UVDeskService` used by the skeleton. This is inferred from the imports and configuration in this repository; the bundle sources are not present here.
- `uvdesk.site_url` is expected to be set to the real deployment host before installation completes, since it is transmitted as the telemetry domain.
- The support-role identifiers `1`, `2`, `3` (member level) and `4` (customer level) used in the CLI duplicate check correspond to fixture-seeded role records.

**Documentation-versus-implementation discrepancies**
1. `.env.example` is a Laravel-style manifest (`APP_NAME`, `DB_CONNECTION`, `DB_HOST`, `MAIL_DRIVER`, `CACHE_DRIVER`, `QUEUE_DRIVER`, `APP_VERSION=1.0.8`) that does not match the Symfony `.env` actually consumed by the application (`APP_ENV`, `APP_SECRET`, `DATABASE_URL`, `MAILER_DSN`, `UV_SESSION_COOKIE_LIFETIME`). It documents variables the code never reads and omits the ones it does.
2. `config/services.yaml` declares `uvdesk.version: "v1.1.8"` while `.env.example` declares `APP_VERSION=1.0.8`; the wizard header renders the former.
3. The installation guide describes a manual Apache/Composer/PHP 8.2 setup, whereas the Dockerfile standardizes on PHP 8.1 with an embedded MySQL server — two divergent supported topologies.
4. `CHANGELOG-1.0.md` records a historical fix for "`/wizard/xhr/load/super-user` error 500", consistent with the endpoint's current defensive structure.
5. Deterministic repository summaries that report this project as JavaScript-only, or as having no routes, pages, or entry points, are contradicted by the PHP sources, the YAML route table, and the annotated `/` route documented above.

## 12. Traceability

### 12.1 Business Objectives

| Objective | Realized by |
|---|---|
| Make an open-source helpdesk installable by non-specialists | FR-01…FR-10, FR-13, FR-25 (UC-01, UC-02) |
| Provide a recoverable, scriptable installation path | FR-08, FR-11…FR-14 (UC-02, UC-03) |
| Assemble a complete support product from independently maintained components | FR-18, FR-20, FR-23, FR-24 (UC-08) |
| Establish a secure authorization model for agents, customers, and API clients | FR-09, FR-19 (§3.1, §4.4) |
| Serve an international community | FR-21 (UC-07) |
| Offer a zero-infrastructure evaluation environment | FR-22 (UC-06) |
| Maintain install visibility for the project maintainer | FR-15, FR-16 (UC-05) |

### 12.2 Business Requirements

| Business requirement | Functional requirements |
|---|---|
| BR-1 Detect and present the correct application state at the site root | FR-01 |
| BR-2 Guide an operator from bare code to running helpdesk without terminal access | FR-02…FR-10, FR-25 |
| BR-3 Support headless installation and post-install repair | FR-11…FR-14 |
| BR-4 Enforce an authorization boundary between agents, customers, and API consumers | FR-09, FR-19 |
| BR-5 Ship deterministic helpdesk defaults (locales, prefixes, uploads, ticket defaults, mail template) | FR-20, FR-21 |
| BR-6 Enable e-mail-based support intake as an opt-in capability | FR-23 |
| BR-7 Support third-party add-ons | FR-24 |
| BR-8 Provide a containerized evaluation deployment | FR-22 |
| BR-9 Report installation to the project maintainer without blocking installation | FR-15, FR-16 |
| BR-10 Suppress technical error detail in production | FR-17 |

### 12.3 Software Requirements

| Software requirement | Implementation locus |
|---|---|
| SR-1 State-based entry routing | `src/Controller/BaseController.php` |
| SR-2 Wizard rendering and client flow | `templates/installation-wizard/index.html.twig`, `public/scripts/wizard.js`, `public/css/wizard.css` |
| SR-3 Requirements evaluation endpoint | `ConfigureHelpdesk::evaluateSystemRequirements` |
| SR-4 Database verification and session capture | `ConfigureHelpdesk::verifyDatabaseCredentials`, `prepareSuperUserDetailsXHR`, `websiteConfigurationXHR` |
| SR-5 Configuration persistence | `ConfigureHelpdesk::updateConfigurationsXHR`, `src/Console/EnvironmentVariables.php` |
| SR-6 Schema lifecycle | `src/Console/Wizard/MigrateDatabase.php`, `ConfigureHelpdesk::migrateDatabaseSchemaXHR`, `populateDatabaseEntitiesXHR` |
| SR-7 Identity provisioning | `ConfigureHelpdesk::createDefaultSuperUserXHR`, `src/Console/Wizard/DefaultUser.php` |
| SR-8 Prefix persistence | `ConfigureHelpdesk::updateWebsiteConfigurationXHR` → `UVDeskService::updateWebsitePrefixes` |
| SR-9 Installation doctor | `src/Console/Wizard/ConfigureHelpdesk.php` |
| SR-10 Image cache and telemetry | `src/Controller/ImageCache/{ImageCacheController,ImageManager}.php`, `src/Service/UrlImageCacheService.php`, `ConfigureHelpdesk::addUserDetailsInTracker` |
| SR-11 Error presentation | `src/EventListener/ExceptionSubscriber.php`, `templates/errors/error.html.twig` |
| SR-12 Route contribution | `src/Routing/RoutingResource.php`, `config/routes.yaml`, `src/Resources/config/routes.yaml` |
| SR-13 Security and authorization model | `config/packages/security.yaml` |
| SR-14 Component assembly and defaults | `config/bundles.php`, `config/packages/{uvdesk,uvdesk_mailbox,uvdesk_extensions,services}.yaml`, `composer.json` |
| SR-15 Localization | `translations/messages.*.yml`, `config/packages/translation.yaml`, `app_locales` |
| SR-16 Container build and provisioning | `Dockerfile`, `.docker/bash/uvdesk-entrypoint.sh`, `.docker/config/apache2/*`, `.docker/config/php/php.ini` |

### 12.4 Test Coverage

**No automated tests exist in this repository.** The file inventory contains no `tests/` directory, no PHPUnit or Behat configuration, no CI workflow definitions under `.github/workflows/`, and no fixtures authored by the skeleton itself (fixtures are loaded from the core-framework dependency via `doctrine:fixtures:load`). `composer.json` declares an `App\Tests\ → tests/` dev autoload mapping and Flex dev requirements for `symfony/test-pack`, `debug-pack`, and `profiler-pack`, but no corresponding code is present. Consequently:

- All acceptance criteria in §10 must be verified manually or by exercising the installer end-to-end.
- The behavioral gaps noted in §4.3, §9.3, and §10.3 (silent 200 responses from the migration and fixture stages, the inverted schema-version branch in the CLI doctor, and the exception-swallowing entry router) are undetected by any automated check.
- Quality assurance for the assembled product is delegated to the upstream `uvdesk/*` packages, whose test suites are outside this repository.

## 13. References

**Application code**
- `src/Controller/BaseController.php`
- `src/Controller/ConfigureHelpdesk.php`
- `src/Controller/ImageCache/ImageCacheController.php`
- `src/Controller/ImageCache/ImageManager.php`
- `src/Service/UrlImageCacheService.php`
- `src/Console/EnvironmentVariables.php`
- `src/Console/Wizard/ConfigureHelpdesk.php`
- `src/Console/Wizard/DefaultUser.php`
- `src/Console/Wizard/MigrateDatabase.php`
- `src/EventListener/ExceptionSubscriber.php`
- `src/Routing/RoutingResource.php`
- `src/Resources/config/routes.yaml`

**Presentation and assets**
- `templates/installation-wizard/index.html.twig`
- `templates/errors/error.html.twig`
- `templates/mail.html.twig`
- `public/scripts/wizard.js`
- `public/css/wizard.css`, `public/css/reset.css`, `public/css/main.css`
- `public/index.php`, `public/.htaccess`, `public/favicon.ico`

**Configuration**
- `config/bundles.php`, `config/routes.yaml`, `config/services.yaml`
- `config/packages/uvdesk.yaml`, `uvdesk_mailbox.yaml`, `uvdesk_extensions.yaml`, `security.yaml`
- `config/packages/doctrine.yaml`, `framework.yaml`, `mailer.yaml`, `translation.yaml`, `twig.yaml`
- `.env`, `.env.example`

**Deployment**
- `Dockerfile`, `.dockerignore`
- `.docker/bash/uvdesk-entrypoint.sh`
- `.docker/config/apache2/{env,httpd.conf,vhost.conf}`, `.docker/config/php/php.ini`

**Localization**
- `translations/messages.{ar,da,de,en,es,fr,he,it,pl,pt_BR,tr,zh}.yml`

**Packaging and documentation**
- `composer.json`, `LICENSE.txt`
- `README.md`, `INSTALLATION GUIDE.md`
- `CHANGELOG-1.0.md`, `CHANGELOG-1.1.md`, `CHANGELOG-1.2.md`
- `.github/CONTRIBUTING.md`, `.github/SECURITY.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/FUNDING.yml`, `.github/ISSUE_TEMPLATE/{Bug_report,Feature_request,Support_question}.md`

**Reserved / empty extension points**
- `src/Entity/.gitignore`, `src/Migrations/.gitignore`, `src/Repository/.gitignore`, `apps/.gitignore`, `public/assets/.gitignore`, `public/attachments/.gitignore`, `translations/.gitignore`

**External services referenced by the implementation**
- `https://updates.uvdesk.com/api/updates` (installation telemetry)
- `https://updates.uvdesk.com/uvdesk-logo.png` (cached branding asset)
- `https://api.github.com/repos/uvdesk/recipes/contents/index.json` (Symfony Flex recipe endpoint)
- `ajax.googleapis.com`, `cdnjs.cloudflare.com` (wizard front-end libraries)
