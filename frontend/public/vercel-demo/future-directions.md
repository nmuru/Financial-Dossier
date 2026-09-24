# Future Directions

## 1. Synthesis of Current State

Next.js Commerce (`vercel/commerce`) is a server-rendered, App Router-based storefront template that uses Shopify's Storefront GraphQL API as its data backend. The current implementation provides:

- A high-performance Next.js 15 storefront with React Server Components, Server Actions, Partial Prerendering (`experimental.ppr`), and `useOptimistic` cart updates.
- A Shopify-specific data layer (`lib/shopify`) with caching via `unstable_cacheLife` / `unstable_cacheTag` and webhook-driven revalidation.
- Standard ecommerce flows: home page (three-item grid + carousel), product detail pages with variant selection and related products, collection/category browsing, keyword search, and a cart drawer with optimistic updates and Shopify-hosted checkout.
- SEO scaffolding (sitemap, robots, per-page metadata, JSON-LD product schema, dynamic OpenGraph images), accessibility-aware components (Headless UI Dialog/Transition), and Tailwind 4 styling.

The codebase has a small, focused surface area: a single Page Router/App Router hybrid template, a single `lib/shopify` provider, no backend of its own, no persistent data store, no authentication, and no test framework configured. The `test` script in `package.json` only runs `prettier --check`, indicating that automated verification is currently limited to formatting.

From this baseline, the most credible next directions cluster around:

1. Strengthening the provider abstraction so alternative backends (Medusa, Saleor, BigCommerce, etc., listed in the README) can be supported without forking the entire template.
2. Hardening the Shopify integration, which currently has several narrow edge cases (single-variant `selectedOptions`, `getCart` race on first paint, optimistic-only quantity math).
3. Establishing a real testing and CI strategy, which is essentially absent.
4. Filling functional gaps in the commerce flow (search relevance, filters beyond sort, wishlist, account, internationalization, accessibility audits, observability).

---

## 2. Explicit Future Intent (Repository Evidence)

The repository does not contain `TODO`, `FIXME`, `XXX`, or `HACK` markers. However, several pieces of in-code evidence express intent:

**Provider strategy is explicit.** The README states that "Vercel will only be actively maintaining a Shopify version" and that alternative providers "should be able to fork this repository and swap out the `lib/shopify` file with their own implementation while leaving the rest of the template mostly unchanged." This is a roadmap-level signal that the `lib/shopify` boundary is intended to be a provider-agnostic seam.

**Integrations exist as forks.** The README explicitly lists Orama (search) and React Bricks (CMS) as optional integrations maintained as separate repositories. This is evidence of a "core + extensions" product shape.

**Experimental Next.js features in use.** `next.config.ts` enables `experimental.ppr`, `experimental.inlineCss`, and `experimental.useCache`. The presence of `useCache: true` and `unstable_cacheLife` / `unstable_cacheTag` indicates the project is on a moving API surface that will need to be tracked as those features graduate.

**Hidden-by-convention collections.** `components/grid/three-items.tsx` and `components/carousel.tsx` both depend on `hidden-homepage-featured-items` and `hidden-homepage-carousel` Shopify collections, and `getCollections` filters collections whose handle starts with `hidden-`. This convention is operational and undocumented beyond the source comments; it is a candidate for an explicit configuration mechanism.

These are evidence of intent, not commitments. They are weighted below as starting points, not as the only drivers of the recommendations.

---

## 3. Functional Gaps

The following gaps are supported by direct evidence in the source:

**Search is query-string only.** `app/search/page.tsx` and `components/layout/navbar/search.tsx` push `?q=...` into the URL and forward it to `getProducts({ query })`. The product GraphQL query (`lib/shopify/queries/product.ts`) hardcodes `first: 100` and does not paginate, expose product facets (size, color, price range, availability), or support any structured filtering beyond a free-text term and a single `sort` key. There is no type-ahead, no faceted refinement, and no "did you mean" affordance.

**Filters are limited to sort and collection navigation.** `components/layout/search/filter/index.tsx` is generic enough to render a list, but `app/search/layout.tsx` only wires it to `sorting`. There is no price filter, no availability filter, and no per-option (size/color) filter despite the variant data being present in the product GraphQL response.

**No customer account flows.** There is no `/account`, no login, no order history, no saved addresses, and no wishlist. The application only models an anonymous cart held in the `cartId` cookie (see `components/cart/actions.ts`).

**No multi-currency or localization.** The UI renders currency from Shopify (`Price` component reads `currencyCode`), but there is no locale switcher, no translated strings, no per-locale route segment, and no `hreflang` strategy. `getMenu` does path rewriting that assumes a single locale.

**Limited product media.** `app/product/[handle]/page.tsx` slices `product.images.slice(0, 5)`, dropping images beyond the first five. There is no video, no 3D model, and no zoom/lightbox beyond the basic arrow-controlled gallery in `components/product/gallery.tsx`.

**No reviews, recommendations explanation, or merchandising rules.** The home page carousel and three-item grid both rely on the existence of specific Shopify collections (`hidden-homepage-carousel`, `hidden-homepage-featured-items`) without any in-app merchandising override or fall-back logic if those collections are empty (the carousel returns `null`; the three-item grid returns `null` only if fewer than three products are present).

**Cart error messaging is generic.** `components/cart/actions.ts` returns strings like `"Error adding item to cart"` regardless of the underlying failure, and `app/error.tsx` only offers a "Try Again" button with no log correlation. There is no structured error type surfaced to the user.

**Sitemap and SEO robustness.** `app/sitemap.ts` calls `validateEnvironmentVariables()` at the top of the function, which will throw if `SHOPIFY_STORE_DOMAIN` or `SHOPIFY_STOREFRONT_ACCESS_TOKEN` is missing, causing the sitemap route to fail in environments that are intentionally unconfigured (e.g., preview deployments without secrets).

---

## 4. Architectural Constraints

Repository evidence supports the following structural observations:

**Single-provider coupling.** Every page that requires commerce data imports from `lib/shopify`. Although the directory structure is suggestive of an abstraction, there is no provider registry, no interface declaration, and no runtime polymorphism. The README's stated strategy of "swap out the `lib/shopify` file" is a fork-based strategy, not a plug-in strategy.

**Caching is tightly coupled to Next.js unstable APIs.** `lib/shopify/index.ts` uses `unstable_cacheLife`, `unstable_cacheTag`, `unstable_cacheLife('seconds')`, and `unstable_cacheLife('days')`. `next.config.ts` enables `experimental.useCache: true`. Any future change to those APIs, or any attempt to deploy on a platform that does not implement them, requires code changes in the data layer.

**Cart state is split across cookie, server, and client optimistic state.** The cart identity is held in a `cartId` cookie (`components/cart/actions.ts`), the authoritative cart lives in Shopify, and the client maintains an `useOptimistic` projection in `components/cart/cart-context.tsx`. The first-render flow in `app/layout.tsx` deliberately does not await `getCart()` and passes the promise to `CartProvider`, then `components/cart/modal.tsx` triggers `createCartAndSetCookie()` from a client `useEffect` if no cart exists. This is intentional for performance but introduces a window where add-to-cart calls could race against cart creation. The current code mitigates the race by always calling `addToCart` (which itself reads the cookie), but the architecture has no test or invariant that prevents a future regression.

**Webhook revalidation is secret-only.** `app/api/revalidate/route.ts` and the `revalidate` function in `lib/shopify/index.ts` authenticate webhooks via a single shared secret query parameter (`?secret=...`) and rely on Shopify's `x-shopify-topic` header. There is no request signature verification (Shopify supports HMAC-signed webhooks natively), no rate limiting, and no allow-list of source IPs.

**Hardcoded API version.** `lib/constants.ts` defines `SHOPIFY_GRAPHQL_API_ENDPOINT = "/api/2023-01/graphql.json"`. As Shopify sunsets older Storefront API versions, this string will need to be updated or made configurable.

**No background work or async boundaries.** Every product, collection, menu, cart, and page action is performed synchronously in the request path. The `useOptimistic` UI hides latency for cart operations, but product, collection, and search reads block render. There is no evidence of streaming, ISR background regeneration beyond the cache tags, or queue-driven work.

**Single process assumption.** The architecture is one Vercel-deployable Next.js application. There is no documented path for splitting edge functions, serverless workers, or scheduled jobs, and no environment file beyond `.env.example`.

---

## 5. Implementation and Maintainability Risks

Direct evidence from the source code reveals the following maintainability concerns:

**`reshapeCart` mutates the input.** `lib/shopify/index.ts` assigns `cart.cost.totalTaxAmount = ...` directly onto the parameter object rather than constructing a new object. This makes the helper harder to reason about and could leak side effects if the same response is reused.

**Stringly-typed error returns in Server Actions.** `components/cart/actions.ts` returns user-facing error strings (`"Error adding item to cart"`) from `addItem`, `removeItem`, and `updateItemQuantity`. These are then rendered into a `sr-only` paragraph in `components/cart/add-to-cart.tsx`. There is no error type, no translation key, and no telemetry hook.

**`actions.ts` parameter shape is `any`.** The `prevState: any` arguments in `addItem`, `removeItem`, and `updateItemQuantity` are untyped. The new `useActionState` API in React 19 expects a typed state.

**Variant matching in `add-to-cart.tsx` is fragile.** `components/cart/add-to-cart.tsx` resolves the selected variant by comparing each variant's `selectedOptions` against lowercase URL search params. This works for current Shopify data but does not normalize option names with spaces, diacritics, or non-ASCII characters.

**Hidden-by-prefix convention is undocumented and scattered.** Both `lib/shopify/index.ts` (`getCollections`) and the homepage components (`three-items.tsx`, `carousel.tsx`) rely on the `hidden-` prefix. A future maintainer editing either location without knowledge of the convention can silently break the home page or expose a hidden collection.

**`app/sitemap.ts` throws on missing env.** `validateEnvironmentVariables()` is called at the top of the sitemap function. This couples the SEO surface to the runtime availability of Shopify credentials, and is likely to cause a hard failure in preview deployments.

**Hardcoded literal in the footer.** `components/layout/footer.tsx` hardcodes `2023` as the start year for the copyright range. This will become a maintenance bug in subsequent years.

**Magic strings for environment variables.** `process.env.SHOPIFY_REVALIDATION_SECRET`, `process.env.SHOPIFY_STORE_DOMAIN`, and `process.env.SHOPIFY_STOREFRONT_ACCESS_TOKEN` are referenced in multiple files without a single source of truth or a typed accessor.

**Test footprint is essentially empty.** `package.json` defines `"test": "pnpm prettier:check"` and no test runner, no test files, no `vitest.config`/`jest.config`/`playwright.config`, and no CI configuration. The `.gitignore` mentions `.playwright` and `coverage`, which suggests past or planned adoption but no in-repo evidence today.

**Use of `any` and `unknown` in critical paths.** `lib/shopify/index.ts` rethrows `e` as `{ error: e }` in the catch block, and the `shopifyFetch` typed returns narrow incorrectly (`Promise<{ status: number; body: T } | never>`). The `| never` makes the function's return type effectively `Promise<{ status: number; body: T }>` for callers but obscures the fact that an error path also returns a value-shaped object.

---

## 6. Testing and Verification Gaps

The testing footprint is the most material gap in the current implementation. Evidence:

- **No test files exist** in the repository (verified by recursive listing of `*.ts`/`*.tsx` and by `grep` for `describe`, `it(`, `test(`, `expect` in the source tree — no matches outside third-party-like patterns).
- **No test framework is installed** (`package.json` has no `vitest`, `jest`, `playwright`, or `@testing-library` dependency).
- **No CI configuration** is committed (no `.github/workflows`, no `.gitlab-ci.yml`, no `vercel.json` for build settings beyond what the platform infers).
- **The `test` script runs only Prettier.** `pnpm test` performs no functional verification at all.
- **The `.gitignore` references `.playwright` and `coverage`** without any matching configuration file, suggesting that E2E testing was considered but is not currently active.
- **Type safety is the only automated guard.** `tsconfig.json` enables `strict: true` and `noUncheckedIndexedAccess: true`, which prevents some categories of bugs but does not verify behavior.

The implication is that any change to the Shopify data layer, cart flow, revalidation logic, or routing is verified only by manual testing. Specific behaviors that warrant explicit verification, based on the code paths observed:

- Cart race conditions between `createCartAndSetCookie` and `addToCart` on first session.
- Webhook revalidation authentication, including the 401 path and the 200-with-no-op path.
- `reshapeCart` and `reshapeProduct` for hidden-product filtering, currency normalization, and missing `totalTaxAmount`.
- URL-driven variant selection in `VariantSelector` against options with multiple values.
- Search query forwarding through `app/search/page.tsx` and `app/search/children-wrapper.tsx` (which re-keys the children on `q` change).
- Sitemap generation when collections, products, or pages are absent.

---

## 7. Operational, Scalability, and Performance Considerations

The repository is engineered for Vercel-style edge/serverless deployment. Evidence supports the following observations:

**Heavy pages fan out many GraphQL requests.** The home page calls `getCollectionProducts` twice (carousel + three-item grid), and the navbar awaits `getMenu` while the layout awaits `getCart`. Each of these is a separate Storefront API request. As catalog size grows, the lack of `first: <small number>` pagination on `getProducts` and `getCollectionProducts` (currently `first: 100` and `first: 250` for variants) will pressure Shopify's response-size and the bundle size of the rendered page.

**`unstable_cacheLife("days")` is aggressive.** `getCollection`, `getCollectionProducts`, `getCollections`, `getProduct`, `getProductRecommendations`, and `getProducts` all use `"days"`. This is correct for content-driven caching but means that any in-stock or pricing change relies on the webhook revalidation path functioning correctly. A missed webhook will leave stale data for up to a day.

**No retry, no circuit breaker, no timeout on `shopifyFetch`.** `lib/shopify/index.ts` performs a single `fetch` with no `AbortController` and no timeout. A slow or hanging Storefront API will block the request and the cache miss will not be retried at the data layer.

**No telemetry.** There is no analytics integration, no error reporting, no performance marks, and no logging beyond `console.log`/`console.error`. `app/sitemap.ts` even throws `JSON.stringify(error, null, 2)` on failure, which surfaces an internal error string to the response body.

**No queueing or background work.** The only POST endpoints are `app/api/revalidate/route.ts` and the implicit Server Actions. There is no evidence of scheduled work (e.g., refreshing menu/collection data) or background processing.

These observations describe a system that will perform well at the scale of the README's demo store but has limited resilience characteristics. They do not, on their own, justify a rewrite; they justify targeted hardening.

---

## 8. Security and Resilience

Repository evidence supports the following security and resilience observations, each tied to specific code:

**Webhook authentication uses a query-string secret.** `lib/shopify/index.ts` checks `req.nextUrl.searchParams.get("secret")` against `SHOPIFY_REVALIDATION_SECRET`. Query-string secrets can be logged in proxies and access logs. Shopify supports HMAC-signed webhooks that should be preferred for production.

**No rate limiting on `app/api/revalidate`.** A malicious caller with the secret can repeatedly force revalidation, which is a DoS vector against the cache layer.

**No CORS or origin checks.** The revalidation endpoint will accept a POST from any origin. The 200-status response is required by the comment, but a future change to validate origin or method would be a low-cost improvement.

**No CSRF protection on Server Actions is visible in the source.** Next.js 15 Server Actions are protected by encrypted action IDs by default, but no additional application-level guard (e.g., captcha on add-to-cart) is in place. This is acceptable for a template but should be reconsidered for production deployments.

**`key` is asserted non-null without a check.** `lib/shopify/index.ts` reads `process.env.SHOPIFY_STOREFRONT_ACCESS_TOKEN!` and uses it directly. If the variable is missing, the Storefront API will reject the call with an opaque error rather than a clear configuration error.

**`baseUrl` falls back to `http://localhost:3000`.** `lib/utils.ts` uses `VERCEL_PROJECT_PRODUCTION_URL` if available, otherwise `http://localhost:3000`. The fallback ensures local development works but means that any environment that forgets to set the production URL will produce absolute URLs pointing to localhost in the sitemap, OpenGraph, and structured data.

**Error responses leak error details.** `app/sitemap.ts` throws `JSON.stringify(error, null, 2)`, which would serialize a full error object — potentially including the GraphQL query — to the response body.

**No secrets management beyond environment variables.** `.env.example` lists the four required variables, and the README warns against committing `.env`, but no integration with a secrets manager or runtime secret rotation is provided.

---

## 9. Prioritized Future Directions

The following directions are ranked by evidence strength, impact on the business purpose (a fast, server-rendered commerce template), and feasibility. Each entry lists the current evidence, the limitation, the proposed direction, expected benefit, prerequisites, priority, and confidence.

### Priority 1 — Establish a Real Testing and CI Strategy

- **Evidence:** `package.json` defines only `"test": "pnpm prettier:check"`; no test runner, no test files, no CI configuration; `.gitignore` references `.playwright` and `coverage` without supporting files.
- **Limitation:** Behavior of the cart, revalidation, search, and Shopify data layer is verified only by manual effort. Regressions will be caught by users.
- **Proposed direction:** Introduce a layered test stack — unit tests for the pure helpers in `lib/shopify` (`reshapeCart`, `reshapeProduct`, `reshapeImages`, `removeEdgesAndNodes`, `cartReducer`) and `lib/utils.ts`; integration tests for Server Actions using a mocked `shopifyFetch`; Playwright end-to-end tests for the home → search → product → cart → checkout flow.
- **Expected benefit:** A regression in the cart race condition, variant matching, or revalidation would be caught before deploy. The `.playwright` reference in `.gitignore` suggests this was previously considered, lowering adoption cost.
- **Prerequisites:** A test runner selection (Vitest is the natural fit given the ESM-first `tsconfig.json`); a Playwright config; CI configuration in `.github/workflows`.
- **Priority:** High.
- **Confidence:** Evidence-backed.

### Priority 1 — Strengthen the `lib/shopify` Provider Boundary

- **Evidence:** The README states the long-term intent is for alternative providers to swap `lib/shopify`. The directory is named generically (`shopify/`) but contains Shopify-specific GraphQL queries, Shopify-flavored type names (`ShopifyProduct`, `ShopifyCartOperation`), and Shopify-specific cache tag taxonomy (`TAGS.collections`, `TAGS.products`, `TAGS.cart`).
- **Limitation:** Forking the entire repository is the only documented path to a non-Shopify provider. The Shopify Storefront API version is hardcoded (`/api/2023-01/graphql.json`).
- **Proposed direction:** Introduce an explicit provider interface (e.g., `commerceProvider` with `getProduct`, `getCollection`, `getCart`, etc.) implemented by `lib/shopify` and selected at startup. Move Shopify-specific types and constants behind the boundary. Externalize the Storefront API version to an environment variable.
- **Expected benefit:** Aligns the implementation with the documented provider strategy. Reduces the cost of supporting additional providers. Decouples business logic from the Storefront API version.
- **Prerequisites:** Agreement on the interface shape; a target provider for a proof-of-concept fork; an upgrade plan for in-flight consumers.
- **Priority:** High.
- **Confidence:** Evidence-backed (the README and the directory naming both point to this intent).

### Priority 1 — Fix the Sitemap Environment Coupling and Error Exposure

- **Evidence:** `app/sitemap.ts` calls `validateEnvironmentVariables()` at the top of the function and throws `JSON.stringify(error, null, 2)` on failure.
- **Limitation:** The SEO surface is non-functional without Shopify credentials, and a sitemap failure surfaces internal error data.
- **Proposed direction:** Make sitemap generation tolerant of missing configuration by returning a minimal route set when `SHOPIFY_STORE_DOMAIN` is unset, and log structured errors without serializing them to the response.
- **Expected benefit:** Preview deployments, documentation sites, and template exploration all work without requiring a real store. Search engines always receive a valid `sitemap.xml`.
- **Prerequisites:** None.
- **Priority:** High.
- **Confidence:** Evidence-backed.

### Priority 2 — Harden Webhook Authentication

- **Evidence:** `lib/shopify/index.ts` authenticates revalidation webhooks via a query-string secret; no HMAC verification, no rate limiting, no method enforcement.
- **Limitation:** A leaked URL parameter becomes a permanent credential. There is no protection against a flood of valid revalidation requests.
- **Proposed direction:** Move to Shopify's HMAC-signed webhook verification, validate the `x-shopify-hmac-sha256` header against `SHOPIFY_WEBHOOK_SECRET`, restrict the route to `POST`, and add basic rate limiting or upstream protection.
- **Expected benefit:** Webhook spoofing is closed; replay storms are bounded; secret leakage through URLs is eliminated.
- **Prerequisites:** A migration of the existing shared-secret URLs to HMAC-signed URLs in the Shopify admin.
- **Priority:** Medium-to-high.
- **Confidence:** Evidence-backed.

### Priority 2 — Add Real Search

- **Evidence:** `lib/shopify/queries/product.ts` hardcodes `first: 100`; `app/search/page.tsx` forwards a single `q` parameter; there is no faceted filter, no type-ahead, and no pagination.
- **Limitation:** Any catalog beyond a few dozen products will return a truncated, unsorted, unfiltered result. The URL-based search cannot expose the underlying variant and option data for filtering.
- **Proposed direction:** Introduce a search provider abstraction (matching the planned provider boundary) with an initial implementation that uses Shopify's Storefront API search. Add faceted filters (price, availability, options), pagination, and structured sort key handling. The README already points to Orama as an integration; a first-class search abstraction would let Orama be selected as an alternative.
- **Expected benefit:** Functional search for real catalogs; foundation for type-ahead and "did you mean"; clearer separation between the data layer and the search experience.
- **Prerequisites:** Decision on whether to use the Storefront API search or a third-party provider; agreement on the facet model.
- **Priority:** Medium-to-high.
- **Confidence:** Evidence-backed.

### Priority 2 — Introduce Server-Side Cart Identity Invariants

- **Evidence:** `app/layout.tsx` passes a non-awaited `getCart()` promise to `CartProvider`; `components/cart/modal.tsx` calls `createCartAndSetCookie()` from a client `useEffect`; `components/cart/actions.ts` reads `cartId` from cookies before calling `addToCart`.
- **Limitation:** The window between first render and cart creation has no test or invariant. A future change to `actions.ts` or `cart-context.tsx` could re-introduce a race that fails silently or, worse, attaches items to the wrong cart.
- **Proposed direction:** Centralize the cart lifecycle in a single server-side helper that ensures a cart exists before any cart mutation. Use a Server Action to materialize a cart lazily on first interaction, and remove the client-side `createCartAndSetCookie()` from `CartModal`. Cover the flow with an integration test.
- **Expected benefit:** Predictable cart state across browsers, slower networks, and concurrent tabs; elimination of a silent failure mode.
- **Prerequisites:** Agreement on the cart-materialization trigger (first add vs. first render).
- **Priority:** Medium.
- **Confidence:** Strongly justified.

### Priority 2 — Observability and Telemetry

- **Evidence:** No logging, no error reporting, no performance marks; `app/error.tsx` displays a generic message with no log correlation; `app/sitemap.ts` serializes errors to the response body.
- **Limitation:** Production failures are invisible. The cache webhook path can fail silently and the cache will be stale for a day.
- **Proposed direction:** Add a small telemetry surface (log lines for webhook authentication, cache misses, and revalidation; an error boundary that reports to a configurable sink; structured error types in the data layer). Avoid premature adoption of a heavy SDK.
- **Expected benefit:** Webhook failures are observable; cache misses are diagnosable; error rates are trackable.
- **Prerequisites:** Choice of telemetry sink (or a pluggable interface).
- **Priority:** Medium.
- **Confidence:** Evidence-backed.

### Priority 3 — Internationalization and Multi-Currency

- **Evidence:** No locale switcher, no translated strings, no per-locale route segment; the only `currencyCode` reference is in `Price` and in Shopify's money types.
- **Limitation:** The template is single-locale and single-currency at the UI layer even though the data layer is currency-aware.
- **Proposed direction:** Add a `locale` route segment or middleware-driven locale resolution, surface a language switcher, and introduce a translation abstraction around the user-visible strings in components (currently inline). The Shopify Storefront API supports multi-currency and translated content, but the application must opt in.
- **Expected benefit:** The template addresses international markets directly. The Shopify data layer already carries the necessary fields.
- **Prerequisites:** Decision on routing strategy (`/[locale]/...` vs. middleware); translation file format.
- **Priority:** Medium-to-low (depends on product strategy).
- **Confidence:** Exploratory.

### Priority 3 — Customer Accounts and Order History

- **Evidence:** No account-related routes or actions; the cart is anonymous and identified only by a cookie.
- **Limitation:** The application cannot expose order history, saved addresses, wishlists, or reorder.
- **Proposed direction:** Add a Customer Account API integration (Shopify's preferred headless account surface) and the corresponding routes (`/account`, `/account/orders`, etc.). Reuse the `commerceProvider` interface from the provider-boundary work so a non-Shopify provider can plug in equivalent functionality.
- **Expected benefit:** Moves the template from a single-session storefront to a recurring-customer storefront.
- **Prerequisites:** Shopify Customer Account API access on the target store; provider-boundary work.
- **Priority:** Long-term.
- **Confidence:** Strongly justified.

### Priority 3 — Replace the Hardcoded "Hidden" Convention with Configuration

- **Evidence:** `lib/shopify/index.ts` filters collections by `handle.startsWith("hidden")`; `components/grid/three-items.tsx` and `components/carousel.tsx` reference `hidden-homepage-featured-items` and `hidden-homepage-carousel` by string literal.
- **Limitation:** The convention is implicit, undocumented beyond source comments, and a single point of failure across multiple files.
- **Proposed direction:** Replace the `hidden-` prefix with an explicit configuration object (e.g., a `homepage` config that names the carousel and featured-item collections). Keep a fallback for existing stores.
- **Expected benefit:** Onboarding is more obvious; the home page is decoupled from string-typed Shopify collection handles; the convention can be removed in a follow-up.
- **Prerequisites:** None.
- **Priority:** Medium-to-low.
- **Confidence:** Evidence-backed.

### Priority 3 — Replace Stringly-Typed Environment Access

- **Evidence:** `process.env.SHOPIFY_STORE_DOMAIN`, `SHOPIFY_STOREFRONT_ACCESS_TOKEN`, `SHOPIFY_REVALIDATION_SECRET`, `SITE_NAME`, `COMPANY_NAME`, `VERCEL_PROJECT_PRODUCTION_URL` are read across `lib/shopify/index.ts`, `app/layout.tsx`, `app/sitemap.ts`, `app/robots.ts`, `components/layout/footer.tsx`, `components/layout/navbar/index.tsx`, and `lib/utils.ts`.
- **Limitation:** There is no single source of truth, no validation at module load, and no type safety around optional vs. required variables. `SHOPIFY_STOREFRONT_ACCESS_TOKEN!` is asserted non-null without a check.
- **Proposed direction:** Introduce an `env` module that validates required variables once at startup, returns typed accessors, and centralizes defaults. Update consumers to import from the module.
- **Expected benefit:** Configuration errors are caught at boot rather than at request time; refactors are safer; the `validateEnvironmentVariables` function in `lib/utils.ts` becomes a single chokepoint.
- **Prerequisites:** None.
- **Priority:** Medium-to-low.
- **Confidence:** Strongly justified.

### Priority 4 — Documentation and Onboarding

- **Evidence:** `README.md` is concise; there is no `CONTRIBUTING.md`, no `ARCHITECTURE.md`, no in-repo explanation of the `hidden-` convention, no operator guide for the revalidation webhook.
- **Limitation:** New contributors and operators must reverse-engineer the conventions from source.
- **Proposed direction:** Add a short operator guide covering: required env vars, the revalidation webhook (with HMAC upgrade notes), the homepage collections, the cache tag taxonomy, and the deployment process. Add an architecture note describing the provider boundary and the cart lifecycle.
- **Expected benefit:** Faster onboarding; fewer misconfigurations in production.
- **Prerequisites:** None.
- **Priority:** Low.
- **Confidence:** Evidence-backed.

### Priority 4 — Resilience Hardening for `shopifyFetch`

- **Evidence:** `lib/shopify/index.ts` performs a single `fetch` with no timeout, no retry, and no circuit breaker. Errors are rethrown as opaque objects.
- **Limitation:** A slow or temporarily failing Storefront API will block SSR for the full platform timeout. There is no graceful degradation.
- **Proposed direction:** Add a per-request timeout via `AbortController`, an exponential backoff for idempotent reads (`getProduct`, `getCollection`, `getMenu`, `getProducts`), and a typed `CommerceError` that distinguishes configuration errors, upstream errors, and rate-limit errors. Optionally fall back to cached data on upstream failure.
- **Expected benefit:** More predictable latency; clearer error messages; better behavior during Shopify-side incidents.
- **Prerequisites:** Decision on whether retries are acceptable given the `unstable_cacheLife` cache layer (likely yes for reads, no for mutations).
- **Priority:** Long-term.
- **Confidence:** Strongly justified.

---

## 10. Phased Evolution Narrative

A reasonable phased order, given the dependencies between the directions above:

### Phase A — Stabilize the existing surface

- Fix the sitemap environment coupling and error exposure (Priority 1).
- Add unit tests for the pure helpers in `lib/shopify` and `lib/utils.ts` (Priority 1).
- Replace the hardcoded `hidden-` convention with a configuration object (Priority 3, low cost).
- Centralize environment access in a typed `env` module (Priority 3, low cost).

### Phase B — Make the integration trustworthy

- Harden webhook authentication to HMAC (Priority 2).
- Add observability: structured logs, error reporting, cache-miss counters (Priority 2).
- Add resilience to `shopifyFetch`: timeouts, typed errors, optional retries (Priority 4).
- Centralize the cart lifecycle to remove the client-side `createCartAndSetCookie()` race surface (Priority 2).

### Phase C — Expand capability

- Introduce the provider boundary and a proof-of-concept second provider (Priority 1).
- Replace the hardcoded `first: 100` search with a real search interface, including facets and pagination (Priority 2).
- Add Playwright E2E coverage for the core commerce flow (Priority 1).

### Phase D — Address longer-term product shape

- Customer accounts and order history (Priority 3).
- Internationalization and multi-currency (Priority 3).
- Documentation and onboarding guides (Priority 4).

---

## 11. Confidence and Speculation Boundaries

The recommendations above are distributed across the following confidence levels:

### Evidence-backed (high confidence)

- Sitemap environment coupling and error exposure (directly observed in `app/sitemap.ts`).
- Missing test infrastructure (directly observed in `package.json` and the file tree).
- Provider-boundary intent (directly stated in the README and supported by directory naming).
- Hidden-by-prefix convention (directly observed in `lib/shopify/index.ts` and the homepage components).
- Stringly-typed environment access (directly observed across multiple files).

### Strongly justified (medium-to-high confidence)

- Cart race-condition hardening (the race is mitigated today but has no invariant).
- Webhook HMAC upgrade (Shopify supports it; the current implementation does not use it).
- `shopifyFetch` resilience (no timeout/retry is evident; impact grows with traffic).
- Centralized `env` module (the current pattern is functional but not robust).

### Exploratory (lower confidence; should not be presented as necessary)

- Internationalization and multi-currency: appropriate if the product strategy expands globally.