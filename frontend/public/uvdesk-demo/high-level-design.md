---
model: z-ai/glm-5.3
---

# High-Level Software Design Description

## 1. Document Title

**High-Level Design — UVdesk Community Helpdesk Skeleton (`uvdesk/community-skeleton`)**

This document describes the logical design of the UVdesk Community Helpdesk application skeleton as it exists in this repository: a PHP/Symfony 5.4 composition shell that assembles an open-source helpdesk platform from six externally maintained UVdesk bundles, and that itself owns the installation lifecycle, root request dispatch, error presentation, image caching, localization catalogs, and containerized deployment of the assembled product.

---

## 2. Design Overview

### 2.1 Purpose

The deployed system is a multi-channel customer-support helpdesk (agent panel, customer-facing knowledge base/support center, email-to-ticket channel, workflow automation, REST API). This repository does not implement those capabilities. Its purpose is to be the **application skeleton and composition root** that:

1. pulls the functional bundles in via Composer and registers them with the Symfony kernel (`config/bundles.php`, `composer.json`);
2. supplies the framework-level configuration that binds the assembled platform to concrete infrastructure (database, mail transport, sessions, security, translations, Twig);
3. implements the **first-run installation lifecycle** — a browser-based wizard and an equivalent interactive console command that provision the database, persist credentials, load fixtures, create the first super-admin, and configure URL prefixes;
4. owns a small set of application-level behaviors that belong to the shell rather than to any bundle: the root `/` dispatcher that decides between "installed" and "not installed" states, the branded error pages, a remote-image caching endpoint, and the installer telemetry callout.

### 2.2 Scope

**In scope (implemented in this repository):**

- HTTP bootstrap and bundle registration (`public/index.php`, `config/bundles.php`, `config/services.yaml`)
- Routing composition, including the application's contribution point (`config/routes.yaml`, `src/Routing/RoutingResource.php`, `src/Resources/config/routes.yaml`)
- Installation subsystem: web wizard controller, Backbone.js wizard front-end, console commands (`src/Controller/ConfigureHelpdesk.php`, `src/Console/**`, `public/scripts/wizard.js`, `templates/installation-wizard/`)
- Root dispatcher (`src/Controller/BaseController.php`)
- Image cache service and tracker route (`src/Controller/ImageCache/**`, `src/Service/UrlImageCacheService.php`)
- Error presentation (`src/EventListener/ExceptionSubscriber.php`, `templates/errors/`)
- Configuration and localization surface (`config/packages/**`, `translations/`, `templates/mail.html.twig`)
- Deployment (`Dockerfile`, `.docker/**`)

**Out of scope (delegated to the six registered UVdesk bundles; their internals are not present in this repository):** ticket lifecycle, agent/customer workflows, mailbox email processing, automation rules, support-center portal pages, REST API implementation, and the `uv_*` domain entity definitions (the skeleton *consumes* several of these entities during installation).

### 2.3 Design Goals

Evidenced by the repository structure and code:

- **Assemble, don't reimplement** — all helpdesk functionality is composition (`composer.json` requires `uvdesk/core-framework`, `uvdesk/support-center-bundle`, `uvdesk/mailbox-component`, `uvdesk/automation-bundle`, `uvdesk/extension-framework`, `uvdesk/api-bundle`).
- **Self-configuring first run** — the product must be installable by a non-expert: the wizard probes PHP version, extensions (`imap`, `mailparse`, `mysqli`), execution limits, and file writability before proceeding.
- **Dual installation channels** — identical outcomes achievable from the browser (wizard) and the terminal (`uvdesk:configure-helpdesk`), sharing a common command layer.
- **Safe re-configuration** — the console command re-validates an existing installation (connectivity, schema drift, super-admin presence) rather than only handling fresh installs.
- **Customizable deployment surface** — URL prefixes for member/customer panels are user-chosen at install time and written into configuration.

### 2.4 Design Constraints

- **PHP `^7.2.5 || ^8.0`, Symfony `^5.4`** (composer.json `extra.symfony.require`); the Docker runtime pins PHP 8.1 with `php8.1-xml/imap/mysql/mailparse/curl`.
- **MySQL persistence** — `config/packages/doctrine.yaml` fixes `pdo_mysql`, `server_version: '5.7'`, `utf8mb4`, and strips `ONLY_FULL_GROUP_BY` from the SQL mode (DBAL init command).
- **Environment-variable-driven secrets** — `APP_SECRET`, `DATABASE_URL`, `UV_SESSION_COOKIE_LIFETIME`, `MAILER_DSN` are read from `.env` / the environment.
- **Writable configuration at install time** — the wizard requires `.env` and `config/packages/uvdesk.yaml` + `uvdesk_mailbox.yaml` to be writable (it attempts `chmod 0666` itself), which constrains hosting permissions.
- **Dev-environment installation** — `uvdesk_wizard:env:update` refuses to run outside the `dev` kernel environment, so the persisted-configuration step of installation is bound to `APP_ENV=dev`.
- **Vendor code is not versioned** — `vendor/` is gitignored; the platform is materialized only after `composer install` (performed in the Docker build).

### 2.5 Design Principles

- **Composition root pattern** — the skeleton's primary artifact is dependency and configuration wiring, not business logic.
- **One-directional dependency** — application code (`App\`) imports bundle classes (entities, services, routing interface); no bundle imports `App\` classes. The bundles reach back into the application only through configuration and the routing-extension interface.
- **Convention over configuration** — `_defaults: { autowire, autoconfigure }` with `App\` resource scanning; controllers tagged `controller.service_arguments`.
- **State-driven dispatch** — the root route's behavior is determined entirely by database state (presence of administrator user instances), not by a configuration flag.
- **Command-layer reuse across channels** — both the HTTP wizard and the CLI configurator drive the same console commands, keeping the mutation logic (`.env` rewrite, schema migration, user creation) in one place.

---

## 3. System Context

### 3.1 System Boundary

The system boundary is the Symfony application rooted at `public/index.php` (Apache `DocumentRoot` points at `public/`). Everything under `src/`, `config/`, `templates/`, `translations/`, `public/`, and the Composer-installed `vendor/` tree is inside the boundary. The six UVdesk bundles are inside the runtime boundary but outside this repository's source control — they are consumed as versioned dependencies (`^1.1.x`).

### 3.2 External Actors

| Actor | Interaction |
|---|---|
| **Installer / Administrator** | Runs the browser wizard (`/`) or `php bin/console uvdesk:configure-helpdesk`; supplies DB credentials, super-admin identity, and URL prefixes |
| **Helpdesk Agent (member)** | Authenticates at the member prefix (form login, remember-me 7 days); uses bundle-provided agent panel |
| **Customer** | Uses the customer/knowledgebase prefix (support-center bundle); form login or anonymous ticket creation |
| **API client** | Authenticates against `^/api` through the API bundle's guard authenticator |
| **UVdesk update service** | Server-side counterpart of installer telemetry (receives domain/email/name on install) |

### 3.3 External Systems

| System | Protocol / Evidence |
|---|---|
| **MySQL server** | TCP, `pdo_mysql` via `DATABASE_URL`; also direct `DriverManager` connections and raw `PDO` in the installer; in the Docker image, a local `mysql-server` runs inside the container |
| **Mail transport** | Symfony Mailer transport `main` from `MAILER_DSN` (default `null://null`); IMAP/SMTP mailbox settings are a commented template in `uvdesk_mailbox.yaml`, configured post-install |
| **`updates.uvdesk.com`** | HTTPS — telemetry `POST /api/updates` (cURL, JSON) and a logo image `GET` used by the image-cache endpoint |
| **Public CDNs** | The installer UI loads jQuery 2.2.4, Underscore 1.9.1, Backbone 1.3.3 and backbone-validation 0.7.1 from `ajax.googleapis.com` / `cdnjs.cloudflare.com` |
| **Composer / Packagist / uvdesk recipes** | Build-time dependency resolution; Symfony Flex endpoint `uvdesk/recipes` |

### 3.4 External Interfaces

- **HTTP** (port 80 per Docker vhost): the `/` root route, the `/wizard/xhr/*` JSON endpoints, `/tracker/xhr/get/cacheImage`, plus all bundle-provided member/customer/API routes referenced by `security.yaml`.
- **CLI**: `bin/console` commands `uvdesk:configure-helpdesk`, `uvdesk_wizard:env:update`, `uvdesk_wizard:database:migrate` (hidden), `uvdesk_wizard:defaults:create-user` (hidden), and standard Doctrine commands invoked internally.
- **Filesystem**: `.env`, `config/packages/uvdesk.yaml`, `config/packages/uvdesk_mailbox.yaml`, `public/cache/images/`, `var/`, `public/attachments/`, `apps/` (extensions directory).

### 3.5 Context Diagram

```mermaid
flowchart TB
    subgraph actors["Actors"]
        INST["Installer / Administrator"]
        AGENT["Helpdesk Agent"]
        CUST["Customer"]
        APIC["API Client"]
    end

    subgraph system["UVdesk Community Skeleton (composition shell)"]
        direction TB
        HTTPIN["HTTP entry — public/index.php"]
        WIZ["Installation subsystem<br/>(web wizard + CLI configurator)"]
        SHELL["App shell: root dispatcher,<br/>error pages, image cache, config"]
        BUNDLES["Assembled UVdesk bundles<br/>core-framework · support-center · mailbox ·<br/>automation · extension-framework · api"]
        HTTPIN --> SHELL
        HTTPIN --> BUNDLES
        HTTPIN --> WIZ
    end

    DB[("MySQL<br/>(DATABASE_URL)")]
    MAIL["Mail transport<br/>(MAILER_DSN)"]
    UPD["updates.uvdesk.com<br/>(telemetry + logo)"]
    CDN["Public CDNs<br/>(wizard JS libraries)"]
    CMP["Composer / Packagist<br/>(build time)"]

    INST -->|"browser wizard / CLI"| WIZ
    AGENT -->|"member prefix, form login"| BUNDLES
    CUST -->|"customer prefix"| BUNDLES
    APIC -->|"^/api guard auth"| BUNDLES
    WIZ --> DB
    WIZ --> UPD
    SHELL --> DB
    SHELL --> UPD
    BUNDLES --> DB
    BUNDLES --> MAIL
    WIZ -.->|"loads Backbone/jQuery"| CDN
    system -.->|"composer install"| CMP
```

---

## 4. Architectural Decomposition

### 4.1 Major Subsystems / Components

The system decomposes into two strata: the **assembly stratum** (bootstrap, bundle registration, routing composition, configuration binding) and the **skeleton application stratum** (installer, dispatcher, image cache, error presentation). A third stratum, the **product stratum**, is composed in from the six bundles.

```mermaid
flowchart TB
    REQ["HTTP request"] --> IDX["public/index.php<br/>(Symfony Runtime front controller)"]
    IDX --> KERN["App\\Kernel<br/>(APP_ENV, APP_DEBUG)"]

    KERN --> BREG["config/bundles.php<br/>registers 6 UVdesk bundles"]
    KERN --> DIC["config/services.yaml<br/>App\\* autowired services"]

    subgraph routing["Routing composition"]
        RAPP["config/routes.yaml<br/>custom loaders: uvdesk · uvdesk_extensions"]
        RRES["App\\Routing\\RoutingResource<br/>implements core-framework<br/>RoutingResourceInterface"]
        RRES --> RYML["src/Resources/config/routes.yaml<br/>wizard XHR + tracker routes"]
    end
    KERN --> RAPP

    subgraph appcode["Skeleton application code (src/)"]
        BASE["BaseController<br/>route / — install-state gate"]
        WIZC["ConfigureHelpdesk controller<br/>wizard XHR endpoints"]
        IMG["ImageCacheController +<br/>ImageManager + UrlImageCacheService"]
        EXSUB["ExceptionSubscriber"]
        CMDS["Console commands<br/>configure-helpdesk · env:update ·<br/>database:migrate · defaults:create-user"]
        WIZC --> CMDS
    end

    subgraph bundles["UVdesk bundles (vendor/, per bundles.php)"]
        CORE["core-framework<br/>entities: User, UserInstance,<br/>SupportRole, Website<br/>services: UVDeskService, user.provider<br/>routing loader: uvdesk"]
        SCB["support-center-bundle"]
        MBX["mailbox-component"]
        AUTO["automation-bundle"]
        EXTF["extension-framework<br/>loader: uvdesk_extensions<br/>extensions dir: apps/"]
        APIB["api-bundle<br/>APIGuard authenticator"]
    end

    subgraph extres["External resources"]
        DB[("MySQL")]
        ENVFILE[".env file"]
        UPD["updates.uvdesk.com"]
        CACHE["public/cache/images"]
    end

    RAPP --> CORE
    RAPP --> EXTF
    BASE --> CORE
    WIZC --> CORE
    WIZC --> CMDS
    CMDS --> DB
    CMDS --> ENVFILE
    WIZC --> UPD
    IMG --> UPD
    IMG --> CACHE
    BUNDLESFULL["member / customer / api traffic"] --> CORE
```

### 4.2 Responsibilities

| Component | Responsibility | Explicitly does **not** own |
|---|---|---|
| **Bootstrap (`public/index.php`, kernel, `bundles.php`, `services.yaml`)** | Instantiate the kernel with `APP_ENV`/`APP_DEBUG`; register the six UVdesk bundles; autowire `App\*` services; expose `locale` and `uvdesk.version` parameters | Any request handling of its own |
| **Routing composition** | Merge bundle routes (via `uvdesk` / `uvdesk_extensions` custom loaders) with the skeleton's routes contributed through `App\Routing\RoutingResource` → `src/Resources/config/routes.yaml` | Route definitions for member/customer/API panels (bundle-owned) |
| **Root dispatcher (`BaseController`)** | Decide, from database state, whether an unauthenticated visit to `/` is redirected to the installed helpdesk panels or forwarded into the installation wizard | Authentication (delegated to security firewalls), panel content |
| **Installation subsystem** | Requirements probing; DB credential verification and optional database creation; `.env` rewriting; schema creation/migration and fixture loading; super-admin provisioning; URL-prefix configuration; install telemetry | Post-install helpdesk behavior |
| **Image cache subsystem** | Fetch a fixed remote logo URL, cache it as `public/cache/images/<md5>.png` with a one-week TTL, and return its public URL as JSON | Generic media management (the single cached source is the class constant `UVDESK_LOGO`) |
| **Error presentation (`ExceptionSubscriber`, `errors/error.html.twig`)** | In production only, render branded 403/404/500 pages | Error handling in non-prod environments (developer exceptions pass through) |
| **Configuration binding (`config/packages/*`)** | Bind the assembled platform to Doctrine/MySQL, Symfony sessions/security/mailer/translation/Twig, UVdesk site settings, mailbox placeholders, and the extensions directory | Business configuration values (mailboxes, workflows) which are post-install concerns |
| **Localization (`translations/messages.*.yml`)** | Twelve catalogs (ar, da, de, en, es, fr, he, it, pl, pt-BR, tr, zh) consumed by the translator with `en` fallback | Bundle-specific catalogs beyond what is provided |
| **Deployment (`Dockerfile`, `.docker/**`)** | All-in-one container: Apache + mod_php 8.1 + local MySQL; non-root execution via `gosu`; entrypoint MySQL provisioning from env vars | Horizontal scaling topology (single-node design) |

### 4.3 Component Relationships

- **Skeleton → bundles (compile-time)**: `BaseController`, `ConfigureHelpdesk`, and the console wizards import `Webkul\UVDesk\CoreFrameworkBundle\Entity\{User, UserInstance, SupportRole, Website}`, `UVDeskService`, and `RoutingResourceInterface`. `security.yaml` references `user.provider` and the API bundle's `ApiCredentials` provider and `APIGuard`; `twig.yaml` injects more than a dozen bundle services as template globals (`user.service`, `uvdesk.service`, `recaptcha.service`, `ticket.service`, `email.service`, `uvdesk.extensibles`, `uvdesk.core.file_system.service`, `uvdesk.automations`).
- **Bundles → skeleton (runtime extension points)**: the core framework's `uvdesk` route loader discovers application routes through `RoutingResourceInterface`, and the extension framework reads the `apps/` directory declared in `uvdesk_extensions.yaml`.
- **Installer → console layer → infrastructure**: the wizard controller executes its own console commands in-process (`Symfony\Bundle\FrameworkBundle\Console\Application` with `ArrayInput`/`NullOutput`); the CLI configurator executes the same command layer via OS subprocesses (`new Process(["php", "bin/console", …])`).
- **Installer → core-framework services**: website prefix read/update is delegated to `UVDeskService::getCurrentWebsitePrefixes()` / `updateWebsitePrefixes()`, which is why `config/packages/uvdesk.yaml` must remain writable during installation.

### 4.4 Dependency Structure

The dependency graph is acyclic and one-directional at the source level:

```
public/index.php → App\Kernel → (container) → App\* services
App\* → Webkul\UVDesk\* bundles → Symfony/Doctrine/Intervention (vendor)
```

Notable characteristics:

- Application code is **upward-coupled to the bundles** — it treats core-framework entities and services as its own domain model. There is no abstraction layer between the installer and the bundle API; this is intentional in a composition-root skeleton, but it means the installer breaks if the core-framework entity model changes.
- The wizard controller holds several distinct responsibilities (requirement probing, DB connectivity, orchestration, user provisioning, telemetry), making it the largest single point of coupling in the shell.
- The presentation layer is broadly coupled to bundle services through Twig globals, rather than through narrow view models.

### 4.5 Allocation of Responsibilities

| Concern | Allocated to |
|---|---|
| Product functionality | UVdesk bundles |
| Installation lifecycle, first-run state | Skeleton (`src/Controller/ConfigureHelpdesk.php`, `src/Console/**`) |
| Configuration persistence (`.env`, `uvdesk.yaml`) | Skeleton console command `uvdesk_wizard:env:update`; core-framework `UVDeskService` for prefixes |
| Database schema and domain data | Bundles (Doctrine `auto_mapping`; `uv_*` tables) |
| Installation-state detection | Skeleton `BaseController` (reads bundle-owned tables) |
| Authentication/authorization | Symfony Security configured in `security.yaml`, executed by bundle providers/guards |
| Error presentation (prod) | Skeleton `ExceptionSubscriber` + template |
| Asset caching (logo) | Skeleton image-cache subsystem |

---

## 5. Logical Design

### 5.1 Logical Components

**A. Composition & Bootstrap.** `public/index.php` requires `vendor/autoload_runtime.php` and returns a closure constructing `App\Kernel($context['APP_ENV'], $context['APP_DEBUG'])`. Both `index.php` and the service-configuration exclusion list (`../src/{…,Kernel.php}`) reference a kernel class; however, **no `Kernel.php` is present among the tracked source files in this repository revision**, and the tracked `config/bundles.php` registers only the six UVdesk bundles even though `config/packages/` configures the framework, Twig, Doctrine, Mailer and Translation bundles. The kernel and the full bundle-registration list are therefore materialized outside the version-controlled tree (e.g., regenerated during a Composer/Flex install); this is a completeness characteristic of the tracked snapshot rather than a designed abstraction, and it is the one place where the runtime composition cannot be fully established from the repository alone.

**B. Routing.** `config/routes.yaml` declares two custom loader entries — `uvdesk` (provided by core-framework, type `uvdesk`) and `uvdesk_extensions` (provided by extension-framework). The application's own routes enter through `App\Routing\RoutingResource`, an implementation of `RoutingResourceInterface` that points the core framework's loader at `src/Resources/config/routes.yaml`. That file defines ten routes: nine wizard XHR endpoints plus the tracker image endpoint. `BaseController` adds the `/` route via annotation.

**C. Installation subsystem.** Two cooperating faces over a shared command layer:

- *Web wizard* — `ConfigureHelpdesk` controller (9 XHR actions) + `templates/installation-wizard/index.html.twig` + `public/scripts/wizard.js` (Backbone.js step views/models with client-side validation).
- *CLI configurator* — `App\Console\Wizard\ConfigureHelpdesk` (`uvdesk:configure-helpdesk`), an interactive health-check/repair flow.
- *Shared commands* — `EnvironmentVariables` (`.env` mutation, dev-only), `MigrateDatabase` (fresh-vs-existing migration strategy), `DefaultUser` (user/role provisioning with interactive and non-interactive modes).

**D. Root dispatcher.** `BaseController::base` (route `/`, `base_route`): queries `SupportRole`/`UserInstance` for an existing administrator; if found, redirects (301) to the knowledgebase website route when the Support Center bundle and its `knowledgebase` website exist, otherwise to the member login; if no administrator exists, forwards internally to `ConfigureHelpdesk::load` (the wizard). Any exception in this check is swallowed and the request still lands on the wizard.

**E. Image cache subsystem.** `ImageCacheController::getCachedImage` (route `uvdesk_community_tracker_cache_image`, `GET /tracker/xhr/get/cacheImage`) → `UrlImageCacheService::getCachedImage(url, domain)` → `ImageManager` (a subclass of `Intervention\Image\ImageManager` that overrides `make()` to fetch remote images through a PHP stream context carrying browser-like `User-Agent`, `Accept-language`, and `Domain` headers). The cache key is `md5(url)`, stored as `public/cache/images/<key>.png`, with a one-week TTL enforced via `filemtime`; expired entries are deleted and refetched. The only fetched source is the constant `https://updates.uvdesk.com/uvdesk-logo.png`. The response body is a JSON-encoded public URL string.

**F. Error presentation.** `ExceptionSubscriber` subscribes to `KernelEvents::EXCEPTION` (priority 10) and acts **only in the `prod` environment**. It renders `errors/error.html.twig` with code/message/description for 404 and 500 unconditionally, and for 403 only when a non-anonymous security token exists (anonymous 403s fall back to framework behavior).

**G. Configuration components.** `config/packages/`: `framework.yaml` (secret from `APP_SECRET`; native sessions with `cookie_lifetime`/`gc_maxlifetime` from `UV_SESSION_COOKIE_LIFETIME`; `http_method_override: false`; `php_errors.log`; CSRF protection present but commented out, i.e., disabled in this revision), `doctrine.yaml`, `security.yaml`, `mailer.yaml`, `translation.yaml`, `twig.yaml`, `uvdesk.yaml` (site URL, upload manager `Localhost`, upload limits 8 MB post / 20 files / 2 MB per file, default avatar assets, default ticket type/status/priority, `mail.html.twig` as the default email template, member/customer URL prefixes), `uvdesk_mailbox.yaml` (empty `emails`/`mailboxes` with a commented IMAP+SMTP template), `uvdesk_extensions.yaml` (`dir: %kernel.project_dir%/apps`).

**H. Localization.** Twelve YAML catalogs under `translations/`, matching the `app_locales` parameter in `uvdesk.yaml`; the translator reads `translations/` as its default path with `en` fallback.

### 5.2 Services / Modules

Skeleton-defined services (autowired via `App\` resource registration, controllers tagged separately):

| Service | Role | Collaborators |
|---|---|---|
| `App\Controller\BaseController` | Root dispatch | Doctrine EM, kernel bundle list, `Website` repository |
| `App\Controller\ConfigureHelpdesk` | Wizard orchestration | DBAL `DriverManager`, Doctrine EM, console `Application`, `UVDeskService`, password encoder, session |
| `App\Controller\ImageCache\ImageCacheController` | Tracker image endpoint | `UrlImageCacheService` |
| `App\Controller\ImageCache\ImageManager` | Remote image fetching | Intervention Image drivers, container |
| `App\Service\UrlImageCacheService` | Cache lifecycle | `ImageManager`, filesystem |
| `App\EventListener\ExceptionSubscriber` | Prod error pages | Twig, container, security token storage |
| `App\Console\Wizard\ConfigureHelpdesk` | CLI configurator | `Dotenv`, `Process`, PDO, question helper |
| `App\Console\Wizard\MigrateDatabase` | Migration strategy | Doctrine EM, migrations commands |
| `App\Console\Wizard\DefaultUser` | User provisioning | Doctrine EM, password encoder |
| `App\Console\EnvironmentVariables` | `.env` mutation | `Dotenv`, filesystem, container |

### 5.3 Interfaces

**Internal interfaces:**

- `Webkul\UVDesk\CoreFrameworkBundle\Definition\RoutingResourceInterface` — implemented by `App\Routing\RoutingResource`; the contract by which the core framework collects application routes (`getResourcePath()`, `getResourceType()`).
- `Webkul\UVDesk\CoreFrameworkBundle\Services\UVDeskService` — consumed by the wizard for `getCurrentWebsitePrefixes()` / `updateWebsitePrefixes(member, customer)`.
- `user.provider` (core framework) and `Webkul\UVDesk\ApiBundle\Providers\ApiCredentials` — security user providers referenced from `security.yaml`.
- Console command names — the invocation contract between the wizard controller, the CLI configurator, and operators: `uvdesk:configure-helpdesk`, `uvdesk_wizard:env:update`, `uvdesk_wizard:database:migrate`, `uvdesk_wizard:defaults:create-user`.

**Wizard XHR HTTP contract** (all under the anonymous-accessible `customer` firewall during installation; JSON request/response):

| Route | Method | Purpose |
|---|---|---|
| `/wizard/xhr/check-requirements` | POST | Probe PHP version, extensions, max execution time, `.env`/config writability, Redis advisory |
| `/wizard/xhr/verify-database-credentials` | POST | Test DBAL connection; stage `DB_CONFIG` in session |
| `/wizard/xhr/intermediary/super-user` | POST | Stage `USER_DETAILS` in session |
| `/wizard/xhr/website-configure` | GET/POST | Read current / stage member+customer URL prefixes |
| `/wizard/xhr/load/configurations` | POST | Create DB if requested; persist `DATABASE_URL` to `.env` |
| `/wizard/xhr/load/migrations` | POST | Fresh install → schema create + fixtures; existing → migrations |
| `/wizard/xhr/load/entities` | POST | `doctrine:fixtures:load --append` |
| `/wizard/xhr/load/super-user` | POST | Persist `User` + `UserInstance` (ROLE_SUPER_ADMIN) |
| `/wizard/xhr/load/website-configure` | POST | Apply prefixes via `UVDeskService`; send install telemetry |
| `/tracker/xhr/get/cacheImage` | GET | Return cached logo URL (JSON string) |
| `/` (`base_route`) | GET | Installed → 301 redirect to panels; else → wizard page |

### 5.4 Data Responsibilities

- The skeleton owns **no Doctrine entities** (`src/Entity` is empty aside from a `.gitignore`; `doctrine.yaml` nevertheless maps `App\Entity` with `auto_mapping`).
- During installation the skeleton **writes** bundle-owned entities (`User`, `UserInstance`) and **reads** `SupportRole` and `Website`.
- The skeleton owns file-resident state: `.env` (`DATABASE_URL`), `config/packages/uvdesk.yaml` (prefixes, via `UVDeskService`), `public/cache/images/` (logo cache), `var/` (framework cache/logs).
- The CLI configurator additionally queries bundle tables directly through raw PDO (`uv_support_role`, `uv_user_instance`, `uv_user`), bypassing the ORM for its super-admin detection.

### 5.5 Control / Coordination

Control flow is synchronous request/response throughout. There are no queues, workers, schedulers, or event buses in this repository. The only event-based coordination is the kernel `EXCEPTION` subscriber. Asynchronous *syntax* in the wizard front-end (`async/await` over jQuery XHRs) sequences the install steps client-side, but each step is an independent synchronous HTTP round trip; the server enforces no step ordering — the browser drives the sequence, with the PHP session as the only cross-step memory.

---

## 6. Behavioral Design

### 6.1 Major Use-Case Realizations

**UC-1: First-run installation via browser (primary skeleton workflow).**

```mermaid
sequenceDiagram
    autonumber
    participant BR as Browser (Backbone wizard)
    participant BC as BaseController (/)
    participant WC as ConfigureHelpdesk controller
    participant SS as PHP session
    participant CM as Console command layer
    participant DB as MySQL
    participant EV as .env file
    participant TS as updates.uvdesk.com

    BR->>BC: GET /
    BC->>DB: any active SUPER_ADMIN / ADMIN user instance?
    alt Not installed
        BC-->>BR: forwarded wizard page (installation-wizard/index.html.twig)
    else Installed
        BC-->>BR: 301 to knowledgebase / member login
    end
    BR->>WC: POST /wizard/xhr/check-requirements
    WC-->>BR: PHP ≥ 7, imap/mailparse/mysqli, max-exec ≥ 30s, .env + uvdesk.yaml/uvdesk_mailbox.yaml writable
    BR->>WC: POST /wizard/xhr/verify-database-credentials
    WC->>DB: DriverManager::getConnection(url).connect()
    WC->>SS: $_SESSION['DB_CONFIG'] = credentials
    BR->>WC: POST /wizard/xhr/intermediary/super-user
    WC->>SS: $_SESSION['USER_DETAILS'] = name/email/password
    BR->>WC: POST /wizard/xhr/website-configure (member/customer prefixes)
    WC->>SS: $_SESSION['PREFIXES_DETAILS']
    BR->>WC: POST /wizard/xhr/load/configurations
    WC->>DB: create database if missing
    WC->>CM: uvdesk_wizard:env:update DATABASE_URL=<url>
    CM->>EV: rewrite DATABASE_URL line
    BR->>WC: POST /wizard/xhr/load/migrations
    WC->>CM: uvdesk_wizard:database:migrate
    CM->>DB: fresh → schema:create + fixtures; else → migrations sync/diff/migrate
    BR->>WC: POST /wizard/xhr/load/entities
    WC->>CM: doctrine:fixtures:load --append
    BR->>WC: POST /wizard/xhr/load/super-user
    WC->>DB: persist User + UserInstance (ROLE_SUPER_ADMIN, encoded password)
    BR->>WC: POST /wizard/xhr/load/website-configure
    WC->>CM: UVDeskService.updateWebsitePrefixes(member, customer)
    WC->>TS: POST /api/updates {domain, email, name}
    WC-->>BR: member/knowledgebase panel URLs (installation complete)
```

The wizard UI presents the steps as: Welcome → System Requirements → Database Configuration → Admin Details → Website prefixes → Installation (which runs the five `/wizard/xhr/load/*` calls in sequence) → Completion screen linking both panels.

**UC-2: CLI configuration / repair (`uvdesk:configure-helpdesk`).** Reads `DATABASE_URL` from `.env` (Dotenv parse), establishes connectivity (interactively re-prompts and re-persists credentials via a `php bin/console uvdesk_wizard:env:update` subprocess if broken), compares schema against mapping metadata (running `doctrine:migrations:version/diff/status` subprocesses and interactively migrating), verifies a super-admin exists (raw PDO against `uv_support_role`/`uv_user_instance`/`uv_user`), provisions one through `uvdesk_wizard:defaults:create-user` if absent, and finally posts installer details to the telemetry endpoint.

**UC-3: Post-install request dispatch.** Any request to `/` with an existing administrator is redirected to the support-center knowledgebase (301, when the `knowledgebase` website record exists) or the member login; everything else under the member/customer/API prefixes is routed and secured by the bundles per `security.yaml` (member firewall: form login + remember-me 7 days; customer firewall: form login; API firewall: guard authenticator; role hierarchy `ROLE_AGENT ⊂ ROLE_ADMIN ⊂ ROLE_SUPER_ADMIN`, `ROLE_CUSTOMER` separate).

**UC-4: Tracker image fetch.** `GET /tracker/xhr/get/cacheImage` → cache lookup by `md5(url)` → TTL check (7 days) → optional refetch via stream context with browser-like headers → respond with the public URL of the cached file.

### 6.2 Key Interaction Flows

The dominant boundary crossings in the shell are:

1. **Browser ↔ wizard controller** — JSON over XHR; client-side validation (regex for name/email; password policy ≥ 8 chars, ≥ 2 letters, 1 digit, 1 special character) precedes server-side verification.
2. **Wizard controller ↔ console layer** — in-process `Application::run(ArrayInput)`; the controller is a *client* of its own commands.
3. **CLI configurator ↔ console layer** — OS-level `Process(["php","bin/console",…])` subprocesses; the same commands invoked differently.
4. **Installer ↔ database** — three distinct access styles coexist: DBAL `DriverManager` (wizard), Doctrine ORM entity operations (super-user creation), and raw `PDO` (CLI admin detection).
5. **Installer ↔ core-framework `UVDeskService`** — the only sanctioned path for mutating site prefixes, which in turn writes `config/packages/uvdesk.yaml`.

### 6.3 State / Lifecycle Behavior

```mermaid
stateDiagram-v2
    [*] --> NotInstalled: composer create-project
    NotInstalled --> Installing: GET / (no admin user instance) → wizard
    state Installing {
        [*] --> RequirementsChecked
        RequirementsChecked --> DbVerified: credentials staged in session
        DbVerified --> AdminStaged: USER_DETAILS staged
        AdminStaged --> PrefixesStaged: member/customer prefixes staged
        PrefixesStaged --> Committed: .env + schema + fixtures + super-user
    }
    Installing --> Installed: prefixes applied, telemetry sent
    Installed --> Installing: uvdesk:configure-helpdesk (re-configure/repair)
```

- **Installation state is inferred, not stored**: "installed" means *an active `UserInstance` with `ROLE_SUPER_ADMIN` or `ROLE_ADMIN` exists in the database*. No install flag exists anywhere in the shell.
- **In-flight installation state** is transient and lives only in the PHP session (`DB_CONFIG`, `USER_DETAILS`, `PREFIXES_DETAILS`).
- **Committed installation state** is distributed across `.env` (credentials), `config/packages/uvdesk.yaml` (prefixes), and the database (schema, fixtures, super-admin, website records).
- **Cached state**: logo image with 1-week TTL; Symfony cache under `var/`.
- **Session state**: native PHP sessions, lifetime governed by `UV_SESSION_COOKIE_LIFETIME` (default 1440 s ≈ 24 min in the tracked `.env`).

### 6.4 Error / Exception Behavior

- **Wizard verification failures** return `{"status": false, "message": …}` JSON; the front-end surfaces inline notices and disables step advancement. Connection failures during credential verification produce a fixed message ("Failed to establish a connection with database server.") without leaking exception details.
- **Installation step failures**: each `/wizard/xhr/load/*` endpoint returns HTTP 500 with an empty/generic body; the front-end maps that to a generic "Something went wrong" notice (the `.env` permission failure gets a specific remediation message). The console command layer returns non-zero codes; the CLI configurator prints the underlying `ProcessFailedException` messages.
- **Root dispatcher**: `BaseController::base` wraps its entire installed-state check in `try/catch` that silently discards exceptions, guaranteeing the visitor always reaches either the panels or the wizard.
- **Production error pages**: `ExceptionSubscriber` renders `errors/error.html.twig` for 404 and 500; for 403 it renders a page only for authenticated users, otherwise leaving framework behavior in place. Non-prod environments bypass the subscriber entirely.
- **Telemetry failure is deliberately swallowed** (empty `catch`) — installation never fails because the vendor callout failed.
- **Image fetch failure** raises Intervention's `NotReadableException`; the cache layer deletes expired files before refetching, so a failed refetch simply leaves no cache entry.
- **Environment guard**: `uvdesk_wizard:env:update` throws unless the kernel environment is `dev`, making the configuration-persistence step fail fast outside development settings.

---

## 7. Data Design

### 7.1 Major Data Entities

The skeleton defines no entities of its own. The entities it manipulates during installation are provided by `uvdesk/core-framework`: `User`, `UserInstance`, `SupportRole`, `Website`. The broader ticketing domain (tickets, threads, tags, saved replies, automations, mailbox records) resides in the bundles and is referenced only indirectly (through README feature claims and configuration).

### 7.2 Logical Data Model (as evidenced from the shell)

- `SupportRole` — code-keyed roles (`ROLE_SUPER_ADMIN`, `ROLE_ADMIN`, `ROLE_AGENT`, `ROLE_CUSTOMER`); table `uv_support_role`.
- `User` — email-identified account with encoded password, first/last name, enabled flag; table `uv_user`.
- `UserInstance` — per-user helpdesk membership (support role, source `website`, active/verified flags); table `uv_user_instance`.
- `Website` — code-keyed site records (`helpdesk`, `knowledgebase`) backing the panel redirects; managed via `UVDeskService`.
- Fixtures (loaded during install) seed the initial dataset, including the support roles the installer depends on.

### 7.3 Data Ownership

| Data | Owner | Mutated by the shell? |
|---|---|---|
| `uv_*` domain tables | UVdesk bundles | Yes, during installation only (users/instances) |
| `.env` | Shell | Yes (wizard / env:update) |
| `config/packages/uvdesk.yaml` | Shell (via `UVDeskService`) | Yes (URL prefixes) |
| `public/cache/images/` | Shell | Yes (logo cache) |
| `var/` (cache, logs) | Symfony runtime | Indirectly |
| `apps/` | Extension framework | No (install target for extensions) |

### 7.4 Persistence Strategy

- Doctrine ORM with `auto_mapping`; bundle entities discovered automatically; `App\Entity` mapping present but empty.
- The installer uses a **bootstrap-aware persistence strategy**: before the container's Doctrine connection is meaningful, it constructs standalone `EntityManager`s over `DriverManager::getConnection(url)` and even raw `PDO` — the application deliberately bypasses its own configured services to bring the database into existence.
- Schema lifecycle is two-branched (`MigrateDatabase`): empty database → `doctrine:schema:create` + `doctrine:fixtures:load`; existing database → `doctrine:migrations:sync-metadata-storage` → `version --add --all` → `diff` → `migrate` as needed.
- MySQL specifics are pinned in configuration: `pdo_mysql`, server version 5.7, `utf8mb4` with `utf8mb4_unicode_ci`, and an init command that removes `ONLY_FULL_GROUP_BY` from the session SQL mode.

### 7.5 Data Flow

Installation data flows: browser form → session staging → (verification) DBAL connection → persisted `.env` → configured Doctrine connection → schema/fixtures → user entities → website prefix configuration → telemetry payload (domain, admin name, admin email). At runtime, the shell adds no data flows of its own beyond the logo cache and error rendering; all domain data movement is bundle-internal.

---

## 8. Interface Design

### 8.1 Internal Interfaces

- `RoutingResourceInterface` (core-framework) ← `App\Routing\RoutingResource` (route contribution).
- `UVDeskService` (core-framework) ← wizard controller (prefix read/update).
- Console command names (see §5.3) — the shared mutation vocabulary for both installer channels.
- Doctrine `EntityManagerInterface` and `UserPasswordEncoderInterface` injected into controllers/commands.
- Service IDs from bundles wired into Twig as globals (see §4.3), which is also the widest internal interface: every template may reach those services.

### 8.2 External Interfaces

- **HTTP/HTTPS**: the route table in §5.3; Apache vhost on port 80 with `DocumentRoot /var/www/uvdesk/public`; `public/.htaccess` handles URL rewriting outside Docker.
- **MySQL wire protocol** via `DATABASE_URL` (default template `mysql://user:password@127.0.0.1:3306/db_name`, optionally with `?serverVersion=`).
- **SMTP** via `MAILER_DSN` (transport `main`; default `null://null`).
- **HTTPS telemetry**: `POST https://updates.uvdesk.com/api/updates` with `{domain, email, name, country_code: null}`, JSON, `Accept: application/json`.
- **HTTPS image fetch**: `GET https://updates.uvdesk.com/uvdesk-logo.png` with synthetic browser headers.
- **Docker provisioning contract**: env vars `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_ROOT_PASSWORD` consumed by the entrypoint.

### 8.3 API / Service Contracts

The REST API surface (`^/api`) is owned by `uvdesk/api-bundle`, authenticated by its `APIGuard` authenticator and `ApiCredentials` user provider, both referenced from `security.yaml`. The skeleton's only first-party "API" is the wizard XHR JSON contract and the single-value tracker image response.

### 8.4 Messaging / Events

No message queues, topics, or application events are defined in this repository. The single event consumer is the kernel `EXCEPTION` subscription (§6.4). (The README characterizes the platform as "event-driven"; that behavior, to the extent it exists, is implemented inside the bundles and is not visible here.)

### 8.5 Protocols and Formats

- Wizard XHR: form-encoded POST bodies, JSON responses (`{"status": bool, "message": …}` or bare arrays/strings).
- The tracker endpoint returns a **JSON-encoded URL string** rather than a JSON object — a quirky but deliberate response shape in `ImageCacheController`.
- Configuration: YAML throughout (`config/packages/*.yaml`, routes, translations); `.env` dotenv format.
- Email templating: `templates/mail.html.twig` is the default email template registered in `uvdesk.yaml`.

---

## 9. Deployment / Physical Allocation

### 9.1 Execution Nodes

Two supported topologies:

1. **Docker (single container, all-in-one)** — `Dockerfile` builds `ubuntu:latest` with Apache 2 + `mod_php 8.1`, `mysql-server`, PHP extensions `xml/imap/mysql/mailparse/curl`, a dedicated non-root `uvdesk` user, `gosu` for privilege step-down, and Composer dependencies installed and warmed at build time (`composer install`, `dump-autoload --optimize`, `cache:clear --env=prod`). The entrypoint starts Apache and MySQL, optionally provisions a database/user from `MYSQL_*` env vars (creating the DB, granting privileges, rotating the root password, writing `my.cnf` credential files), then drops to the `uvdesk` user.
2. **Bare metal / VM (INSTALLATION GUIDE)** — Ubuntu + Apache (doc-root pointed at the project's `public/`) or the built-in dev server (`php bin/console server:run`), MySQL 5.7.23+, PHP with IMAP and Mailparse, Composer 2+.

### 9.2 Component-to-Node Allocation

Everything — web server, PHP runtime, application, bundles, and (in the Docker topology) the database — executes on one node. The only external runtime dependencies are the updates.uvdesk.com endpoints and the CDN-hosted installer libraries.

### 9.3 Network / Communication Boundaries

- Browser ↔ Apache: HTTP (port 80).
- PHP ↔ MySQL: local socket/TCP (`127.0.0.1:3306` default).
- Container ↔ updates.uvdesk.com and CDNs: outbound HTTPS.
- Composer ↔ Packagist/uvdesk recipes: build-time HTTPS.

### 9.4 Runtime Dependencies

- PHP ≥ 7.2.5 (practically 8.1 per Docker/README), extensions `ctype`, `iconv`, `imap`, `mailparse`, `mysqli` (the latter three are wizard-verified requirements).
- Symfony 5.4 component set, Doctrine ORM/DBAL/Migrations, DoctrineFixturesBundle, Intervention Image (+ `intervention/imagecache`), `google/recaptcha`, `knp-paginator-bundle`, Monolog — assembled through Symfony Flex with the `uvdesk/recipes` endpoint.

---

## 10. Cross-Cutting Design

### 10.1 Security

- **Firewall topology** (`security.yaml`): `dev` (profiler/assets unsecured), `back_support` (member prefix — form login, 7-day remember-me, logout), `uvdesk_api` (`^/api` — guard authenticator), `customer` (catch-all `/` — form login for customers, anonymous allowed).
- **Access control** rules gate the member prefix behind `ROLE_AGENT` (with anonymous exceptions for login/create-account/forgot-password/mailbox-listener) and the customer prefix behind `ROLE_CUSTOMER` (with anonymous exceptions for login, ticket creation, and public read-only ticket access).
- **Role hierarchy**: `ROLE_AGENT → ROLE_ADMIN → ROLE_SUPER_ADMIN`; customers are a separate branch.
- **Wizard endpoints are intentionally anonymous** — installation must precede any authentication; they fall under the catch-all customer firewall with anonymous access.

### 10.2 Authentication / Authorization

- Form-login authentication for both member and customer panels; API authentication via the API bundle's guard; user provider `user.provider` from core-framework.
- Password hashing: `UserPasswordEncoderInterface` with `auto` encoder for the core-framework `User` entity; the CLI prompts enforce 8–32 character passwords interactively (the web wizard enforces its policy client-side).
- CSRF protection is **disabled** in this revision (`csrf_protection` is commented out in `framework.yaml`).

### 10.3 Logging / Monitoring

- `php_errors.log: true`; Monolog is in the dependency set; no application-specific logging is implemented in the shell (installer diagnostics go to console output only; telemetry is the only outbound reporting).
- Apache access/error logs in the Docker vhost.

### 10.4 Configuration

Three configuration strata: environment variables (`.env`: `APP_ENV`, `APP_SECRET`, `DATABASE_URL`, `UV_SESSION_COOKIE_LIFETIME`, `MAILER_DSN`), YAML package configuration (`config/packages/**`), and database-stored site configuration (websites/prefixes). Installation mutates all three strata (the second through `UVDeskService`).

### 10.5 Error Handling

See §6.4. Architecturally: verification failures stop the flow before commit; committed-step failures surface as HTTP 500 with front-end retry messaging; production traffic gets branded error pages; telemetry failures never propagate.

### 10.6 Concurrency

No explicit concurrency handling. Installation is expected to be single-operator; the wizard's step sequence is client-serialized; the image cache uses a check-then-write pattern against the filesystem without locking.

### 10.7 Transactions

No explicit transaction boundaries in the shell. Installation effects are applied incrementally (env write → schema → fixtures → user → prefixes); a mid-sequence failure leaves a partially installed system, which the CLI configurator is designed to detect and repair.

### 10.8 Resilience / Recovery

- The dual-branch migration strategy (fresh vs. existing) plus the interactive CLI repair flow constitute the recovery design.
- `BaseController`'s silent exception handling guarantees the root route always resolves to a usable page.
- The image cache self-heals by deleting expired entries before refetching.
- The Docker entrypoint fails fast (exit 1) if the local MySQL cannot start.

---

## 11. Quality Attribute Design

### 11.1 Performance

- `mod_php` (no FPM/process pooling in the provided topology); `optimize-autoloader`, `dump-autoload --optimize`, and prod cache warming in the image build.
- The only shell-level performance mechanism is the 7-day TTL logo cache (avoids repeated remote fetches).

### 11.2 Availability / Reliability

- Single-node deployment; no redundancy mechanisms in the shell. Reliability effort concentrates on the installer's verification-then-commit ordering and the CLI repair path.

### 11.3 Scalability

- The design is single-instance (in-container MySQL, filesystem sessions, filesystem cache). No horizontal-scaling provisions are present in this repository.

### 11.4 Maintainability

- Twelve-locale translation catalogs; three maintained changelog lines; structured community governance (issue templates, PR template, security policy, contributing guide with the five dependent repositories enumerated).
- The composition approach itself is the main maintainability lever: platform upgrades flow through Composer version constraints (`^1.1.x` on all six bundles).

### 11.5 Security

See §10.1–10.2. Additional shell-relevant characteristics: the installer transmits the administrator's name/email/domain to the vendor's update service at the end of installation; requirement checks attempt to widen file permissions (`chmod 0666`) on `.env` and the two UVdesk config files; a tracked `.env` ships development placeholders (`APP_SECRET=YOUR_APP_SECRET`); the wizard's unauthenticated XHR endpoints can create a database and persist credentials while the system is uninstalled.

### 11.6 Usability

- Two installation channels with interactive feedback; step-gated wizard with inline validation and remediation links (including OS-specific installation blog links); progress checklist with success/failure icons.
- End-user usability (panels, knowledge base) is bundle-owned.

### 11.7 Other Applicable Attributes

- **Portability**: Composer-based distribution; Docker image; Apache/Nginx support per README.
- **Localizability**: 12 catalogs; `app_locales` parameter; `en` fallback.
- **Installability**: the system's defining quality attribute — requirements probing, permission self-repair, optional database creation, and re-entrant repair.

---

## 12. Design Decisions and Trade-offs

### 12.1 Major Decisions

1. **Skeleton/composition-root architecture.** All product capability is delegated to six versioned bundles; the repository contributes wiring, installation, and shell behaviors. Consequence: near-zero business-logic maintenance burden here, but the shell is tightly coupled to core-framework's entity/service model.
2. **Database-state as installation state.** "Installed" is defined by the existence of an administrator user instance rather than a flag. Consequence: no extra state to corrupt, and the root dispatcher is self-healing; the same query runs on every visit to `/`.
3. **Session-staged, client-driven wizard.** Each step stages its data in the PHP session; the browser sequences the commit steps. Consequence: a simple, stateless-per-request server design, but the server does not enforce step ordering or replay protection.
4. **Console command layer shared by both channels**, with two different invocation styles (in-process `Application::run` from the controller vs. `php bin/console` subprocesses from the CLI configurator). Consequence: single source of truth for mutations, at the cost of two invocation idioms and (in the subprocess case) dependency on CLI PHP availability.
5. **Mutable `.env`, dev-only.** The wizard persists `DATABASE_URL` by rewriting `.env` through a command that hard-refuses non-dev environments. Consequence: simple bootstrap, but installation is architecturally bound to `APP_ENV=dev`.
6. **Fresh-vs-existing migration strategy.** One command handles both pristine databases (`schema:create` + fixtures) and upgrades (migrations diff/migrate). Consequence: the same artifact serves first install and upgrade.
7. **Install telemetry.** The final step posts installer identity to `updates.uvdesk.com`; failures are swallowed so they never affect installation.
8. **All-in-one Docker image.** Apache + PHP + MySQL in one container with entrypoint provisioning and non-root step-down. Consequence: frictionless evaluation; production-grade separation is not provided by this artifact.
9. **CDN-served installer libraries.** The wizard loads jQuery/Underscore/Backbone from public CDNs. Consequence: no bundling step for the installer, but the installer requires internet access to render.

### 12.2 Alternatives Considered

Not recoverable from the repository — no design records (ADRs, RFCs) are tracked. The changelogs describe release-level changes only.

### 12.3 Trade-offs

- **Composition vs. control**: the shell inherits the bundles' entity model verbatim (no anti-corruption layer), making version upgrades of core-framework the dominant compatibility risk for the installer.
- **Simplicity vs. robustness in installation**: incremental commit steps without transactions mean partial installs are possible; this is accepted and mitigated by the repair command rather than by transactional installation.
- **Writability vs. hardening**: installation requires (and self-grants) permissive file modes on `.env` and `uvdesk.yaml`, trading filesystem strictness for installability.

### 12.4 Design Risks (observed characteristics)

- The wizard's XHR endpoints are reachable anonymously whenever no administrator exists; combined with CSRF protection being disabled in `framework.yaml`, unauthenticated state-mutating requests are possible during the uninstalled window.
- Installation sends administrator PII (name, email, domain) to an external vendor endpoint.
- The root dispatcher swallows all exceptions, which can mask genuine misconfiguration as "not installed."
- Version guidance drift exists across the corpus: composer allows PHP `^7.2.5||^8.0`, the wizard checks ≥ 7.0, the README requires 8.1, the installation guide demonstrates 8.2, Docker installs 8.1; `.env.example` carries `APP_VERSION=1.0.8` while `services.yaml` pins `uvdesk.version: v1.1.8` (the `^1.1.x` bundle constraints align with the latter).
- `.env.example` is written in a different framework's key convention (`APP_KEY`, `DB_CONNECTION`, `CACHE_DRIVER`, `MAIL_DRIVER`, `QUEUE_DRIVER`, …). None of those keys are referenced by the Symfony configuration in this repository; the operative environment contract is `APP_ENV`, `APP_SECRET`, `DATABASE_URL`, `UV_SESSION_COOKIE_LIFETIME`, and `MAILER_DSN` (the tracked `.env`). The file is therefore vestigial and does not describe the running system.

---

## 13. Traceability

### 13.1 Capabilities to Design Elements

| Capability | Design elements |
|---|---|
| Guided web installation | `ConfigureHelpdesk` controller, `installation-wizard/index.html.twig`, `wizard.js`, routes in `src/Resources/config/routes.yaml` |
| CLI installation/repair | `App\Console\Wizard\ConfigureHelpdesk` + shared command layer |
| Credential persistence | `EnvironmentVariables` command, `.env`, `doctrine.yaml` |
| Schema/data provisioning | `MigrateDatabase`, `DefaultUser`, Doctrine fixtures |
| Install-state dispatch | `BaseController::base`, `SupportRole`/`UserInstance` queries |
| Member/customer/API access control | `security.yaml` firewalls, providers, role hierarchy (bundle-provided guards) |
| URL prefix customization | `websiteConfigurationXHR` / `updateWebsiteConfigurationXHR`, `UVDeskService`, `uvdesk.yaml` |
| Production error pages | `ExceptionSubscriber`, `errors/error.html.twig` |
| Remote image caching | `ImageCacheController`, `UrlImageCacheService`, `ImageManager` |
| Localization | `translations/messages.*.yml`, `translation.yaml`, `app_locales` |
| Extension hosting | `uvdesk_extensions.yaml` (`apps/`), extension-framework bundle |
| Containerized deployment | `Dockerfile`, `.docker/**` |

### 13.2 Design Elements to Interfaces

| Design element | Interface |
|---|---|
| `RoutingResource` | `RoutingResourceInterface` (core-framework) |
| Wizard controller | XHR JSON contract (§5.3) |
| Command layer | `uvdesk:configure-helpdesk`, `uvdesk_wizard:env:update`, `uvdesk_wizard:database:migrate`, `uvdesk_wizard:defaults:create-user` |
| Installer ↔ database | `DATABASE_URL` (DBAL URL format, optional `serverVersion`) |
| Installer ↔ core framework | `UVDeskService::getCurrentWebsitePrefixes` / `updateWebsitePrefixes` |
| Telemetry | `POST https://updates.uvdesk.com/api/updates` |

### 13.3 Design Elements to Verification

The repository contains no automated tests (no `tests/` directory, empty `require-dev`, `App\Tests` autoload target unused). Verification of the design is currently exercised through the installation flows themselves (the wizard's requirement checks and the CLI configurator's health checks double as runtime self-verification), the Doctrine migration status comparison, and the fixtures-load result. Bundle-level behavior is verified in the respective upstream repositories.

---

## 14. References

| # | Artifact |
|---|---|
| 1 | `public/index.php`, `vendor/autoload_runtime.php` (front controller) |
| 2 | `composer.json` (dependency graph, Flex configuration, `App\` PSR-4 mapping) |
| 3 | `config/bundles.php`, `config/services.yaml`, `config/routes.yaml` |
| 4 | `src/Routing/RoutingResource.php`, `src/Resources/config/routes.yaml` |
| 5 | `src/Controller/BaseController.php`, `src/Controller/ConfigureHelpdesk.php` |
| 6 | `src/Controller/ImageCache/ImageCacheController.php`, `ImageManager.php`, `src/Service/UrlImageCacheService.php` |
| 7 | `src/EventListener/ExceptionSubscriber.php`, `templates/errors/error.html.twig` |
| 8 | `src/Console/EnvironmentVariables.php`, `src/Console/Wizard/{ConfigureHelpdesk,DefaultUser,MigrateDatabase}.php` |
| 9 | `config/packages/{framework,doctrine,security,mailer,translation,twig,uvdesk,uvdesk_mailbox,uvdesk_extensions}.yaml` |
| 10 | `.env`, `.env.example` |
| 11 | `templates/installation-wizard/index.html.twig`, `public/scripts/wizard.js`, `public/css/wizard.css` |
| 12 | `templates/mail.html.twig`, `translations/messages.*.yml` |
| 13 | `Dockerfile`, `.docker/bash/uvdesk-entrypoint.sh`, `.docker/config/apache2/vhost.conf`, `.docker/config/php/php.ini` |
| 14 | `README.md`, `INSTALLATION GUIDE.md`, `CHANGELOG-1.0/1.1/1.2.md`, `.github/CONTRIBUTING.md` |

**Open items in the tracked snapshot** (material to a complete picture but not resolvable from this repository alone): the `App\Kernel` class referenced by the front controller and service configuration is not present among tracked sources; the tracked `config/bundles.php` lists only the six UVdesk bundles although `config/packages/` configures additional framework bundles; and all product-stratum behavior (ticket lifecycle, mailbox processing, automation, API) resides in the six dependent repositories listed in `.github/CONTRIBUTING.md`.
