---
model: moonshotai/kimi-k3
---

# Architecture Evolution and Future Direction

## 1. Document Title

**Architecture Evolution and Future Directions — UVdesk Community Skeleton (`uvdesk/community-skeleton`)**

This document identifies realistic, evidence-based future directions for the UVdesk Community Skeleton: the installable Symfony project skeleton that packages, configures, and distributes the UVdesk open-source helpdesk. It separates observed current-state constraints from proposed evolution, and prioritizes directions by impact on the system's viability as a secure, deployable helpdesk distribution.

## 2. Executive Summary

### 2.1 Current Position

This repository is the **assembly, configuration, and deployment layer** of the UVdesk helpdesk — not the product logic itself. It wires six external `uvdesk/*` Composer packages (Core Framework, Support Center bundle, Mailbox Component, Automation bundle, Extension Framework, API bundle) into a working Symfony 5.4 application, and ships a setup wizard, twelve translation catalogs, an all-in-one Docker image, and release changelogs (1.0.x → 1.1.8 → nascent 1.2.x).

Its current technology position carries **concentrated lifecycle risk**: the stack is pinned to Symfony 5.4 and PHP 8.1 (both at or near end of support), retains multiple deprecated or abandoned dependencies, assumes MySQL 5.7 (EOL October 2023), and ships a Docker image built on an unpinned `ubuntu:latest` base. The skeleton has **no automated verification of its own** — no CI pipeline and no tests — even though installation regressions are a recurring theme in its own changelog.

### 2.2 Target Direction

A staged evolution, in order of leverage:

1. **Foundation hygiene** — retire deprecated/abandoned dependencies, repair configuration drift, and add distribution-level smoke verification.
2. **Platform modernization** — move the pinned runtime to actively supported PHP (8.2+) and Symfony (6.4/7.x), which requires migrating the legacy security configuration, Doctrine annotations, and SwiftMailer coexistence out of the skeleton.
3. **Deployment topology evolution** — harden and split the container image (application vs. database), enable stateless operation via externalized storage, and reduce dependence on deprecated platform extensions (PHP IMAP).

### 2.3 Major Drivers

- **Security exposure from EOL runtimes**: `composer.json` constrains the project to Symfony `^5.4` and PHP `^7.2.5 || ^8.0`; the Dockerfile installs PHP 8.1, whose security support ends December 2025; Symfony 5.4 security support ends November 2025.
- **Hard upgrade blockers in this repository**: `config/packages/security.yaml` uses constructs removed in Symfony 6 (`encoders`, `anonymous: ~`, `guard` authenticators, `IS_AUTHENTICATED_ANONYMOUSLY`), making the skeleton itself a blocker to framework upgrades.
- **Recurring installation fragility**: the changelog documents installation failures across releases (issues #438, #410, #805; "database connection related issues" in 1.1.7), yet nothing automatically verifies that a release assembles into a working install.
- **Database platform obsolescence**: `config/packages/doctrine.yaml` declares `server_version: '5.7'` and the entrypoint script uses pre-MySQL-8 provisioning syntax.

### 2.4 Key Evolution Themes

- **Lifecycle currency over feature growth** — the skeleton's risk is dependency and platform obsolescence, not missing features.
- **Verification of the distribution boundary** — the skeleton's unique responsibility (assembly, packaging, install) is precisely what is currently untested.
- **Statelessness and deployment reproducibility** — the container story exists but is monolithic and non-reproducible.
- **Deliberate boundary management** — the skeleton absorbs churn from six external packages and external email/database infrastructure; managing those boundaries is its core future work.

## 3. Current-State Baseline

### 3.1 Current Architecture / System State

- **Skeleton architecture**: no application logic beyond setup-wizard assets (`public/scripts/wizard.js`, `public/css/`), YAML configuration under `config/packages/`, routing in `config/routes.yaml` and `src/Resources/config/routes.yaml`, and translations. All functional behavior is delivered by six `uvdesk/*` packages pinned in `composer.json` (`core-framework ^1.1.7`, `mailbox-component ^1.1.5`, `api-bundle ^1.1.4`, `automation-bundle ^1.1.4`, `support-center-bundle ^1.1.3`, `extension-framework ^1.1.2`).
- **Symfony Flex distribution** with a **custom recipes endpoint** (`https://api.github.com/repos/uvdesk/recipes/contents/index.json`) ahead of `flex://defaults`, making the build dependent on a project-owned GitHub recipes repository.
- **Runtime wiring**: Doctrine DBAL over `pdo_mysql` (`%env(DATABASE_URL)%`), Symfony Mailer over `%env(MAILER_DSN)%`, per-mailbox IMAP/SMTP configuration in `config/packages/uvdesk_mailbox.yaml` (empty by default), and local-filesystem attachment storage via `Webkul\UVDesk\CoreFrameworkBundle\FileSystem\UploadManagers\Localhost`.
- **Security model**: form-login firewalls for agents (`/member`) and customers (`/customer`), a Guard-authenticator API firewall (`^/api`), and a four-role hierarchy (`ROLE_SUPER_ADMIN` → `ROLE_ADMIN` → `ROLE_AGENT`; `ROLE_CUSTOMER`) — all expressed in the legacy pre-Symfony-5.4 security configuration dialect.
- **Deployment**: a single root `Dockerfile` producing an all-in-one image (Ubuntu base, Apache + PHP 8.1 via `ppa:ondrej/php`, and `mysql-server` in the same image), with a bash entrypoint that starts both services, provisions the database as root, and steps down to a non-root `uvdesk` user via gosu.

### 3.2 Current Capabilities

- Guided web-based and CLI-based installation (`uvdesk:configure-helpdesk`, web wizard) with documented database-version handling.
- Multilingual delivery across twelve locales (en, fr, it, de, da, ar, es, tr, zh, pl, he, pt_BR), with he and pt_BR added in recent releases (1.1.7, 1.1.8).
- Containerized deployment with pinned PHP runtime settings (`.docker/config/php/php.ini`), plus documented Vagrant and AWS AMI options.
- Versioned release management with per-minor changelogs and deprecation notes (e.g., dropping `uvdesk/composer-plugin` for Symfony Flex in 1.1.2).
- Mature community governance intake: security policy, issue/PR templates, contribution guide, funding configuration.

### 3.3 Current Technology Position

| Layer | Current position | Lifecycle status |
|---|---|---|
| PHP | Constraint `^7.2.5 \|\| ^8.0`; Docker installs 8.1 | PHP 7.2–7.4 EOL; 8.1 security support ends Dec 2025 |
| Symfony | `^5.4` (via Flex `extra.symfony.require`) | 5.4 security support ends Nov 2025 |
| Mail | `symfony/mailer` wired **and** `symfony/swiftmailer-bundle ^3.5` required | SwiftMailer EOL since Nov 2021 |
| Framework extras | `sensio/framework-extra-bundle ^6.1` | Deprecated; superseded by native Symfony attributes |
| Image handling | `intervention/image ^2.4` + `intervention/imagecache ^2.5.2` | imagecache effectively abandoned; image 2.x superseded by 3.x |
| Composer plugins | `composer/package-versions-deprecated` allow-listed | Deprecated (superseded by composer-runtime-api) |
| Database | MySQL `server_version: '5.7'` (README: 5.7.23+) | MySQL 5.7 EOL Oct 2023 |
| Mail parsing | PHP `imap` and `mailparse` extensions required | `ext-imap` unbundled from PHP core in 8.4 (PECL-only) |
| ORM mapping | Doctrine `type: annotation` | Annotations superseded by PHP 8 attributes |
| Base image | `ubuntu:latest` + `apt-get -y upgrade` | Unpinned; non-reproducible |

### 3.4 Current Constraints

- **Security configuration blocks Symfony 6+**: `encoders`, `anonymous: ~`, `guard` authenticators, and `IS_AUTHENTICATED_ANONYMOUSLY` in `security.yaml` were removed in Symfony 6.0. The skeleton cannot absorb a framework major upgrade until this file and the API Guard in the dependent API bundle are migrated to the authenticator-based system.
- **Monolithic container**: Apache and MySQL run in one image via `service` scripts; the default command is `/bin/bash` (services run in background), with no healthcheck and no foreground process supervision.
- **Local-only attachment storage**: the upload manager is pinned to the `Localhost` implementation, so attachments live on the container/host filesystem.
- **Hard-coded operational parameters**: upload limits (`max_post_size`, `max_file_uploads`, `upload_max_filesize`) carry an explicit `# @TODO: Set these parameters via compilers`; `site_url` defaults to `localhost:8000`; `support_email` is a null placeholder.
- **MySQL-5.7-oriented provisioning**: the Docker entrypoint uses `GRANT ... IDENTIFIED BY` (removed syntax in MySQL 8; the script's own comment acknowledges this) and sets `mysql_native_password` (deprecated in MySQL 8.0, removed in 8.4); `doctrine.yaml` applies an `ONLY_FULL_GROUP_BY` sql_mode workaround, indicating queries in dependent bundles assume permissive SQL behavior.

### 3.5 Known Risks / Technical Debt

1. **EOL runtime stack** (PHP 7.x allowance, PHP 8.1 image, Symfony 5.4) — no upstream security patches; growing incompatibility with current Composer ecosystem.
2. **Deprecated dependency stack** — SwiftMailer, SensioFrameworkExtraBundle, intervention/imagecache, `composer/package-versions-deprecated`.
3. **Configuration drift** — `.env.example` documents a legacy variable scheme (`DB_HOST`, `MAIL_DRIVER`, `APP_VERSION=1.0.8`) while runtime configuration actually consumes `DATABASE_URL` and `MAILER_DSN`; neither appears in the example file.
4. **No distribution verification** — no CI workflows (`.github/workflows/` absent) and no `tests/` directory, despite `autoload-dev` mapping `App\Tests\` and `symfony/test-pack` being provisioned in `flex-require-dev`. `require-dev` is empty.
5. **Base-image regression** — CHANGELOG-1.0.13 records pinning `FROM ubuntu:latest` → `ubuntu:18.04`; the current Dockerfile is back on `ubuntu:latest`, reintroducing non-reproducible builds.
6. **Credential handling in container provisioning** — database credentials are written in plaintext to `/etc/mysql/my.cnf` and `/home/uvdesk/.my.cnf` by the entrypoint; `.env` is made group/world-accessible (`chmod -R 775` including `.env`).
7. **Stale upload-parameter wiring** — the acknowledged `uvdesk.yaml` TODO.
8. **Dual mailer coexistence** — transitional state (SwiftMailer + Symfony Mailer) persisting since the 1.0.x line, with a changelog history of SwiftMailer-specific defects (#461, #457, #276).

Note: automated scans flagged "todo" markers in `translations/messages.es.yml` and `public/css/main.css`; inspection shows these are translation text ("todo" = "all" in Spanish) and CSS class names (`.uv-check-todo`, `.uv-app-glyph-todo`), not maintenance markers. The only genuine code-level TODO is the compiler-pass note in `config/packages/uvdesk.yaml`.

## 4. Evolution Drivers

### 4.1 Business Drivers

- The README markets "User Friendly Web Installer" and one-command Docker/AWS AMI deployment — install reliability is a stated product quality, yet install regressions recur (issues #382, #410, #438, #805).
- The project positions itself as a self-hosted alternative for organizations worldwide (twelve locales); runtime EOL status directly affects adopters' security posture and willingness to deploy.
- The extension framework and app store model depend on a stable, current core platform that third-party developers can target.

### 4.2 Technology Drivers

- Upstream lifecycle ends: Symfony 5.4 (Nov 2025), PHP 8.1 (Dec 2025), MySQL 5.7 (Oct 2023, already EOL), SwiftMailer (Nov 2021, already EOL).
- `ext-imap` unbundling from PHP core (8.4+) threatens the mailbox ingestion path that the Docker image currently satisfies via `php8.1-imap`.
- The Composer ecosystem is converging on PHP 8.1+ minimums; the `^7.2.5` allowance increasingly produces unsatisfiable or degraded dependency resolution.

### 4.3 Quality Attribute Drivers

- **Reliability**: email ingestion is the dominant external boundary and the single largest source of changelog fixes across every release line (fetch errors, deletion-after-fetch, credential encryption, OAuth modernization for Microsoft in 1.1.7).
- **Reproducibility**: unpinned base image, build-time `apt-get upgrade`, and a third-party PPA contradict the reproducibility intent signaled by the pinned `php.ini`.
- **Verifiability**: nothing gates a release against the skeleton's actual responsibility — assembling six bundles into a bootable, installable application.

### 4.4 Regulatory / Compliance Drivers

No regulatory obligations are evidenced in the repository. Adjacent concern only: running EOL runtimes is incompatible with common customer security-review expectations for self-hosted software; the presence of a `SECURITY.md` disclosure policy indicates the project fields security reports and therefore has an implicit obligation to ship patchable software.

### 4.5 Operational Drivers

- All-in-one container couples database lifecycle to application lifecycle (no independent backup/upgrade), and its background-service model defeats container orchestrators' health management.
- Operators on modern MySQL 8 infrastructure must contend with the sql_mode workaround and legacy provisioning syntax.
- The custom Flex recipes endpoint is a build-time dependency on GitHub API availability and on the continued existence of the `uvdesk/recipes` repository.

## 5. Target-State Direction

### 5.1 Target Capabilities

- Every release automatically verified to install and boot (CLI and web-wizard paths, Docker build included) before publication.
- First-class, reproducible container deployment with separable database, health signaling, and no embedded credentials.
- Documented, current environment contract (`.env.example` regenerated from actually consumed variables).
- Continued multilingual expansion with an explicit community translation workflow.

### 5.2 Target Architecture

- Same modular skeleton-plus-bundles architecture (it is sound and should be preserved), but with the skeleton acting as a **curated, continuously verified integration point**: pinned supported platform versions, authenticator-based security wiring, single mailer, attribute-based ORM mapping.
- Deployment topology: application container separate from database container (or external managed database), with object storage available for attachments.

### 5.3 Target Technology

- PHP 8.2/8.3+ as the supported floor; Symfony 6.4 LTS (then 7.x) as the framework target.
- Symfony Mailer only; maintained image library; Doctrine attributes; MySQL 8.0/8.4 (or documented MariaDB equivalent).
- Mailbox ingestion decoupled from `ext-imap` over the medium term.

### 5.4 Target Operating Model

- CI-gated releases: dependency audit, configuration/translation lint, Docker build, and an install smoke test per release.
- Changelog-driven deprecation management continued (the project already does this well) extended with explicit EOL policies for PHP/Symfony/MySQL floors.

### 5.5 Target Quality Attributes

- Security: only upstream-supported runtimes; no plaintext credential files in images.
- Reliability: verified install path per release; resilient email ingestion.
- Maintainability: no abandoned dependencies; configuration contract documented and tested.
- Portability: stateless application container option.

## 6. Architecture Evolution Options

### Option FD-1 — Platform modernization campaign (PHP 8.2+/Symfony 6.4+)

- **Option identifier:** FD-1
- **Description:**
  - *Current-state basis:* `composer.json` (`php: ^7.2.5 || ^8.0`, `extra.symfony.require: ^5.4`); Dockerfile installs PHP 8.1; `security.yaml` uses Symfony-6-removed constructs; Doctrine annotation mapping; changelog history of reactive compatibility pushes (1.0.13 "maximum deprication messages removed" for Symfony 4.3; 1.0.17/1.1.0 PHP 8 compatibility).
  - *Limitation / opportunity:* the distribution is pinned to runtimes at or past end of security support; the skeleton's own configuration is a hard blocker to the next framework major.
  - *Proposed direction:* a staged upgrade — (a) drop PHP 7.x from the constraint and require a supported PHP floor; (b) migrate `security.yaml` to the authenticator system (`password_hashers`, no `anonymous`, replace the API Guard with a custom authenticator in the API bundle); (c) convert Doctrine mapping from annotations to attributes; (d) then move `extra.symfony.require` to `^6.4` and validate, treating 7.x as the follow-on.
- **Benefits:** restores security-patch eligibility; unblocks the current Composer ecosystem; removes the recurring reactive compatibility work visible in the changelog.
- **Costs:** coordinated releases across six `uvdesk/*` packages (the code changes mostly live there, but the skeleton orchestrates and pins them).
- **Risks:** breaking changes for self-hosted upgraders on old PHP; the Guard → authenticator migration changes API authentication behavior for existing API consumers.
- **Dependencies:** dependent bundles must support the target framework before the skeleton can pin it.
- **Trade-offs:** accepting a new minimum PHP excludes legacy shared-hosting users — mitigated by keeping the current 1.1.x line available as a maintenance branch.
- **Preconditions:** FD-2 (dependency retirement) is a prerequisite.
- **Priority:** High. Rationale: this is the skeleton's central responsibility (version curation) and its largest demonstrated risk.

### Option FD-2 — Retire deprecated and abandoned dependencies

- **Option identifier:** FD-2
- **Description:**
  - *Current-state basis:* `symfony/swiftmailer-bundle ^3.5` required alongside an already-wired Symfony Mailer (`mailer.yaml` uses `MAILER_DSN`); `sensio/framework-extra-bundle ^6.1`; `intervention/image ^2.4` + `intervention/imagecache ^2.5.2`; `composer/package-versions-deprecated` in `allow-plugins`.
  - *Limitation / opportunity:* the manifest carries libraries that receive no fixes; SwiftMailer defects recur in the changelog (#461, #457, #276); the dual-mailer state is transitional debt that was never completed.
  - *Proposed direction:* complete the consolidation onto Symfony Mailer and remove SwiftMailer; replace SensioFrameworkExtraBundle usage with native Symfony attributes/argument resolvers (in dependent bundles, then drop the requirement here); replace `intervention/imagecache` with maintained image handling (e.g., intervention/image 3.x or framework-native processing); remove the deprecated Composer plugin in favor of the runtime API.
- **Benefits:** shrinks the unpatched attack surface; simplifies the mail stack to one supported transport; unblocks FD-1.
- **Costs:** email behavior changes must be regression-tested against mailbox workflows.
- **Risks:** the changelog shows this area's fragility; image-processing changes may alter thumbnail/branding behavior.
- **Dependencies:** changes land in dependent bundles first; the skeleton drops the requirements afterward.
- **Priority:** High. Rationale: cheap, concrete, and a precondition for the platform upgrade.

### Option FD-3 — Distribution-level verification (release gating for the skeleton)

- **Option identifier:** FD-3
- **Description:**
  - *Current-state basis:* no `.github/workflows/`; no `tests/`; empty `require-dev`; `symfony/test-pack` provisioned but unused; changelog evidence of repeated install-time regressions (#438, #410, 1.1.7 "database connection related issues", #805 migration failure in 1.1.8).
  - *Limitation / opportunity:* the one thing this repository uniquely owns — assembling bundles, configuration, wizard, and image into a working install — has no automated check.
  - *Proposed direction:* a focused CI pipeline that (a) builds the project from `composer.json` on the supported PHP matrix; (b) runs `composer audit` for known-vulnerable dependencies; (c) lints YAML configuration and translation catalogs; (d) builds the Docker image; (e) executes an install smoke test — run `uvdesk:configure-helpdesk` (or drive the wizard non-interactively) against a test database and assert the login page responds. Optionally a minimal PHPUnit skeleton under the already-mapped `App\Tests\` for configuration invariants.
- **Benefits:** converts the historically most common failure mode (broken installs discovered by users) into a pre-release signal; verifies the exact boundary FD-1/FD-2 will be changing.
- **Costs:** modest CI maintenance; smoke tests against external services (mailhog/fake SMTP, ephemeral MySQL) add pipeline time.
- **Dependencies:** none blocking; complements all other options by de-risking them.
- **Priority:** High. Rationale: highest confidence-to-effort ratio; directly targets evidenced, recurring failure modes rather than generic "more tests."

### Option FD-4 — Container hardening and topology separation

- **Option identifier:** FD-4
- **Description:**
  - *Current-state basis:* `FROM ubuntu:latest` (a regression from the 1.0.13 pin to 18.04); build-time `apt-get -y upgrade`; PHP from `ppa:ondrej/php`; gosu 1.11 (2018-era); Apache + `mysql-server` in one image started via `service` scripts; `CMD ["/bin/bash"]` with background services and no healthcheck; plaintext credentials written to `my.cnf` files; `.env` chmod'ed to 775.
  - *Limitation / opportunity:* the image is non-reproducible, couples data and application lifecycles, lacks health signaling for orchestrators, and embeds credential-handling practices that conflict with the security posture the project otherwise promotes (attachment renaming "for security purpose" in 1.1.7, `SECURITY.md`).
  - *Proposed direction:* pin the base image by version/digest and gosu to a current release; remove build-time OS upgrades; publish a compose-style reference topology separating the database; run the web server as the container's foreground process; add a healthcheck against the login page; pass database credentials purely through environment variables rather than written credential files; tighten `.env` permissions to owner-only.
- **Benefits:** reproducible builds; orchestrator-friendly lifecycle; independent database backup/upgrade; removal of embedded secrets.
- **Risks:** splitting the database changes the documented "single container" quick-start — mitigated by keeping the all-in-one image as a demo option while documenting the split topology for production.
- **Dependencies:** relates to FD-5 (MySQL 8 provisioning rewrite); benefits from FD-3's Docker build gate.
- **Preconditions:** entrypoint changes must preserve first-boot provisioning.
- **Priority:** Medium-High.

### Option FD-5 — MySQL 8 migration readiness

- **Option identifier:** FD-5
- **Description:**
  - *Current-state basis:* `doctrine.yaml` (`server_version: '5.7'`, `ONLY_FULL_GROUP_BY` sql_mode workaround); README requirement "MySQL 5.7.23 or higher"; entrypoint's pre-MySQL-8 `GRANT ... IDENTIFIED BY` provisioning and `mysql_native_password` default; MySQL 5.7 EOL October 2023.
  - *Limitation / opportunity:* new deployments increasingly land on MySQL 8.x by default, where the entrypoint's provisioning syntax fails and the sql_mode workaround masks queries that need correction in dependent bundles.
  - *Proposed direction:* validate and declare support for MySQL 8.0/8.4 (and/or a documented MariaDB floor); rewrite entrypoint provisioning with MySQL 8-compatible `CREATE USER`/`GRANT` and `caching_sha2_password` handling; work with the dependent bundles to eliminate the `ONLY_FULL_GROUP_BY` workaround rather than disabling the check; update `server_version` and README requirements.
- **Benefits:** installs succeed on current managed database offerings; removes a silent query-correctness risk.
- **Costs:** query fixes belong to dependent bundles (core-framework primarily).
- **Risks:** behavior changes possible in result ordering/grouping.
- **Dependencies:** FD-3 provides the test harness to validate; FD-4's entrypoint rewrite overlaps.
- **Priority:** Medium-High.

### Option FD-6 — Configuration contract and environment hygiene

- **Option identifier:** FD-6
- **Description:**
  - *Current-state basis:* `.env.example` is stale (`APP_VERSION=1.0.8`; legacy `DB_*`/`MAIL_*` scheme while runtime config consumes `DATABASE_URL`/`MAILER_DSN`); the `# @TODO: Set these parameters via compilers` in `uvdesk.yaml`; hard-coded `site_url: localhost:8000` and `support_email: ~`; custom Flex recipes endpoint on GitHub.
  - *Limitation / opportunity:* new adopters are guided by an example file that does not match what the application reads; the acknowledged TODO leaves upload limits as magic parameters; the recipes endpoint is an unversioned build dependency.
  - *Proposed direction:* regenerate `.env.example` from the variables the configuration actually consumes; resolve the compiler-pass TODO (move upload constraints into bundle configuration); parameterize `site_url` through the environment; pin or mirror the Flex recipes index and document it as a release artifact.
- **Benefits:** fewer first-install failures; closes the only genuine code-level TODO in the repository; makes builds independent of a live GitHub API response.
- **Costs:** low; mostly documentation and wiring.
- **Priority:** Medium.

### Option FD-7 — Email ingestion beyond `ext-imap` (exploratory)

- **Option identifier:** FD-7
- **Description:**
  - *Current-state basis:* README and Dockerfile require PHP `imap` and `mailparse` extensions; `uvdesk_mailbox.yaml` configures per-mailbox IMAP/SMTP; 1.1.7 added Microsoft modern-app (OAuth) support, demonstrating the boundary's continuing evolution; `ext-imap` is unbundled from PHP core as of 8.4.
  - *Limitation / opportunity:* the mailbox channel — the product's dominant external integration — rests on a PHP extension that future PHP versions no longer ship.
  - *Proposed direction:* track a migration of the mailbox component's ingestion to a maintained pure-PHP IMAP client or provider APIs (Gmail/Microsoft Graph), with the skeleton's role being to drop the extension requirement from the Docker image and README when ready.
- **Benefits:** keeps the email channel viable on PHP 8.4+; aligns with the OAuth direction already started.
- **Costs:** substantial work in the mailbox-component package (outside this repo).
- **Risks:** behavioral parity (delimiter handling, deletion-after-fetch, strict mode) must be preserved.
- **Dependencies:** FD-1 (supported PHP) raises the urgency; implementation belongs to `uvdesk/mailbox-component`.
- **Priority:** Longer-term (exploratory) — justified by a concrete upstream change, but not yet blocking.

### Option FD-8 — Externalized attachment storage (exploratory)

- **Option identifier:** FD-8
- **Description:**
  - *Current-state basis:* `upload_manager.id` is configured by class name (`...UploadManagers\Localhost`), evidencing a pluggable upload-manager strategy; attachments default to the local filesystem; the Docker image has no volume guidance for attachment persistence.
  - *Proposed direction:* ship or document a remote object-storage upload manager (S3-compatible) so containerized deployments can be stateless.
- **Benefits:** enables FD-4's stateless application container; removes a data-loss mode on container replacement.
- **Dependencies:** the strategy interface lives in core-framework; FD-4 makes the need concrete.
- **Priority:** Longer-term (exploratory) — the extension point exists; adoption value grows with container usage.

### Option FD-9 — API surface modernization (exploratory)

- **Option identifier:** FD-9
- **Description:**
  - *Current-state basis:* `uvdesk/api-bundle ^1.1.4` is pinned and a `^/api` firewall exists using a Guard authenticator (`APIGuard`); README lists "API Bundle" as a feature.
  - *Proposed direction:* when the security migration (FD-1) replaces the Guard authenticator, take the opportunity to modernize API authentication (token-based) and publish machine-readable API documentation, strengthening the integration surface the extension ecosystem builds on.
- **Priority:** Longer-term (exploratory) — no repository evidence of API consumer demand; framed as a natural sequel to FD-1 rather than an independent initiative.

## 7. Transition Architectures / Stages

### 7.1 Transition State 1 — Hygienic 1.x (FD-2, FD-6, FD-3)

The 1.x line stays on Symfony 5.4 while deprecated dependencies are removed, configuration drift is repaired, and the CI smoke gate is introduced. **Exit conditions**: no abandoned packages in the manifest; `.env.example` matches consumed variables; every release passes the install smoke test. **Entry conditions**: none — all work is additive or subtractive within the current major line.

### 7.2 Transition State 2 — Supported-platform 2.x line (FD-1, FD-5, FD-4)

A new minor/major skeleton line pins PHP 8.2+ and Symfony 6.4, with rewritten security configuration, attribute mapping, MySQL 8 support, and the hardened/splittable container. The 1.x line receives security-only maintenance for a defined window. **Entry conditions**: FD-2 complete in dependent bundles; FD-3 gate available to validate the new line. **Exit conditions**: install smoke test passes on the new platform matrix; upgrade notes published for self-hosted installations.

### 7.3 Transition State 3 — Stateless-capable deployment (FD-4 continued, FD-7, FD-8)

Database separated by default, object-storage option available, mailbox ingestion independent of `ext-imap`. **Entry conditions**: Transition 2 platform in place; dependent-bundle work for storage and mail ingestion delivered.

### 7.4 Entry / Exit Conditions

Each stage ships only when the FD-3 verification gate passes; deprecations continue to be announced per release in the changelogs, following the project's established practice (e.g., the 1.1.2 composer-plugin → Flex migration pattern: announce, migrate, remove).

### 7.5 Dependencies Between Transitions

FD-2 → FD-1 (dependency retirement precedes framework upgrade); FD-3 underpins all stages; FD-5 and FD-4 share entrypoint work and should be delivered together; FD-7/FD-8 depend on dependent-bundle roadmaps outside this repository.

## 8. Roadmap

### 8.1 Major Initiatives

1. **Release-verification gate** (FD-3) — can start immediately.
2. **Dependency retirement** (FD-2) — next, coordinated with bundle releases.
3. **Configuration contract repair** (FD-6) — parallel, low-risk.
4. **Platform upgrade line** (FD-1) with **MySQL 8 and container hardening** (FD-5, FD-4) — the next numbered line.
5. **Statelessness and mail-stack evolution** (FD-7, FD-8, FD-9) — opportunistic, following upstream and bundle capacity.

### 8.2 Sequencing

FD-3 → (FD-2 ∥ FD-6) → FD-1 + FD-4 + FD-5 → FD-7/FD-8/FD-9.

### 8.3 Milestones

- M1: first CI-gated release of the skeleton.
- M2: manifest free of deprecated/abandoned packages.
- M3: supported-platform line generally available with migration notes.
- M4: documented production topology (split database, optional object storage).

### 8.4 Dependencies

Cross-repository coordination is the governing dependency: `.github/CONTRIBUTING.md` designates the five `uvdesk/*` repositories as the owners of functional code, so FD-1/FD-2/FD-5/FD-7/FD-8 require synchronized releases there before the skeleton can pin the results.

### 8.5 Resource Considerations

The project's governance structure (issue templates, PR template, branch conventions, Open Collective funding) already supports community contribution; the CI gate (FD-3) is the force multiplier that makes community contributions safe to accept against a moving dependency matrix.

## 9. Migration and Implementation Considerations

### 9.1 Data Migration

MySQL 8 adoption requires entrypoint provisioning changes and validation of the `ONLY_FULL_GROUP_BY` workaround's removal against bundle queries; no schema format changes are evidenced. Attachments remain file-based unless FD-8 is adopted, in which case a one-time copy to object storage with path-preserving keys suffices.

### 9.2 Application Migration

Self-hosted upgrades across Transition 2 require: PHP upgrade on the host, `composer update` against the new skeleton release, security-configuration replacement (handled by the skeleton, since the file lives here), and cache rebuild. The Guard→authenticator change requires API consumers to be notified via changelog.

### 9.3 Infrastructure Migration

Base-image pinning changes build reproducibility without interface changes; topology separation introduces a documented compose/reference deployment while retaining the all-in-one image for evaluation.

### 9.4 Integration Migration

Mail transport consolidation (SwiftMailer removal) must preserve existing `MAILER_DSN`-based configuration so operators' SMTP settings carry over unchanged. Mailbox OAuth additions (1.1.7) indicate per-provider migration notes will be needed again when FD-7 lands.

### 9.5 Organizational / Operational Change

The contribution guide already routes changes to the correct repository; the platform campaign should be tracked as cross-repository milestones so the skeleton is never pinned ahead of its bundles.

### 9.6 Rollback / Contingency

Per-release changelogs and semantic version pinning (`^1.1.x`) already allow adopters to hold a prior line; Transition 2 should keep the 1.x line installable (Packagist retains it) while security fixes continue for a defined window.

## 10. Risks, Assumptions, and Constraints

### 10.1 Risks

- **Cross-repository coordination failure**: skeleton pinned ahead of bundle compatibility, breaking `create-project` installs — mitigated by FD-3's gate.
- **Security exposure window** until FD-1/FD-2 land, given EOL components.
- **Email-channel regression** during mailer consolidation — the changelog shows this area's historical fragility.
- **Adopter fragmentation** if legacy-PHP hosting users cannot follow the platform upgrade.

### 10.2 Assumptions

- Dependent bundles will deliver the code-level changes (security authenticators, attribute mapping, query fixes) the skeleton must pin.
- Upstream lifecycle dates (PHP 8.1 → Dec 2025; Symfony 5.4 → Nov 2025; MySQL 5.7 → Oct 2023) are the operative planning horizon.
- Continued community maintenance capacity, as evidenced by the 2023–2025 release cadence.

### 10.3 Constraints

- The skeleton cannot fix bundle-internal defects itself; its leverage is version curation, configuration, packaging, and verification.
- Backward compatibility for existing self-hosted installations constrains how abruptly minimum versions can move.

### 10.4 Open Issues

- The exact scope of the 1.2.x line is undefined (its changelog contains a single translation fix); whether it becomes the platform-upgrade line is an unrecorded decision.
- No evidence exists in this repository of bundle-level test/CI status, so the end-to-end verification picture across the six packages cannot be assessed from here.

## 11. Governance and Decision Points

### 11.1 Architecture Governance

The skeleton's maintainers already govern the dependency manifest, Docker packaging, and release notes; this document's directions fall within that existing authority.

### 11.2 Decision Gates

- Gate A: adopt the CI release gate (FD-3) — low cost, precedes everything.
- Gate B: declare the PHP/Symfony floor for the next line and the 1.x maintenance window (FD-1).
- Gate C: remove SwiftMailer and other retired packages from the manifest (FD-2), contingent on bundle releases.
- Gate D: publish the split-topology deployment as the documented production path (FD-4/FD-5).

### 11.3 Review Points

Each tagged release: review the manifest against upstream EOL calendars (PHP, Symfony, MySQL) and the changelog's deprecation notes; review CI gate results.

### 11.4 Ownership

Skeleton-level items (manifest, Docker, `.env` contract, CI, changelogs) belong to this repository's maintainers; bundle-level items (security authenticators, mail ingestion, query corrections, storage strategies) belong to the respective `uvdesk/*` repositories per `CONTRIBUTING.md`, with the skeleton tracking readiness before version pins move.

## 12. Success Measures

### 12.1 Business Outcomes

- Decline in installation-failure issue reports (the recurring #382/#410/#438/#805 pattern).
- Continued download/adoption on supported platforms (Packagist metrics the README already surfaces).

### 12.2 Architecture Outcomes

- Manifest contains only upstream-supported dependencies; Symfony and PHP constraints reference supported majors; security configuration uses the authenticator system.

### 12.3 Quality Measures

- Every release passes the install smoke test, dependency audit, and configuration/translation lint; no release ships with known-vulnerable dependencies flagged by `composer audit`.

### 12.4 Operational Measures

- Reproducible image builds (pinned base, no build-time OS upgrades); container health signaling present; database provisioned without plaintext credential files; documented MySQL 8 support.

## 13. References

- `composer.json` — dependency manifest, platform constraints, Flex endpoint, deprecated plugin allowance.
- `config/packages/uvdesk.yaml` — upload-parameter TODO, upload manager strategy, site defaults.
- `config/packages/security.yaml` — legacy security dialect (Guard, encoders, anonymous) blocking Symfony 6+.
- `config/packages/doctrine.yaml` — MySQL 5.7 server version, sql_mode workaround, annotation mapping.
- `config/packages/mailer.yaml`, `config/packages/uvdesk_mailbox.yaml` — mail transport and mailbox boundary.
- `.env.example` — stale environment contract (version 1.0.8; legacy variable scheme).
- `Dockerfile`, `.docker/bash/uvdesk-entrypoint.sh`, `.docker/config/php/php.ini` — container build, provisioning, and runtime.
- `CHANGELOG-1.0.md`, `CHANGELOG-1.1.md`, `CHANGELOG-1.2.md` — release history, deprecation practice, install-regression evidence, email-channel evolution.
- `README.md`, `INSTALLATION GUIDE.md` — stated requirements (PHP 8.1, MySQL 5.7.23+, IMAP/Mailparse) and deployment options (Docker, Vagrant, AWS AMI).
- `.github/CONTRIBUTING.md`, `.github/SECURITY.md` — cross-repository ownership model and security intake.
- Upstream lifecycle references: PHP supported-versions policy (8.1 security EOL December 2025), Symfony release cycle (5.4 security EOL November 2025), MySQL 5.7 EOL (October 2023), SwiftMailer end-of-life (November 2021), PHP 8.4 unbundling of `ext-imap`.
