---
model: z-ai/glm-5.3
---

# Low-Level Software Design Description

## 1. Document Title

**Low-Level Design Description — UVdesk Community Helpdesk Skeleton (`uvdesk/community-skeleton`)**

Detailed internal design of the composer-based application skeleton for the UVdesk open-source helpdesk: the concrete modules, classes, functions, interfaces, data structures, state transitions, and interactions through which the skeleton composes, installs, configures, and serves the UVdesk platform.

## 2. Design Scope and Overview

### 2.1 Purpose

This document describes how the high-level design of the community skeleton is concretely implemented: which classes, commands, routes, templates, configuration files, and data structures realize each logical component, how the installation workflows execute end-to-end, and where the skeleton's responsibilities end and the external UVdesk bundles' responsibilities begin.

### 2.2 Scope

The repository is a **PHP 7.2+/8.x, Symfony Framework (5.4 line) application skeleton**. Its own code (11 PHP classes under `src/`, plus routing, configuration, templates, translations, and one substantial JavaScript client) implements:

1. **First-run installation** — an interactive web wizard and an equivalent console workflow that verify system requirements, validate and persist database credentials, create the schema, load fixtures, provision a super-administrator, and configure website URL prefixes.
2. **Installation-state routing** — a root controller that decides whether to serve the installed helpdesk (external bundles) or the installation wizard.
3. **Error presentation** — a kernel exception subscriber that renders branded error pages in production.
4. **A tracker image-cache subsystem** — a small service cluster that fetches and locally caches the UVdesk logo served from the vendor update endpoint.
5. **Composition wiring** — bundle registration, service autowiring, custom route-loader integration, environment configuration, and localization catalogs.

All helpdesk business behavior (ticket lifecycle, agent workflows, mailbox email processing, automation, support-center portal, API) is delegated to six external bundles (`config/bundles.php`), pulled in by Composer:

- `Webkul\UVDesk\CoreFrameworkBundle` (core-framework ^1.1.7)
- `Webkul\UVDesk\SupportCenterBundle` (support-center-bundle ^1.1.3)
- `Webkul\UVDesk\MailboxBundle` (mailbox-component ^1.1.5)
- `Webkul\UVDesk\AutomationBundle` (automation-bundle ^1.1.4)
- `Webkul\UVDesk\ExtensionFrameworkBundle` (extension-framework ^1.1.2)
- `Webkul\UVDesk\ApiBundle` (api-bundle ^1.1.4) — a sixth bundle present in `composer.json` and `config/bundles.php` beyond the five listed in the contributing guide.

Out of scope for this document: the internals of those bundles, and the untracked `vendor/` tree.

### 2.3 Design Objectives

Evident implementation objectives:

- Provide a guided, self-service installation path for non-expert operators (web wizard with progressive validation and human-readable remediation hints).
- Provide an equivalent, scriptable console path (`uvdesk:configure-helpdesk`) usable on headless servers and as a repair/diagnostic tool.
- Make the installed system fully configured by files the skeleton itself owns (`.env`, `config/packages/uvdesk*.yaml`) so the external bundles need no local code.
- Keep the skeleton's own surface small: no local entities, no local migrations, no local repositories (those directories exist only as `.gitignore` placeholders).

### 2.4 Design Constraints

- **Runtime**: PHP `^7.2.5 || ^8.0`; Symfony components constrained to `^5.4` via `extra.symfony.require`; runtime bootstrapped through `symfony/runtime`. The Docker image uses PHP 8.1 + Apache mod_php + MySQL server on Ubuntu.
- **Database**: MySQL only — the wizard hardcodes the DSN template `mysql://[user]:[password]@[host]:[port]`, Doctrine is configured for `pdo_mysql` (server version 5.7 default), and required extensions include `mysqli` and `imap`/`mailparse` (mail-channel support).
- **Writable filesystem at install time**: the wizard requires (and attempts `chmod 0666` on) `.env`, `config/packages/uvdesk.yaml`, and `config/packages/uvdesk_mailbox.yaml`, because installation *writes back into the repository's own configuration files*.
- **Session-staged multi-request flow**: wizard state crosses HTTP requests only through `$_SESSION` keys.
- **Front-end stack**: jQuery 2.2.4, Underscore 1.9.1, Backbone 1.3.3, Backbone.Validation 0.7.1 — all loaded from public CDNs at runtime.
- **Icon/image processing**: `intervention/image ^2.4` and `intervention/imagecache`.

### 2.5 Relationship to High-Level Design

| High-level subsystem | Concrete implementation in this repository |
|---|---|
| Application shell / kernel | `public/index.php` (runtime front controller), `config/services.yaml` (App service registration), `config/bundles.php` (bundle set), `config/packages/*` |
| Routing | `config/routes.yaml` (delegates to custom `uvdesk`/`uvdesk_extensions` loaders), `src/Routing/RoutingResource.php`, `src/Resources/config/routes.yaml`, annotation route on `src/Controller/BaseController.php` |
| Installation / first-run setup | `src/Controller/ConfigureHelpdesk.php`, `src/Console/Wizard/*` (4 commands), `src/Console/EnvironmentVariables.php`, `public/scripts/wizard.js`, `templates/installation-wizard/index.html.twig`, `public/css/wizard.css` |
| Installation-state gate | `src/Controller/BaseController.php` |
| Error presentation | `src/EventListener/ExceptionSubscriber.php`, `templates/errors/error.html.twig` |
| Tracker / image cache | `src/Controller/ImageCache/ImageCacheController.php`, `src/Service/UrlImageCacheService.php`, `src/Controller/ImageCache/ImageManager.php` |
| Email channel configuration | `config/packages/uvdesk_mailbox.yaml`, `config/packages/mailer.yaml`, `MAILER_DSN` in `.env` |
| Extension subsystem | `config/packages/uvdesk_extensions.yaml` (`uvdesk_extensions.dir: %kernel.project_dir%/apps`, empty `apps/` workspace) |
| Persistence configuration | `config/packages/doctrine.yaml` (no local entities/migrations — empty placeholder dirs) |
| Security configuration | `config/packages/security.yaml` (firewalls, role hierarchy, access control) |
| Localization | `translations/messages.*.yml` — 12 catalogs exactly matching the `app_locales` parameter (`en\|fr\|it\|de\|da\|ar\|es\|tr\|zh\|pl\|he\|pt_BR`) |
| Runtime / deployment | `Dockerfile`, `.docker/config/*`, `.docker/bash/uvdesk-entrypoint.sh` |

```mermaid
flowchart LR
    subgraph APP["Application skeleton (this repository)"]
        direction TB
        INDEX["public/index.php<br/>(runtime front controller)"]
        BASE["src/Controller/BaseController<br/>route / (base_route)"]
        WIZC["src/Controller/ConfigureHelpdesk<br/>wizard XHR API"]
        WIZJS["public/scripts/wizard.js<br/>Backbone wizard client"]
        TPL["templates/installation-wizard"]
        RR["src/Routing/RoutingResource"]
        EXC["src/EventListener/ExceptionSubscriber"]
        IMGC["src/Controller/ImageCache/ImageCacheController"]
        IMGS["src/Service/UrlImageCacheService"]
        IMGM["src/Controller/ImageCache/ImageManager"]
        CONW["src/Console/Wizard (4 commands)"]
        ENVV["src/Console/EnvironmentVariables"]
        SESSION[("PHP session:<br/>DB_CONFIG / USER_DETAILS / PREFIXES_DETAILS")]
        ENVFILE[(".env")]
        CACHE[("public/cache/images")]
    end
    subgraph BUNDLES["External Webkul UVdesk bundles"]
        CORE["CoreFrameworkBundle<br/>UVDeskService, User/UserInstance/<br/>SupportRole/Website entities, route loaders"]
        SC["SupportCenterBundle"]
        MAIL["MailboxBundle"]
        AUTO["AutomationBundle"]
        EXTB["ExtensionFrameworkBundle"]
        APIB["ApiBundle"]
    end
    DB[("MySQL")]
    TRACKER["updates.uvdesk.com<br/>/api/updates, /uvdesk-logo.png"]

    INDEX --> KERNEL["App Kernel class<br/>(referenced, not present in tracked tree)"]
    KERNEL --> BUNDLES
    BASE --> WIZC
    WIZJS --> WIZC
    WIZC --> SESSION
    WIZC --> DB
    WIZC --> ENVV
    ENVV --> ENVFILE
    WIZC --> CORE
    CONW --> DB
    CONW --> ENVV
    RR --> CORE
    WIZC --> TRACKER
    IMGC --> IMGS --> IMGM --> TRACKER
    IMGS --> CACHE
    EXC --> TPL
```

## 3. Detailed Component Design

### 3.1 HTTP Composition Root and Service Wiring

**Identification.** `public/index.php`, `config/services.yaml`, `config/bundles.php`, `composer.json`.

**Responsibilities.** Boot the Symfony application, register the six UVdesk bundles plus the Symfony/D stack, and register every class under `src/` as an autowired, autoconfigured service.

**Internal structure and processing logic.**
- `public/index.php` requires `dirname(__DIR__).'/vendor/autoload_runtime.php'` and returns a closure that constructs `new Kernel($context['APP_ENV'], (bool) $context['APP_DEBUG'])` — the standard Symfony Runtime pattern. Notably, **no `src/Kernel.php` exists in the tracked tree**; the class is referenced by the front controller and explicitly excluded from service scanning in `config/services.yaml` (`exclude: '../src/{DependencyInjection,Entity,Migrations,Tests,Kernel.php}'`), but its source is not committed in this revision. The bundle set such a kernel must register is, however, fully specified by `config/bundles.php`.
- `config/bundles.php` returns all six `Webkul\UVDesk\*Bundle` classes with `['all' => true]`.
- `config/services.yaml` defines parameters `locale: 'en'` and `uvdesk.version: "v1.1.8"`, applies `_defaults: {autowire: true, autoconfigure: true, public: false}`, registers the `App\` resource over `../src/*` (excluding `Kernel.php` and the empty `Entity/Migrations` dirs), and separately tags `App\Controller\` with `controller.service_arguments` so controller action arguments (e.g. `KernelInterface`, `UserPasswordEncoderInterface`, `UVDeskService`) are injectable.
- `composer.json` directly requires only `php`, `ext-ctype`, `ext-iconv`, and `symfony/flex`; the full dependency set (Doctrine ORM pack, security, twig, mailer, swiftmailer, `intervention/image`, the six `uvdesk/*` packages) is declared in `flex-require`/`flex-require-dev` and materialized by Symfony Flex recipes at `composer create-project` time, pinned to the Symfony `^5.4` line. `scripts.auto-scripts` runs `cache:clear` and `assets:install %PUBLIC_DIR%` on every install/update.

**Dependencies.** `vendor/autoload_runtime.php` (untracked), the six bundles, the Flex recipe endpoint list (`uvdesk/recipes`).

**Error handling.** Composition failures surface as framework boot failures before any skeleton code executes; no local boot-time error handling exists.

### 3.2 Routing Layer

**Identification.** `config/routes.yaml`, `src/Routing/RoutingResource.php`, `src/Resources/config/routes.yaml`, annotation route on `BaseController`.

**Responsibilities.** Contribute the skeleton's own routes (wizard XHR endpoints, tracker image endpoint, root route) to the application and delegate all remaining route discovery to the external bundles.

**Internal structure.** `config/routes.yaml` contains exactly two entries — `uvdesk: { resource: ., type: uvdesk }` and `uvdesk_extensions: { resource: ., type: uvdesk_extensions }` — i.e., the skeleton installs two *custom route loaders* provided by the external bundles and hands route discovery to them. `App\Routing\RoutingResource` implements `Webkul\UVDesk\CoreFrameworkBundle\Definition\RoutingResourceInterface` and returns `src/Resources/config/routes.yaml` (`YAML_RESOURCE`), which is how the core-framework loader discovers the skeleton's route file. Route registration therefore flows: bundle loader → `RoutingResource` → `src/Resources/config/routes.yaml`. The root route is contributed as a `@Route("/", name="base_route")` annotation on `BaseController::base()` and is picked up by the same loader chain. In total the skeleton defines 11 named routes (10 in YAML, 1 annotation).

**Interfaces.** `RoutingResourceInterface::getResourcePath()` / `getResourceType()` — the only interface the skeleton itself implements against an external bundle.

**Error handling.** None local; unknown routes fall through to the framework and are handled by `ExceptionSubscriber` (§3.6).

### 3.3 Installation-State Gate (`BaseController`)

**Identification.** `src/Controller/BaseController.php`, route `base_route` (`/`).

**Responsibilities.** Single decision point for "is this helpdesk installed?" — route the visitor to the installed product or to the wizard.

**Processing logic.**
1. Query `SupportRole` by code `ROLE_SUPER_ADMIN` and `ROLE_ADMIN` (entities from core-framework). If neither exists → not installed.
2. If roles exist, query `UserInstance` by each support role. If no owners/administrators exist → not installed.
3. If installed: if `UVDeskSupportCenterBundle` is present in `kernel->getBundles()` **and** a `Website` with code `knowledgebase` exists, redirect (301) to `helpdesk_knowledgebase`; otherwise, if a `Website` with code `helpdesk` exists, redirect to `helpdesk_member_handle_login` (both target routes live in external bundles).
4. Otherwise (including any exception — e.g. the database not being reachable yet): `return $this->forward(ConfigureHelpdesk::class . "::load")` — an internal sub-request that renders the wizard.

**Design significance.** Installation detection is a *data heuristic* (roles + admin user instances + website rows), not a persisted flag; and the `try/catch` deliberately swallows all exceptions so that a broken database degrades to "please install" rather than a 500 error. This also means a database outage on an installed system re-presents the wizard page.

### 3.4 Web Installation Wizard

**Identification.** `src/Controller/ConfigureHelpdesk.php` (backend), `public/scripts/wizard.js` (client), `templates/installation-wizard/index.html.twig` (view), routes under `/wizard/xhr/*` in `src/Resources/config/routes.yaml`.

**Responsibilities.** Interactive, multi-step, browser-driven installation: system-requirements verification, database credential capture/validation, super-admin capture, website prefix configuration, and a final install phase that provisions `.env`, schema, fixtures, the admin account, and prefixes.

**Internal structure.**

*Backend* — `App\Controller\ConfigureHelpdesk extends AbstractController`, with constants:

| Constant | Value / role |
|---|---|
| `DB_URL_TEMPLATE` | `mysql://[user]:[password]@[host]:[port]` (placeholder-substituted DSN) |
| `DB_ENV_PATH_TEMPLATE`, `DB_ENV_PATH_PARAM_TEMPLATE` | declared but never referenced (dead constants) |
| `DEFAULT_JSON_HEADERS` | `Content-Type: application/json` |
| `$requiredExtensions` | `imap`, `mailparse`, `mysqli` |
| `$requiredConfigfiles` | `uvdesk`, `uvdesk_mailbox` |

Eleven public actions map 1:1 to routes (§4.3). The class also imports `Symfony\Component\Yaml\Yaml`, which is unused.

*Client* — `wizard.js` is a Backbone application (one `Backbone.View`/`Backbone.Model` pair per step) driven by Underscore templates embedded in the Twig page:

| Model/View pair | Defaults | Validation | Completion side effect |
|---|---|---|---|
| `UVDeskCommunitySystemRequirementsModel/View` | six checks: php-version, php-extensions, php-maximum-execution, php-envFile-permission, php-configFiles-permission, redis-status | server-side results aggregated by `evaluateOverallRequirements()` (all must pass) | enables/disables the wizard's next button |
| `UVDeskCommunityDatabaseConfigurationModel/View` | `serverName: 127.0.0.1`, `serverPort: 3306`, `username: root`, `createDatabase: 1` | mandatory serverName/username/password/database | POSTs to `verify-database-credentials` |
| `UVDeskCommunityAccountConfigurationModel/View` | user name/email/password/confirm | name regex `^[A-Za-z][A-Za-z]*[\sA-Za-z]*$`, RFC-style email regex, password regex `^(?=(.*[a-zA-Z].*){2,})(?=.*\d)(?=.*[^\w\s]|.*_)[^\s]{8,}$` (min 8 chars, ≥2 letters, 1 digit, 1 special, no spaces) | POSTs to `intermediary/super-user` |
| `UVDeskCommunityWebsiteConfigurationModel/View` | `member_panel_url: "member"`, `customer_panel_url: "customer"` | mandatory, prefixes must differ, alphanumeric-only `^[a-z0-9A-Z]*$`; `getDefaultAttributes()` GETs current prefixes to pre-fill | POSTs to `website-configure` |

`getDefaultAttributes()` — the installation's only pre-existing code symbol — is a `Promise` that fetches the currently persisted prefixes (`GET ./wizard/xhr/website-configure`) and rewrites the model defaults before rendering; on failure it disables the next step.

`UVDeskCommunityInstallSetupView` orchestrates the final install phase as one async sequence of `await $.post(...)` calls with per-step UI templates and a five-node progress checklist (Welcome → System Requirements → Database Configuration → Admin Details → Installation).

**Dependencies.** Doctrine DBAL/ORM (`DriverManager`, `EntityManager`, `Setup`), Symfony Console `Application` (in-process), `UserPasswordEncoderInterface`, `UVDeskService` (core-framework), `App\Console\Wizard\ConfigureHelpdesk::addUserDetailsInTracker()` (static), PHP session, `.env` file.

**Processing logic (backend actions).**

- `load()` renders `installation-wizard/index.html.twig` (the Backbone container plus embedded templates; displays `uvdesk_version`).
- `evaluateSystemRequirements()` switches on the `specification` POST parameter and probes the live runtime: PHP ≥ 7.0.0; the three required extensions; `max_execution_time >= 30`; writability of `.env` (attempting `chmod 0666` first); writability of `config/packages/uvdesk.yaml` and `config/packages/uvdesk_mailbox.yaml` (also `chmod 0666`); and a special `redis-status` branch that returns an instructional JSON payload when the `redis` extension is loaded (guiding users to the Redis host configuration referenced from a GitHub issue). Unknown specifications return HTTP 404.
- `verifyDatabaseCredentials()` builds a DSN from POSTed `serverName/serverPort/username/password` (+ optional `?serverVersion=`), creates an ad-hoc `DriverManager` connection and throws away a standalone `EntityManager` configured against `src/Entity`, connects, checks `listDatabases()` for the requested database (unless `createDatabase` is set), and stages the full credential set into `$_SESSION['DB_CONFIG']`.
- `prepareSuperUserDetailsXHR()` stages `name/email/password` into `$_SESSION['USER_DETAILS']`.
- `websiteConfigurationXHR()` — GET returns `UVDeskService::getCurrentWebsitePrefixes()` plus `status: true`; POST stages `member-prefix`/`customer-prefix` into `$_SESSION['PREFIXES_DETAILS']`. This is the only wizard route without a `methods:` constraint (accepts both).
- `updateConfigurationsXHR()` (install step 1) — re-reads `DB_CONFIG` from the session, reconnects, creates the database via the schema manager if absent and requested, appends the database name to the DSN, then runs `uvdesk_wizard:env:update DATABASE_URL <url>` **through an in-process Symfony Console `Application`** (`ArrayInput`/`NullOutput`), persisting the credentials to `.env`.
- `migrateDatabaseSchemaXHR()` (step 2) runs `uvdesk_wizard:database:migrate` in-process (→ §3.5 `MigrateDatabase`).
- `populateDatabaseEntitiesXHR()` (step 3) runs `doctrine:fixtures:load --append` in-process (fixtures themselves are defined in the external bundles).
- `createDefaultSuperUserXHR()` (step 4) — looks up `SupportRole` `ROLE_SUPER_ADMIN` and any active `UserInstance` holding it; only when none exists does it create/update the account: existing `User` by email is reused (promoting its instance's role if different), otherwise a new `User` is created (name split on first space into first/last name, password encoded by `UserPasswordEncoderInterface`, `isEnabled = true`), persisted and flushed, followed by a separate `UserInstance` (`source: 'website'`, `isActive: true`, `isVerified: true`) persist + flush.
- `updateWebsiteConfigurationXHR()` (step 5) calls `UVDeskService::updateWebsitePrefixes(member, customer)` (core-framework persists the prefixes into the UVdesk configuration) and then `Helpdesk::addUserDetailsInTracker()` with `{name, email, domain: uvdesk.site_url}`.

**State / lifecycle.** The wizard is a session-staged state machine; see §6.3.

**Error / exception handling.** Every external-facing failure is a JSON body (`{"status": false, "message": ...}`) with HTTP 200 — the client inspects `status`, not the HTTP code, except for `.fail()` handlers keyed on 500. Database connection failures during verification return "Failed to establish a connection with database server."; a missing database returns "The requested database was not found."; `updateConfigurationsXHR` returns `{"success": false}` with HTTP 500 if the env-update command fails. The client surfaces each failure as an inline `wizard-form-notice` or a 404/500 title/description pair from its `ERRORS` map.

### 3.5 Console Installation Tooling

**Identification.** Four commands under `src/Console/`:

| Class | Command name | Visibility |
|---|---|---|
| `App\Console\Wizard\ConfigureHelpdesk` | `uvdesk:configure-helpdesk` | public |
| `App\Console\Wizard\MigrateDatabase` | `uvdesk_wizard:database:migrate` | hidden |
| `App\Console\Wizard\DefaultUser` | `uvdesk_wizard:defaults:create-user` | hidden |
| `App\Console\EnvironmentVariables` | `uvdesk_wizard:env:update` | public (dev-guarded) |

**`EnvironmentVariables` (`.env` writer).** Arguments `name`, `value`. `initialize()` reads `.env` and parses it with `symfony/dotenv` into a map, overlaying the new value (key uppercased). `execute()` **refuses to run outside the `dev` environment** (throws an exception with code 500), then rewrites the file line-by-line: every non-comment line containing `=` whose key exists in the updated map is replaced with `KEY=value`; the result is re-joined with newlines and written only if it differs. This preserves all unrelated lines and comments. This command is the single mutation point through which both web and console installation persist credentials.

**`MigrateDatabase` (schema provisioning).** Validates the Doctrine connection (connecting, catching `DBALException`); resolves the schema manager with a DBAL 2/3 compatibility branch (`createSchemaManager()` vs `getSchemaManager()`). Decision algorithm: **if the database has no tables → fresh install** (`doctrine:schema:create`, then `doctrine:fixtures:load --no-interaction --quiet`); **otherwise → migration flow** (`doctrine:migrations:sync-metadata-storage`, record all versions via `doctrine:migrations:version --add --all`, `doctrine:migrations:diff` + `status` to derive the latest version, and `doctrine:migrations:migrate` only if current ≠ latest). All sub-commands are executed **in-process** via `$this->getApplication()->find($name)` with a non-interactive `ArrayInput` — in contrast to the sibling command below.

**`DefaultUser` (user factory).** Arguments `role name email password`; supports an interactive mode (email validated via `filter_var`, password prompted hidden with 8–32 length rule and confirmation) and a `--no-interaction` mode (arguments validated, exit code 2 on insufficiency). Execution: resolves the `SupportRole` by code, reuses an existing `User` by email or creates one, then determines whether the user already holds an account at the requested level using hard-coded role IDs (IDs 1–3 treated as member-level — an existing member-level instance blocks creation; ID 4 treated as customer level). If no conflicting account exists, persists `User` and `UserInstance` (source `website`, active, verified) in two flushes; returns 1 if the account already exists.

**`Console\Wizard\ConfigureHelpdesk` (diagnostic/repair command).** `uvdesk:configure-helpdesk` — "Scans through your helpdesk setup to check for any mis-configurations." `initialize()` chmods `.env`, `var/`, `config/`, `public/`, `migrations/` to 0775. `execute()` runs three checks:

1. **Database connectivity** — parses `DATABASE_URL` out of `.env` (via `Dotenv` + manual string splitting of user:password@host:port/database), connects through a standalone `EntityManager` (`pdo_mysql`), and — if unreachable — enters an interactive re-configuration loop (ANSI cursor manipulation for redraw; hidden password entry; database creation on request), persisting new credentials by shelling out `php bin/console uvdesk_wizard:env:update DATABASE_URL <url>` through a Symfony `Process` **subprocess**.
2. **Schema currency** — captures the current migration version, then runs `doctrine:migrations:version --add --all`, `:diff`, `:status`, and reads `doctrine:migrations:latest` (all as `Process` subprocesses); if versions differ, interactively offers migration (`doctrine:migrations:migrate --no-interaction`, 900 s timeout) plus fixtures (`doctrine:fixtures:load --append`, 120 s timeout).
3. **Super-admin existence** — queries **raw PDO** against `uv_support_role`, `uv_user_instance`, and `uv_user` (bypassing the ORM entirely); if no super admin exists, interactively collects email/name/password (email re-validated, password confirmed) and delegates creation to `uvdesk_wizard:defaults:create-user ROLE_SUPER_ADMIN … --no-interaction` as a subprocess.

Finally it reports the resolved admin identity to `addUserDetailsInTracker()` (same tracker call as the web path).

**`addUserDetailsInTracker` (static).** cURL POST of `{"domain", "email", "name", "country_code": null}` to `https://updates.uvdesk.com/api/updates` with JSON accept/content-type headers. All exceptions are caught and silently discarded — telemetry must never break installation.

**Error handling.** Console exit codes: 0 success, 1 soft failure (connection refused by user, migration declined, subprocess failure), 2 argument errors in `DefaultUser`. `refreshDatabaseConnection()` documents an array return but returns `false` on connection exception — an internal type inconsistency the interactive loop tolerates.

### 3.6 Error Presentation (`ExceptionSubscriber`)

**Identification.** `src/EventListener/ExceptionSubscriber.php`, `templates/errors/error.html.twig`.

**Responsibilities.** Convert kernel exceptions into branded error pages.

**Internal structure.** `EventSubscriberInterface` subscribing to `KernelEvents::EXCEPTION` at priority 10. Constructor takes `Twig\Environment`, `ContainerInterface`, and an optional `UserInterface` (user token injection). `onKernelException()`:

- Returns immediately unless `kernel.environment == 'prod'` (dev keeps the Symfony error pages).
- 403-coded exceptions: if a security token with a non-anonymous user exists, renders `errors/error.html.twig` (code 403, "Access Forbidden"); if the user is anonymous, no response is set and the framework default applies.
- 404 (`NotFoundHttpException` or code 404): renders the 404 page.
- Everything else: renders the 500 page ("Something has gone wrong on the server").

A source comment acknowledges an unfinished concern: response content type (html/xml/json) is not yet taken into account.

### 3.7 Tracker Image-Cache Subsystem

**Identification.** `src/Controller/ImageCache/ImageCacheController.php`, `src/Service/UrlImageCacheService.php`, `src/Controller/ImageCache/ImageManager.php`, route `uvdesk_community_tracker_cache_image` (`GET /tracker/xhr/get/cacheImage`).

**Responsibilities.** Locally cache the UVdesk logo (served from `https://updates.uvdesk.com/uvdesk-logo.png`) and expose its public URL, so the deployed helpdesk can reference the logo without a remote round-trip.

**Internal structure and processing logic.**
- `ImageCacheController::getCachedImage()` ignores request input entirely — it always fetches the constant `UVDESK_LOGO` — computes `siteUrl` from `getSchemeAndHttpHost() + getBasePath()`, delegates to `showImage()`, then converts the served file's real path into a public URL (by stripping `kernel.project_dir . '/public'`) and returns it as a bare JSON-encoded string (not an object).
- `UrlImageCacheService` (constructor-injected into the controller) computes the cache key `md5($url)`, targets `<project>/public/cache/images/<md5>.png`, creates the directory (0775, recursive) on demand, and applies a **7-day TTL** (`filemtime` comparison). On expiry it unlinks and re-fetches. It constructs its `ImageManager` collaborator directly with `new ImageManager($container)` rather than through dependency injection.
- `ImageManager extends Intervention\Image\ImageManager` (v2). Its `make()` override accepts `{imageUrl, siteUrl}`; after resolving the driver class from the inherited base configuration (`Intervention\Image\{Driver}\Driver`), it validates both URLs and calls `initFromUrl()` — a `file_get_contents` GET over a custom stream context (HTTP/1.1, `Accept-language: en`, a `Domain:` header carrying the site URL, and a spoofed desktop Chrome user-agent), feeding the binary to the Intervention decoder. Failure throws `NotReadableException`. Non-URL input falls back to the base `driver->init()` behavior.

**State.** The only persistent state is the file cache: `public/cache/images/<md5(url)>.png` with mtime-based expiry.

**Error handling.** `NotReadableException` on unreadable images; no higher-level catch — failures propagate to `ExceptionSubscriber`.

### 3.8 Configuration, Localization, and Presentation Assets

**Identification.** `config/packages/uvdesk.yaml`, `uvdesk_mailbox.yaml`, `uvdesk_extensions.yaml`, `doctrine.yaml`, `security.yaml`, `mailer.yaml`, `framework.yaml`, `translation.yaml`, `twig.yaml`; `translations/`; `templates/`; `apps/`; `.env`.

**Responsibilities.** These files *are* the skeleton's integration surface with the external bundles and the install-time write targets of the wizard.

**Key structures.**
- `uvdesk.yaml` — `app_locales` (the 12 supported locales, matching the translation catalogs exactly); default profile-image asset paths; `uvdesk_site_path.member_prefix: member` and `uvdesk_site_path.knowledgebase_customer_prefix: customer` (the two parameters the wizard's prefix step ultimately rewrites, and which `security.yaml` firewall/access-control patterns are parameterized by); upload constraints (`max_post_size` 8 MB, `max_file_uploads` 20, `upload_max_filesize` 2 MB); `uvdesk.site_url` (default `localhost:8000`); upload manager service (`Webkul\UVDesk\CoreFrameworkBundle\FileSystem\UploadManagers\Localhost`); default ticket type/status/priority; default email template `mail.html.twig` (present at `templates/mail.html.twig`).
- `uvdesk_mailbox.yaml` — `emails: ~` and `mailboxes: ~`, with commented templates describing the full mailbox contract (IMAP fetch settings, SMTP send settings, reply delimiter, strict mode, `disable_outbound_emails`) that operators fill in post-install.
- `uvdesk_extensions.yaml` — `uvdesk_extensions.dir: '%kernel.project_dir%/apps'`; the `apps/` directory is an empty, gitignored workspace where the extension framework materializes installed extensions.
- `doctrine.yaml` — `pdo_mysql`, server version `5.7`, `utf8mb4` with `utf8mb4_unicode_ci` default table options, `url: '%env(DATABASE_URL)%'`, and a DBAL init-command (option 1002) that strips `ONLY_FULL_GROUP_BY` from the MySQL `sql_mode`. The ORM mapping declares `App\Entity` over `src/Entity` — a directory that is **empty** in the tracked tree (entities actually arrive from the bundles via `auto_mapping`).
- `translations/messages.{en,fr,it,de,da,ar,es,tr,zh,pl,he,pt_BR}.yml` — 12 catalogs.

## 4. Detailed Interface Design

### 4.1 Internal Interfaces

| Interface | Provider → Consumer | Contract |
|---|---|---|
| `RoutingResourceInterface` (`getResourcePath`, `getResourceType`) | core-framework → `App\Routing\RoutingResource` | locates `src/Resources/config/routes.yaml` |
| `UVDeskService::getCurrentWebsitePrefixes()` / `updateWebsitePrefixes(member, customer)` | core-framework → `ConfigureHelpdesk` controller | read/persist the member and knowledgebase URL prefixes (implementation external; persistence target is the UVdesk configuration the wizard pre-flights for writability) |
| `uvdesk_wizard:env:update <name> <value>` | `EnvironmentVariables` → web wizard (in-process `Application::run`) and console wizard (`Process` subprocess) | line-preserving `.env` rewrite |
| `uvdesk_wizard:database:migrate` | `MigrateDatabase` → web wizard step 2 | fresh-install vs migration decision (§3.5) |
| `uvdesk_wizard:defaults:create-user <role> <name> <email> <password> [--no-interaction]` | `DefaultUser` → console wizard step 3 | user + user-instance creation |
| `$_SESSION['DB_CONFIG' \| 'USER_DETAILS' \| 'PREFIXES_DETAILS']` | wizard XHR actions → later XHR actions | staged installation state (§6.3) |
| `user.provider`, `Webkul\UVDesk\ApiBundle\Providers\ApiCredentials` | external services referenced by `security.yaml` | security user providers |

### 4.2 External Interfaces

- **MySQL server** — DSN `mysql://user:password@host:port/database[?serverVersion=…]`, accessed via Doctrine DBAL/ORM (wizard, fixtures, migrations) and raw PDO (console check 3).
- **UVdesk updates endpoint** — `POST https://updates.uvdesk.com/api/updates` (JSON: domain, email, name, country_code) and `GET https://updates.uvdesk.com/uvdesk-logo.png` (image fetch with custom headers).
- **Mail transport** — `MAILER_DSN` (`.env`, default `null://null`) plus the `uvdesk_mailbox.yaml` IMAP/SMTP contract.
- **CDN assets** — jQuery/Underscore/Backbone/Backbone.Validation for the wizard UI.

### 4.3 API Operations (skeleton-defined HTTP endpoints)

| Route name | Path | Method | Controller action |
|---|---|---|---|
| `uvdesk_community_installation_wizard_check_requirements` | `/wizard/xhr/check-requirements` | POST | `evaluateSystemRequirements` |
| `uvdesk_community_installation_wizard_verify_database_credentials` | `/wizard/xhr/verify-database-credentials` | POST | `verifyDatabaseCredentials` |
| `uvdesk_community_installation_wizard_store_super_user_credentials` | `/wizard/xhr/intermediary/super-user` | POST | `prepareSuperUserDetailsXHR` |
| `uvdesk_community_installation_wizard_store_website_configuration` | `/wizard/xhr/website-configure` | any | `websiteConfigurationXHR` (GET read / POST stage) |
| `uvdesk_community_installation_wizard_update_configurations_xhr` | `/wizard/xhr/load/configurations` | POST | `updateConfigurationsXHR` |
| `uvdesk_community_installation_wizard_migrate_database_schema_xhr` | `/wizard/xhr/load/migrations` | POST | `migrateDatabaseSchemaXHR` |
| `uvdesk_community_installation_wizard_populate_database_entities_xhr` | `/wizard/xhr/load/entities` | POST | `populateDatabaseEntitiesXHR` |
| `uvdesk_community_installation_wizard_create_default_super_user_xhr` | `/wizard/xhr/load/super-user` | POST | `createDefaultSuperUserXHR` |
| `uvdesk_community_installation_wizard_update_website_configuration` | `/wizard/xhr/load/website-configure` | POST | `updateWebsiteConfigurationXHR` |
| `uvdesk_community_tracker_cache_image` | `/tracker/xhr/get/cacheImage` | GET | `ImageCacheController::getCachedImage` |
| `base_route` | `/` | any | `BaseController::base` (annotation) |

### 4.4 Parameters and Data Types

| Operation | Request parameters | Response |
|---|---|---|
| check-requirements | `specification` ∈ {php-version, php-extensions, php-maximum-execution, php-envfile-permission, php-configfiles-permission, redis-status} | JSON: `{status, version, message[, description]}` or `{extensions:[{name:bool}]}` / `{configfiles:[{name:bool}]}`; unknown → HTTP 404, empty body |
| verify-database-credentials | `serverName`, `serverPort`, `serverVersion?`, `username`, `password`, `database`, `createDatabase` (0/1) | `{status: true}` \| `{status: false, message}` |
| intermediary/super-user | `name`, `email`, `password` | `{status: true}` |
| website-configure (POST) | `member-prefix`, `customer-prefix` | `{status: true}` |
| website-configure (GET) | — | prefix collection + `{status: true}` or `{status: false}` |
| load/configurations | — (reads `DB_CONFIG` session) | `{success: true}` \| `{success: false}` (500) \| `{status: false, message}` |
| load/migrations, load/entities, load/super-user | — (session / database) | `[]` (empty JSON array), HTTP 200 |
| load/website-configure | — (reads `PREFIXES_DETAILS`, `USER_DETAILS`) | JSON URL collection (member login / knowledgebase URLs) |
| tracker cache image | — (fixed constant URL) | JSON-encoded URL string |

All requests are form-encoded POSTs; responses use `json_encode` (mostly plain `Response` with JSON headers, occasionally `JsonResponse`).

### 4.5 Preconditions / Postconditions

- `updateConfigurationsXHR`, `updateWebsiteConfigurationXHR`, `createDefaultSuperUserXHR` **require prior session state** (`DB_CONFIG`, `USER_DETAILS`, `PREFIXES_DETAILS`) written by earlier steps; there is no server-side guard that the earlier steps ran — the sequencing contract lives entirely in `wizard.js`.
- `createDefaultSuperUserXHR` requires fixtures to have created the `SupportRole` rows (it queries `ROLE_SUPER_ADMIN` and returns an empty 200 if the lookup yields nothing usable).
- Postconditions: `load/configurations` ⇒ `.env` contains a working `DATABASE_URL`; `load/migrations` ⇒ schema exists; `load/entities` ⇒ seed data present; `load/super-user` ⇒ an active super-admin `UserInstance` exists; `load/website-configure` ⇒ prefixes persisted and the tracker notified. After all five, `BaseController` classifies the system as installed.

### 4.6 Error Conditions

Summarized in §3.4/§3.5: JSON `status:false` payloads with operator-facing remediation text (including external blog links for permission and execution-time issues), HTTP 404 for unknown specification values, HTTP 500 for env-update failure, silent swallowing of tracker errors, and console exit codes 0/1/2.

### 4.7 Protocols / Serialization

HTTP/1.1 form-encoded POST + JSON responses; MySQL DSN strings; `.env` line format (`KEY=value`, `#` comments); JSON payload to the tracker API; Intervention binary image decoding over a customized HTTP stream context.

## 5. Detailed Data Design

### 5.1 Data Structures

- **Session staging structures** (the wizard's only cross-request data):
  - `DB_CONFIG`: `{host, port, version, username, password, database, createDatabase}` (values are raw POST strings; `createDatabase` coerced to bool).
  - `USER_DETAILS`: `{name, email, password}` (password held in plaintext in the session until user creation).
  - `PREFIXES_DETAILS`: `{member, customer}`.
- **Client models** mirror these as Backbone model attributes with defaults (§3.4 table).
- **`.env`** as an ordered line list; the rewrite algorithm treats it as a keyed map plus untouched lines.

### 5.2 Classes / Records / Types

| Class | Kind | Notable members |
|---|---|---|
| `Controller\ConfigureHelpdesk` | controller | 11 actions; DSN template + requirement tables constants |
| `Controller\BaseController` | controller | `base()` installation gate |
| `Controller\ImageCache\ImageCacheController` | controller | `UVDESK_LOGO` constant; `getCachedImage`, `showImage` |
| `Controller\ImageCache\ImageManager` | service class (extends `Intervention\Image\ImageManager`) | `make`, `initFromUrl`, `createDriver` |
| `Service\UrlImageCacheService` | service | `getCachedImage`, `isCacheExpired`, `cacheImage` |
| `Console\Wizard\ConfigureHelpdesk` | console command | `execute`, `refreshDatabaseConnection`, `createDatabase`, `getUpdatedDatabaseCredentials`, `getLatestMigrationVersion`, `askInteractiveQuestion`, static `addUserDetailsInTracker` |
| `Console\Wizard\DefaultUser` | console command | `interact`, `execute`, three `prompt*Interactively` helpers |
| `Console\Wizard\MigrateDatabase` | console command | `execute`, `versionMigrations`, `compareMigrations`, `migrateDatabaseToLatestVersion`, `runCommand`, `isDatabaseConfigurationValid` |
| `Console\EnvironmentVariables` | console command | `initialize` (parse), `execute` (guarded rewrite) |
| `Routing\RoutingResource` | static resource locator | `getResourcePath`, `getResourceType` |
| `EventListener\ExceptionSubscriber` | event subscriber | `onKernelException` |

### 5.3 Database Structures

The skeleton defines **no entities, no migrations, and no repositories** (`src/Entity`, `src/Migrations`, `src/Repository` each contain only `.gitignore`). All persistence metadata is imported from the external bundles through Doctrine `auto_mapping`. The skeleton's code nonetheless binds directly to four core-framework entity types — `User`, `UserInstance`, `SupportRole`, `Website` — and, in the console wizard, to three physical tables by name: `uv_support_role` (column `code`), `uv_user_instance` (column `supportRole_id`), `uv_user` (columns `id`, `first_name`, `last_name`, `email` implied by usage).

### 5.4 Relationships

`User` 1—1..* `UserInstance` (an instance carries `source`, `isActive`, `isVerified`, and exactly one `SupportRole`); `SupportRole` 1—* `UserInstance`; `Website` rows keyed by code (`helpdesk`, `knowledgebase`) drive the post-install redirects. Role semantics: `ROLE_SUPER_ADMIN` > `ROLE_ADMIN` > `ROLE_AGENT` (hierarchy in `security.yaml`), plus `ROLE_CUSTOMER`; `DefaultUser` additionally hard-codes numeric role IDs 1–3 (member levels) and 4 (customer).

### 5.5 Validation Rules

| Layer | Rules |
|---|---|
| Server (runtime probes) | PHP ≥ 7.0.0; `imap`/`mailparse`/`mysqli` loaded; `max_execution_time ≥ 30`; `.env` and the two `uvdesk*.yaml` files writable |
| Server (wizard data) | database presence in `listDatabases()` unless `createDatabase`; super-admin email uniqueness by reuse-or-create logic; `createDefaultSuperUserXHR` idempotence via existing-instance check |
| Client (wizard.js regexes) | name, email, password (≥8 chars, ≥2 letters, 1 digit, 1 special, no spaces), prefix equality and `[a-z0-9A-Z]` |
| Console (`DefaultUser`) | email `FILTER_SANITIZE_EMAIL` + `FILTER_VALIDATE_EMAIL`; password 8–32 chars, hidden input, confirmation |
| Doctrine | `utf8mb4` charset/collation on all tables; `sql_mode` without `ONLY_FULL_GROUP_BY` |

There is a deliberate asymmetry: the rich validation lives in the browser; the server-side wizard endpoints perform only the checks listed above.

### 5.6 Persistence / Caching

- **`.env`** — the authoritative runtime configuration store, mutated only through `uvdesk_wizard:env:update` (write-if-changed).
- **`public/cache/images/<md5(url)>.png`** — 7-day-TTL file cache (§3.7).
- **PHP session** — install-time staging only.
- **No application-level caching** is configured in the skeleton itself.

### 5.7 Data Lifecycle

Installation-time data follows the pipeline: browser input → client validation → XHR POST → `$_SESSION` → (during the install phase) `.env` write, DDL/fixture execution, `User`/`UserInstance` rows, prefix persistence → session becomes irrelevant once installed (the gate no longer consults it). The tracker image cache cycles fetch → 7-day validity → delete → re-fetch. The mailbox configuration remains intentionally unpopulated (`~`) until an operator edits it post-install.

## 6. Detailed Behavioral Design

### 6.1 Algorithms

- **`.env` rewrite** (`EnvironmentVariables`): parse → overlay one key → rebuild file by mapping each non-comment `KEY=…` line through the updated map → write only on change. Comment lines, blank lines, and unknown keys are preserved verbatim; only `dev` environment permitted.
- **Fresh-vs-migrated database decision** (`MigrateDatabase`): empty table set ⇒ `schema:create` + fixtures; else sync migration metadata, mark all known versions, diff, and migrate only when the recorded version differs from the latest.
- **Installation detection** (`BaseController`): presence of admin-level support roles AND user instances holding them AND the expected `Website` rows; any exception ⇒ treat as uninstalled.
- **Idempotent super-user creation**: check for an existing active `ROLE_SUPER_ADMIN` instance first; reuse-by-email; role promotion instead of duplication; two separate flushes.
- **Cache expiry**: `time() - filemtime(path) > 604800` ⇒ evict and re-fetch.
- **Console interactive UX** (`Console\Wizard\ConfigureHelpdesk`): ANSI escape constants (`\033[H`, `\033[K`, `\033[2J`, `\033[1A`) drive cursor-home/line-clear/cursor-up redraws around a do/while retry loop for database credentials and validated input loops for email/password.

### 6.2 Processing Sequences

```mermaid
sequenceDiagram
    participant B as Browser (wizard.js)
    participant C as ConfigureHelpdesk controller
    participant S as PHP session
    participant K as Console Application (in-process)
    participant F as .env file
    participant D as MySQL (Doctrine)
    participant U as UVDeskService (core-framework)
    participant T as updates.uvdesk.com

    Note over B,C: Interactive steps
    B->>C: POST /wizard/xhr/check-requirements (x6, parallel)
    C-->>B: JSON runtime/permission status
    B->>C: POST /wizard/xhr/verify-database-credentials
    C->>D: DriverManager connect + listDatabases
    C->>S: store DB_CONFIG
    C-->>B: {"status": true}
    B->>C: POST /wizard/xhr/intermediary/super-user
    C->>S: store USER_DETAILS
    B->>C: POST /wizard/xhr/website-configure
    C->>S: store PREFIXES_DETAILS

    Note over B,T: Install phase (sequential awaits in wizard.js)
    B->>C: POST /wizard/xhr/load/configurations
    C->>S: read DB_CONFIG
    C->>D: connect; create database if requested
    C->>K: run uvdesk_wizard:env:update DATABASE_URL <dsn>
    K->>F: line-based rewrite
    C-->>B: {"success": true}
    B->>C: POST /wizard/xhr/load/migrations
    C->>K: run uvdesk_wizard:database:migrate
    K->>D: schema:create+fixtures OR migrations sync/diff/migrate
    B->>C: POST /wizard/xhr/load/entities
    C->>K: run doctrine:fixtures:load --append
    B->>C: POST /wizard/xhr/load/super-user
    C->>D: find/create User + UserInstance (ROLE_SUPER_ADMIN)
    B->>C: POST /wizard/xhr/load/website-configure
    C->>U: updateWebsitePrefixes(member, customer)
    C->>T: cURL POST tracker {domain, email, name}
    C-->>B: JSON member/knowledgebase URLs
```

### 6.3 State Machines

```mermaid
stateDiagram-v2
    [*] --> NotConfigured: composer create-project
    NotConfigured --> WizardPresented: GET / — BaseController finds no admin roles/instances, forwards to wizard
    WizardPresented --> RequirementsVerified: six check-requirements probes pass
    RequirementsVerified --> DatabaseStaged: verify-database-credentials → DB_CONFIG
    DatabaseStaged --> SuperUserStaged: intermediary/super-user → USER_DETAILS
    SuperUserStaged --> PrefixesStaged: website-configure → PREFIXES_DETAILS
    PrefixesStaged --> Installing: install button
    Installing --> Configured: env update → migrate → fixtures → super-user → prefixes (+tracker)
    Configured --> WizardPresented: admin roles/instances or Website rows missing, or DB unreachable
    Configured --> [*]: BaseController redirects to helpdesk/knowledgebase
    NotConfigured --> RepairMode: php bin/console uvdesk:configure-helpdesk
    RepairMode --> Configured: interactive checks and fixes
```

The "installed" state is not a persisted flag: it is continuously re-derived from database contents, so deleting the admin `UserInstance` rows (or losing database connectivity) returns the system to the wizard.

### 6.4 Concurrency / Synchronization

- The install phase is strictly sequential client-side (`await` per XHR), because each step depends on the previous step's effects (`.env` before migrations; schema before fixtures; fixtures before super-user).
- Two invocation styles coexist for console commands: **in-process** (`Application::run` with `ArrayInput`/`NullOutput`, used by the web wizard) and **subprocess** (`Process(["php","bin/console", …])`, used by `uvdesk:configure-helpdesk`), which re-boot the kernel per command.
- No locking exists: two concurrent wizard runs against the same host would race on `.env`, schema creation, and fixture loading. The design assumes a single operator during first-run setup.

### 6.5 Transactions

No explicit transactions are used anywhere in the skeleton. `User` and `UserInstance` creation performs two independent `persist`/`flush` cycles; a failure between them would leave an orphaned `User` row without an instance (recoverable by re-running the step, which reuses the user by email). Database creation and migration run under Doctrine's own command semantics.

### 6.6 Failure and Recovery Behavior

- Every wizard step has a visible failure surface (client error bar/inline notices; JSON `status:false`).
- `uvdesk:configure-helpdesk` is the designated **repair tool**: it re-validates connectivity, schema currency, and admin existence, offering interactive fixes for each.
- `ExceptionSubscriber` converts unexpected production failures into 403/404/500 pages.
- `BaseController` degrades any database failure to the wizard (recovery-by-reinstallation).
- Tracker telemetry failures are silently ignored so they can never affect installation.

## 7. Detailed Security Design

### 7.1 Authentication

Defined declaratively in `config/packages/security.yaml` for the *installed* system: `form_login` firewalls for the member back panel (pattern `/%uvdesk_site_path.member_prefix%/`, login/logout/remember-me with `%kernel.secret%`, 7-day `REMEMBERME` cookie) and the customer front panel (pattern `/`, login/logout); an `uvdesk_api` firewall (`^/api`, guard authenticator `Webkul\UVDesk\ApiBundle\Security\Guards\APIGuard`); a `dev` firewall disabling security for profiler/assets. User providers are the external services `user.provider` and `ApiCredentials`. Password encoding for the core-framework `User` entity is `auto`. **The wizard endpoints themselves are unauthenticated** — they exist precisely before any users exist; they fall under the catch-all customer firewall, which is anonymous.

### 7.2 Authorization

Role hierarchy `ROLE_SUPER_ADMIN` ⊃ `ROLE_ADMIN` ⊃ `ROLE_AGENT`, plus `ROLE_CUSTOMER`; access-control rules are parameterized by the same `uvdesk_site_path.*` prefix parameters the wizard configures, covering login/create-account/forgot-password exceptions, the mailbox listener path, customer read-only ticket access, and the member/customer panel defaults.

### 7.3 Input Validation

Client-side regex validation (§5.5) is the primary gate for wizard input; server-side validation is limited to database existence checks, email filtering in the console path, and command-argument checks in `DefaultUser`. The wizard XHR endpoints do not re-validate name/email/password strength, and none of them carry CSRF protection (acceptable only within the pre-install window; see §10).

### 7.4 Secrets / Credential Handling

- Database credentials travel: browser → POST body → `$_SESSION` (plaintext, including the super-user password) → DSN → `.env` (plaintext, per Doctrine convention). The wizard even instructs operators to make `.env` world-writable (0666) during install.
- `APP_SECRET` ships as the placeholder `YOUR_APP_SECRET`; `.env` is a tracked file with placeholder credentials (`db_user:db_password@127.0.0.1:3306/db_name`).
- `uvdesk_wizard:env:update` refuses to run outside the `dev` environment — the guard that prevents using the credential-rewriting path in production.

### 7.5 Data Protection

The tracker beacon transmits the administrator's name, email, and site domain to `updates.uvdesk.com` at install completion (both web and console paths). The image cache identifies the installation to the remote endpoint through `Domain` and user-agent headers. No encryption-at-rest concerns exist locally beyond `.env` file permissions; upload constraints (`uvdesk.yaml`) bound attachment sizes.

### 7.6 Audit / Security Logging

No audit or security logging is implemented in the skeleton; the only observability is the install-time tracker beacon and standard framework logging (Monolog via Flex).

## 8. Detailed Operational Design

### 8.1 Configuration

- **`.env`** (tracked, with placeholder values): `APP_ENV=dev`, `APP_SECRET`, `DATABASE_URL`, `UV_SESSION_COOKIE_LIFETIME=1440`, `MAILER_DSN=null://null`. A `.env.example` exists but describes a **Laravel-style** variable set (`APP_KEY`, `DB_CONNECTION`, `MAIL_DRIVER`, …) that does not match the Symfony `.env` actually consumed — it is not a functional template for this application (§10).
- **`config/packages/uvdesk.yaml`** is the UVdesk platform contract (site URL, prefixes, upload manager, upload constraints, defaults) and, together with `uvdesk_mailbox.yaml`, is the wizard's declared write target.
- **`config/packages/uvdesk_extensions.yaml`** points the extension framework at `apps/`.
- Configuration-dependent behavior: `APP_ENV` gates `ExceptionSubscriber` (prod only) and `uvdesk_wizard:env:update` (dev only); `APP_DEBUG` is passed to the kernel; `uvdesk_site_path.*` parameters reshape both routing and security; the presence of the Redis extension adds an advisory branch; `kernel.project_dir` anchors every filesystem path.

### 8.2 Logging

None implemented in skeleton code (all output is either HTTP JSON, console text, or rendered templates).

### 8.3 Monitoring

Install-time telemetry only (`addUserDetailsInTracker`); no health checks or metrics in the skeleton.

### 8.4 Resource Management

- Image cache directory auto-creation (0775) under `public/cache/images`; upload size limits from `uvdesk.yaml`.
- The Dockerfile creates a non-root `uvdesk` user, installs PHP 8.1 with `imap`/`mailparse`/`mysql`/`curl` extensions plus Apache and MySQL server, sets 775 permissions on `var/`, `config/`, `public/`, `migrations/`, and `.env` for the web user, and runs `composer install`, `composer dump-autoload --optimize`, and a best-effort `cache:clear --env=prod` at image build. Container entrypoint is `.docker/bash/uvdesk-entrypoint.sh` (with `gosu` for privilege step-down; script contents not part of this analysis).

### 8.5 Startup / Shutdown

Request startup: web server → `public/index.php` → runtime closure → kernel → router (custom loaders) → controller. Console startup: `bin/console` → command discovery via `autoconfigure` (all four `src/Console` classes are auto-registered as commands through the `App\` service resource). Composer hooks (`cache:clear`, `assets:install`) run on every dependency install/update.

### 8.6 Recovery

`uvdesk:configure-helpdesk` (interactive re-configuration of credentials, schema, and admin), wizard re-entry via the root route, and the swallow-and-degrade behavior of `BaseController` constitute the recovery model.

## 9. Traceability

### 9.1 Requirements to Components

| Capability | Implementing components |
|---|---|
| Guided web installation | `ConfigureHelpdesk` controller, 9 wizard routes, `wizard.js`, wizard Twig template, session staging |
| Console installation / repair | `Console\Wizard\ConfigureHelpdesk`, `DefaultUser`, `MigrateDatabase`, `EnvironmentVariables` |
| System requirement verification | `evaluateSystemRequirements` + client aggregation model |
| Credential persistence | `EnvironmentVariables` command + `.env` |
| Database provisioning | `MigrateDatabase` (web), migration subprocess flow (console) |
| Super-admin provisioning | `createDefaultSuperUserXHR` (web), `DefaultUser` (console) |
| Website prefix configuration | `websiteConfigurationXHR`/`updateWebsiteConfigurationXHR` + `UVDeskService` (external) |
| Installed/uninstalled routing | `BaseController` |
| Production error pages | `ExceptionSubscriber` + `templates/errors/error.html.twig` |
| Logo caching / tracker support | Image-cache subsystem (3 classes) |
| Platform composition | `bundles.php`, `services.yaml`, `routes.yaml`, `uvdesk*.yaml`, translations |

### 9.2 Components to Interfaces

| Component | Exposed interface | Consumers |
|---|---|---|
| `ConfigureHelpdesk` controller | 10 HTTP XHR routes (§4.3) | `wizard.js` |
| `BaseController` | `base_route` (`/`) | end users / `RoutingResource`-loaded routing |
| `RoutingResource` | `RoutingResourceInterface` | core-framework route loader |
| Console commands | 4 named commands | web wizard (in-process), console wizard (subprocess), operators |
| `UrlImageCacheService` / `ImageCacheController` | `GET /tracker/xhr/get/cacheImage` | helpdesk front end (logo URL) |
| `ExceptionSubscriber` | `KernelEvents::EXCEPTION` subscription | Symfony event dispatcher |
| `.env` / `uvdesk*.yaml` | file contracts | Doctrine, mailer, security, all bundles |

### 9.3 Design to Test Cases

No tests are present: `composer.json` declares an `App\Tests\` autoload-dev mapping, but no `tests/` directory, test class, or PHPUnit configuration is tracked in this revision. Design-to-test traceability is therefore empty; the wizard's client-side validation and the console commands' interactive flows are the only executable verification paths shipped.

## 10. Design Decisions and Open Issues

**Observed design decisions (with consequences).**

1. **The skeleton writes its own configuration.** Installation mutates `.env` and the UVdesk YAML files in place — hence the writability pre-flight, the `chmod 0666` attempts, and the Docker image's 775 permission grants. This keeps the skeleton stateless (no install flag file) but couples installation to filesystem permissions.
2. **Derived installation state instead of persisted state.** "Installed" is inferred from database contents on every request to `/`, making the gate self-healing but also making a database outage indistinguishable from "not installed".
3. **Duplicated dual install paths.** The web wizard (in-process command invocation) and the console wizard (subprocess invocation, raw PDO, ANSI-driven UX) implement overlapping logic with divergent mechanics — e.g., DBAL 2/3 compatibility is handled in `MigrateDatabase` but not in the console wizard's own schema-manager calls. The shared pieces are the `.env` update command and `DefaultUser`.
4. **Client-trusted sequencing and validation.** All cross-step ordering and rich input validation live in the browser; server endpoints rely on session state existing and re-check little.
5. **Two-flush, non-transactional user creation** in both provisioning paths.
6. **Silent telemetry** — tracker calls can never fail an installation.
7. **Ad-hoc persistence connections in the wizard** (standalone `DriverManager`/`EntityManager` against the empty `src/Entity`), because the kernel's configured connection still points at the *old* `DATABASE_URL` until `.env` is rewritten.

**Open issues / irregularities observed in this revision.**

- **`App\Kernel` is referenced but not tracked.** `public/index.php` instantiates it and `config/services.yaml` excludes it from service registration, yet no `src/Kernel.php` exists in the repository tree. The composition contract is complete (`config/bundles.php`), but the kernel class itself is not part of the committed snapshot; the repository as tracked is a skeleton that expects this class (like `vendor/`) to be present in the installed distribution.
- **`.env.example` describes a different framework's environment** (Laravel-style keys) and does not match the actual `.env` contract (`APP_ENV`, `APP_SECRET`, `DATABASE_URL`, `MAILER_DSN`, `UV_SESSION_COOKIE_LIFETIME`).
- **Dead/unused artifacts:** the `Yaml` import in `ConfigureHelpdesk`, the `DB_ENV_PATH_TEMPLATE`/`DB_ENV_PATH_PARAM_TEMPLATE` constants, the discarded `EntityManager` instances in `verifyDatabaseCredentials`, and `ExceptionSubscriber`'s 403 branch that sets no response for anonymous users.
- **Version indicator drift:** `config/services.yaml` declares `uvdesk.version: "v1.1.8"` (rendered in the wizard UI) while `.env.example` carries `APP_VERSION=1.0.8`.
- **Hard-coded role IDs (1–4)** in `DefaultUser` depend on fixture ordering in the external core-framework rather than role codes.
- **`refreshDatabaseConnection()` return-type inconsistency** (`false` vs `[$bool, $bool]`) in the console wizard.
- **Unresolved externals:** the internals of `UVDeskService::updateWebsitePrefixes`, the fixture dataset, the `user.provider` service, and the Docker entrypoint script are outside this repository and were not inspected.

## 11. References

| # | Artifact |
|---|---|
| 1 | `public/index.php` — runtime front controller |
| 2 | `composer.json` — dependency/flex composition contract |
| 3 | `config/bundles.php`, `config/services.yaml`, `config/routes.yaml` — composition wiring |
| 4 | `config/packages/uvdesk.yaml`, `uvdesk_mailbox.yaml`, `uvdesk_extensions.yaml`, `doctrine.yaml`, `security.yaml`, `mailer.yaml` — bundle configuration contracts |
| 5 | `src/Controller/BaseController.php` — installation-state gate |
| 6 | `src/Controller/ConfigureHelpdesk.php` — wizard XHR API |
| 7 | `src/Controller/ImageCache/ImageCacheController.php`, `src/Controller/ImageCache/ImageManager.php`, `src/Service/UrlImageCacheService.php` — image-cache subsystem |
| 8 | `src/Console/EnvironmentVariables.php`, `src/Console/Wizard/{ConfigureHelpdesk,DefaultUser,MigrateDatabase}.php` — console tooling |
| 9 | `src/Routing/RoutingResource.php`, `src/Resources/config/routes.yaml` — route contribution |
| 10 | `src/EventListener/ExceptionSubscriber.php`, `templates/errors/error.html.twig` — error presentation |
| 11 | `public/scripts/wizard.js`, `templates/installation-wizard/index.html.twig`, `public/css/wizard.css` — wizard client |
| 12 | `.env`, `.env.example` — environment contracts |
| 13 | `translations/messages.*.yml` — localization catalogs |
| 14 | `Dockerfile`, `.docker/` — containerized runtime |
| 15 | `INSTALLATION GUIDE.md`, `README.md`, `CHANGELOG-1.0/1.1/1.2.md`, `.github/*` — documentation and governance |
