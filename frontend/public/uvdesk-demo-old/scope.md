---
model: deepseek/deepseek-v4-flash-0731
---

# Scope Documentation — UVdesk Community Skeleton

## 1. Scope Summary

The repository is **UVdesk Community Skeleton** (`uvdesk/community-skeleton`), the open-source "community edition" distribution of **UVdesk**, a customer-support helpdesk / ticketing platform developed by the UVdesk team (Webkul). The repository is a Composer project skeleton (`"type": "project"`) that acts as the **installation, composition, and configuration layer** for the full UVdesk helpdesk product.

The defining scoping fact is that the repo does **not** implement the helpdesk product itself. The product behavior is delivered by six separately maintained UVdesk bundles required from Packagist — core framework, support center, mailbox component, automation bundle, extension framework, and API bundle — all registered in `config/bundles.php` and declared in `composer.json`. What this repository actually delivers and owns is:

- a **first-run installation wizard** (web UI + console commands) that configures a new instance against a MySQL server, creates the schema, loads fixtures, creates the super-admin account, and sets the member/customer URL prefixes;
- the **Symfony application shell** that wires the bundles together (routing, services, security, Doctrine, mailer, translation);
- **containerized deployment support** (Dockerfile, Apache/PHP runtime configuration);
- **localization catalogs** for the skeleton's own UI strings (notably the wizard);
- a small set of **in-repo runtime surfaces**: a root route that redirects a configured install to the product portals or dispatches an unconfigured install to the wizard, custom production error pages, and an image-proxy/cache endpoint for the UVdesk installation tracker; and
- **distribution and governance scaffolding** (Packagist metadata, changelogs, installation guide, issue/PR templates, security policy, contribution guide).

In short: this is the deployment and composition layer of the UVdesk helpdesk; the functional scope of the helpdesk itself (tickets, knowledge base, mailbox, automation, API) is delegated to external bundles that are runtime dependencies of the delivered system but outside this repository's code.

## 2. System Boundary

### 2.1 What belongs to the analyzed system (in-repo, verified)

| Area | In-repo artifacts |
|---|---|
| Web installer front end | `templates/installation-wizard/index.html.twig`, `public/scripts/wizard.js`, `public/css/wizard.css`, `public/css/reset.css` |
| Installer backend (XHR endpoints + session-staged install state) | `src/Controller/ConfigureHelpdesk.php`, routes in `src/Resources/config/routes.yaml` |
| Installer/ops console commands | `src/Console/EnvironmentVariables.php`, `src/Console/Wizard/ConfigureHelpdesk.php`, `src/Console/Wizard/DefaultUser.php`, `src/Console/Wizard/MigrateDatabase.php` |
| Root request dispatcher | `src/Controller/BaseController.php` (route `/`) |
| Error handling | `src/EventListener/ExceptionSubscriber.php`, `templates/errors/error.html.twig` |
| Tracker image proxy/cache | `src/Controller/ImageCache/ImageCacheController.php`, `src/Controller/ImageCache/ImageManager.php`, `src/Service/UrlImageCacheService.php`, route `/tracker/xhr/get/cacheImage` |
| Application shell configuration | `config/` (`bundles.php`, `routes.yaml`, `services.yaml`, `packages/*.yaml`), `src/Routing/RoutingResource.php` |
| Default email template | `templates/mail.html.twig` (referenced as default in `uvdesk.yaml`) |
| Localization | `translations/messages.{ar,da,de,en,es,fr,he,it,pl,pt_BR,tr,zh}.yml` |
| Containerized deployment | `Dockerfile`, `.docker/` (Apache configs, PHP ini, entrypoint script) |
| Distribution/governance docs | `README.md`, `INSTALLATION GUIDE.md`, `CHANGELOG-1.0/1.1/1.2.md`, `LICENSE.txt`, `.github/` |

The `src/Entity`, `src/Migrations`, `src/Repository`, `public/assets`, `public/attachments`, and `apps` directories exist only as empty, git-ignored placeholders intended to be populated by the bundles/operators at runtime; they contain no committed implementation.

### 2.2 What the delivered system additionally includes (out of repo, dependency-delivered)

At runtime the skeleton composes (via `config/bundles.php` and `composer.json`):

- **UVDesk Core Framework** (`Webkul\UVDesk\CoreFrameworkBundle`) — helpdesk domain APIs, entities (User, UserInstance, SupportRole, Website, referenced from `src/Controller/*.php`), member (agent/admin) panel security (`security.yaml` firewalls/roles).
- **Support Center Bundle** — the customer-facing knowledge base and ticket portal (customer firewall, `helpdesk_knowledgebase` route targets referenced in `BaseController.php`).
- **Mailbox Component** — IMAP/SMTP email-to-ticket and outbound mail configuration (`config/packages/uvdesk_mailbox.yaml`).
- **Automation Bundle** — workflow/prepared-response automation.
- **Extension Framework** — third-party package integration, extension directory `%kernel.project_dir%/apps` (`config/packages/uvdesk_extensions.yaml`).
- **API Bundle** — `/api` surface protected by the `uvdesk_api` firewall (`security.yaml` references `Webkul\UVDesk\ApiBundle\Providers\ApiCredentials` and an API guard).

These bundles are the product boundary of the *delivered system*; they are outside the *repository boundary* of this codebase.

## 3. Included Capabilities

### 3.1 First-run installation (web wizard)

Externally visible at the site root (`/`) via `BaseController::base()`, which forwards to `ConfigureHelpdesk::load()` when no super-admin/administrator users exist. The wizard (`public/scripts/wizard.js`, Backbone.js/Underscore/jQuery-based) walks the installer through:

1. **System requirements check** (`/wizard/xhr/check-requirements`): PHP version (requires ≥ 7.0; composer allows PHP `^7.2.5 || ^8.0`), required PHP extensions (`imap`, `mailparse`, `mysqli`), `max_execution_time ≥ 30`, write permission on the project `.env` and on `config/packages/uvdesk.yaml` and `uvdesk_mailbox.yaml` (the controller attempts `chmod 0666`), plus a non-blocking Redis extension notice.
2. **Database configuration** (`/wizard/xhr/verify-database-credentials`): validates MySQL server connectivity, verifies/creates the database, and stages credentials in the PHP session.
3. **Admin account setup** (`/wizard/xhr/intermediary/super-user`): collects name/email/password with client-side validation (name regex, email regex, password: ≥ 8 chars, ≥ 2 letters, ≥ 1 digit, ≥ 1 special character, no spaces), staged in session.
4. **Website prefix configuration** (`/wizard/xhr/website-configure`): sets the `member` and `customer` URL prefixes (alphanumeric only, mandatory, must differ).
5. **Executed installation sequence** (`/wizard/xhr/load/configurations`, `/load/migrations`, `/load/entities`, `/load/super-user`, `/load/website-configure`): writes `DATABASE_URL` into `.env`, runs schema migration, loads fixtures, creates the `ROLE_SUPER_ADMIN` user instance, and persists the prefixes via the core framework service.

### 3.2 First-run installation / operations (console)

- `uvdesk:configure-helpdesk` — scans the setup: verifies database credentials (interactive reconfiguration, database creation), runs Doctrine migrations and fixture loading, creates a super-admin account if none exists, and reports installation telemetry to the UVdesk tracker. It also `chmod 0775`s `.env`, `var/`, `config/`, `public/`, `migrations/`.
- `uvdesk_wizard:env:update` — rewrites environment variables in the project-root `.env` (dev environment only).
- `uvdesk_wizard:database:migrate` (hidden) — fresh-install path (`doctrine:schema:create` + `doctrine:fixtures:load`) versus upgrade path (migrations sync/version/diff/migrate).
- `uvdesk_wizard:defaults:create-user` (hidden) — programmatic user creation by role code (used by the CLI wizard and the web wizard's super-user step).

### 3.3 Post-installation request dispatch

`BaseController::base()` (route `/`) checks whether super-admin/administrator users exist; if so it redirects (301) to the support-center knowledge base (`helpdesk_knowledgebase`) or the member login (`helpdesk_member_handle_login`); otherwise it forwards to the installation wizard. This is the in-repo seam between the installer scope and the bundle-delivered product scope.

### 3.4 Production error pages

`ExceptionSubscriber` renders a unified Twig error page for 403, 404, and 500 responses in `prod` environment.

### 3.5 UVdesk installation tracker (image cache / telemetry)

- `GET /tracker/xhr/get/cacheImage` fetches the UVdesk tracker logo (`https://updates.uvdesk.com/uvdesk-logo.png`), caches it locally in `public/cache/images/` (1-week TTL) via `UrlImageCacheService`, and returns the local image URL as JSON — a privacy-preserving local copy of a remote asset.
- `ConfigureHelpdesk::addUserDetailsInTracker` POSTs installer name/email/domain to `https://updates.uvdesk.com/api/updates` at the end of installation (both console and web paths).

### 3.6 Localization

Twelve YAML message catalogs (Arabic, Danish, German, English, Spanish, French, Hebrew, Italian, Polish, Portuguese-BR, Turkish, Chinese) localize the skeleton's own strings; `uvdesk.yaml` declares `app_locales` as `en|fr|it|de|da|ar|es|tr|zh|pl|he|pt_BR` and the default `locale` is `en`.

### 3.7 Containerized deployment

The Dockerfile builds an Ubuntu-based image with PHP 8.1, Apache 2, MySQL server, PHP IMAP/Mailparse/mysqli extensions, Composer, and gosu; the entrypoint (`uvdesk-entrypoint.sh`) starts Apache/MySQL, provisions a database and user from `MYSQL_USER`/`MYSQL_PASSWORD`/`MYSQL_DATABASE`/`MYSQL_ROOT_PASSWORD` environment variables, and steps down to the non-root `uvdesk` user.

### 3.8 Distribution and governance

Packagist packaging with install instructions (`composer create-project uvdesk/community-skeleton`), a documented archive download path (`cdn.uvdesk.com`), changelogs for 1.0.x/1.1.x/1.2.x, a step-by-step install guide, security reporting policy, contribution workflow referencing the per-bundle issue trackers, and issue/PR templates.

## 4. Actors and Interacting Systems

| Actor / system | Interaction | Evidence basis |
|---|---|---|
| **System installer / operator** (human) | Runs the web wizard at the site root, or the `uvdesk:configure-helpdesk` CLI; supplies MySQL credentials, super-admin details, URL prefixes; later runs Composer/console maintenance commands | Wizard routes, console commands, README/INSTALLATION GUIDE |
| **Docker operator / provisioner** | Launches the container; supplies `MYSQL_*` environment variables for automatic DB provisioning | `Dockerfile`, `.docker/bash/uvdesk-entrypoint.sh` |
| **End customers** | Use the support-center portal (default `/customer` prefix) to submit/track tickets — runtime surface supplied by the Support Center Bundle | `security.yaml` customer firewall/access control; README login URLs |
| **Support agents and administrators** | Use the member panel (default `/member` prefix) to manage tickets — runtime surface supplied by Core Framework + Automation/Mailbox bundles | `security.yaml` back_support firewall; role hierarchy `ROLE_SUPER_ADMIN`/`ROLE_ADMIN`/`ROLE_AGENT` |
| **API consumers** | Call `/api` endpoints protected by the ApiBundle guard | `security.yaml` `uvdesk_api` firewall; `composer.json` `uvdesk/api-bundle` |
| **MySQL server** | Required external database service; the wizard verifies/creates the schema, Doctrine ORM persists domain data | `config/packages/doctrine.yaml` (`pdo_mysql`), wizard DB endpoints, Docker `mysql-server` |
| **Mail servers (IMAP/SMTP)** | Email-to-ticket ingestion and outbound notification after installation | `config/packages/uvdesk_mailbox.yaml` (template config), `config/packages/mailer.yaml` (`MAILER_DSN`) |
| **UVdesk tracker service** (`updates.uvdesk.com`) | Receives installation telemetry (name/email/domain) and provides the logo asset proxied/cached locally | `ConfigureHelpdesk::addUserDetailsInTracker`, `ImageCacheController` |
| **Public CDNs** | Google Hosted Libraries (jQuery 2.2.4) and cdnjs (Underscore, Backbone, backbone.validation) serve the wizard's runtime scripts | `templates/installation-wizard/index.html.twig` script tags |
| **Composer / Packagist ecosystem** | Distribution medium; Symfony Flex recipes sourced from the `uvdesk/recipes` endpoint during install | `composer.json` (`extra.symfony.endpoint`) |
| **Community platforms** (Gitter, forums, Open Collective, Twitter, YouTube, Facebook) | Support/awareness channels; links only in README, no code-level integration | README badges/links |

## 5. External Interfaces and Dependencies

### 5.1 HTTP routes implemented in this repository

All routes are declared in `src/Resources/config/routes.yaml` and registered through `src/Routing/RoutingResource`:

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Dispatch: configured install → product portal/login; else → wizard (`BaseController`) |
| POST | `/wizard/xhr/check-requirements` | System requirement checks (PHP version, extensions, execution time, file permissions, Redis notice) |
| POST | `/wizard/xhr/verify-database-credentials` | MySQL connectivity/database existence check; stages DB config in session |
| POST | `/wizard/xhr/intermediary/super-user` | Stages admin credentials in session |
| GET/POST | `/wizard/xhr/website-configure` | Read/stage member & customer URL prefixes |
| POST | `/wizard/xhr/load/configurations` | Writes `DATABASE_URL` to `.env` and (re)connects; may create the database |
| POST | `/wizard/xhr/load/migrations` | Runs schema create/migrations (`uvdesk_wizard:database:migrate`) |
| POST | `/wizard/xhr/load/entities` | Loads doctrine fixtures (`--append`) |
| POST | `/wizard/xhr/load/super-user` | Creates the `ROLE_SUPER_ADMIN` user instance |
| POST | `/wizard/xhr/load/website-configure` | Persists URL prefixes via the core framework service; sends tracker telemetry |
| GET | `/tracker/xhr/get/cacheImage` | Returns locally cached UVdesk tracker logo URL |

An additional `uvdesk`-typed root resource loader (`config/routes.yaml`) delegates route discovery for the composed bundles; their routes live in the external bundles.

### 5.2 CLI interfaces implemented in this repository

- `uvdesk:configure-helpdesk` (public, documented in README and INSTALLATION GUIDE).
- `uvdesk_wizard:env:update` (dev-only guard).
- `uvdesk_wizard:database:migrate` (hidden), `uvdesk_wizard:defaults:create-user` (hidden).

### 5.3 Outbound service calls

- `POST https://updates.uvdesk.com/api/updates` — installation/user telemetry (name, email, domain), sent from both install paths.
- `GET https://updates.uvdesk.com/uvdesk-logo.png` — fetched with a custom `Domain` header and cached locally (`public/cache/images/`, md5 key, 1-week TTL; requires `allow_url_fopen`-style fetching via `file_get_contents` and the Intervention Image driver).

### 5.4 Composer dependency boundary

Runtime platform requirements: PHP `^7.2.5 || ^8.0` (`composer.json`; README documents PHP 8.1 as the recommended requirement and the Docker image pins PHP 8.1; the install guide uses PHP 8.2), `ext-ctype`, `ext-iconv`; the wizard additionally requires `imap`, `mailparse`, `mysqli`. Bundle constraints: `uvdesk/core-framework ^1.1.7`, `uvdesk/support-center-bundle ^1.1.3`, `uvdesk/mailbox-component ^1.1.5`, `uvdesk/automation-bundle ^1.1.4`, `uvdesk/extension-framework ^1.1.2`, `uvdesk/api-bundle ^1.1.4`; supporting libraries include Symfony components (Flex-managed), `google/recaptcha`, `knplabs/knp-paginator-bundle`, and `intervention/image` + `intervention/imagecache`. Symfony version floor is `^5.4` with a `uvdesk/recipes` Flex endpoint; `minimum-stability: dev` with `prefer-stable: true`.

## 6. Constraints and Current Limitations

- **MySQL-only database support at installation.** Doctrine is pinned to `pdo_mysql` (`server_version: '5.7'`, `utf8mb4`/`utf8mb4_unicode_ci`); the wizard builds `mysql://` URLs and the Docker image bundles `mysql-server`. No other database drivers are wired in the skeleton. (The `.env.example` comment mentions SQLite only as a Doctrine generic example.)
- **Write access to project files at install time.** The wizard requires read/write on the project-root `.env` and on `config/packages/uvdesk.yaml` and `config/packages/uvdesk_mailbox.yaml` (the controller attempts `chmod 0666`; the CLI wizard `chmod 0775`s `.env`, `var/`, `config/`, `public/`, `migrations/`).
- **Runtime environment variables.** Effective Symfony-style variables: `APP_ENV`, `APP_SECRET`, `DATABASE_URL`, `MAILER_DSN`, `UV_SESSION_COOKIE_LIFETIME` (default 1440 s), plus Docker-only `MYSQL_USER`/`MYSQL_PASSWORD`/`MYSQL_DATABASE`/`MYSQL_ROOT_PASSWORD`. A committed `.env` additionally contains legacy Laravel-style variables (`APP_NAME`, `DB_CONNECTION`, `MAIL_DRIVER`, …) that do not match any code in this Symfony shell (see §9).
- **Required PHP extensions.** `imap`, `mailparse`, `mysqli` are enforced by the wizard's requirements check; `ctype`/`iconv` by composer.
- **Upload/request limits.** Configured defaults in `uvdesk.yaml`: `max_post_size` 8 MiB, `max_file_uploads` 20, `upload_max_filesize` 2 MiB (marked in source as intended to be parameterized via compilers).
- **Password policy.** CLI wizard enforces 8–32 characters; web wizard enforces ≥ 8 chars, ≥ 2 letters, ≥ 1 digit, ≥ 1 special character, no spaces.
- **URL prefix rules.** Member/customer prefixes are mandatory, alphanumeric-only, and must differ from each other.
- **Environment gate on config mutation.** `uvdesk_wizard:env:update` refuses to run outside the `dev` environment; error rendering is suppressed except in `prod`.
- **Session-based install state.** Wizard stages database credentials, admin details, and prefixes in the PHP session across XHR steps.
- **External CDN dependency for the wizard UI.** jQuery, Underscore, Backbone, and backbone.validation are loaded from Google/cdnjs; an air-gapped or CDN-blocked environment cannot render the wizard.
- **Tracked telemetry.** Both install paths transmit installer name, email, and instance domain to `updates.uvdesk.com` (documented in source as the "uvdesk tracker"); the logo proxy also requires outbound HTTPS to `updates.uvdesk.com`.
- **Version alignment.** `config/services.yaml` parameter `uvdesk.version: "v1.1.8"` matches changelog entry 1.1.8 (2025-09-19); the wizard header renders `Version {{ uvdesk_version }}`.
- **Extension directory.** Third-party extensions must be placed in `apps/` (`uvdesk_extensions.dir`), which is git-ignored and empty in this repo.
- **Docker runtime constraints.** PHP `memory_limit=1024M`; Apache configs under `.docker/config/apache2/`; non-root runtime user `uvdesk` via gosu; image derived from `ubuntu:latest` (not version-pinned).

## 7. Exclusions / Unsupported Areas

The following are **outside this repository's implementation** (delegated to Composer-installed bundles) and are therefore not analyzable from this code: the ticket lifecycle and domain model, knowledge-base/FAQ authoring, email-to-ticket ingestion, automation rule semantics, extension/plugin runtime, and the `/api` API surface. The repository only wires their configuration (routing resource types, firewalls, prefix parameters, mailbox/extension config templates).

Additional evidence-supported exclusions and gaps:

- **No test suite** exists in the repository (no `tests/` tree; `autoload-dev` references `App\Tests\` but no tests are committed; no CI workflows under `.github/`).
- **No composer.lock is committed**, so the exact resolved dependency versions of the bundles are not pinned in this repo (they are resolved at `composer install`/`create-project` time).
- **No Vagrant configuration** is present, although the README links to a Vagrant virtual-environment wiki page.
- **No S3/cloud storage or CDN configuration** is implemented in-repo for user uploads; the default upload manager is the core framework's `Localhost` manager (`uvdesk.yaml`), and the README CDN references (`cdn.uvdesk.com`) are distribution/branding assets only.
- **No webpack/build pipeline**: front-end assets are static files plus CDN-loaded libraries.
- **No PostgreSQL/other RDBMS support** in the skeleton's install path (MySQL-only; see §6).
- Framework bundles beyond those needed by the shell (e.g., `doctrine-migrations` configuration file) are not explicitly present under `config/packages/`; the migrations commands used by the wizard must be supplied through the dependency graph. This is an unverified wiring detail rather than a confirmed exclusion.

## 8. Scope Evidence

Key boundary claims and the repository artifacts that substantiate them:

| Claim | Evidence artifacts |
|---|---|
| Skeleton identity and composition role | `composer.json` (`name: uvdesk/community-skeleton`, `type: project`, `uvdesk/*` bundle constraints), `config/bundles.php` (six UVdesk bundle registrations), `.github/CONTRIBUTING.md` (per-bundle issue trackers and per-repository PRs), README (Packagist badges, "project skeleton", bundle descriptions) |
| Installer scope | `src/Controller/ConfigureHelpdesk.php` + `src/Resources/config/routes.yaml` (wizard XHR endpoints and requirement checks), `src/Console/Wizard/*` and `src/Console/EnvironmentVariables.php` (commands), `templates/installation-wizard/index.html.twig` + `public/scripts/wizard.js` + `public/css/wizard.css` (wizard UI), `INSTALLATION GUIDE.md` and README installation sections |
| Post-install dispatch seam | `src/Controller/BaseController.php` (route `/` redirects to `helpdesk_knowledgebase`/`helpdesk_member_handle_login` or forwards to the wizard) |
| Tracker integration | `ConfigureHelpdesk::addUserDetailsInTracker` (`https://updates.uvdesk.com/api/updates`), `ImageCacheController`/`UrlImageCacheService`/`ImageManager` (logo cache, `/tracker/xhr/get/cacheImage`) |
| Product portal/security wiring (delegated) | `config/packages/security.yaml` (member/customer/API firewalls, role hierarchy, access-control entries referencing bundle-provided login routes), `config/routes.yaml` (`uvdesk` and `uvdesk_extensions` resource loaders), `config/packages/uvdesk_mailbox.yaml`, `config/packages/uvdesk_extensions.yaml` |
| Runtime constraints | `config/packages/doctrine.yaml` (MySQL driver), `config/packages/mailer.yaml` (`MAILER_DSN`), `config/packages/uvdesk.yaml` (locales, prefixes, upload limits, site URL), `.env.example` (effective Symfony env vars), Dockerfile + `.docker/` (PHP 8.1, Apache, MySQL, entrypoint provisioning) |
| Localization | 12 translation catalogs in `translations/`, `app_locales` parameter |
| Version/state | `config/services.yaml` (`uvdesk.version: v1.1.8`), CHANGELOG-1.1.md (1.1.8, 2025-09-19), CHANGELOG-1.2.md (translation fixes) |

## 9. Scope Uncertainties and Unknowns

- **Bundle behavior is not verifiable from this repo.** The functional scope of tickets, knowledge base, mailbox, automation, extensions, and API is implemented in external bundles; claims about those capabilities here rest on configuration, route names, and naming conventions (e.g., `helpdesk_knowledgebase`, `helpdesk_member_handle_login`, `ROLE_SUPER_ADMIN`), not on in-repo code.
- **Committed `.env` vs `.env.example` contradiction.** The tracked `.env` contains Laravel-style variables (`APP_NAME`, `DB_CONNECTION=mysql`, `MAIL_DRIVER=smtp`, `BROADCAST_DRIVER`, etc.) while `.env.example` and all code use Symfony-style variables (`APP_ENV`, `DATABASE_URL`, `MAILER_DSN`). The Laravel-style file appears to be a vestigial artifact; the resulting state of a fresh `composer create-project` install (which of these files Flex preserves or rewrites) cannot be determined from the repository, and neither can the behavior of `uvdesk_wizard:env:update` against a `.env` lacking a `DATABASE_URL` line (the command rewrites existing keys in place).
- **Exact resolved dependency versions** are unknown because no `composer.lock` is committed; only compatibility constraints are visible.
- **Telemetry details** (payload schema accepted by `updates.uvdesk.com`, retention, opt-out) are not documented in-repo beyond the code sending name/email/domain; tracker endpoint behavior is unverified.
- **Wizard UI runtime dependencies on public CDNs** mean the observed behavior of the wizard depends on third-party availability that this repo cannot guarantee.
- **Organizational/product ownership boundaries** (which team maintains which bundle, commercial vs. community edition commitments, AWS Marketplace AMI described in README) are external to the repository and not verifiable here.
- **The image-cache feature's runtime requirements** (GD or Imagick driver for Intervention Image, outbound URL fetching) are partially documented in code; Docker does not explicitly install `php-gd`, so the cache endpoint's behavior inside the shipped container is unverified.
- **No tests** exist to confirm the wizard's edge-case behavior (e.g., Redis extension present, `.env` permission failures, interrupted installations).

## 10. Recommendations

Recommendations are grounded in the current implementation and are intended for maintainers and adopters of this repository.

1. **Resolve the `.env`/`.env.example` contradiction explicitly.** The committed Laravel-style `.env` will mislead installers and can corrupt install behavior (wizard mutations operate on Symfony-style keys). Decide whether `.env` should be removed from tracking (with `.env.example`/recipes as the sole source) or rewritten to Symfony-style defaults, and verify `uvdesk_wizard:env:update` appends missing keys rather than only rewriting existing ones.
2. **Pin the container base image and runtime versions.** The Dockerfile uses `ubuntu:latest` and installs PHP 8.1 while composer permits `^7.2.5 || ^8.0` and the install guide demonstrates PHP 8.2; pin base image and PHP/MySQL versions so the shipped runtime and the documented requirements cannot drift apart.
3. **Verify the tracker/telemetry dependency before relying on the image-cache feature.** The wizard and logo proxy depend on outbound access to `updates.uvdesk.com`; if the image cache endpoint is a user-visible feature (it is reachable as a public GET route), document its behavior, add failure handling when `allow_url_fopen`/GD are unavailable, and confirm it needs no authentication in production.
4. **Make the wizard's runtime CDN dependency explicit or vendor the assets.** The wizard page loads jQuery/Underscore/Backbone from Google/cdnjs; for offline or restricted deployments, vendoring these scripts under `public/` would remove an external runtime dependency that currently can break first-run installation.
5. **Add a minimal smoke test.** No tests exist, yet the wizard mutates files and executes irreversible schema operations; even a small test suite covering `uvdesk_wizard:database:migrate` fresh-install branching, env-rewrite behavior, and `BaseController` dispatch logic would materially reduce regression risk in the installation path.
6. **Document scope boundaries in the README.** The README's feature list describes bundle-delivered capabilities that are not implemented in this repo; a sentence distinguishing "skeleton (installer/composition)" from "bundles (product)" would set correct expectations for adopters triaging issues between `uvdesk/community-skeleton` and the five component repositories referenced in `CONTRIBUTING.md`.
