# Testing Harness

## Overview

Next.js Commerce includes no automated test suite for application behavior verification. The repository ships as a starter template for headless Shopify storefronts, relying on manual verification, development-time testing, and code formatting quality gates rather than a structured testing program.

## Test Command and Execution

The repository defines a single test-related script in `package.json`:

```json
"test": "pnpm prettier:check"
```

This command invokes Prettier to check code formatting against the configured style rules. It does not execute any behavioral tests. Running `pnpm test` validates that all source files conform to the Prettier formatting standard but provides no verification of application behavior, component rendering, API correctness, or cart operations.

## Test Framework and Dependencies

No testing framework is installed in the project. The `package.json` dependency manifests contain no testing libraries.

### Declared Dependencies

| Package | Purpose |
|---------|---------|
| `@headlessui/react` | Headless UI component primitives |
| `@heroicons/react` | Icon library |
| `clsx` | Class name utility |
| `geist` | Geist font |
| `next` (15.6.0-canary.60) | Next.js framework |
| `react` (19.0.0) | React library |
| `react-dom` (19.0.0) | React DOM |
| `sonner` | Toast notifications |

### Declared DevDependencies

| Package | Purpose |
|---------|---------|
| `@tailwindcss-container-queries`, `@tailwindcss/postcss`, `@tailwindcss/typography` | Tailwind plugins |
| `@types/node`, `@types/react`, `@types/react-dom` | TypeScript type definitions |
| `postcss` | CSS processing |
| `prettier`, `prettier-plugin-tailwindcss` | Code formatting |
| `tailwindcss` | CSS framework |
| `typescript` (5.8.2) | TypeScript compiler |

### Notably Absent

- No Jest
- No Vitest
- No React Testing Library
- No Playwright
- No Cypress
- No unit testing, component testing, integration testing, or end-to-end testing libraries

The `pnpm-lock.yaml` references `@playwright/test` as an optional peer dependency of Next.js, but this is not installed, configured, or used by the project itself.

## Quality Gates

The only automated quality gate is Prettier formatting verification. The Prettier configuration includes:

- `prettier --write --ignore-unknown .` — Format all supported files
- `prettier --check --ignore-unknown .` — Verify formatting without modifying files

### Not Present

- No ESLint configuration or linting
- No TypeScript strictness enforcement beyond `tsconfig.json`
- No code coverage measurement
- No static analysis tooling
- No security scanning
- No build-time validation beyond `next build`

## Test Locations and Structure

The repository contains no test files, test directories, or test-related infrastructure:

| Search Pattern | Results |
|----------------|---------|
| `**/*.test.{ts,tsx,js,jsx}` | None found |
| `**/*.spec.{ts,tsx,js,jsx}` | None found |
| `**/test/**/*` | None found |
| `**/tests/**/*` | None found |
| `**/__tests__/**/*` | None found |
| `**/__mocks__/**/*` | None found |
| `**/fixtures/**/*` | None found |
| `**/jest.config.*` | None found |
| `**/vitest.config.*` | None found |
| `**/cypress/**/*` | None found |
| `**/playwright*` | None found |

The `.gitignore` file contains `/coverage` and `.playwright` entries, suggesting that test coverage reports and Playwright artifacts would be ignored if generated, but this infrastructure is never created.

## Application Behavior Verification

The absence of tests means no automated verification exists for the following behavioral areas.

### Not Evidenced by Tests

**Cart Operations**

- Creating a new cart
- Adding items to cart
- Removing items from cart
- Updating item quantities
- Calculating cart totals and taxes
- Persisting cart across sessions via cookies
- Optimistic UI updates

**Product Browsing**

- Product listing and pagination
- Collection filtering and sorting
- Product search
- Product detail page rendering
- Variant selection
- Price display formatting
- Related product recommendations

**API Layer**

- GraphQL query execution
- Shopify API error handling
- Environment variable validation
- Cache tag management
- Revalidation webhook processing
- Response reshaping and transformation

**UI Components**

- Modal open/close behavior
- Cart drawer rendering
- Carousel navigation
- Product grid layout
- Filter and sort controls
- Loading states
- Error boundaries

**Server Actions**

- `addItem` action
- `removeItem` action
- `updateItemQuantity` action
- `redirectToCheckout` action
- `createCartAndSetCookie` action

### Indirectly Covered

TypeScript strict mode (`strict: true` in `tsconfig.json`) provides limited type-safety verification at compile time. The `noUncheckedIndexedAccess` compiler option adds runtime safety for array access patterns. These compiler checks catch some categories of defects but do not verify runtime behavior.

The Prettier formatting check ensures consistent code style but does not validate application logic.

## Test Fixtures and Controlled Dependencies

No test fixtures, factories, mocks, stubs, or controlled dependencies exist in the repository.

The application interacts with several external systems that would require substitution for isolated testing:

| External System | Usage | Testing Approach |
|-----------------|-------|------------------|
| Shopify Storefront API | All data operations | Not mocked, not tested |
| Browser cookies | Cart persistence | Not tested |
| Next.js cache layer | Data caching with `unstable_cacheLife` | Not mocked, not tested |
| Next.js routing | Navigation and redirects | Not tested |
| React state management | Optimistic cart updates | Not tested |

## CI and Automated Execution

No GitHub Actions workflows or CI configuration exist in the repository. The `.github` directory is absent.

The only automated execution paths are:

1. **Local development:** `pnpm dev` starts the Next.js development server
2. **Production build:** `pnpm build` runs Next.js production compilation
3. **Code formatting check:** `pnpm test` runs Prettier verification
4. **Vercel deployment:** Repository is designed for Vercel deployment with environment variables

There is no automated test execution in CI, no deployment previews that run tests, and no integration with external testing services.

## Verification Coverage Model

| Category | Coverage |
|----------|----------|
| Unit tests | Not evidenced |
| Component tests | Not evidenced |
| Integration tests | Not evidenced |
| API tests | Not evidenced |
| End-to-end tests | Not evidenced |
| Contract tests | Not evidenced |
| Type checking | Partial (TypeScript compiler) |
| Code formatting | Partial (Prettier) |
| Build verification | Partial (`next build`) |

## Verification Gaps

The repository has significant verification gaps across all behavioral areas.

### Critical Gaps

1. **Cart operations are completely untested.** The entire cart lifecycle (create, add, remove, update, checkout redirect) has no automated verification.

2. **Shopify API integration is untested.** All GraphQL queries and mutations execute against the live Shopify API with no test doubles.

3. **Server Actions are untested.** All `"use server"` functions handle form submissions without behavioral tests.

4. **Error handling is untested.** Error paths in `shopifyFetch`, cart actions, and API routes have no verification.

5. **Cart context and optimistic updates are untested.** The React context for cart state management with `useOptimistic` is not verified.

### Moderate Gaps

6. **Component rendering is not verified.** All React components render without automated verification of output.

7. **Cache invalidation is not tested.** The `revalidateTag` calls and cache life configuration are not verified.

8. **Environment variable validation is not tested.** The `validateEnvironmentVariables` function in `lib/utils.ts` has no test coverage.

9. **Type guard functions are untested.** The `isShopifyError` and `isObject` functions in `lib/type-guards.ts` have no automated verification.

10. **Webhook revalidation is untested.** The `revalidate` function has no automated test coverage for secret validation or tag invalidation.

### Minor Gaps

11. **URL utilities are not tested.** The `createUrl` and `ensureStartsWith` functions have no tests.

12. **Cart state calculations are not tested.** The `calculateItemCost`, `updateCartTotals`, and reducer logic in `cart-context.tsx` have no verification.

13. **Price formatting is not verified.** The Price component behavior is untested.

## Type Safety as Partial Verification

The TypeScript configuration provides some compile-time verification:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

These compiler settings catch type mismatches, missing null checks, and inconsistent casing at compile time, providing limited protection against certain classes of defects. However, this does not constitute behavioral testing.

## Conclusion

Next.js Commerce is distributed as a production-ready starter template without an automated test suite. The repository relies on:

- Manual developer testing during customization
- TypeScript type checking for compile-time safety
- Prettier for code formatting consistency
- Next.js framework conventions
- Shopify API contracts for data shape expectations

The absence of automated tests means that:

- No behavioral verification exists for cart operations
- No component rendering tests exist
- No API integration tests exist
- No end-to-end workflows are automated
- No CI gates validate changes

Users of this template are expected to add their own testing infrastructure appropriate to their customization and deployment context. The repository provides the application structure but not the verification harness.