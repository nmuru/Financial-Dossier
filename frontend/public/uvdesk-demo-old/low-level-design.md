---
model: deepseek/deepseek-v4-flash-0731
---

# Low-Level Design — UVdesk Community Skeleton

## 1. Scope and Design Overview

This repository is the **UVdesk Community helpdesk skeleton**: a Symfony Framework application distribution whose first-party code is deliberately small. The actual helpdesk domain logic, entities, repositories, and migrations are supplied by external Composer packages (`uvdesk/core-framework`, `uvdesk/support-center-bundle`, `uvdesk/mailbox-component`, `uvdesk/automation-bundle`, `uvdesk/extension-framework`, `uvdesk/api-bundle`), registered in `config/bundles.php`. The skeleton contributes the following concrete subsystems, which this document reconstructs at module/symbol level:

- **Application composition and routing glue** — `public/index.php`, `config/services.yaml`, `config/bundles.php`, `config/routes.yaml`, `src/Routing/RoutingResource.php`, and the `config/packages/*.yaml` parameter files.
- **Web installation wizard** — `src/Controller/ConfigureHelpdesk.php` (10 XHR/HTTP actions), `templates/installation-wizard/index.html.twig`, and the Backbone.js client `public/scripts/wizard.js`.
- **Console (CLI) installation wizard** — `src/Console/Wizard/ConfigureHelpdesk.php` (`uvdesk:configure-helpdesk`), `src/Console/Wizard/MigrateDatabase.php`, `src/Console/Wizard/DefaultUser.php`, and `src/Console/EnvironmentVariables.php`.
- **Tracker image-cache pipeline** — `src/Controller/ImageCache/ImageCacheController.php`, `src/Controller/ImageCache/ImageManager.php`, `src/Service/UrlImageCacheService.php`.
- **Error surface and entry routing** — `src/EventListener/ExceptionSubscriber.php`, `src/Controller/BaseController.php`, `templates/errors/error.html.twig`.
- **Deployment contract** — `Dockerfile` and `.docker/` (Apache vhost, PHP ini, `uvdesk-entrypoint.sh`).

The skeleton's PHP is written in the Symfony dialect (polyfill built-ins such as `filter_var`, `extension_loaded`, `strtr`, `array_map`, `curl_init`, `list(...) =` destructuring). `composer.json` declares polyfill replacements (`symfony/polyfill-ctype`, `symfony/polyfill-iconv`, `symfony/polyfill-php72`) to support this syntax.

Two files referenced by first-party code are **not present in the repository**: `src/Kernel.php` (used by `public/index.php`, excluded from service scanning in `config/services.yaml`) and the `bin/console` console binary (all console commands are invoked as `php bin/console <command>`). Both are expected to be generated/provided by the Composer "Symfony runtime" recipe during `composer install`; their absence means the runtime bootstrap contract is only partially visible in this repository.

---

## 2. Module Organization Map

| Logical component | Concrete implementation |
|---|---|
| Application bootstrap | `public/index.php` → `App\Kernel` (generated), `config/` |
| Service container composition | `config/services.yaml` (auto-wired `App\` services, controller argument tag) |
| Bundle composition | `config/bundles.php` (6 Webkul bundles) |
| First-party route table | `src/Resources/config/routes.yaml` (10 routes), exposed by `src/Routing/RoutingResource.php` |
| Root forwarder / installed-check | `src/Controller/BaseController.php::base` (`@Route("/")`) |
| Web installer | `src/Controller/ConfigureHelpdesk.php` + `templates/installation-wizard/index.html.twig` + `public/scripts/wizard.js` |
| Console installer | `src/Console/Wizard/ConfigureHelpdesk.php`, `MigrateDatabase.php`, `DefaultUser.php`, `src/Console/EnvironmentVariables.php` |
| Tracker image cache | `ImageCacheController` → `UrlImageCacheService` → `ImageManager` (Intervention/Image) |
| Error handling | `src/EventListener/ExceptionSubscriber.php` → `templates/errors/error.html.twig` |
| Localization/presentation | `config/packages/translation.yaml` + `translations/messages.*.yml` (14 locales), `templates/mail.html.twig` |
| Extension mount point | `apps/` (empty, wired by `config/packages/uvdesk_extensions.yaml`) |

### Module Dependency Diagram

```mermaid
graph TD
    subgraph Bootstrap
        IDX[public/index.php] --> KRN[App\Kernel (generated, not in repo)]
        KRN --> SV[config/services.yaml]
        KRN --> PKG[config/packages/*.yaml]
        KRN --> BND[config/bundles.php]
    end

    subgraph First-party code (App\)
        RT[Routing\RoutingResource] --> RY[src/Resources/config/routes.yaml]
        RY --> WEBCTL[Controller\ConfigureHelpdesk]
        RY --> IMGCTL[Controller\ImageCache\ImageCacheController]
        BC[Controller\BaseController] --> WEBCTL
        WEBCTL --> UVS[Webkul\UVDesk\CoreFrameworkBundle\Services\UVDeskService]
        WEBCTL --> ENT[SupportRole / User / UserInstance entities (bundle)]
        WEBCTL --> APP[Symfony Bundle Framework Console Application]
        APP --> MIG[Console\Wizard\MigrateDatabase]
        APP --> ENV[Console\EnvironmentVariables]
        CON[Console\Wizard\ConfigureHelpdesk] --> ENV
        CON --> DU[Console\Wizard\DefaultUser]
        IMGCTL --> CACHE[Service\UrlImageCacheService]
        CACHE --> IMGMGR[Controller\ImageCache\ImageManager]
        EXC[EventListener\ExceptionSubscriber] --> ERR[errors/error.html.twig]
    end

    subgraph External bundles (composer)
        UVS --> CORE[uvdesk/core-framework]
        ENT --> CORE
        DOCT[doctrine/* console commands] --> MIG
        SCR[security encoders] --> DU
    end
```

The dependency direction is one-way: first-party code depends on bundle-provided services, entities, and console commands; bundles never depend on `src/`.

---

## 3. Application Composition and Bootstrap

`public/index.php` is the front controller. `.htaccess` (with `mod_rewrite`) maps non-file requests to `index.php/<path>`, and the Apache vhost (`.docker/config/apache2/vhost.conf`) sets `DocumentRoot /var/www/uvdesk/public`. `index.php` loads `vendor/autoload_runtime.php` and instantiates `App\Kernel` with `APP_ENV` and `APP_DEBUG` from the request context.

`config/services.yaml` is the composition root:

- Parameters `locale: 'en'` and `uvdesk.version: "v1.1.8"` are declared.
- Defaults enable `autowire: true` and `autoconfigure: true` (services auto-register as console commands / event subscribers).
- `App\` maps `../src/*` to services keyed by fully-qualified class name, excluding `DependencyInjection`, `Entity`, `Migrations`, `Tests`, and `Kernel.php` (confirming `Kernel.php` is intended to exist at `src/Kernel.php` but is not checked in).
- `App\Controller\` is registered with the `controller.service_arguments` tag, which is what allows service injection into controller action parameters (e.g., `UVDeskService`, `UserPasswordEncoderInterface`).

`config/routes.yaml` registers two bundle-typed resources (`uvdesk` and `uvdesk_extensions`) that delegate to the external bundles' own route tables. First-party routes are aggregated through `src/Routing/RoutingResource.php`, which implements the Core Framework's `RoutingResourceInterface` and points to `src/Resources/config/routes.yaml`.

---

## 4. Web Installation Wizard

### 4.1 Route Table

All first-party routes are defined in `src/Resources/config/routes.yaml`:

| Method | Path | Action |
|---|---|---|
| POST | `/wizard/xhr/check-requirements` | `evaluateSystemRequirements` |
| POST | `/wizard/xhr/verify-database-credentials` | `verifyDatabaseCredentials` |
| POST | `/wizard/xhr/intermediary/super-user` | `prepareSuperUserDetailsXHR` |
| GET/POST | `/wizard/xhr/website-configure` | `websiteConfigurationXHR` |
| POST | `/wizard/xhr/load/configurations` | `updateConfigurationsXHR` |
| POST | `/wizard/xhr/load/migrations` | `migrateDatabaseSchemaXHR` |
| POST | `/wizard/xhr/load/entities` | `populateDatabaseEntitiesXHR` |
| POST | `/wizard/xhr/load/super-user` | `createDefaultSuperUserXHR` |
| POST | `/wizard/xhr/load/website-configure` | `updateWebsiteConfigurationXHR` |
| GET | `/tracker/xhr/get/cacheImage` | `ImageCacheController::getCachedImage` |

The wizard page itself is rendered by `ConfigureHelpdesk::load()` (`installation-wizard/index.html.twig`), which is the fallback target of `BaseController::base` (see §7).

### 4.2 Controller Actions (`App\Controller\ConfigureHelpdesk`)

The controller uses four class constants that define the environment-update contract:

- `DB_URL_TEMPLATE = "mysql://[user]:[password]@[host]:[port]"` — placeholder-substituted with `strtr`.
- `DB_ENV_PATH_TEMPLATE` / `DB_ENV_PATH_PARAM_TEMPLATE` — `DATABASE_URL=...` line formats (declared, not active in the current flow).
- `DEFAULT_JSON_HEADERS` — `Content-Type: application/json`.
- Two static requirement lists: `$requiredExtensions` (`imap`, `mailparse`, `mysqli`) and `$requiredConfigfiles` (`uvdesk`, `uvdesk_mailbox`).

**`evaluateSystemRequirements(Request, Kernel)`** — a polymorphic check endpoint keyed by the `specification` form field:

- `php-version`: compares `phpversion()` against `7.0.0`, returns status + `version` (from `PHP_MAJOR_VERSION`/`PHP_MINOR_VERSION`/`PHP_RELEASE_VERSION`) and a message.
- `php-extensions`: maps `$requiredExtensions` to booleans via `extension_loaded()`.
- `php-maximum-execution`: compares `ini_get('max_execution_time')` against 30 s and embeds help URLs in the failure description.
- `php-envfile-permission`: attempts `chmod(0666)` on `<projectDir>/.env` and reports writability (`is_writable`).
- `php-configfiles-permission`: attempts `chmod(0666)` on `<projectDir>/config/packages/{uvdesk,uvdesk_mailbox}.yaml` and reports writability per file.
- `redis-status`: if the `redis` extension is loaded, returns `status: false` with instructions referencing GitHub issue #364; otherwise the response is undefined (the switch falls through and `$response ?? []` is returned).
- Unknown specification → HTTP 404.

**`verifyDatabaseCredentials(Request)`** — establishes a raw Doctrine DBAL connection from the submitted `serverName`, `serverPort`, `username`, `password`, optional `serverVersion` (appended as `?serverVersion=`), and `database`. It verifies the database exists unless `createDatabase` is truthy, then stores the complete configuration in `$_SESSION['DB_CONFIG']` and returns `{"status": true}`. Any exception is translated to `{"status": false, "message": "Failed to establish a connection with database server."}`. Session is started lazily via `session_start()`.

**`prepareSuperUserDetailsXHR(Request)`** — validates nothing; stores `{name, email, password}` into `$_SESSION['USER_DETAILS']` and returns `{"status": true}`. (A commented-out `unset` shows an abandoned attempt to reset the session entry.)

**`updateConfigurationsXHR(Request, Kernel)`** — the first install-pipeline step. It:

1. Reads `DB_CONFIG` from session (host/port/version/user/password/database/createDatabase).
2. Connects with DBAL; creates the database if missing and `createDatabase` is set.
3. Rewrites the connection URL to include the database name.
4. Runs the `uvdesk_wizard:env:update` console command **in-process** by constructing a `Symfony\Bundle\FrameworkBundle\Console\Application($kernel)` with `setAutoExit(false)` and `ArrayInput(['command' => ..., 'name' => 'DATABASE_URL', 'value' => $connectionUrl])`, writing to `NullOutput`.
5. Returns `{"success": true}` on return code 0, otherwise HTTP 500 with `{"success": false}`; exceptions return `{"status": false, "message": ...}`.

**`migrateDatabaseSchemaXHR(Request, Kernel)`** — runs `uvdesk_wizard:database:migrate` in-process (§5.2) and always returns `[]` with HTTP 200; the client treats HTTP 500 as failure.

**`populateDatabaseEntitiesXHR(Request, Kernel)`** — runs `doctrine:fixtures:load --append` in-process, always returns `[]` HTTP 200.

**`createDefaultSuperUserXHR(Request, UserPasswordEncoderInterface $encoder)`** — creates the super-admin account:

1. Looks up `SupportRole` with code `ROLE_SUPER_ADMIN` and an active `UserInstance` for that role; if found, does nothing.
2. Otherwise reconstructs `{name, email, password}` from `$_SESSION['USER_DETAILS']`.
3. If a `User` with that email exists, it reuses it; if the existing user has an agent instance, it upgrades that instance's role to super-admin and flushes.
4. Otherwise creates the user: splits the name into first/last at the first space, encodes the password through the injectable `UserPasswordEncoderInterface`, sets `isEnabled(true)`, persists.
5. Creates and persists a `UserInstance` (`source = 'website'`, active, verified) bound to the user and the super-admin role.

**`websiteConfigurationXHR(Request, UVDeskService)`** —

- GET: calls `uvdesk->getCurrentWebsitePrefixes()` (Core Framework service) and returns `{...prefixes, status: true}` or `{"status": false}`; the client consumes keys `memberPrefix` and `knowledgebasePrefix`.
- POST: stores `{member-prefix, customer-prefix}` into `$_SESSION['PREFIXES_DETAILS']` and returns `{"status": true}`.

**`updateWebsiteConfigurationXHR(Request, UVDeskService)`** — reads the session prefixes, calls `uvdesk->updateWebsitePrefixes(member, customer)`, then posts `{name, email, domain}` to the UVdesk tracker via the static `Helpdesk::addUserDetailsInTracker()` (cURL POST to `https://updates.uvdesk.com/api/updates`; exceptions are swallowed). Returns the collection URL payload; the client reads keys `memberLogin` and `knowledgebase` from it. (`UpdateConfigurationXHR`'s session `PREFIXES_DETAILS` contract is therefore: `member`/`customer` keys in, `memberLogin`/`knowledgebase` keys out.)

### 4.3 Client-Side Wizard (`public/scripts/wizard.js`)

The client is a Backbone.js (1.3.3) application embedded in underscore templates inside `index.html.twig`. It is bound on `$(window).bind("load", ...)` and bootstraps a `Backbone.Router` with route `:installationStep` → `UVDeskCommunityInstallationWizardView::iterateInstallationSteps`, then starts `Backbone.history`.

**`UVDeskCommunityInstallationWizardView`** owns the step machine. Its `timeline` array defines five step records (`check-requirements`, `configure-database`, `create-admin`, `website-prefixes`, `install`), each mapping `path` → a View/Model pair. Navigation and gating are implemented through:

- `events['click #wizardCTA-StartInstallation']` — marks the welcome step complete and navigates to `check-requirements`.
- `events['click #wizardCTA-IterateInstallation']` — calls `activeSetupProcedure.model.isProcedureCompleted(callback)`; on success marks the active step checked and navigates to the next unvisited step. While a step is in flight, a `processing-request` spinner is prepended to the Proceed button.
- `events['click #wizardCTA-IterateBackward']` — navigates back one step, with a special case that resets to system requirements from database configuration.
- `enableNextStep()` / `disableNextStep()` toggle the `disabled` attribute on `#wizardCTA-IterateInstallation`.
- `iterateInstallationSteps(iteration)` — renders a step's View via `renderWizardInstallationStep` (which instantiates `new StepView({wizard, existingModel})`), enabling per-step model reuse when navigating backward.

Each step model implements an `isProcedureCompleted(callback)` contract and its view implements `validateForm` (debounced 400 ms). Key details per step:

1. **System Requirements** — `UVDeskCommunitySystemRequirementsModel::fetch()` fires six parallel POSTs to `/wizard/xhr/check-requirements` (one per specification). Each response handler re-renders its criteria block (loader/success/notice icons) and calls `evaluateOverallRequirements()`, which aggregates the six verdicts into a `verified` flag that enables/disables the Proceed button. Failures substitute the localized `ERRORS.error404/error500` copy.
2. **Database Configuration** — defaults `serverName: '127.0.0.1'`, `serverPort: '3306'`, `username: 'root'`, `createDatabase: 1`. Mandatory fields: serverName, username, password, database. `isProcedureCompleted` POSTs credentials to `/wizard/xhr/verify-database-credentials` and only advances on `status === true`, else renders a persistent `wizard-error-id` notice.
3. **Admin Details** — client-side validation with `nameRegex` (letters/spaces), `emailRegex` (RFC-style), and `passwordRegix` `^(?=(.*[a-zA-Z].*){2,})(?=.*\d)(?=.*[^\w\s]|.*_)[^\s]{8,}$` (≥ 8 chars, ≥ 2 letters, ≥ 1 digit, ≥ 1 special or underscore, no spaces), plus confirm-password equality. `Backbone.Validation.bind(this)` is invoked in `initialize`, mixing the framework validator with the hand-rolled version. `isProcedureCompleted` POSTs to `/wizard/xhr/intermediary/super-user`.
4. **Website Prefixes** — `getDefaultAttributes()` GETs `/wizard/xhr/website-configure` to pre-fill the member/customer prefixes (`member`/`customer` defaults). Validation requires both prefixes, requires them to differ, and matches `/^[a-z0-9A-Z]*$/`. `isProcedureCompleted` POSTs `{member-prefix, customer-prefix}` to the same endpoint.
5. **Install** — `UVDeskCommunityInstallSetupView::updateConfigurations()` executes an async sequential pipeline (`(async () => {...})()`):

```mermaid
sequenceDiagram
    participant B as Browser (wizard.js)
    participant C as ConfigureHelpdesk (web)
    participant A as Console Application (in-process)
    participant F as Doctrine / .env / DB

    B->>C: POST /wizard/xhr/load/configurations
    C->>A: uvdesk_wizard:env:update DATABASE_URL
    A->>F: rewrite .env
    C-->>B: 200 {"success": true}
    B->>C: POST /wizard/xhr/load/migrations
    C->>A: uvdesk_wizard:database:migrate
    A->>F: doctrine:schema:create / fixtures / migrate
    C-->>B: 200 []
    B->>C: POST /wizard/xhr/load/entities
    C->>A: doctrine:fixtures:load --append
    C-->>B: 200 []
    B->>C: POST /wizard/xhr/load/super-user
    C->>F: create User + UserInstance (ROLE_SUPER_ADMIN)
    C-->>B: 200 []
    B->>C: POST /wizard/xhr/load/website-configure
    C->>F: uvdesk.updateWebsitePrefixes(member, customer)
    C-->>B: {memberLogin, knowledgebase}
    B->>B: render success template (prefixCollection)
```

Each step swaps the progress UI (`installation_process_template({currentStep})`), advances a five-node progress indicator via `next(i)`, and attaches `.fail` handlers that render the failure icon and an `#error-message-bar` message (the configurations step specifically points to `.env` read/write permission remediation). The final step consumes `memberLogin`/`knowledgebase` from the last response, marks the install node complete, and renders the success template with `prefixCollection.member` / `prefixCollection.knowledgebase` links (Admin Panel / Knowledgebase).

### 4.4 Session Data Structures

| Session key | Shape | Written by | Read by |
|---|---|---|---|
| `DB_CONFIG` | `{host, port, version, username, password, database, createDatabase}` | `verifyDatabaseCredentials` | `updateConfigurationsXHR` |
| `USER_DETAILS` | `{name, email, password}` | `prepareSuperUserDetailsXHR` | `createDefaultSuperUserXHR`, `updateWebsiteConfigurationXHR` |
| `PREFIXES_DETAILS` | `{member, customer}` | `websiteConfigurationXHR` (POST) | `updateWebsiteConfigurationXHR` |

---

## 5. Console Installation Subsystem

All console commands are `Symfony\Component\Console\Command\Command` subclasses auto-registered as services. The web controller invokes `EnvironmentVariables` and `MigrateDatabase` in-process; `ConfigureHelpdesk` shells out to sibling commands via `php bin/console ...`.

### 5.1 `EnvironmentVariables` — `uvdesk_wizard:env:update`

- Arguments: `name` (required), `value` (required).
- `initialize`: loads `<projectDir>/.env`, parses via `Dotenv`, uppercases the target key and merges the new value.
- `execute`: **guards on kernel environment** — throws HTTP-500-style exception unless `kernel.getEnvironment() == 'dev'`, which makes the wizard's env writes dev-only. It rewrites only lines whose variable name matches an updated key (comments and unrelated lines are preserved verbatim), and writes back only when the stream differs.

### 5.2 `MigrateDatabase` — `uvdesk_wizard:database:migrate` (hidden)

A state-adaptive migration runner:

- `isDatabaseConfigurationValid()` — connects via the injected `EntityManagerInterface`, catching `DBALException`; returns failure text otherwise.
- Schema inspection uses a DBAL-version-compatible branch: `connection->createSchemaManager()` (DBAL 3) or `connection->getSchemaManager()` (DBAL 2).
- **Fresh path** — if `listTableNames()` is empty: `doctrine:schema:create --no-interaction` then `doctrine:fixtures:load --no-interaction --quiet` (this is the path exercised by the web wizard's first ever run).
- **Existing-DB path** — `doctrine:migrations:sync-metadata-storage --quiet`; reads the latest version; `doctrine:migrations:version --add --all --quiet`; compares `doctrine:migrations:latest` before/after `doctrine:migrations:diff --quiet` + `doctrine:migrations:status --quiet`; and runs `doctrine:migrations:migrate --no-interaction` when versions differ.
- All sub-commands run **in-process** via `$this->getApplication()->find($commandName)` with `ConsoleOptions` input, rather than shelling out.

### 5.3 `ConfigureHelpdesk` — `uvdesk:configure-helpdesk`

The terminal counterpart of the web wizard: a linear diagnostic pipeline with interactive recovery. Terminal-control constants (`CLS`, `CLL`, `MCH`, `MCA`) drive screen management between prompts.

**`initialize`** — permission remediation: `chmod(0775)` on `.env`, `var/`, `config/`, `public/`, and `migrations/` under `kernel.project_dir`.

**`execute`** flow:

1. *Database connectivity*: `getUpdatedDatabaseCredentials()` parses `.env` `DATABASE_URL` (split on `://`, then `@`, `/`, `:`) into host/port/name/user/password. If the `redis` extension is loaded, it prints a warning linking to issue #364 (Redis host config). `refreshDatabaseConnection()` (a `Doctrine\ORM\EntityManager::create` with `pdo_mysql` + annotation metadata on `src/Entity`) returns a `[isServerAccessible, isDatabaseAccessible]` tuple. On failure it interactively prompts for host (default `127.0.0.1`), port (default `3306`), name, user, and hidden password, optionally creating the database via `createDatabase()` (schema-manager based), then rewrites credentials by shelling out: `php bin/console uvdesk_wizard:env:update DATABASE_URL mysql://user:pass@host:port/name`. Any failure exits with code 1.
2. *Schema check*: compares `getLatestMigrationVersion()` (buffered output of `doctrine:migrations:latest`) before and after running `doctrine:migrations:version --add --all --no-interaction`, `doctrine:migrations:diff --quiet`, `doctrine:migrations:status --quiet`. On mismatch and confirmation, runs `doctrine:migrations:migrate --no-interaction --quiet` (900 s timeout) then `doctrine:fixtures:load --append` (120 s). **Irregularity**: on *equal* versions the command prints a red error ("There are entities that have not been updated to the `$databaseName` database yet", referencing an undefined variable) and returns 1; a surrounding `catch` treats any exception as "schema up-to-date" and continues. The equality branch therefore behaves as a failure path rather than a no-op.
3. *Super-admin check*: direct PDO queries against `uv_support_role` (`code = 'ROLE_SUPER_ADMIN'`), `uv_user_instance` (by `supportRole_id`), and `uv_user` (by user id). If absent, prompts for an email (sanitized with `FILTER_SANITIZE_EMAIL`, validated with `FILTER_VALIDATE_EMAIL`), a name, and a password/confirm loop, then shells out to `uvdesk_wizard:defaults:create-user ROLE_SUPER_ADMIN <name> <email> <password> --no-interaction`. `ProcessFailedException` is translated to an error exit.
4. *Telemetry*: builds `{name, email, domain}` (domain from the `uvdesk.site_url` parameter; falls back to the found user's name/email) and calls the public static `addUserDetailsInTracker($userDetails)` — a cURL POST (`curl_init`/`curl_setopt`/`curl_exec`) with JSON headers and a `country_code: null` field; **all exceptions are swallowed**, so telemetry failure never fails installation. Returns `Command::SUCCESS`.

**Interactive input** — `askInteractiveQuestion($question, $default, $indentLength, $nullable, $secure, $warningMessage)` loops hidden (`setHidden`) or visible prompts until a non-null answer, using `Question` + the `question` console helper.

### 5.4 `DefaultUser` — `uvdesk_wizard:defaults:create-user` (hidden)

- Arguments: `role` (required), `name`, `email`, `password` (optional); option `--no-interaction`.
- Resolves the role via `SupportRole::findOneByCode`; exits 2 on invalid role or (in no-interaction mode) missing args.
- Interactive mode (`interact()`): prompts email (re-sanitized/validated), name (with autocomplete to the existing user's name), and password with an 8–32 character policy; passwords are encoded through the injected `UserPasswordEncoderInterface`.
- Persistence: existing users are reused; otherwise `User::setIsEnabled(true)`. An account-existence check walks the user's `UserInstance`s: role IDs 1–3 are treated as the member-level family, ID 4 as customer; if the target privilege level already exists, the command returns 1 without persisting. Otherwise it persists the user plus a new active/verified `UserInstance` (`source = 'website'`).

### 5.5 Console Flow Overview

```mermaid
sequenceDiagram
    participant T as Terminal
    participant CH as ConfigureHelpdesk (uvdesk:configure-helpdesk)
    participant EV as EnvironmentVariables (cmd)
    participant MB as MigrateDatabase (cmd)
    participant DU as DefaultUser (cmd)

    T->>CH: php bin/console uvdesk:configure-helpdesk
    CH->>CH: chmod 0775 (.env, var, config, public, migrations)
    CH->>CH: getUpdatedDatabaseCredentials() from .env DATABASE_URL
    CH->>CH: refreshDatabaseConnection() [server, database]
    alt connection failed
        CH->>T: interactive DB prompts (defaults 127.0.0.1:3306)
        CH->>MB: optional createDatabase()
        CH->>EV: php bin/console uvdesk_wizard:env:update DATABASE_URL mysql://...
    end
    CH->>CH: compare doctrine:migrations:latest before/after (version, diff, status)
    alt version mismatch
        CH->>MB: doctrine:migrations:migrate + doctrine:fixtures:load
    end
    CH->>CH: PDO check uv_support_role / uv_user_instance / uv_user
    alt no super-admin
        CH->>DU: php bin/console uvdesk_wizard:defaults:create-user ROLE_SUPER_ADMIN ...
    end
    CH->>T: POST tracker (updates.uvdesk.com) — errors swallowed
```

---

## 6. Tracker Image-Cache Pipeline

**`ImageCacheController::getCachedImage`** (GET `/tracker/xhr/get/cacheImage`) is the only externally reachable image-cache entry:

1. Builds `siteUrl` from `request.schemeAndHttpHost + basePath`.
2. Calls `showImage(UVDESK_LOGO, siteUrl)` where `UVDESK_LOGO = 'https://updates.uvdesk.com/uvdesk-logo.png'`.
3. Resolves the returned file's real path, strips `<projectDir>/public` to form a relative path, and responds with a **JSON string** containing the absolute image URL.

**`UrlImageCacheService`** (a named service, injected via constructor) implements the cache:

- Cache directory `<projectDir>/public/cache/images`; key = `md5(url)`; file `<key>.png`; directory created with mode 0775 on demand.
- `isCacheExpired()` compares `filemtime` against a fixed 7-day TTL and unlinks stale entries before re-fetching.
- `cacheImage()` delegates to `ImageManager::make(['imageUrl' => $url, 'siteUrl' => $domain])` and saves the resulting image.

**`ImageManager`** extends `Intervention\Image\ImageManager`:

- `make($data)`: if both `imageUrl` and `siteUrl` pass `FILTER_VALIDATE_URL`, fetches via `initFromUrl`; otherwise falls back to `$driver->init($data)`.
- `initFromUrl()`: opens a PHP stream context with method GET, HTTP/1.1, and custom headers (`Accept-language: en`, `Domain: <domain>`, a Chrome user agent), reads the remote bytes (`@file_get_contents`), and initializes a driver-decoded image from binary. Both failure paths throw `Intervention\Image\Exception\NotReadableException`.
- `createDriver()`: instantiates `Intervention\Image\<Driver>\Driver` from `$this->config['driver']` (uppercased first letter, e.g. `GD` → `Intervention\Image\GD\Driver`) via `class_exists`; unknown drivers throw.

---

## 7. Root Routing and Navigation

`BaseController::base` is annotated `@Route("/", name="base_route")` and implements the "installed?" decision:

1. Queries `SupportRole` for `ROLE_SUPER_ADMIN` and `ROLE_ADMIN`; if either exists, queries `UserInstance` for users of those roles.
2. If owners/administrators exist: checks `kernel.getBundles()` for `UVDeskSupportCenterBundle`; when present and a `Website` with code `knowledgebase` exists, issues a 301 redirect to the `helpdesk_knowledgebase` route; otherwise (or additionally) redirects to `helpdesk_member_handle_login` when a `helpdesk` website exists.
3. Any exception (and the not-yet-installed path) forwards to `ConfigureHelpdesk::load`, exposing the web installer.

This creates the first-run state transition: **uninstalled → BaseController → wizard page → (install pipeline) → installed → redirects to member login or knowledge base**.

---

## 8. Error Handling

`ExceptionSubscriber` implements `EventSubscriberInterface`:

- `getSubscribedEvents()` returns `KernelEvents::EXCEPTION → [['onKernelException', 10]]` (priority 10).
- **Production-only behavior**: it early-returns unless `kernel.getEnvironment() == 'prod'`.
- Forks on exception code: 403 (with an authenticated non-anonymous token) renders a forbidden page; `NotFoundHttpException`/404 renders a 404 page; everything else renders a 500 page — each via `twig->render('errors/error.html.twig', {code, message, description})` and `$event->setResponse(...)`.
- The template (`templates/errors/error.html.twig`) is fully localized, resolves the knowledgebase website details via the `user_service` Twig global, and picks navigation links based on whether the current path contains `/en/member/`. Errors are rendered only for HTML responses per a `@TODO` comment (JSON/XML handling is noted as missing).

---

## 9. Configuration-Dependent Implementation Behavior

| Configuration | Effect on code paths |
|---|---|
| `kernel.environment` (`APP_ENV`) | `uvdesk_wizard:env:update` only runs in `dev`; `ExceptionSubscriber` renders custom error pages only in `prod`; `twig.debug`/`strict_variables` follow `kernel.debug` |
| `DATABASE_URL` in `.env` | Doctrine DBAL endpoint (`config/packages/doctrine.yaml` `env(DATABASE_URL)`); parsed by the console and rewritten by both wizard flavors; `.env.example` documents the granular `DB_*` variables but not `DATABASE_URL` itself |
| `uvdesk.site_url` (`config/packages/uvdesk.yaml`) | Domain reported to the tracker by both wizards |
| `uvdesk_site_path.member_prefix` / `knowledgebase_customer_prefix` | Security firewall patterns and access-control rules (`security.yaml`); the wizard's prefix step mutates them through the Core Framework service |
| PHP extensions (`redis`, `imap`, `mailparse`, `mysqli`) | Requirement checks (web) / connection warnings (console) |
| `MAILER_DSN`, `APP_SECRET`, `UV_SESSION_COOKIE_LIFETIME`, `MYSQL_*` (Docker) | Mailer transport, framework secret, session lifetime, and container DB provisioning respectively |
| `apps/` + `uvdesk_extensions.yaml` dir | Extension runtime mount point |

---

## 10. Data Contracts Summary

- **XHR responses**: requirement and credential checks return `status` (+ payload); env update returns `success`; the migrate/entity/super-user endpoints return `[]` with 200; website-prefix GET returns `{memberPrefix, knowledgebasePrefix, status}`, POST returns `{status}`; final prefix application returns `{memberLogin, knowledgebase}` (consumed by `wizard.js`; exact keys originate in the external Core Framework service).
- **`.env` mutations**: `DATABASE_URL=mysql://user:password@host:port/database[?serverVersion=...]` written by `uvdesk_wizard:env:update`; comment-preserving, case-uppercasing line rewrite.
- **Email/mail surface**: `templates/mail.html.twig` is a minimal XHTML layout exposing `{% block title %}`/`{% block metadata %}` and a raw `message` body; it is referenced as the default email template by `uvdesk.yaml` (`default.templates.email: mail.html.twig`).

---

## 11. Notable Implementation Irregularities

- **Console schema-check inverted branch**: `ConfigureHelpdesk` (console) treats *equal* migration versions as an error (returns 1) while treating *exceptions* as success ("up-to-date"), and references undefined `$databaseName` in that branch.
- **Missing runtime artifacts in-repo**: `src/Kernel.php` and `bin/console` are referenced but not checked in (generated by the Composer runtime recipe); `src/Entity/`, `src/Repository/`, `src/Migrations/` contain only `.gitignore` placeholders — entities/repositories/migrations are supplied by the bundles — and `apps/` is an empty extension mount point.
- **Client-side validation leakage**: `wizard.js` assigns `enteredField`/`enteredValue` without declaration (implicit globals), and mixes Backbone.Validation with hand-rolled regex validation on the account step.
- **Always-200 XHR contracts**: `migrateDatabaseSchemaXHR` and `populateDatabaseEntitiesXHR` compute `$resultCode` but ignore it, returning `[]`/200 unconditionally; the client infers failure solely from HTTP status. Similarly, tracker telemetry failures are silently swallowed in both the controller and console command.
- **No server-side re-validation**: `prepareSuperUserDetailsXHR` stores credentials without validation; all password/email/name policy enforcement for the web wizard is client-side only.
- The deterministic parser's symbol hits (`getPartialDetails`, `as`, `and`, `in`) originate in CHANGELOG markdown text, not executable code, and are not part of the design.
