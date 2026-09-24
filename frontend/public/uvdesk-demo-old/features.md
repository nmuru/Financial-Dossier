---
model: deepseek/deepseek-v4-flash-0731
---

# Features — UVdesk Community Skeleton (`uvdesk/community-skeleton`)

## 1. Feature-Surface Overview

This repository is the community-edition skeleton of the UVdesk helpdesk product: a Composer project that assembles the six UVdesk bundles (core framework, support center, mailbox component, automation bundle, extension framework, API bundle) and contributes the capabilities needed to bring an instance from a blank project to a configured, running helpdesk.

The externally meaningful capabilities implemented inside this repository are therefore concentrated in two areas:

1. **First-run installation and configuration** — a browser-based installation wizard, a terminal-based configuration command, and three hidden CLI commands that perform environment, database, schema, and account provisioning.
2. **Operational behavior of the composed application** — installation-state routing at the site root, production error pages, a tracker logo cache endpoint, localization catalog shipping, security/session configuration shaping the composed product, and containerized deployment packaging.

The helpdesk domain capabilities themselves (tickets, support center, mailbox-to-ticket ingestion, automation rules, API, extensions) are **composed in** as external bundle dependencies; they are documented and required by this repository but their implementation is not present in it. They are described in Section 6 as inherited product-level capability with the evidence boundary made explicit.

Actors and triggers:

| Actor | Trigger | Feature area |
|---|---|---|
| Web installer (human operator) | Opens the project's `public/` URL on an unconfigured instance | Installation wizard |
| Terminal operator | Runs `php bin/console uvdesk:configure-helpdesk` | CLI configuration command |
| Operator / developer | Runs hidden provisioning commands directly | Auxiliary CLI commands |
| Visitor / browser | Requests the site root of a configured instance | Installation-state routing |
| End users (customers, agents) | Any request during production operation | Production error pages (404/403/500) |
| Tracking script | Requests the cached logo endpoint | Tracker image cache |
| External service | Receives attribution records at `https://updates.uvdesk.com/api/updates` | Installation attribution (web + CLI) |

---

## 2. First-Run Installation and Provisioning

### 2.1 Installation-state detection and root routing

**Status: Implemented.**

The application root (`/`) does not serve a fixed page; a base controller decides what to show based on database and bundle state:

- If support roles (`ROLE_SUPER_ADMIN` / `ROLE_ADMIN`) and at least one administrator `UserInstance` exist, the instance is considered installed.
  - When the support-center bundle is loaded and a `knowledgebase` website record exists, the request is redirected (HTTP 301) to the knowledge-base front panel.
  - Otherwise it is redirected to the member (agent/admin) login route.
- If roles or administrator users are absent, or the database is unreachable (exceptions swallowed), the request is forwarded to the installation wizard controller, which renders the wizard page.

This produces the observable workflow: a fresh instance presents the installer at the site root, and a configured instance presents the product. The outcome depends on the state of entities (`uv_support_role`, `uv_user_instance`, `uv_website`) defined in the core-framework bundle.

### 2.2 Browser-based installation wizard

**Status: Implemented.**

The wizard is a single-page, client-driven flow rendered from `templates/installation-wizard/index.html.twig` and driven by `public/scripts/wizard.js`, a Backbone.js application loaded with jQuery, Underscore, and Backbone.Validation from CDNs. It presents five sequential stages with a progress header: **Welcome → System Requirements → Database Configuration → Admin Details → Website Configuration → Installation**.

Workflow and behavior:

- **Step gating.** The "Proceed" control remains disabled until the active stage's procedure reports completion; each stage validates live on input (debounced 400 ms), displays inline field errors, and supports backward navigation, cancellation, and Enter-key submission.
- **System Requirements stage.** Six criteria are evaluated concurrently against XHR endpoints: PHP version (≥ 7.0.0), PHP extensions (`imap`, `mailparse`, `mysqli`), PHP `max_execution_time` (≥ 30 seconds), `.env` file writability, `config/packages/uvdesk.yaml` and `uvdesk_mailbox.yaml` writability, and an advisory Redis check (warning only, cannot block). The server-side check attempts `chmod 0666` remediation on the `.env` and config files before confirming writability, and failed checks return remediation guidance (e.g., links for enabling extensions or raising the execution-time limit).
- **Database Configuration stage.** The installer enters server (default `127.0.0.1`), optional server version, port (default `3306`), username (default `root`), password, database name, and a "create database if not found" checkbox (enabled by default). Mandatory fields (server, username, password, database) gate submission. Submission verifies credentials server-side and, on success, buffers them in the server session (`DB_CONFIG`).
- **Admin Details stage.** Name, email, password, and confirmation are collected with client-side rules: name letters/spaces only, RFC-style email, password of ≥ 8 characters with at least two letters, one digit, and one special character, no spaces, and matching confirmation. Accepted values are buffered in the session (`USER_DETAILS`).
- **Website Configuration stage.** Member and customer URL prefixes (defaults `member` and `customer`) are pre-filled by fetching the current site configuration; both are mandatory, mutually different, and alphanumeric-only. Accepted values are buffered in the session (`PREFIXES_DETAILS`).
- **Completion.** After installation, a success screen presents the configured admin-panel and knowledge-base URLs as links.

The wizard page itself is the only UI delivered by this repository; its text is hardcoded English (not localized despite the shipped translation catalogs).

### 2.3 Installation execution pipeline

**Status: Implemented.**

"Install Now" triggers five sequential server-side stages, each surfaced in the progress header and each waiting for its predecessor's response:

1. **Load configurations** — connects with the buffered credentials, creates the database if absent (only when the create-database option is on), builds the MySQL DSN, and invokes the hidden `uvdesk_wizard:env:update` command to write `DATABASE_URL` into the project's `.env` (updated *in-place*, preserving unrelated lines and comments). A 500 response surfaces `.env` permission errors with remediation text.
2. **Load migrations** — runs the hidden `uvdesk_wizard:database:migrate` command, which detects an empty database (no tables) and, on a fresh install, creates the schema (`doctrine:schema:create`) and loads default fixtures; on an existing database it synchronizes migration metadata, versions and diffs the schema, and migrates to the latest version.
3. **Load entities** — runs `doctrine:fixtures:load --append` to populate the initial helpdesk dataset.
4. **Create super user** — creates an active, verified `ROLE_SUPER_ADMIN` user from the buffered details (name split into first/last, password encoded through the framework user-password encoder). Creation is idempotent: if an active super-admin already exists nothing happens; if the email exists with a member role, the existing instance is promoted to super-admin rather than duplicated.
5. **Load website prefixes** — persists the buffered member/customer prefixes through the UVdesk service and returns the resulting member-login and knowledge-base URLs, which populate the completion screen.

The same finalization step posts an attribution record (name, email, site domain) to the UVdesk tracker endpoint as a fire-and-forget call that must never break installation when the remote service is unavailable.

### 2.4 Terminal-based configuration command (`uvdesk:configure-helpdesk`)

**Status: Implemented.**

The CLI counterpart scans an existing setup and remediates mis-configuration through three examination stages with interactive prompts and ANSI-colored status output:

1. **Database connection.** Parses `DATABASE_URL` from `.env`, attempts a connection, and on failure interactively re-prompts for host, port, database, user, and hidden password, with retry loops, an option to create a missing database, and a non-zero exit on unrecoverable failure. Corrected credentials are written back through `uvdesk_wizard:env:update` (the rewrite is `mysql://user:pass@host:port/db`).
2. **Schema drift.** Compares the current migration version with mapping metadata (versioning, diff, status checks) and, when out of date, asks for consent before running `doctrine:migrations:migrate` (900-second timeout) followed by fixture reload (120-second timeout); declining aborts with a failure result.
3. **Super-admin existence.** Queries the `uv_support_role` / `uv_user_instance` / `uv_user` tables directly and, when no super-admin exists, interactively collects a validated email, name, and matching 8–32-character password, then creates the account via `uvdesk_wizard:defaults:create-user --no-interaction`.

On completion (or when an account already exists) the command posts the same attribution record to the UVdesk tracker. The command also normalizes file permissions (`chmod 0775`) on `.env`, `var/`, `config/`, `public/`, and `migrations/` at startup.

### 2.5 Hidden auxiliary CLI commands

**Status: Implemented.**

- `uvdesk_wizard:env:update <name> <value>` — updates or inserts an environment variable in the project-root `.env`, preserving other content, comments, and blank lines; refuses to run outside the `dev` environment (throws rather than mutating).
- `uvdesk_wizard:database:migrate` — initializes and seeds an empty database, or migrates an existing database to the latest Doctrine migration version.
- `uvdesk_wizard:defaults:create-user <role> [name] [email] [password]` — creates a user instance with the given support role; in interactive mode it validates email, prompts hidden passwords, and enforces 8–32-character length. Duplicate avoidance treats member-level roles (1–3) as interchangeable while the customer role (4) is distinct, and returns exit code 1 when an equivalent account already exists.

These commands are the implementation substrate for the wizard pipeline and the terminal command; they are also directly invocable by operators but are hidden from standard command listing.

### 2.6 Installation attribution to the UVdesk tracker

**Status: Implemented (external dependency).**

Both the web finalization stage and the terminal command post `{domain, email, name, country_code}` to `https://updates.uvdesk.com/api/updates` over cURL with JSON headers. Failures are swallowed (`catch` without rethrow), and both contexts treat the call as best-effort — the installation must succeed regardless of tracker availability.

---

## 3. Operational Behavior of the Composed Application

### 3.1 Production error pages (404 / 403 / 500)

**Status: Implemented.**

A kernel exception subscriber listens for the kernel exception event and, **only in the production environment**, replaces unhandled exceptions with branded pages:

- 403 with an authenticated session renders an "Access Forbidden" page; 403 for anonymous users is left for the framework's redirect-to-login handling.
- 404 renders "Page not Found"; other errors render a 500 "Internal Server Error" page.

The shared error template resolves the knowledge-base website branding (logo/name), offers home/support navigation links, and renders locale-translated messages via the translation filter. In non-production environments exceptions are not suppressed.

### 3.2 Tracker image cache endpoint

**Status: Implemented.**

`GET /tracker/xhr/get/cacheImage` returns the site-relative URL of a cached UVdesk logo:

- The canonical logo (`https://updates.uvdesk.com/uvdesk-logo.png`) is fetched with a browser-like HTTP client (with the requester's domain in headers), and a PNG copy is stored under `public/cache/images/<md5(url)>.png` (directory created on demand, mode 0775).
- The cached copy is served for up to 7 days; expired or missing files are deleted and re-fetched on the next request.
- The response is a JSON string of the site-relative image URL, so a remote tracker script can render the logo from the local installation.

### 3.3 Localization surface

**Status: Implemented (shipping/integration level).**

Twelve message catalogs ship under `translations/` (Arabic, Danish, German, English, Spanish, French, Hebrew, Italian, Polish, Brazilian Portuguese, Turkish, Chinese), wired through the translation package with English as the default locale and fallback. The wizard application itself is not localized (its strings are hardcoded English); the catalogs serve the composed bundles' user interfaces. The `app_locales` parameter and Twig globals expose the locale list to templates.

### 3.4 Web-server and front-controller integration

**Status: Implemented.**

The public document root (`public/`) contains the application front controller (`index.php` → `App\Kernel`) and an Apache `.htaccess` that rewrites all non-file requests to `index.php/<path>` (mod_rewrite) and preserves the `Authorization` header for API credential authentication. This makes the site routable as a clean-URL front controller and is a prerequisite for both the wizard at the site root and the composed product's routes.

### 3.5 Authentication and access-control baseline

**Status: Implemented (configuration level; enforcement by composed bundles).**

The security configuration defines the skeleton's portion of the product's authentication posture: a role hierarchy (`ROLE_CUSTOMER`, `ROLE_AGENT ⊂ ROLE_ADMIN ⊂ ROLE_SUPER_ADMIN`), form-login firewalls bound to the member and customer URL prefixes (distinct login/check/default-target/logout routes), an API firewall with a credential-based guard for `/api`, remember-me sessions (7-day `REMEMBERME` cookie), and access-control rules that keep the member panel behind agent-level roles, the customer panel behind `ROLE_CUSTOMER`, and explicitly public login/registration/password-recovery and the mailbox listener route. Because the prefixes are configurable, the wizard's website-prefix step directly influences this security surface.

### 3.6 Session and environment configuration

**Status: Implemented.**

Framework configuration binds sessions to environment variables (`UV_SESSION_COOKIE_LIFETIME`, default 1440 seconds; SameSite `lax`; `secure: auto`), secrets to `APP_SECRET`, mail transport to `MAILER_DSN`, and the Doctrine database layer to `DATABASE_URL` (MySQL `pdo_mysql` driver, default server version 5.7, `utf8mb4`, and a SQL-mode workaround for `ONLY_FULL_GROUP_BY`). The committed `.env` provides the operative variable template; `.env.example` is a stale, unrelated Laravel-style sample (see Section 7).

---

## 4. Product Composition and Deployment Delivery

### 4.1 Assembly of the helpdesk product from bundles

**Status: Implemented (composition); behavior inherited.**

The skeleton is the delivery vehicle for the full product: `composer.json` pins `uvdesk/core-framework ^1.1.7`, `uvdesk/support-center-bundle ^1.1.3`, `uvdesk/mailbox-component ^1.1.5`, `uvdesk/automation-bundle ^1.1.4`, `uvdesk/extension-framework ^1.1.2`, and `uvdesk/api-bundle ^1.1.4` (plus ~35 Symfony ecosystem packages) under Symfony Flex recipes. `config/bundles.php` registers all six bundles; `config/routes.yaml` declares the UVdesk package resources; and `config/services.yaml` autowires the skeleton's `src/` classes as services and controllers. Twig globals expose the bundles' services (user, ticket, email, reCAPTCHA, automations, extensibles, file system) to templates, along with defaults for avatar images, upload constraints, and the default email template — so the assembled application retains a consistent look, permission model, and template surface.

The observable outcome for the operator is a complete helpdesk installation (ticket handling, support center at the configured customer prefix, agent/admin panels at the member prefix) after running only the installer.

### 4.2 Extension hosting capability

**Status: Implemented.**

The extensions package pins the extension directory to `<project>/apps` (`uvdesk_extensions.dir`); an `apps/` directory ships (git-ignored) and is provisioned writable. This is the install target the extension framework uses for third-party add-ons. The extension framework bundle provides the installation/management behavior itself; this repository supplies the hosting location and the writable-directory contract.

### 4.3 Containerized deployment

**Status: Implemented.**

A Dockerfile packages an Ubuntu-based runtime with Apache 2, PHP 8.1 (`mod_php`, including the `imap`, `mailparse`, `mysql`, and `curl` extensions), a MySQL server, Composer, and gosu. At image build time, Composer installs all dependencies and the writable paths (`var/`, `config/`, `public/`, `migrations/`, `.env`) are chmodded to 775 with `uvdesk` ownership; a cache-clear step tolerates pre-install failure.

The container entrypoint restarts Apache and MySQL, and — when `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_ROOT_PASSWORD` are supplied — creates the database, grants the user privileges, resets the root password, and writes MySQL client configuration for both `root` and `uvdesk`; it then drops privileges from root to the `uvdesk` user via gosu before executing the container command. Without those variables it skips provisioning with a notice.

### 4.4 Default assets, email template, and domain defaults

**Status: Implemented.**

The skeleton ships default profile images (agent, customer, helpdesk) referenced from the core-framework bundle, a minimal HTML email wrapper (`templates/mail.html.twig`) as the default email template, and default ticket semantics (type `support`, status `open`, priority `low`) as configuration defaults — preconditions for the composed product's notifications and ticket creation to function without further tuning.

---

## 5. Feature Dependencies

The dependency structure among the implemented capabilities is direct and materially evidenced:

- **Root routing → database/bundle state:** the routing decision depends on core-framework entities and on the support-center bundle being loaded; when either is unavailable the wizard is shown. The wizard is therefore both a first-run surface and the system's failure fallback.
- **Wizard pipeline → hidden CLI commands → framework commands:** each install stage invokes `uvdesk_wizard:env:update`, `uvdesk_wizard:database:migrate`, `doctrine:fixtures:load`, or `uvdesk_wizard:defaults:create-user`; these in turn depend on Doctrine schema/migration commands and the security password encoder.
- **Terminal command → wizard commands:** `uvdesk:configure-helpdesk` reuses `uvdesk_wizard:env:update`, `uvdesk_wizard:defaults:create-user`, and Doctrine migration/fixture commands, so web and CLI provisioning converge on the same primitives.
- **Website prefixes → security and routing:** the prefixes collected in the wizard are persisted through the website service and simultaneously determine the member/customer login firewalls and access-control path patterns, so misconfiguring prefixes would shift the product's authentication surface.
- **Installation stages depend on prior stage state:** database credentials, admin details, and prefixes travel through the server session between stages; the finalization step requires all three.
- **Composed product → skeleton defaults:** the bundles depend on the extension directory, default assets/templates, translation catalogs, and service/route registration supplied by this repository.

---

## 6. Inherited Product-Level Capability (Documented, Not Verifiable in This Repository)

The README's feature list — unlimited agents/groups/teams/tickets, agent privileges, saved replies, ticket filtering, spam blocking, agent activity, marketing announcement, kudos, reCAPTCHA, standard automated workflows, agent notes, custom branding, logo/favicon changes, broadcasting, ticket forwarding, prepared responses, email notifications, effective search, multiple attachments, knowledge base/FAQ, ticket types and tags, email templates, API bundle, collaborators, ticket/thread editing and pinning — describes the **composed product**. The versioned changelogs (`CHANGELOG-1.0/1.1/1.2.md`) corroborate the evolution of these behaviors at product level (e.g., mailbox refresh converting email into tickets, collaborator replies, kudos, workflow-driven ticket transfer, mailbox delete-after-fetch options). However, none of these behaviors is implemented in this repository: no ticket, mailbox, automation, or API code is present. Within the skeleton's own scope these are **documented capabilities delivered by the pinned bundle dependencies**, not verifiable features. Any precise statement about their behavior must be reconstructed from the bundle repositories (`uvdesk/core-framework`, `uvdesk/support-center-bundle`, `uvdesk/mailbox-component`, `uvdesk/automation-bundle`, `uvdesk/extension-framework`, `uvdesk/api-bundle`).

---

## 7. Documentation versus Implementation Comparison

| Claim / artifact | Repository reality | Assessment |
|---|---|---|
| README "Features" list (tickets, mailbox, workflows, kudos, etc.) | Owned by the six bundle dependencies; no in-repo code | Documented intent at product level; consistent with the architecture but not verifiable here |
| README/install guide "User Friendly Web Installer" | Fully implemented wizard (controller, routes, client logic, templates) | Verified; this is the flagship in-repo feature |
| README login URLs (`/en/member/login`, `/en/customer/login`) | Prefixes default to `member`/`customer` in `uvdesk.yaml` and are set by the wizard | Verified defaults; final URLs depend on installation-time input |
| `.env.example` | Laravel-style variables (`APP_KEY`, `DB_HOST`, `MAIL_DRIVER`, …) that no consumed code reads | Stale artifact; the operative interface is the Symfony-style `.env` (`APP_ENV`, `APP_SECRET`, `DATABASE_URL`, `UV_SESSION_COOKIE_LIFETIME`, `MAILER_DSN`) |
| License: composer.json declares MIT; README/LICENSE.txt state OSL-3.0 | Inconsistent declarations | Documentation drift; does not affect behavior |
| PHP requirement: composer `^7.2.5 \|\| ^8.0`; README "8.1"; wizard gate ≥ 7.0; Docker PHP 8.1; guide demonstrates 8.2 | Enforcement floor is PHP ≥ 7.0 | Documented recommendation exceeds enforced minimum |
| Wizard localization | Wizard UI strings hardcoded English; only the composed bundles' UI uses the 12 catalogs | Verified limitation, not a gap in bundle behavior |
| Docker "persistent container" and "Vagrant" sections in README | Links to wiki pages; no Vagrantfile/container-compose artifacts in this repository | Documented externally; not verifiable from this repository |

---

## 8. Notable Constraints and Gaps

- **No in-repo tests.** No automated tests cover the wizard, CLI commands, routing, or error handling; behavioral guarantees rest on the implemented controllers, commands, and client-side validation, not on test evidence.
- **Unhandled failure semantics in the wizard client.** The client-side pipeline treats a failed stage's 500 response as a hard stop for that stage but continues the async chain; the error bar and retry-by-refresh guidance are the only recovery affordances. No automated resume state is persisted client-side beyond the server session.
- **Static asset delivery in development.** The wizard loads jQuery, Underscore, Backbone, and Backbone.Validation from CDNs, so the wizard UI depends on outbound CDN availability; the changelog references earlier issues around jQuery/Underscore versions (Issue #439), indicating this surface has been revision-sensitive.
- **Session-based wizard state.** Credentials and admin details are held in the server session between stages; a session loss forces the operator to restart the wizard (consistent with the retry-by-refresh guidance).
- **Redis is advisory only.** The "Redis extension loaded" check returns a warning with configuration links and never blocks installation — an intentional advisory design documented in both web and CLI paths.

---

## 9. Summary

What this system can meaningfully do, within its own evidence:

- **For an installing operator:** provision a complete helpdesk from a blank project through a guided web wizard (system checks → database → admin → prefixes → five-stage install), or remediate a broken/aging instance from the terminal; both paths converge on the same hidden provisioning commands, persist configuration to `.env` and package YAML, create the super-admin, set the panels' URL prefixes, and record installation attribution with the UVdesk tracker without letting tracker failures block installation.
- **For a deployed instance:** route the site root according to install state, render branded 404/403/500 pages in production, serve a cached UVdesk logo URL to tracker scripts, apply the authentication/session baseline that protects the composed panels and API, and provide the localization catalogs, extension directory, defaults, and bundle registration on which the composed product depends.
- **For deployers and integrators:** obtain the entire product as a Composer-assembled project and as a Docker image with automated database provisioning, and host third-party extensions through a dedicated writable directory.

The helpdesk domain features (tickets, customer portal, email ingestion, automation, API, extensions) are genuinely delivered by this distribution but implemented in its bundle dependencies; within the skeleton, they are composed-in rather than built-in, and their detailed behavior must be evidenced from those repositories.
