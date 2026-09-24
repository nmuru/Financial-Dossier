---
model: x-ai/grok-4.6
---

# Design / Architecture Pattern Description

## Document Title
- **UVdesk Community Skeleton — Recurring Design Patterns**  
  This document describes the design patterns and recurring structural approaches that are actually present in the `uvdesk/community-skeleton` host application. The repository is a Symfony composition root: it wires, configures, installs, themes, translates, and deploys a helpdesk assembled from Composer packages. Domain object models and most runtime behaviors live in those packages, not in local `src/` types.

## 1. Pattern Identification
### 1.1 Pattern Name
The dominant, repository-wide pattern is **Composition Root with Bundle Composition** (a host skeleton that assembles independently versioned Symfony bundles). Supporting patterns that appear in local code and configuration are:

- **Plugin / extension directory** (configuration-driven add-on loading)
- **Routing resource plugin** (host implements a bundle-defined routing contract)
- **Front controller with installation-state dispatch**
- **Installation wizard as a sequential bootstrap workflow**
- **Command** (console operations reused from HTTP and CLI)
- **Event subscriber** (kernel exception presentation)
- **Library adapter plus cache-aside** (remote image fetch and local file cache)
- **Configuration-driven multi-firewall security** (actor-separated authentication)

Textbook creational patterns (Factory, Abstract Factory, Builder) and data-access patterns (Repository, Unit of Work) are **not implemented in this skeleton**. Empty `src/Entity` and `src/Repository` directories are placeholders; Doctrine mappings and repositories used at runtime belong to vendor packages such as Core Framework.

### 1.2 Pattern Classification
| Pattern | Classification |
| --- | --- |
| Composition root / bundle composition | Architectural-adjacent / structural |
| Plugin / extension directory | Structural / integration |
| Routing resource plugin | Structural (host implements a vendor interface) |
| Front controller + state-based dispatch | Behavioral / presentation |
| Installation wizard | Repository-specific workflow |
| Command (console + in-process invocation) | Behavioral |
| Kernel exception subscriber | Behavioral (Observer-style, framework-adapted) |
| Image manager adapter + file cache | Structural + data/integration |
| Multi-firewall security configuration | Integration / configuration, not a local Strategy hierarchy |

### 1.3 Intent
Keep product capabilities in replaceable Composer packages while this project remains the **deployable shell**: kernel bootstrap, YAML integration, security and persistence wiring, first-run setup, localization catalogs, public assets, and Docker packaging. Local PHP exists mainly to **bootstrap an unconfigured helpdesk** and to **adapt a few host-only concerns** (custom routes, branded error pages, logo cache).

### 1.4 Also Known As
Skeleton application, host application, composition root, Symfony Flex project, modular monolith assembled at Composer time.

### 1.5 Scope / Applicability
These patterns apply to this repository as a **packaging and wiring layer**. They do not describe ticket lifecycle, mailbox IMAP/SMTP engines, automation rules, or extension APIs. Those concerns are documented as **owned by required packages** (`uvdesk/core-framework`, `uvdesk/support-center-bundle`, `uvdesk/mailbox-component`, `uvdesk/automation-bundle`, `uvdesk/extension-framework`, `uvdesk/api-bundle`) and are only **configured** here.

## 2. Context
### 2.1 Problem Context
A full helpdesk needs tickets, agents, customers, mailboxes, automations, APIs, and a support portal. Those features evolve independently and are contributed across several GitHub projects. Operators still need **one installable application**: a single Composer project, one web front controller, one configuration tree, one installer, and one container image.

### 2.2 System Context
- **Host:** `uvdesk/community-skeleton` (`type: project` in Composer), PSR-4 `App\` → `src/`.
- **Assembled product packages:** listed under `flex-require` and registered in `config/bundles.php` as UVDesk Core, Automation, Extension Framework, Mailbox, Support Center, and API bundles.
- **Framework:** Symfony Flex (^5.4 extra), Doctrine ORM, Twig, Mailer/Swiftmailer, Security.
- **Actors visible in this repo:** installer/operator (wizard, console, Docker), member/agent vs customer (security firewalls and site-path prefixes), extension author (`apps/` directory).
- **Local runtime surface:** installation wizard (Twig + Backbone.js), wizard XHR routes, image-cache route, exception HTML, translations, Docker/Apache entrypoint.

### 2.3 Forces / Constraints
- Product logic must stay in versioned bundles so community contributions can target the correct repository.
- The host must still be runnable after `composer install` and must detect **unconfigured vs configured** state.
- First-run setup must write `.env`, create/migrate the database, load fixtures, and create a super-admin without requiring operators to run a long manual command sequence.
- Symfony conventions (YAML packages, autowiring, Flex recipes) replace hand-written factories in the skeleton.
- Empty local entity/repository trees must not collide with vendor mappings (`doctrine.yaml` still maps `App\Entity` for future host entities).

## 3. Problem
### 3.1 Problem Statement
How can a helpdesk be delivered as **one deployable Symfony application** while keeping domain modules independently developed, configured by YAML rather than host classes, and bootstrapped by a guided installer rather than by domain code living in `App\`?

### 3.2 Symptoms / Recurring Situation
- Feature ownership is explicitly split across sibling repositories in README and contributing docs.
- `config/bundles.php` contains only UVDesk product bundles (framework bundles are expected from Flex recipes / generated kernel, not duplicated as domain code here).
- `config/routes.yaml` does not list controllers; it declares **custom route types** `uvdesk` and `uvdesk_extensions`.
- Almost all local PHP is wizard, console, exception handling, or image cache—not tickets or mail.
- `src/Entity` and `src/Repository` contain only `.gitignore` files.

### 3.3 Conditions Under Which the Problem Occurs
These structures appear whenever the application is installed, configured, or started: Composer assembly, kernel boot (bundle and route loading), first HTTP hit to `/`, wizard XHR steps, CLI `uvdesk:configure-helpdesk`, and Docker entry.

## 4. Applicability
### 4.1 When to Apply
- Assembling a product from multiple Symfony bundles with a thin host.
- Exposing host-only setup UX while domain modules remain vendor code.
- Discovering routes from bundles via a shared `RoutingResourceInterface`.
- Reusing the same setup operations from a web wizard and from CLI.
- Caching a remote branding asset without pulling that concern into Core.

### 4.2 When Not to Apply
- Do not treat this skeleton as the place to implement Repository, Strategy, or Observer for tickets, automations, or mailboxes.
- Do not treat GitHub issue templates, `SECURITY.md`, or `FUNDING.yml` as Adapter implementations; they are community process artifacts.
- Do not treat Symfony autowiring, Twig, or translation catalogs by themselves as application-invented patterns.
- Do not label empty `src/Repository` as the Repository pattern.

### 4.3 Preconditions
Composer installation of UVDesk packages, a Symfony kernel capable of loading `config/bundles.php` and package YAML, and (for the wizard) writable `.env` and `config/packages` files. Domain patterns inside vendor packages are **out of scope** of this repository’s source tree.

## 5. Solution
### 5.1 Solution Overview
The host **registers bundles, supplies YAML as the integration API, and implements a small App layer** for bootstrap and a few host-only endpoints. Installation is a **wizard that orchestrates Commands**. After configuration, `BaseController` **dispatches** the root URL to the support center or member login based on database and bundle presence. Cross-cutting HTML errors use a **kernel exception subscriber**. A **subclassed image manager** plus file cache serves a remote logo.

### 5.2 Structure
```
Composer (flex-require UVDesk + Symfony packs)
        │
        ▼
   Kernel / bundles.php  ── registers Core, Automation, Extension, Mailbox, Support Center, API
        │
        ├── config/packages/*.yaml   (uvdesk, mailbox, extensions, security, doctrine, mailer, twig, translation)
        ├── config/routes.yaml       type: uvdesk | uvdesk_extensions
        └── App\Routing\RoutingResource  implements Core RoutingResourceInterface
                └── src/Resources/config/routes.yaml  (wizard + image cache)

HTTP /  ── App\Controller\BaseController
              ├── if roles + admin users + websites exist → redirect (knowledgebase or member login)
              └── else → forward ConfigureHelpdesk::load (wizard)

Wizard XHR ── ConfigureHelpdesk ── in-process Console Application::run
                                      ├── uvdesk_wizard:env:update
                                      ├── uvdesk_wizard:database:migrate
                                      └── doctrine:fixtures:load

CLI ── uvdesk:configure-helpdesk / uvdesk_wizard:* 

Kernel EXCEPTION ── App\EventListener\ExceptionSubscriber → Twig errors/error.html.twig

GET /tracker/xhr/get/cacheImage ── ImageCacheController → UrlImageCacheService → ImageManager (Intervention subclass)
```

### 5.3 Participants / Components
**Composition root**
- `composer.json` — project type; `flex-require` pulls UVDesk packages and Symfony components.
- `config/bundles.php` — enables UVDesk product bundles for all environments.
- `config/packages/uvdesk.yaml`, `uvdesk_mailbox.yaml`, `uvdesk_extensions.yaml` — host-side configuration of vendor features.
- `config/services.yaml` — autowires `App\` (excluding Entity, Migrations, Kernel).
- `public/index.php` — runtime front controller creating `App\Kernel`.

**Plugin / extensions**
- `uvdesk_extensions.dir: '%kernel.project_dir%/apps'` — filesystem location for add-ons.
- `UVDeskExtensionFrameworkBundle` — implementation lives in the extension package; the host only points at `apps/`.

**Routing resource**
- `App\Routing\RoutingResource` — `getResourcePath()` / `getResourceType()` for YAML routes.
- `Webkul\UVDesk\CoreFrameworkBundle\Definition\RoutingResourceInterface` — contract defined in Core, implemented here.

**Installation dispatch and wizard**
- `App\Controller\BaseController` — root route `base_route`.
- `App\Controller\ConfigureHelpdesk` — wizard page and XHR steps.
- `App\Console\Wizard\ConfigureHelpdesk`, `MigrateDatabase`, `DefaultUser`.
- `App\Console\EnvironmentVariables` — `uvdesk_wizard:env:update`.
- `templates/installation-wizard/index.html.twig`, `public/scripts/wizard.js` (Backbone views).

**Exception handling**
- `App\EventListener\ExceptionSubscriber`.

**Image cache**
- `App\Controller\ImageCache\ImageCacheController`, `ImageManager`, `App\Service\UrlImageCacheService`.

**Security wiring (configuration only)**
- `config/packages/security.yaml` — role hierarchy, `user.provider`, API credential provider, firewalls `back_support`, `uvdesk_api`, `customer`.

### 5.4 Responsibilities
| Participant | Responsibility |
| --- | --- |
| Skeleton host | Assemble packages, hold env and YAML, expose installer and static assets |
| UVDesk bundles | Domain services, entities, routes, UI (not present as source in this repo) |
| `RoutingResource` | Publish host wizard/cache routes into the Core routing loader |
| `BaseController` | Choose wizard vs live helpdesk from DB/bundle state |
| Wizard controller/commands | Validate environment, persist `DATABASE_URL`, migrate/load schema, create super-admin |
| `ExceptionSubscriber` | Replace default exception output with branded HTML in `prod` |
| Image cache types | Fetch remote logo with a custom `Domain` header and cache under `public/cache/images` |
| Security YAML | Separate member, customer, and API authentication channels |

### 5.5 Collaborations / Interactions
- **Bundle composition:** Flex installs packages; `bundles.php` activates them; package YAML binds parameters (site URL, upload manager id, mailbox IMAP/SMTP placeholders, extension dir, locale list).
- **Route aggregation:** `config/routes.yaml` uses loaders `type: uvdesk` and `type: uvdesk_extensions`. Host routes are not listed there; they are contributed through `RoutingResource` → `src/Resources/config/routes.yaml`.
- **Wizard ↔ commands:** HTTP actions construct `Symfony\Bundle\FrameworkBundle\Console\Application` and `run()` commands with `ArrayInput` and `NullOutput`, so the same operations exist as CLI.
- **Wizard ↔ session:** Database and super-user details are stored in `$_SESSION` between XHR steps (procedural session, not a State object graph).
- **BaseController ↔ Core entities:** Uses Doctrine repositories for `SupportRole`, `UserInstance`, and `Website` **from Core Framework**, then Symfony `forward`/`redirectToRoute`.
- **Image path:** Controller asks `UrlImageCacheService` for a path; the service may call `ImageManager::make()` which HTTP-GETs a URL with a `Domain` header.

### 5.6 Behavioral Flow
**Unconfigured application (HTTP)**  
1. Request hits `/` (`base_route`).  
2. `BaseController` tries to load `ROLE_SUPER_ADMIN` / `ROLE_ADMIN`. If missing or no matching users, or on exception, it forwards to `ConfigureHelpdesk::load`.  
3. Wizard UI (`wizard.js`) posts to `/wizard/xhr/*` in order: requirements, database, super-user, website config, write `.env`, migrations, fixtures, create super-user, website configuration.  
4. `updateConfigurationsXHR` may create a MySQL database, then runs `uvdesk_wizard:env:update`.  
5. `migrateDatabaseSchemaXHR` runs `uvdesk_wizard:database:migrate` (fresh schema + fixtures, or migrations).  
6. Subsequent `/` sees roles and users; if Support Center bundle is loaded and a `knowledgebase` website exists, redirect there; otherwise redirect to member login.

**Configured request (errors)**  
In `prod`, `ExceptionSubscriber` listens to `KernelEvents::EXCEPTION` and renders 403/404/500 Twig pages (403 only when a non-anonymous user is present).

**CLI repair**  
`uvdesk:configure-helpdesk` interactively re-checks database connectivity, can rewrite `DATABASE_URL` via a subprocess, and migrates schema—parallel to the web wizard, not a second domain model.

## 6. Representation
### 6.1 Structural Diagram
```
                    ┌─────────────────────────────────────┐
                    │     uvdesk/community-skeleton       │
                    │  (composition root / host)          │
                    │  config/, public/, translations/,   │
                    │  App\ wizard, routing, errors, cache│
                    └──────────────┬──────────────────────┘
                                   │ requires / registers
          ┌───────────────┬────────┴────────┬──────────────┬─────────────┐
          ▼               ▼                 ▼              ▼             ▼
   Core Framework   Support Center     Mailbox      Automation    Extension FW
   (+ API bundle)   (customer portal)  (IMAP/SMTP)  (workflows)   (apps/)
```

### 6.2 Interaction / Behavioral Diagram
```
Browser                BaseController              ConfigureHelpdesk           Console commands
  │                         │                              │                         │
  │ GET /                   │                              │                         │
  │────────────────────────►│ query SupportRole/User/Website                         │
  │                         │── if not installed ─────────►│ GET wizard page         │
  │                         │                              │◄── render Twig          │
  │ POST .../configurations │                              │ run env:update ────────►│
  │ POST .../migrations     │                              │ run database:migrate ──►│
  │ POST .../entities       │                              │ fixtures:load ─────────►│
  │ GET / (again)           │ redirect knowledgebase/login │                         │
```

### 6.3 Example Configuration / Pseudocode
Bundle registration (actual host list):

```php
return [
    UVDeskCoreFrameworkBundle::class => ['all' => true],
    UVDeskAutomationBundle::class => ['all' => true],
    UVDeskExtensionFrameworkBundle::class => ['all' => true],
    UVDeskMailboxBundle::class => ['all' => true],
    UVDeskSupportCenterBundle::class => ['all' => true],
    UVDeskApiBundle::class => ['all' => true],
];
```

Host routing contribution:

```php
class RoutingResource implements RoutingResourceInterface {
    public static function getResourcePath() {
        return __DIR__ . "/../Resources/config/routes.yaml";
    }
    public static function getResourceType() {
        return RoutingResourceInterface::YAML_RESOURCE;
    }
}
```

In-process command (wizard):

```text
Application(kernel).run(ArrayInput{ command: uvdesk_wizard:database:migrate }, NullOutput)
```

Extension point (host config, implementation in vendor):

```yaml
uvdesk_extensions:
    dir: '%kernel.project_dir%/apps'
```

Upload manager is selected **by service id** in YAML (`Webkul\UVDesk\CoreFrameworkBundle\FileSystem\UploadManagers\Localhost`), which is a configuration-time strategy **defined in Core**, not a local Strategy class hierarchy.

## 7. Consequences
### 7.1 Benefits
- Clear **host vs product** split: this repo changes wiring, installer, Docker, i18n, and a few host routes; ticket/mailbox/automation work belongs in sibling packages.
- Operators get a **single Composer project** and a **user-facing installer**.
- Bundles can contribute routes through a shared interface without the host enumerating every path.
- The same migration and env-update operations work from HTTP and CLI.
- Actor-specific security is expressed in one YAML file (member prefix, customer prefix, `/api`).

### 7.2 Costs
- Understanding runtime behavior requires **vendor sources** not present in this tree.
- Wizard HTTP handlers are large, procedural, and duplicate CLI logic in places (`ConfigureHelpdesk` controller vs `Console\Wizard\ConfigureHelpdesk`).
- Direct `$_SESSION` usage bypasses Symfony’s session abstraction.
- `Application::run` from a web request couples HTTP latency to console commands and makes error handling coarse (often empty JSON on success).
- `ExceptionSubscriber` still uses `ContainerInterface` service location and mixed `getThrowable`/`getException` compatibility.

### 7.3 Trade-offs
Convention and YAML replace explicit factories in the host, which reduces local pattern surface but also hides creation and extension points until one reads vendor bundles. Duplicated web/CLI wizard paths favor operator convenience over a single orchestration service.

### 7.4 Quality Attribute Implications
- **Modularity / evolvability:** high at package boundaries; low cohesion inside wizard controllers.
- **Deployability:** Docker image, Apache vhost, entrypoint, and Composer install are first-class.
- **Extensibility:** `apps/` + Extension Framework; host does not define local plugin interfaces.
- **Observability / error UX:** production HTML errors are centralized; JSON/API error shaping is explicitly unfinished (`@TODO` on response type).
- **Testability:** no application tests in-tree; wizard logic is hard to unit test as written.

### 7.5 New Constraints / Risks
- Kernel class is referenced (`App\Kernel` from `public/index.php`) as a Flex/runtime artifact; host-only analysis cannot fully describe bundle boot without that generated kernel.
- Empty `App` Doctrine mapping may confuse contributors expecting entities here.
- Image cache writes under `public/cache/images` and subclasses Intervention’s manager; driver config is assumed rather than injected.
- `uvdesk_wizard:env:update` refuses non-`dev` environments, which constrains how the web wizard can be used if the kernel environment is not `dev`.

## 8. Implementation Considerations
### 8.1 Implementation Guidance
Treat `src/` as **bootstrap and host adapters**, not a domain layer. New helpdesk features should land in the appropriate UVDesk package unless they are installer, packaging, translation, or host-only routes. When adding host routes, follow `RoutingResource` + YAML rather than only `config/routes.yaml` controller maps. When adding setup steps, prefer a console command that the wizard can invoke, matching existing `uvdesk_wizard:*` names.

### 8.2 Technology Considerations
- Symfony Flex endpoints include UVDesk recipes (`extra.symfony.endpoint`), so recipe-generated files participate in composition.
- Autowire/autoconfigure in `config/services.yaml` is **framework DI convention**, not an application-specific Inversion of Control framework.
- Doctrine `auto_mapping` plus vendor entities is the persistence approach; this repo does not implement repositories.
- Client wizard uses **Backbone.js views** and Underscore templates—localized MVC for installation only, not the main helpdesk UI (README also cites Backbone for the product, which is served from bundles).

### 8.3 Common Pitfalls
- Inferring Adapter from `.github/*` filenames or from “there is a wrapper.”
- Calling `src/Repository` the Repository pattern.
- Assuming Observer/event-driven automations are implemented here because `automation-bundle` is required.
- Assuming Strategy because `evaluateSystemRequirements` switches on a string (`specification`); that is a procedural dispatcher, not interchangeable strategy objects.
- Assuming a full helpdesk is implemented by the skeleton files alone; Composer packages are required.

### 8.4 Variations
- **Web wizard vs CLI wizard:** same goals, different UX; CLI uses `symfony/process` to spawn `bin/console` in some steps, HTTP uses in-process `Application::run`.
- **Fresh vs existing database:** `MigrateDatabase` branches: empty table list → `doctrine:schema:create` + fixtures; otherwise migrations sync/diff/migrate.
- **Optional Support Center:** `BaseController` only redirects to knowledgebase if `UVDeskSupportCenterBundle` is among kernel bundles.
- **ImageManager** is a **partial Adapter**: it extends Intervention’s `ImageManager` and overrides `make()` / URL init rather than wrapping a foreign interface behind a new port.

## 9. Known Uses / Examples
### 9.1 Known Uses
- **Composition root:** entire project layout; README describes “project skeleton packaged along with the bare essential utilities.”
- **Bundle composition:** `config/bundles.php` and `flex-require` UVDesk packages.
- **Config as integration API:** `uvdesk.yaml` (site URL, `upload_manager.id`, default ticket fields, email template), `uvdesk_mailbox.yaml` (IMAP/SMTP mailbox slots), `security.yaml` (three firewalls).
- **Plugin directory:** `apps/` + `uvdesk_extensions.yaml`.
- **Routing plugin:** `App\Routing\RoutingResource`.
- **Front controller dispatch:** `BaseController::base`.
- **Command:** `uvdesk:configure-helpdesk`, `uvdesk_wizard:env:update`, `uvdesk_wizard:database:migrate`, `uvdesk_wizard:defaults:create-user` (hidden).
- **Event subscriber:** `ExceptionSubscriber`.
- **Adapter + cache-aside:** `ImageManager` + `UrlImageCacheService` (MD5 key, one-week TTL, PNG files).
- **i18n resource catalogs:** `translations/messages.*.yml` with `app_locales` in `uvdesk.yaml`—Symfony translator convention, not a custom pattern.

### 9.2 Representative Examples
- Root URL installation gate in `App\Controller\BaseController`.
- Wizard route table in `src/Resources/config/routes.yaml`.
- In-process command execution in `ConfigureHelpdesk::migrateDatabaseSchemaXHR` and `updateConfigurationsXHR`.
- Production 404/500/403 rendering in `ExceptionSubscriber::onKernelException`.
- Remote logo constant `ImageCacheController::UVDESK_LOGO` and cache path `public/cache/images`.

## 10. Related Patterns / Alternatives
### 10.1 Related Patterns
- **Dependency injection:** used via Symfony’s container (`autowire`/`autoconfigure`); not reimplemented.
- **Template Method:** Symfony `Command` lifecycle (`configure` / `initialize` / `interact` / `execute`) in wizard commands—framework convention.
- **Facade:** `MigrateDatabase` sequences several Doctrine commands; it is an orchestrating command, not a broad subsystem facade.
- **Front controller:** `public/index.php` is the Symfony front controller; `BaseController` is an additional **application-level dispatcher**.
- Patterns that **likely exist in vendor packages but are not evidenced here:** domain Repository, event-driven automation (Observer), mailbox channel adapters, extension service providers.

### 10.2 Alternative Solutions
- Monolithic in-repo domain instead of Composer bundles (rejected by the skeleton/package split).
- A single installer service class instead of HTTP controller + multiple commands (not how the code is structured).
- Symfony Messenger instead of in-process console for long setup steps (not present).
- Native Intervention URL init instead of a subclass with custom headers (the subclass exists specifically to send `Domain` and User-Agent).

### 10.3 Pattern Combinations
Composition root **plus** plugin directory **plus** custom routing type is the core combination. The wizard combines **Front Controller dispatch**, **Command**, and a **stepwise UI** (Backbone). Image handling combines **inheritance-based adapter** and **cache-aside**. Security YAML combines role hierarchy with multiple firewalls (configuration analog of strategy selection, without local strategy types).

## 11. Decision / Rationale
### 11.1 Decision Context
UVdesk Community is documented as service-oriented and extensible, built on Symfony, with modules published as separate packages. This repository’s job is to **ship an installable helpdesk** without becoming the canonical location of those modules.

### 11.2 Alternatives Considered
Not recorded as ADRs in this tree. The implementation implies rejection of a fat `App` domain layer and of host-local factories/providers for tickets, mail, and automations. Community process (issue templates, contributing guide) steers feature work to Core, Support Center, Mailbox, Automation, and Extension Framework rather than inventing parallel types here.

### 11.3 Selection Rationale
YAML and bundle registration scale with Symfony Flex and independent package versions. A wizard in the host is appropriate because **only the host owns `.env`, `config/packages`, and the Composer project**. Implementing `RoutingResourceInterface` is the least-invasive way to add installer routes into a loader owned by Core. Exception HTML and logo cache are presentation/host concerns and are therefore local, without pretending to be domain services.

**Patterns not claimed:** Repository (empty local repos; vendor entities only), Factory/Abstract Factory, Observer for domain events, Strategy as a type hierarchy, Adapter for GitHub metadata files.

## 12. References
- Project identity and module split: `composer.json`, `README.md`, `.github/CONTRIBUTING.md`
- Bundle composition: `config/bundles.php`
- Integration configuration: `config/packages/uvdesk.yaml`, `uvdesk_mailbox.yaml`, `uvdesk_extensions.yaml`, `security.yaml`, `doctrine.yaml`, `config/services.yaml`, `config/routes.yaml`
- Host routing plugin: `src/Routing/RoutingResource.php`, `src/Resources/config/routes.yaml`
- Installation dispatch and wizard: `src/Controller/BaseController.php`, `src/Controller/ConfigureHelpdesk.php`, `src/Console/Wizard/*`, `src/Console/EnvironmentVariables.php`, `public/scripts/wizard.js`
- Exception subscriber: `src/EventListener/ExceptionSubscriber.php`
- Image adapter/cache: `src/Controller/ImageCache/*`, `src/Service/UrlImageCacheService.php`
- HTTP entry: `public/index.php`
- Deployment wrapping: `Dockerfile`, `.docker/bash/uvdesk-entrypoint.sh`
