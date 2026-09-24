---
model: z-ai/glm-5.3
---

# Implementation Detail

> Supplementary engineering artifact describing the practical concerns that affect building, configuring, deploying, releasing, and operating the implemented product. It is not a separate SDLC lifecycle phase.

## 1. Delivery Summary

The repository is the Composer-distributed application skeleton (`uvdesk/community-skeleton`) of the UVdesk helpdesk: a Symfony 5.4 project whose functional bundles (core framework, support center, mailbox, automation, API, extension framework) are installed as external packages. The material delivery concerns are:

- **Assembly by Composer/Symfony Flex** with a custom UVdesk recipe endpoint; no build step beyond `composer install`.
- **First-run provisioning via a setup wizard** (web UI plus console commands) that creates the database, loads fixtures or runs Doctrine migrations, and rewrites `.env` credentials.
- **A monolithic Docker image** (Apache + MySQL + PHP 8.1 in one container) as the containerized delivery path.
- **No CI/CD pipelines** and no rollback mechanics are established in the repository.

## 2. Build and Packaging

- **Build/package mechanism:** Composer project. Operators either run `composer create-project uvdesk/community-skeleton` or download a prebuilt zip archive from the vendor CDN (both documented in `INSTALLATION GUIDE.md`). `composer install` resolves the platform via `flex-require` (UVdesk bundles pinned to `^1.1.x` plus the Symfony `^5.4` component set) using the UVdesk recipe endpoint (`uvdesk/recipes` on GitHub). Composer `post-install-cmd`/`post-update-cmd` hooks run `cache:clear` and `assets:install %PUBLIC_DIR%`.
- **Important build artifacts or outputs:** a standard PHP web project — front controller `public/index.php` with `.htaccess`, writable `var/` cache, `vendor/` (uncommitted), and an install-time-generated `migrations/` directory.
- **Docker packaging (`Dockerfile`):** built `FROM ubuntu:latest`; installs Apache 2 + `libapache2-mod-php8.1`, `mysql-server`, and PHP extensions (`xml`, `imap`, `mysql`, `mailparse`, `curl`) from `ppa:ondrej/php`; creates a non-root `uvdesk` user; installs `gosu 1.11` and Composer with signature/hash verification; copies Apache config and the entrypoint script; runs `composer install`, `composer dump-autoload --optimize`, and `php bin/console cache:clear --env=prod --no-debug` during image build; sets `uvdesk-entrypoint.sh` as `ENTRYPOINT`.
- **Material constraints:**
  - The image is all-in-one: web server, database, and application in a single container, with `CMD /bin/bash` (service startup is performed by the entrypoint).
  - No `EXPOSE` or `HEALTHCHECK` directives are declared.
  - PHP version guidance diverges: `composer.json` requires `^7.2.5 || ^8.0`, the Dockerfile uses PHP 8.1, the installation guide installs PHP 8.2.

## 3. Configuration and Environments

| Concern | Repository evidence / finding |
|---|---|
| Runtime configuration | Symfony Dotenv. A committed root `.env` supplies defaults: `APP_ENV=dev`, `APP_SECRET`, `DATABASE_URL`, `MAILER_DSN`, `UV_SESSION_COOKIE_LIFETIME`. `config/packages/doctrine.yaml` consumes `DATABASE_URL` (DBAL `pdo_mysql`, `server_version: '5.7'`, `utf8mb4`, and a `SET sql_mode` init option that strips `ONLY_FULL_GROUP_BY`). `config/packages/uvdesk_mailbox.yaml` (IMAP in / SMTP out mailbox definitions) and `config/packages/uvdesk_extensions.yaml` (extensions loaded from the `apps/` directory) are empty by default and must be populated for full operation. |
| Environment variables / secrets references | The committed `.env` contains only placeholders (e.g. `APP_SECRET=YOUR_APP_SECRET`, generic `db_user:db_password`), not real secrets. `.gitignore` excludes `.env.local*` and `config/secrets/prod/`, so real credentials are expected in uncommitted overrides or the Symfony secrets store; `.env` comments recommend `composer dump-env prod` for production and state that real environment variables take precedence. The Docker entrypoint consumes `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, and `MYSQL_ROOT_PASSWORD` at container start to provision the embedded MySQL instance. |
| Environment-specific differences | Standard Symfony layering (`.env.local`, `.env.$APP_ENV.local`) with a fallback `env(DATABASE_URL): ''` for cache warmup. The console command `uvdesk_wizard:env:update` refuses to run outside the `dev` environment. The Docker entrypoint skips local database provisioning when `MYSQL_USER`/`MYSQL_PASSWORD`/`MYSQL_DATABASE` are unset (an externally managed database is then required, but the wizard variables in `.env` must be edited manually). |

## 4. Deployment and Release

| Concern | Repository evidence / finding |
|---|---|
| Deployment mechanism | Two paths. (1) **Manual LAMP deployment** per `INSTALLATION GUIDE.md`: Ubuntu host, Apache with `mod_rewrite` and mod_php, MySQL, a non-root `uvdesk` user made writable for Apache's `www-data` group, then `php bin/console uvdesk:configure-helpdesk` for interactive first-run configuration. (2) **Docker**: the image ships Apache with a vhost pointing `DocumentRoot /var/www/uvdesk/public` on port 80; the entrypoint restarts `apache2` and `mysql`, provisions the database and credentials, then drops privileges to the `uvdesk` user via `gosu`. |
| CI/CD | **Not established by the repository.** No workflow/pipeline definitions exist; `.github/` contains only governance files (issue/PR templates, contributing guide, security policy, funding). |
| Release / promotion | Distribution as a versioned Composer package on Packagist and as a zip archive from the vendor CDN. Release lines are documented in `CHANGELOG-1.0.md`, `CHANGELOG-1.1.md`, and `CHANGELOG-1.2.md`. The skeleton itself declares no version; effective functionality comes from the pinned UVdesk bundle versions resolved by Composer. |
| Rollback | **Not established by the repository.** No rollback procedure, migration-down path, or version pinning of previous releases is provided. |

## 5. Database / Data Migration

Migrations are part of delivery but are **generated at install time, not committed**: no migration files exist in the repository (`src/Migrations/` contains only a `.gitignore`), while both the `Dockerfile` (permissions) and the `uvdesk:configure-helpdesk` wizard expect a project-level `migrations/` directory to exist after installation.

The hidden console command `uvdesk_wizard:database:migrate` (`src/Console/Wizard/MigrateDatabase.php`) implements the migration flow:

- **Empty database (fresh install):** `doctrine:schema:create` followed by `doctrine:fixtures:load` to seed default data.
- **Existing database:** `doctrine:migrations:sync-metadata-storage`, `doctrine:migrations:version --add --all`, `doctrine:migrations:diff`, then `doctrine:migrations:migrate` to the latest version (no-op if already current).
- Compatible with both DBAL 2 and DBAL 3 schema-manager APIs; validates the DB connection first and fails fast on invalid configuration.

The setup wizard can also create the database on demand and rewrite the DB credentials into `.env`. No down-migration or rollback path is exposed.

## 6. Operational Readiness

- **Runtime prerequisites:** Apache with `mod_rewrite`; PHP extensions `xml`, `imap`, `mysql`, `mailparse`, `curl`; a MySQL server (DBAL configured against `server_version: '5.7'`, with `ONLY_FULL_GROUP_BY` stripped via connection init command).
- **Writable paths required by the installer:** `.env`, `var/`, `config/`, `public/`, and `migrations/` (Dockerfile and wizard set `0775`).
- **Post-install actions:** replace the `APP_SECRET` placeholder; set `DATABASE_URL` and `MAILER_DSN`; define mailbox IMAP/SMTP entries in `config/packages/uvdesk_mailbox.yaml` for the email channel (none configured by default); install extensions into the `apps/` directory.
- **External connectivity during setup:** the `uvdesk:configure-helpdesk` wizard references the vendor update service (`https://updates.uvdesk.com/api/updates`).
- **Container operation:** the Docker image bundles the web server and MySQL in one container; the entrypoint runs as root (required to start services and alter MySQL accounts) and then steps down to the `uvdesk` user via `gosu`. No health checks are declared.
- **Operational notes:** if the PHP `redis` extension is loaded, the wizard warns about a known database-connection issue and points to an upstream issue link.

## 7. Open Implementation / Delivery Concerns

- **Stale `.env.example`:** it uses a Laravel-style variable set (`APP_NAME`, `DB_CONNECTION`, `DB_HOST`, `MAIL_DRIVER`, `smtp.mailtrap.io`, `APP_VERSION=1.0.8`) that does not correspond to the Symfony variables the application actually consumes (`APP_ENV`, `APP_SECRET`, `DATABASE_URL`, `MAILER_DSN`). It is misleading as an operator template.
- **No CI/CD or automated test/release pipeline** exists in the repository.
- **No rollback or downgrade mechanics** are documented or implemented.
- **PHP version divergence** across `composer.json` (`^7.2.5 || ^8.0`), the Dockerfile (8.1), and the installation guide (8.2).
- **Monolithic container** (Apache + MySQL + application) deviates from typical production separation of concerns; the entrypoint's `MYSQL_*` handling applies only to the embedded database.
- **Top-level `migrations/` directory** referenced by the Dockerfile and wizard is not committed and must be created during installation.

## 8. References

- `composer.json`
- `Dockerfile`, `.dockerignore`, `.docker/bash/uvdesk-entrypoint.sh`, `.docker/config/apache2/vhost.conf`
- `.env`, `.env.example`, `.gitignore`
- `INSTALLATION GUIDE.md`
- `config/packages/doctrine.yaml`, `config/packages/uvdesk_mailbox.yaml`, `config/packages/uvdesk_extensions.yaml`
- `src/Console/Wizard/ConfigureHelpdesk.php`, `src/Console/Wizard/MigrateDatabase.php`, `src/Console/EnvironmentVariables.php`
- `CHANGELOG-1.0.md`, `CHANGELOG-1.1.md`, `CHANGELOG-1.2.md`
- `.github/` (governance files only; no CI/CD workflows)
